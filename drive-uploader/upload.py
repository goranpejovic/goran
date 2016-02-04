#!/usr/bin/python
# Google Drive Python Uploader script
# Author: Goran Pejovic <goran@itn.me>
#
# Should work on python 2.6 and 2.7. Python 3 not tested.
# Use this script to upload files to Google drive.
# Get OAuth 2.0 keys from https://console.developers.google.com/
# Create new Project, enable Drive API, go to Credentials,
# create new OAuth2 credential and download JSON.
# Place it in same folder as script and rename it to "client_secrets.json"
# First time you run Uploader it will ask you to paste URL in web browser and
# ask you to paste String from the browser back to the script.
# It will store authentication token in ~/.credentials/python-gdrive.json.
#
# Dependencies install google-api-python-client using pip or easy install:
# easy_install --upgrade google-api-python-client
#
# use ./upload.py -h to see flags

import httplib2
import os, sys, getopt

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from apiclient.http import MediaFileUpload

CLIENT_SECRET_FILE = 'client_secrets.json'
CREDENTIALS_FILE = 'credentials.json'
APPLICATION_NAME = 'GDrive Uploader'
SCOPES = 'https://www.googleapis.com/auth/drive'
UPLOADFOLDER = 'FOLDER_UUID'

# Message describing how to use the script.
USAGE = """
Flags:
	-h - help screen
	-f <filename> - filename you want to upload
	-c - convert file to Google Doc format after upload
	-t <title> - title of the file in Drive
	-d - upload to "Mail Lists" directory in Drive (folder ID in UPLOADFOLDER var)
		 by default file is uploaded to root of GDrive


Usage examples:
	$ python upload.py -f <filename>
	$ python upload.py -f <filename> -c
	$ python upload.py -f <filename> -c -t "My File 1"
	$ python upload.py -f <filename> -c -t "My File 1" -d
"""

try:
	import argparse
	flags = argparse.Namespace()
	flags.logging_level = 'ERROR'
	flags.auth_host_name = 'localhost'
	flags.auth_host_port = [8080, 8090]
	flags.noauth_local_webserver = True
except ImportError:
	flags = None

def get_credentials():
	# Store credentials in ~/.credentials/python-gdrive.json
	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir,'python-gdrive.json')

	# Use client_secrets.json to authenticate and store credentials
	store = oauth2client.file.Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else: # Needed only for compatibility with Python 2.6
			credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)
	return credentials

def upload(filename,convert,DEFAULT_TITLE,parent_id):
	# Authorize with Google
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('drive','v2', http=http)
	# Insert a file
	media_body = MediaFileUpload(filename, resumable=True)
	body = {
		'title': DEFAULT_TITLE,
		'description': DEFAULT_TITLE
	}

	if parent_id:
		body['parents'] = [{'id': parent_id}, ]

	# Build a request to upload and execute it
	file = service.files().insert(body=body,media_body=media_body,convert=convert).execute()

	print "Upload successful."

def main(argv):
	CONVERT = False
	filename = None
	DIRECTORY = None

	# check flags
	try:
		opts, args = getopt.getopt(argv,"hf:ct:d",["file="])
	except getopt.GetoptError:
		print USAGE
		sys.exit(2)
	for opt, arg in opts:
		# help flag
		if opt == '-h':
			print USAGE
			sys.exit()
		# set filename with -f flag
		elif opt in ("-f", "--file"):
			filename = arg
			# set default title to original filename
			DEFAULT_TITLE = filename.split("/")[-1]
			DIRECTORY = None
		elif opt in ("-c"):
			CONVERT = True
		elif opt in ("-t"):
			DEFAULT_TITLE = arg
		elif opt in ("-d"):
			DIRECTORY = UPLOADFOLDER
		else:
			print USAGE

    # call upload() function and pass it filename that has been set with opt
	if (filename):
		try:
			upload(filename,CONVERT,DEFAULT_TITLE,DIRECTORY)
		# usually file not found exception
		except IOError as e:
			print "I/O error({0}): {1}".format(e.errno, e.strerror)
		# file has to have extension, if not ResumableUploadError is thrown
		# Bad Request HttpError if file cannot be converted to GDoc
		# and other errors
		except:
			print "Error:", sys.exc_info()[1]
	else:
		print USAGE

if __name__ == '__main__':
	main(sys.argv[1:])
