import argparse
import json
import aoulib as aou

#-------------------------------------------------------------------------------
# Site-specific configuration

PAIR_ORGANIZATION_PARAM = {'organization': 'COLUMBIA_WEILL'}

#-------------------------------------------------------------------------------

def slurpjson(fname):
  with open(fname, 'r') as f:
    return json.loads(f.read())

#-------------------------------------------------------------------------------

def main():
  p = argparse.ArgumentParser()
  p.add_argument('--aou-api-spec',
                 help='Path to a custom aou-api-spec JSON file.',
                 default=None)
  p.add_argument('--db-spec',
                 help='Path to a custom db-spec JSON file.',
                 default=None)
  p.add_argument('--maxrows',
                 type=int,
                 help='Maximum amount of rows to retrieve (approx).',
                 default=None)
  args = p.parse_args()
  api_spec_fname = (args.aou_api_spec if args.aou_api_spec
                    else 'enclave/aou-api-spec.json')
  db_spec_fname = args.db_spec if args.db_spec else 'enclave/db-spec.json'
  api_spec = slurpjson(api_spec_fname)
  db_spec = slurpjson(db_spec_fname)
  maxrows = args.maxrows if args.maxrows else None
  result = aou.etl.api2db(api_spec, db_spec, maxrows, PAIRED_ORGANIZATION_PARAM)

if __name__ == '__main__': main()

