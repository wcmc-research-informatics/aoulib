import time
import pytds
import certifi

'''
==============================================================================

This module requires the following packages be installed:

    - python-tds(this is the package name for pytds)
    - pyOpenSSL

Also recommended:

    - bitarray

E.g.,

    pip install pyOpenSSL bitarray git+https://github.com/denisenkom/pytds

Or, in a requirements.txt file:

pyOpenSSL==19.1.0
certifi==2020.11.8
bitarray==1.5.3
python-tds @ git+https://github.com/denisenkom/pytds/#egg=python-tds


==============================================================================
'''

QUERY = 'query'
NONQUERY = 'nonquery'

# Nov 2020 not checking version; moved to latest version from git master branch.
# Require version 1.9.1 of pytds.
# Note: version 1.9.1 confusingly returns '1.9.0'.
#if pytds.__version__ != '1.9.0':
#    raise Exception('Needs pytds version 1.9.1; version {} is installed.'.format(
#                    pytds.__version__))

class AgentJobException(Exception):
  pass

class NoDatabaseSpecifiedException(Exception):
    '''Raised when db_spec is missing the `database` key-value pair
     but the called function required it.'''
    pass

class ConnectionNotSecureException(Exception):
    'Raised if secure db connection could not be established.'
    pass

# This query will return TRUE or FALSE (as a string).
qy_check_conn_encrypted = '''
    select encrypt_option
    from sys.dm_exec_connections
    where session_id = @@spid '''

def db_make_secure_conn_obj(db_spec, as_dict=True, autocommit=True):
    '''
    Returns a secure, encrypted db connection object. Caller is
    responsible for closing the connection.
    Might raise these exceptions:
        - NoDatabaseSpecifiedException
        - ConnectionNotSecureException (will close conn 
          automatically in this case).
        - pytds.connect can also raise exceptions.
    '''
    if 'database' not in db_spec:
        raise NoDatabaseSpecifiedException
    # Enforce TLS via `cafile` key-value pair. Note that pytds does not allow self-signed
    # certs so this will enforce cert verification as well.
    # See certifi documentation for more details on what `where()` does.
    db_spec['cafile'] = certifi.where()
    # Comment on 'login_timeout' and why we do both `test_conn` and `conn` below:
    # Create test_conn with default of 15 for login_timeout; however this also is
    # the connect_timeout and needs to be much larger in prod scenarios; so,
    # for actual conn, we'll use much larger value. 
    # A connection that fails indicates certficate issue and long timeout in 
    # that situation is not desirable (library will make retries).
    # Regarding login_timeout, see: https://github.com/denisenkom/pytds/issues/37
    # It prevents random errors, which pytds otherwise seems to have an issue with.
    test_conn = pytds.connect(**db_spec)
    # if no exception thrown, so far so good. This means server's certificate is OK.
    # So, close test_conn and do actual conn with different login_timeout value.
    test_conn.close()
    conn = pytds.connect(**db_spec,
                        as_dict=as_dict,
                        autocommit=autocommit,
                        login_timeout=1200)    
    cur = conn.cursor()
    # Now, ensure encrypted connection.
    cur.execute(qy_check_conn_encrypted)
    rslt = cur.fetchone()['encrypt_option']
    cur.close()
    if rslt != 'TRUE':
        # Conn not encrypted, so we bail.
        conn.close()
        raise ConnectionNotSecureException
    else:
        return conn

def _run(db_spec, sql, kind, as_dict=True):
    '''kind should be `query` or `nonquery` (see vars at top of file)'''
    conn = db_make_secure_conn_obj(db_spec, as_dict)
    cur = conn.cursor()
    cur.execute(sql)
    rslt = None
    if kind == QUERY:
        while cur.description == None:
            cur.nextset()
        rslt = cur.fetchall()
    elif kind == NONQUERY:
        pass
    else:
        raise Exception('unknown `kind` value of {} passed in'.format(kind))
    conn.close()
    return rslt

