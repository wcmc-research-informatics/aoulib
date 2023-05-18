import argparse
import json
import traceback
import aoulib as aou
import aoulib.db as s
from aoulib.db import AgentJobException
from aoulib.utils import *

import sys
if sys.version_info[0] < 3:
    raise Exception('Requires Python 3')

'''
# refresh.py

This script provides a command-line interface to the aoulib 
library's 'etl.api2db' function; this can be scheduled as a cron job for
fully automated refreshes from the API into a SQL Server database table,
with the data transformed into the HealthPro data format. A SQL Server
Agent job can also be run after.

## Setting up and running refresh.py

### Requirements

* Currently targets Python 3.9 and a modern version of SQL Server; the 
  SQL Server must serve a CA-issued certificate.

### Virtualenv and dependencies

    mkdir venv
    virtualenv -p pythonX.Y venv
    source venv/bin/activate
    ./installdeps.sh

Alternate invocation using a local install of virtualenv and python:

    ~/.local/bin/virtualenv -p ~/python-X.Y.Z/bin/pythonX.Y venv

### Specification files

Several specification files need to be passed into refresh.py on the command line:

* site-config file
* AoU API specification file
* Database specification file

It's suggested to put 'spec' files in a folder named 'enclave'.

Create the `enclave` folder for storing specification files

    mkdir enclave

#### AoU API specification file

Create  `enclave/aou-api-spec.json` with these contents:

    {"path-to-key-file": "/path/to/my/key.json",
     "base-url": "https://all-of-us-rdr-prod.appspot.com/rdr/v1/",
     "service-account": "X",
     "awardee": "X",
     "project": "all-of-us-ops-data-api-prod"}

_Note:_ please confirm the URL and project, but the one above will most likely be what you'll use.

#### Database specification file

Create a file named `enclave/db-spec.json` inside `enclave` with the contents:

    {"server": "X",
     "user": "X",
     "password": "X",
     "database": "DM_AOU"}

This will be used to connect to your SQL Server instance.

### A note about time zone 

* Uses `US/Eastern` timezone for conversions. Change this in `transform.py` if desired.

### Site-specific configuration items

There are some site-specific config items that need to be configured. Create the file
enclave/site-config.json with the following key-value pairs:

    {"should-send-emails": true,
     "from-email": "from email address",
     "to-email": "to email address",
     "paired-organization-params": {"organization": "COLUMBIA_WEILL"},
     "db-table-name": "dm_aou.dbo.healthpro2",
     "should-update-metadata": true,
     "metadata-table-name": "dm_aou.dbo.metadata",
     "should-run-agent-job": true,
     "agent-job-name": "DM_AOU REDCap Refresh Decoupled",
     "agent-job-table-name": "rc_prj_2525",
     "agent-job-timeout": 20000}

- Set should-send-emails to false (no quotes) to skip this.

- paired-organization-params -- These are query filters
you can use to filter the records queried from the API.
to null (no quotes) if no filtering is needed. 

- You can optionally run a SQL Server agent job afterward. Configure the 
last three items as desired. Set should-run-agent-job to false (no quotes)
to skip this.

- If you want to keep a record of when data is updated, set "should-update-metadata" to
true (no quotes) and create a table in your database like so:

    create table [dm_aou].[dbo].[metadata] (
      rid       bigint not null identity(1,1) primary key
    , ts        datetime default getdate() not null
    , tag       nvarchar(max) not null
    , details   nvarchar(max) null
    );

... or set "should-update-metadata" to false (no quotes) to skip this.

- "agent-job-table-name" is solely for recording the datetime in
the metadata table after the agent job runs.

### Actually running refresh.py 

Example:

    source venv/bin/activate
    python refresh.py --site-config enclave/site-config.json --aou-api-spec enclave/aou-api-spec.json --db-spec enclave/p03.json

... or, just use the provided shell script: ...

  ./runrefresh.sh    

Note: if you wish to conduct a test, you can specify a value for maxrows
(the program doesn't honor the value exactly but will be close). This way,
you can test your pipeline and configuration without waiting for an entire dataset
to load/process.

### Setting up as cron job

The included script runrefresh.sh shows how to 
initiate the virtual env first and then run the software. Customize for your
environment.

'''

#-------------------------------------------------------------------------------

log = smart_logger('refresh')


# email footer
emfooter = '''\n\n
Nexus articles:

AoU Email Notifications At A Glance:
https://nexus.weill.cornell.edu/display/ARCH/AoU+Email+Notifications+At+a+Glance

AoU Data Refresh and GCP Key Cycling
https://nexus.weill.cornell.edu/pages/viewpage.action?pageId=111677100 '''


