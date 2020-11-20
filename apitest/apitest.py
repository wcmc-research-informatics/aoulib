from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

# pip install -r requirements.txt 

# Set path to your key.json
credentials = service_account.Credentials.from_service_account_file('../gcp/key.json')
scoped_credentials = credentials.with_scopes(
  ['https://www.googleapis.com/auth/cloud-platform',
   'https://www.googleapis.com/auth/userinfo.email'])
authed_session = AuthorizedSession(scoped_credentials)

# Set URL as appropriate for your site.
response = authed_session.get('https://all-of-us-rdr-prod.appspot.com/rdr/v1/ParticipantSummary?_count=10&_sort=lastModified&awardee=COLUMBIA')

print(response.request.headers)
print(response.request.body)
print(response.status_code)
print(response.headers)
print(response.text)

