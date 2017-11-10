"""
Classes for things that go on your calendar,
e.g. Events, Tasks, Errands, and Goals.
"""

import httplib2
import os
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

from apiclient import discovery
import datetime

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Table Of Hours'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    storage = Storage('my_credentials')

    if not storage.get():

        flow = flow_from_clientsecrets('client_secrets.json',
                                       scope='https://www.googleapis.com/auth/calendar',
                                       redirect_uri='http://localhost')
        auth_uri = flow.step1_get_authorize_url()
        print("Go here: " + auth_uri)
        code = input("Enter code from authorization flow.")
        credentials = flow.step2_exchange(code)
        storage.put(credentials)
    else:
        credentials = storage.get()
    return credentials


def get_pretty_time(ugly_time):
    """
    Get the time out of an ugly ISO string
    """
    ugly_time = ugly_time[:-3] + ugly_time[-2:]
    dt = datetime.datetime.strptime(ugly_time, '%Y-%m-%dT%H:%M:%S%z')
    pretty_time = dt.strftime('%H:%M')
    return pretty_time


def get_pretty_time_range(ugly_start, ugly_end):
    """
    Take an pair of ugly ISO format strings and make it look nice:
    5:00am - 7:00am
    """
    pretty_start = get_pretty_time(ugly_start)
    pretty_end = get_pretty_time(ugly_end)
    return pretty_start + " - " + pretty_end


def list_daily_events():
    """
    Creates a Google Calendar API service object and outputs a list of the
    day's events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.now()
    utc_now = datetime.datetime.utcnow()

    timezone = utc_now.hour - now.hour
    # TODO: fix that this only works in single-digit timezones
    timezone_string = '-0{0}00'.format(str(timezone))

    end_of_day = datetime.datetime(now.year, now.month, now.day, 23, 59, 59, 999999)
    now_string = now.isoformat() + timezone_string
    end_of_day_string = end_of_day.isoformat() + timezone_string

    eventsResult = service.events().list(
        calendarId='primary', timeMin=now_string, timeMax=end_of_day_string, maxResults=25, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['start'].get('date'))
        pretty_range = get_pretty_time_range(start, end)
        print(pretty_range, event['summary'])




