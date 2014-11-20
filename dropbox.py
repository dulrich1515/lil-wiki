from __future__ import division
from __future__ import unicode_literals

# https://www.dropbox.com/developers/core/start/python

import dropbox

from django.conf import settings

app_key = settings.DROPBOX_APP_KEY
app_secret = settings.DROPBOX_APP_SECRET

flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

authorize_url = flow.start()

# Have the user sign in and authorize this token
authorize_url = flow.start()
print '1. Go to: ' + authorize_url
print '2. Click "Allow" (you might have to log in first)'
print '3. Copy the authorization code.'
code = raw_input("Enter the authorization code here: ").strip()

# This will fail if the user enters an invalid authorization code
access_token, user_id = flow.finish(code)

client = dropbox.client.DropboxClient(access_token)
print 'linked account: ', client.account_info()

## Uploading files

f = open('working-draft.txt', 'rb')
response = client.put_file('/magnum-opus.txt', f)
print "uploaded:", response

## Listing folders

folder_metadata = client.metadata('/')
print "metadata:", folder_metadata

## Downloading files

f, metadata = client.get_file_and_metadata('/magnum-opus.txt')
out = open('magnum-opus.txt', 'wb')
out.write(f.read())
out.close()
print metadata