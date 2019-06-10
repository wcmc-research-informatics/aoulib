import json
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession

SCOPES = ['https://www.googleapis.com/auth/cloud-platform',
          'https://www.googleapis.com/auth/userinfo.email']

def make_authed_session(path_to_key_file):
  '''Returns an authorized session object that can be used to 
  makes calls to the AoU API.'''
  creds = Credentials.from_service_account_file(path_to_key_file)
  scoped_creds = creds.with_scopes(SCOPES)
  return AuthorizedSession(scoped_creds)

def get_modified_info(api_spec, session):
  '''Returns a dataset of PMI IDs and the date last modified for each.'''
  full_url = (api_spec['base-url'] 
              + 'ParticipantSummary/Modified'
              + '?'
              + 'awardee=' + api_spec['awardee']
              )
  return json.loads(session.get(full_url).text)

def spit(fname, dat):
  with open(fname, 'w') as f:
    f.write(dat)

def get_all_records(api_spec, session):
  '''
  Some notes about the FHIR bundles returned from the API:
    o Eentry is a list of maps
    o Each map in the entry list has two keys:
          - resource
          - fullUrl
    o Each resource key has a value which is a map of actual data.
    o the last 'page' will not have a link element.
    o How to know your'e on last page?  The last 'page' will not 
      have a 'link' key.
  '''
  resultset = []
  #-----------------
  def has_link(bundle):
    if not bundle: return False
    return ('link' in bundle and len(bundle['link']))
  #-----------------
  def get_records_from_bundle(bundle):
    return [mp['resource'] for mp in bundle['entry']]
  #-----------------
  def get_page(full_url=None):
    if not full_url:
      # Start with first page in this case.
      full_url = (api_spec['base-url'] 
              + 'ParticipantSummary'
              + '?'
              + 'awardee=' + api_spec['awardee']
              + '&count=200')
    return json.loads(session.get(full_url).text)
  #-----------------
  bundle = get_page()
  if bundle: resultset.extend(get_records_from_bundle(bundle))  
  
  while has_link(bundle):
    next_link = bundle['link'][0]['url']
    bundle = get_page(next_link)
    if bundle: resultset.extend(get_records_from_bundle(bundle))  
  return resultset 

def compare_pmi_ids(api_spec, session):
  '''Test to confirm that the set of PMI IDs returned from the
  Modified dataset (which has IDs and timestamps only) matches
  the set of PMI IDs retrieved when paging through the entire
  dataset via API.'''
  modified_info_set = get_modified_info(api_spec, session)
  full_set = get_all_records(api_spec, session)
  a = set([mp['participantId'] for mp in modified_info_set])
  print('Modified:')
  print(a)
  b = set([mp['participantId'] for mp in full_set])
  print('Full set:')
  print(b)
  return a == b