def db_qy(db_spec, qy, as_dict=True):
    return _run(db_spec, qy, QUERY, as_dict)

def db_stmt(db_spec, stmt, as_dict=True):
    '''Execute a SQL DDL/DML statement. Normally returns None.'''
    return _run(db_spec, stmt, NONQUERY, as_dict)

def db_get_version(db_spec):
    qy = 'select @@version'
    return db_qy(db_spec, qy)

def db_test_conn(db_spec):
    qy = 'select 1 as test'
    return db_qy(db_spec, qy)

def db_trunc_table(db_spec, table_name):
    stmt = 'truncate table ' + table_name
    db_stmt(db_spec, stmt) 

def db_executemany(db_spec, stmt, tuples):
    '''Execute a parameterized statement for a collection of rows.
    tuples should be a sequence of tuples (not maps).'''
    conn = db_make_secure_conn_obj(db_spec)
    cur = conn.cursor()
    cur.executemany(stmt, tuples)
    conn.close()

def db_drop_table(db_spec, schema, table):
    ddl = ddl_drop_table(schema, table)
    db_stmt(db_spec, ddl)

def make_fqtn(catalog, schema, table):
    '''Returns fully qualified table name as a string.'''
    return '[' + catalog + '].[' + schema + '].[' + table + ']'

def db_table_from_fqtn(fqtn, brackets=False):
    out = fqtn.split('.')[-1].replace('[','').replace(']','')
    if brackets:
        return '[' + out + ']'
    else:
        return out

def db_get_table_info(db_spec, schema, table):
    '''Returns data about a table's columns and data types.'''
    qy = ("select ordinal_position, column_name, data_type, "
          "character_maximum_length, is_nullable "
          "from information_schema.columns "
          "where table_schema ='{}' "
          "and table_name = '{}'".format(schema, table))
    return db_qy(db_spec, qy)

def ddl_drop_table(schema, table):
    qtn = '[' + schema + '].[' + table + ']'
    stmt = ("if object_id('{}', 'U') is not null drop table {}"
           ''.format(qtn, qtn))
    return stmt

def ddl_drop_view(schema, view):
    qtn = '[' + schema + '].[' + view + ']'
    stmt = ("if object_id('{}', 'V') is not null drop view {}"
           ''.format(qtn, qtn))
    return stmt

def _ddl_column_entries(table_info):
    '''Utility function to build out the portion of a DDL statement
    containing column entries.'''
    chartypes= ['varchar', 'nvarchar']
    ddl = ''
    for r in table_info:
        line = '[' + r['column_name'] + '] ' + r['data_type']
        #if r['character_maximum_length'] != -1:
        if r['data_type'] in chartypes:
            if r['character_maximum_length'] == -1:
                line += '(max)'
            else:
                line += '(' + str(r['character_maximum_length']) + ')'
        if r['is_nullable'] == 'YES':
            line += ' null'
        else: 
            line += ' not null'
        line += ',\n'
        ddl += line
    ddl = ddl[:-2] # Snip off the final trailing comma and newline.
    return ddl

def ddl_create_table(schema, table, table_info):
    '''
    Returns a ready-to-run DDL statment.
    Note: this handles our use cases, but could need enhancing to work 
    with data types that we don't work with presently.
    '''
    qtn = '[' + schema + '].[' + table + ']'
    ddl = 'create table {} (\n'.format(qtn)
    ddl += _ddl_column_entries(table_info)
    ddl += ')'
    return ddl

def db_create_table(db_spec, schema, table, table_info):
    ddl = ddl_create_table(schema, table, table_info)
    return db_stmt(db_spec, ddl)

def _parameterized_insert_stmt(table_name, data):
    '''data should be a sequence of maps.'''
    stmt = ('insert into ' + table_name
             + ' ([' 
             + '],['.join(data[0]) # All rows should have same keys.
             + ']) values ('
             + ','.join(list(map(lambda x: '%s', data[0])))
             + ')')
    return stmt

