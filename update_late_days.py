#!/usr/bin/env python3
import os
import csv
import sys
import math
from collections import Counter
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SPREADSHEET_ID = '1mJcYCHdniddMP1Nyj51Z6GkJFr_25-HGWzZUK1bJtuY'

def lateness_to_late_days(lateness):
    total_seconds = sum([60 ** i * int(num)
                        for i, num in enumerate(lateness.split(':')[::-1])])
    return math.ceil(total_seconds / (24 * 60 * 60))

def update_gradescope_late_days(filepath, email_to_late_days):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, filepath)
    try:
        with open(filename, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                lateness_str = row['Lateness (H:M:S)']
                if lateness_str and lateness_str != '00:00:00':
                    email_to_late_days[row['Email']] = max(
                        email_to_late_days.get(row['Email'], 0),
                        lateness_to_late_days(lateness_str)
                    )
    except Exception as e:
        print(f'Error while processing file {filename}: {e}')


def get_sheets_data(pset_num):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # The ID and range of a sample spreadsheet.
    
    SAMPLE_RANGE_NAME = f'Pset{pset_num}!A:B'

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    prev_late_days = Counter({x[0]: int(x[1]) for x in values[1:]})
    return prev_late_days


def write_sheets_data(rows, pset_num):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # The ID and range of a sample spreadsheet.
    SHEET_NAME = f'Pset{pset_num}'
    SAMPLE_RANGE_NAME = SHEET_NAME + '!A:B'

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": SHEET_NAME
                    }
                }
            }
        ]
    }

    response = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                       body=body).execute()
    body = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": response['replies'][0]['addSheet']['properties']['sheetId'],
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 1
                    },
                    "properties": {
                        "pixelSize": 200
                    },
                    "fields": "pixelSize"
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                       body=body).execute()

    body = {
        'values': rows
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
        valueInputOption='RAW', body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

def main(pset_num):
    prev_late_days = get_sheets_data(pset_num - 1)
    gradescope_csv_paths = [f'PSet_{pset_num}_Written__scores.csv', f'PSet_{pset_num}_Coding__scores.csv', f'PSet_{pset_num}_Extra__scores.csv']
    email_to_late_days = Counter()
    for filepath in gradescope_csv_paths:
        update_gradescope_late_days(filepath, email_to_late_days)
    new_late_days = prev_late_days + email_to_late_days

    values_to_write = [['Email', 'Late days used']] + [[x[0], x[1]]
                                                    for x in sorted(new_late_days.items())]
    write_sheets_data(values_to_write, pset_num)

if __name__ == '__main__':
    # Usage:
    # update_late_days.py <pset number>
    assert len(sys.argv) == 2
    main(int(sys.argv[1]))
