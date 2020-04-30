import time
import pytds

class AgentJobException(Exception):
  pass

def db_test_conn(db_spec):
  qy = 'select 1 as test'
  return db_qy(db_spec, qy)

def db_stmt(db_spec, stmt):
  '''Execute a SQL DDL/DML statement. Doesn't return anything.'''
  with pytds.connect(**db_spec) as conn:
    cursor = conn.cursor()
    cursor.execute(stmt)
    conn.commit()

def db_trunc_table(db_spec, table_name):
  stmt = 'truncate table ' + table_name
  db_stmt(db_spec, stmt) 

def db_executemany(db_spec, stmt, tuples):
  '''Execute a parameterized statement for a collection of rows.
  tuples should be a sequence of tuples (not maps).'''
  with pytds.connect(**db_spec) as conn:
    cursor = conn.cursor()
    cursor.executemany(stmt, tuples)
    conn.commit()

def parameterized_insert_stmt(table_name, data):
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
  stmt = parameterized_insert_stmt(table_name, data) 
  tuples = list(map(lambda mp: tuple([mp[k] for k in mp]), data))
  db_executemany(db_spec, stmt, tuples)

def db_start_job(db_spec, job_name):
  '''Start a SQL Server Agent job. Returns immediately.'''
  with pytds.connect(**db_spec) as conn:
    cursor = conn.cursor()
    cursor.callproc('msdb.dbo.sp_start_job', (job_name,))
    conn.commit()

def db_is_job_idle(db_spec, job_name):
  '''job_name should be a SQL Server Agent job name. Returns boolean.'''
  result = []
  with pytds.connect(**db_spec, as_dict=True) as conn:
    cursor = conn.cursor()
    stmt = "exec msdb.dbo.sp_help_job @job_name=N'" + job_name + "'"
    cursor.execute(stmt) 
    result = cursor.fetchall()
  return result[0]['current_execution_status'] == 4 # 4 means idle.

def db_last_run_succeeded(db_spec, job_name):
  '''job_name should be a SQL Server Agent job name. Returns boolean.'''
  result = []
  with pytds.connect(**db_spec, as_dict=True) as conn:
    cursor = conn.cursor()
    stmt = "exec msdb.dbo.sp_help_job @job_name=N'" + job_name + "'"
    cursor.execute(stmt) 
    result = cursor.fetchall()
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