#-------------------------------------------------------------------------------

def update_metadata_for(db_spec, cfg, table_name):
  # Get table name without db or schema portions, etc.
  tbl = table_name[table_name.rfind('.')+1:].replace('[','').replace(']','')
  # We're just inserting one row; but we use db_insert_many for convenience.
  s.db_insert_many(db_spec, cfg['metadata-table-name'],
                   [{'tag': tbl, 'details': 'refreshed'}])
  log.info('Inserted new row into metadata table.')

def main():
  # (1) Process any command-line options.
  log.info('========== refresh.py started ============')
  try:
    p = argparse.ArgumentParser()
    p.add_argument('--site-config',
                   required=True,
                   help='Path to a site-config file (see docs in refresh.py).')
    p.add_argument('--aou-api-spec',
                   required=True,
                   help='Path to a custom aou-api-spec JSON file.')
    p.add_argument('--db-spec',
                   required=True,
                   help='Path to a custom db-spec JSON file.')
    p.add_argument('--maxrows',
                   type=int,
                   default=None,
                   help='Maximum amount of rows you wish to retrieve (approx).'\
                        'Useful for testing your setup/configuration.')
    args = p.parse_args()

    cfg = slurpj(args.site_config)
    log.info('site config filename: ' + args.site_config)
    PAIRED_ORGANIZATION_PARAM = cfg['paired-organization-params']
    DB_TABLE_NAME = cfg['db-table-name']
    SHOULD_RUN_AGENT_JOB = cfg['should-run-agent-job']
    AGENT_JOB_NAME = cfg['agent-job-name']
    AGENT_JOB_TIMEOUT = cfg['agent-job-timeout']
    
    api_spec_fname = args.aou_api_spec
    log.info('api spec filename: ' + api_spec_fname)
    api_spec = slurpj(api_spec_fname)

    db_spec_fname = args.db_spec
    log.info('db spec filename: ' + db_spec_fname)
    db_spec = slurpj(db_spec_fname)

    maxrows = args.maxrows

    # (2) Ok, let's do the actual ETL process.
    print('Starting api2db.')
    log.info('Starting api2db.')
    result = aou.etl.api2db(api_spec, db_spec, DB_TABLE_NAME, 
                            PAIRED_ORGANIZATION_PARAM, maxrows)
    print('api2db ran OK.')
    log.info('api2db ran OK.')
    if cfg['should-update-metadata']:
      update_metadata_for(db_spec, cfg, DB_TABLE_NAME)

    # (3) Optionally, run an agent job afterward.
    if SHOULD_RUN_AGENT_JOB:
      try:
        print('Starting agent job: {}'.format(AGENT_JOB_NAME))
        log.info('Starting agent job: {}'.format(AGENT_JOB_NAME))
        s.db_run_agent_job(db_spec, AGENT_JOB_NAME, AGENT_JOB_TIMEOUT)
        print('Agent job ran OK.') 
        log.info('Agent job ran OK.') 
        if cfg['should-update-metadata']:
          update_metadata_for(db_spec, cfg, cfg['agent-job-table-name'])
      except AgentJobException as ex:
        log.error(str(ex) + '\n' +  traceback.format_exc())
        if cfg['should-send-emails']:
          send_email(
            frm=cfg['from-email'],
            to=cfg['to-email'],
            subj='AoU Data Refresh - Error - ' + today_as_str(),
            body=('HealthPro table for this run: ' + DB_TABLE_NAME + '\n\n' 
                  + 'AgentJobException occurred. ' + '\n\n' + str(ex)
                  + emfooter))
        # Bail.
        return
    else:
      log.info('Won\'t run agent job.')
    print('Done!')
    log.info('Done!')
    if cfg['should-send-emails']:
      send_email(
        frm=cfg['from-email'],
        to=cfg['to-email'],
        subj='AoU Data Refresh - Success - ' + today_as_str(),
        body=('HealthPro table for this run: ' + DB_TABLE_NAME + '\n\n' 
              + 'AoU data refresh success!' + emfooter))
  except Exception as ex:
      print(traceback.format_exc())
      log.error(traceback.format_exc())
      if cfg['should-send-emails']:
        send_email(
          frm=cfg['from-email'],
          to=cfg['to-email'],
          subj='AoU Data Refresh - Error - ' + today_as_str(),
          body=('HealthPro table for this run: ' + DB_TABLE_NAME + '\n\n' 
                + 'There was an issue during the AoU data refresh. '
                + 'Please check the log.' + emfooter))
  print('Exiting.')
  log.info('Exiting.')

#-------------------------------------------------------------------------------

if __name__ == '__main__': main()

