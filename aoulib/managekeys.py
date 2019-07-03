from __future__ import division
from __future__ import print_function
import os
import base64
import json
import datetime
from google.oauth2 import service_account # from google-auth
import googleapiclient.discovery # from google-api-python-client
import kickshaws as ks
import core as c

__all__ = [ 'get_key_id',
            'list_keys',
            'disp_keys', # display keys and creation dates in console
            'create_key',
            'create_key_to_file',
            'delete_key',
            'cycle_keys']

def _build_full_key_name(api_spec, private_key_id):
  '''Returns the 'name' of a key as it appears in the results
  returned from the get_list results (which come from GCP).'''
  return (
    'projects/'
    + api_spec['project']
    + '/serviceAccounts/'
    + api_spec['service-account']
    + '/keys/'
    + private_key_id)

def _id_from_key_name(key_name):
  return key_name[key_name.rfind('/')+1:]

def get_key_id(api_spec):
  '''Returns the private key ID of key file specified by api_spec'''
  return ks.slurp_json(api_spec['path-to-key-file'])['private_key_id']

def _make_svc(api_spec):
  '''Returns an object of type googleapiclient.discovery.Resource.'''
  creds = service_account.Credentials.from_service_account_file(
            filename=api_spec['path-to-key-file'], scopes=c.SCOPES)
  return googleapiclient.discovery.build('iam', 'v1', credentials=creds)

def list_keys(api_spec, detailed=False):
  '''Returns list of key IDs. If detailed is True,
  will instead return all key information returned from GCP.'''
  svc = _make_svc(api_spec)
  rslt = svc.projects().serviceAccounts().keys().list(
           name='projects/-/serviceAccounts/'
           + api_spec['service-account']).execute()
  if detailed == True:
    return rslt
  else:
    # Below, we parse out the private_key_id from the full key name.
    return [_id_from_key_name(mp['name']) for mp in rslt['keys']]

def disp_keys(api_spec):
  '''Output key IDs and creation dates to stdout. Asterisk (*)
  indicates this is the key in the key file specified by 
  api_spec.'''
  curr_key_id = get_key_id(api_spec)
  dat = list_keys(api_spec, detailed=True)['keys']
  #for row in sorted(dat, lambda x,y: x['validAfterTime'] < y['validAfterTime']):
  for row in dat:
    id = _id_from_key_name(row['name'])
    print(id + '\t\t'
          + row['validAfterTime']
          + (' * key-file key' if id == curr_key_id else ''))

def create_key(api_spec):
  '''Returns a map. Item of interest is 'privateKeyData' which is
  effectively the contents of a key-file -- it must be base-64 decoded 
  before writing out to the filesystem.'''
  svc = _make_svc(api_spec)
  return svc.projects().serviceAccounts().keys().create(
    name='projects/-/serviceAccounts/' + api_spec['service-account'],
    body={}).execute()

def create_key_to_file(api_spec):
  '''Creates a new key and writes it to a key file in the current
  working directory with filename having a unique timestamp. Returns
  the name of the new file.'''
  key_info = create_key(api_spec)
  key_file_contents = base64.b64decode(key_info['privateKeyData'])
  timestamp = str(datetime.datetime.now())
  fname = 'key-' + timestamp.replace(' ','-').replace(':','-') + '.json'
  ks.spit(fname, key_file_contents)
  return fname

def delete_key(api_spec, private_key_id):
  '''Returns an empty map (which is what GCP returns) if successful.'''
  svc = _make_svc(api_spec)
  key_name = _build_full_key_name(api_spec, private_key_id)
  return svc.projects().serviceAccounts().keys().delete(name=key_name).execute()

def cycle_keys(api_spec):
  '''This function:
  1. Creates a new service account key in GCP.
  2. Retires the current service account key in GCP.
  3. Adds ".old" to the end of the current key file's filename.
  4. Writes a new key file (same name as what was current).
  Returns a map containing the old and new key IDs.
  '''
  # Don't delete the old before you create the new!
  new_key_info = create_key(api_spec)
  old_private_key_id = ks.slurp_json(
                          api_spec['path-to-key-file'])['private_key_id']
  delete_key(api_spec, old_private_key_id)
  os.rename(api_spec['path-to-key-file'], api_spec['path-to-key-file'] + '.old')
  key_file_data = base64.b64decode(new_key_info['privateKeyData'])
  ks.spit(api_spec['path-to-key-file'], key_file_data)
  return {'old-private-key-id': old_private_key_id,
          'new-private-key-id': json.loads(key_file_data)['private_key_id']}

