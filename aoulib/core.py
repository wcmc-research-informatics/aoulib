import json
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession
#from urllib.parse import urlencode
import urllib

#------------------------------------------------------------------------------

# See notes at end of file.

#------------------------------------------------------------------------------

SCOPES = ['https://www.googleapis.com/auth/cloud-platform',
          'https://www.googleapis.com/auth/userinfo.email']

#------------------------------------------------------------------------------

def make_authed_session(path_to_key_file):
  '''Returns an authorized session object that can be used to 
  makes calls to the AoU API.'''
  creds = Credentials.from_service_account_file(path_to_key_file)
  scoped_creds = creds.with_scopes(SCOPES)
  return AuthorizedSession(scoped_creds)

def get_last_modified_info(api_spec, session):
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

def get_records(api_spec, session, params=None, maxrows=None):
  '''
  This is the main function for retrieving data from the API.
  Arguments:
    o api_spec (required): see README.
    o session (required): an AuthorizedSession object; use the 
      make_authed_session function to make one.
    o params (optional): a map of key-value pairs which will be
      applied as URL parameters. If no params, it essentially will
      retrieve the entire dataset for your awardee.
      For details on possible params, see:
        - https://github.com/all-of-us/raw-data-repository#get-participantsummary
        - https://www.hl7.org/fhir/search.html
    o maxrows (optional): function will stop retrieving any additional pages
      once the rows accumulated surpasses this value.
  Returns:
    o A sequence of maps containing the dataset. 
  Also: see Note 1 (end of file) for FHIR bundle notes.
  Example usage:
    get_records(spec, sess, {'participantId':'X'}) # remove 'P' from ID first.
    get_records(spec, sess, {'organization': 'COLUMBIA_WEILL'})
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
              #+ '&' + urlencode(params)
              + '&' + urllib.urlencode(params)
              + '&count=100')
    return json.loads(session.get(full_url).text)
  #-----------------
  bundle = get_page()
  if bundle: resultset.extend(get_records_from_bundle(bundle))  
  while has_link(bundle) and ((maxrows is None) or (len(resultset) < maxrows)):
    next_link = bundle['link'][0]['url']
    bundle = get_page(next_link)
    if bundle: resultset.extend(get_records_from_bundle(bundle))  
  return resultset 

def compare_pmi_ids(api_spec, session):
  '''Test to confirm that the set of PMI IDs returned from the
  last-modified dataset (which has IDs and timestamps only) matches
  the set of PMI IDs retrieved when paging through the entire
  dataset via API.'''
  last_modified_info_set = get_last_modified_info(api_spec, session)
  full_set = get_records(api_spec, session)
  a = set([mp['participantId'] for mp in last_modified_info_set])
  print('Modified:')
  print(a)
  b = set([mp['participantId'] for mp in full_set])
  print('Full set:')
  print(b)
  return a == b

#------------------------------------------------------------------------------
'''

~~~~~~
Note 1: FHIR bundle for ParticipantSummary
~~~~~~
Details on the FHIR bundle returned from the API:
    o 'entry' is a list of maps
    o Each map in the entry list has two keys:
          - resource
          - fullUrl
    o Each 'resource' key has a value which is a map of actual data.
    o How to know you're on last page? The last 'page' will not 
      have a 'link' key.
#

~~~~~~
Note 2: PMI ID and the 'P' prefix
~~~~~~

When passing a PMI ID explicitly, eg:

   c.get_records(spec, sess, {'participantId':'X'})

...remove the 'P' from the beginning of the ID; you'll get this error 
if you leave the 'P' at the front:

  {'message': "Invalid value for property of type INTEGER: u'X'}

#


'''
#------------------------------------------------------------------------------