def db_insert_many(db_spec, table_name, data):
    '''Takes a seq of maps. Doesn't return anything.'''
    stmt = _parameterized_insert_stmt(table_name, data) 
    tuples = list(map(lambda mp: tuple([mp[k] for k in mp]), data))
    db_executemany(db_spec, stmt, tuples)

def db_table_does_exist(db_spec, qtn):
    '''Returns boolen.
    Argument `qtn` (qualified table name) should be 
    in 'schema.tablename' format.'''
    qy = ("if object_id('{}', 'U') is not null select 1 else select 0"
          "".format(qtn))
    rslt = db_qy(db_spec, qy)
    return rslt[0][0] == 1

def db_start_job(db_spec, job_name):
    '''Start a SQL Server Agent job. Returns immediately.'''
    conn = db_make_secure_conn_obj(db_spec)
    cur = conn.cursor()
    cur.callproc('msdb.dbo.sp_start_job', (job_name,))
    conn.close()

def db_is_job_idle(db_spec, job_name):
    '''job_name should be a SQL Server Agent job name. Returns boolean.'''
    result = []
    conn = db_make_secure_conn_obj(db_spec)
    cur = conn.cursor()
    stmt = "exec msdb.dbo.sp_help_job @job_name=N'" + job_name + "'"
    cur.execute(stmt) 
    result = cur.fetchall()
    conn.close()
    return result[0]['current_execution_status'] == 4 # 4 means idle.

def db_last_run_succeeded(db_spec, job_name):
    '''job_name should be a SQL Server Agent job name. Returns boolean.'''
    result = []
    conn = db_make_secure_conn_obj(db_spec)
    cursor = conn.cursor()
    stmt = "exec msdb.dbo.sp_help_job @job_name=N'" + job_name + "'"
    cursor.execute(stmt) 
    result = cursor.fetchall()
    conn.close()
    return result[0]['last_run_outcome'] == 1 # 1 means succeeded.

def db_run_agent_job(db_spec, job_name, timeout_threshold=60):
  '''Run an agent job in a synchronous fashion -- that is, this
  function will not return until the job has completed/failed OR the
  timeout_threshold amount of seconds has passed (will raise Exception
  in the latter case). Timeout default is 2 minutes. Note: the agent
  job might/will continue running even if timeout_threshold is passed.'''
  try:
    db_start_job(db_spec, job_name)
    # Below we poll to see if the job has finished; when finished we check if
    # it was successful. If the job is still running past the designated
    # threshold, then we raise an exception, with the assumption that something
    # is wrong.
    interval = 10 # Check every 10 seconds.
    havewaited = 0 # How long have we been waiting so far?
    while True:
      time.sleep(interval)
      if not db_is_job_idle(db_spec, job_name):
        havewaited += interval
        if havewaited > timeout_threshold:
          raise AgentJobException('Runtime for job [{}] has exceeded '\
                          'specified threshold of {} seconds.'\
                          ''.format(job_name, timeout_threshold))
        else:
          print('Waiting for job to finish ...')
          continue
      else:
        break
  except Exception as ex:
    raise AgentJobException('Exception occurred when attempting to run the Agent Job '
            '[{}]; details: {}'.format(job_name, str(ex)))
  if not db_last_run_succeeded(db_spec, job_name):
    raise AgentJobException('The Agent job [{}] did not run successfully. Check job history in SSMS.'\
                    ''.format(job_name))
  else:
    return True 

def db_get_table_info(db_spec, schema, table):
    '''Returns data about a table's columns and data types.'''
    if 'database' not in db_spec:
        raise NoDatabaseSpecifiedException
    qy = ("select ordinal_position, column_name, data_type, "
          "character_maximum_length, is_nullable "
          "from information_schema.columns "
          "where table_schema ='{}' "
          "and table_name = '{}'".format(schema, table))
    return db_qy(db_spec, qy)

