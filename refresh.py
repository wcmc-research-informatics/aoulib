from __future__ import division
from __future__ import print_function
import argparse
import json
import traceback
import aoulib as aou
import kickshaws as ks
import sqlsrvwrapper as s

'''
This script provides a command-line interface to the aoulib 
library's 'etl.api2db' function; this can be scheduled as a cron job for
fully automated refreshes from the API into a SQL Server database table,
with the data transformed into the HealthPro data format.

## Setting up and running refresh.py

### Requirements

* Known to work with Python 2.7.16 and a modern version of SQL Server.

### Virtualenv and dependencies

    mkdir venv
    virtualenv -p python2 venv
    source venv/bin/activate
    ./installdeps.sh

### Specification files

Two specification files need to be passed into refresh.py on the command line:

* AoU API specification file
* Database specification file

It's suggested to put 'spec' files in a folder named 'enclave'.

Create the `enclave` folder for storing specification files

    md enclave

#### AoU API specification file

Create  `enclave/aou-api-spec.json` with these contents:

    {"path-to-key-file": "/path/to/my/key.json",
     "base-url": "https://all-of-us-rdr-prod.appspot.com/rdr/v1/",
     "service-account": "X",
     "awardee": "X"}

_Note:_ please confirm the URL, but the one above will most likely be what you'll use.

#### Database specification file

Create a file named `enclave/db-spec.json` inside `enclave` with the contents:

    {"host": "X",
     "user": "X",
     "password": "X",
     "fully-qualified-table-name", "X"}

This will be used to connect to your SQL Server instance.

### A note about time zone 

* Uses `US/Eastern` timezone for conversions. Change this in `transform.py` if desired.

### Configuration items

See the site-specific configuration items a bit further below.

### Actually running refresh.py 

Example:

    python refresh.py --aou-api-spec-fpath enclave/aou-api-spec.json --db-spec-fpath enclave/p03.json

Finally, if you wish to conduct a test, you can specify a value for maxrows
(the program doesn't honor the value exactly but will be close). This way,
you can test your pipeline and configuration without waiting for an entire dataset
to load/process.

'''

#####################################
# Site-specific configuration items #
#####################################

PAIRED_ORGANIZATION_PARAM = {'organization': 'COLUMBIA_WEILL'}
DB_TABLE_NAME = 'dm_aou.dbo.healthpro2'

# You can optionally run a SQL Server agent job afterward.

SHOULD_RUN_AGENT_JOB = True
AGENT_JOB_NAME = 'DM_AOU REDCap Refresh Decoupled'
AGENT_JOB_TIMEOUT = 20000

#-------------------------------------------------------------------------------

log = ks.smart_logger()

def slurpjson(fname):
  with open(fname, 'r') as f:
    return json.loads(f.read())

#-------------------------------------------------------------------------------

def main():
  # (1) Process any command-line options.
  log.info('refresh.py started')
  try:
    p = argparse.ArgumentParser()
    p.add_argument('--aou-api-spec-fpath',
                   required=True,
                   help='Path to a custom aou-api-spec JSON file.')
    p.add_argument('--db-spec-fpath',
                   required=True,
                   help='Path to a custom db-spec JSON file.')
    p.add_argument('--maxrows',
                   type=int,
                   default=None,
                   help='Maximum amount of rows you wish to retrieve (approx).'\
                        'Useful for testing your setup/configuration.')
    args = p.parse_args()
    api_spec_fname = args.aou_api_spec_fpath
    db_spec_fname = args.db_spec_fpath
    api_spec = slurpjson(api_spec_fname)
    db_spec = slurpjson(db_spec_fname)
    maxrows = args.maxrows
  except Exception, ex:
    print(traceback.format_exc())
    log.error(traceback.format_exc())

  # (2) Ok, let's do the actual ETL process.
  print('Starting api2db.')
  log.info('Starting api2db.')
  try:
    result = aou.etl.api2db(api_spec, db_spec, DB_TABLE_NAME, 
                            PAIRED_ORGANIZATION_PARAM, maxrows)
    print('api2db ran OK.')
    log.info('api2db ran OK.')
  except Exception, ex:
    print(traceback.format_exc())
    log.error(traceback.format_exc())

  # (3) Optionally, run an agent job afterward.
  if SHOULD_RUN_AGENT_JOB:
    print('Starting agent job: {}'.format(AGENT_JOB_NAME))
    log.info('Starting agent job: {}'.format(AGENT_JOB_NAME))
    try:
      s.db_run_agent_job(db_spec, AGENT_JOB_NAME, AGENT_JOB_TIMEOUT)
      print('Agent job ran OK.') 
      log.info('Agent job ran OK.') 
    except Exception, ex:
      print(traceback.format_exc())
      log.error(traceback.format_exc())
  
  print('Done!')
  log.info('Done!')

#-------------------------------------------------------------------------------

if __name__ == '__main__': main()

