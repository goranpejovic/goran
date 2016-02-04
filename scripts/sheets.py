#!/usr/bin/python
import json, sys, os
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

path = os.path.dirname(os.path.realpath(__file__))

json_key = json.load(open(path+'/client_secrets.json'))
scope = ['https://spreadsheets.google.com/feeds']

# change to True to see Debug messages
DEBUG = False

def updateSheet(csv,sheet,length):
    linelen = 0
    counter1 = 1 # starting column in spreadsheet: A
    counter2 = 1 # starting row in spreadsheet: 1
    counter3 = 0 # helper for iterating through line entries
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)

    gc = gspread.authorize(credentials)

    wks = gc.open("ESnet Mailing Lists")
    worksheet = wks.get_worksheet(sheet)
    if worksheet is None:
        if sheet == 0:
            worksheet = wks.add_worksheet("ESnet Mailing Lists",200,8)
        elif sheet == 1:
            worksheet = wks.add_worksheet("ESnet Email Aliases",200,8)
        else:
            print "Error: spreadsheet does not exist"
            sys.exit(1)

    worksheet.resize(length,8)

    for i in csv:
        line = i.split(",")
        linelen = len(line)-1
        if (counter3 > linelen):
            counter3 = 0
        if (counter1 > linelen):
            counter1 = 1

        if (DEBUG):
            print "entry length (starting from 0): ", linelen
            print "line: ",  line
            print "counter1: ", counter1
            print "counter3: ", counter3
        while (counter3<=linelen):
            if (DEBUG):
                print "writing line: ", line[counter3]
            worksheet.update_cell(counter2, counter1, line[counter3].rstrip('\n'))
            counter3 += 1
            counter1 += 1

        counter2 += 1
