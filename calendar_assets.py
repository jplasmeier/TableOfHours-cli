"""
Classes for things that go on your calendar,
e.g. Events, Tasks, Errands, and Goals.
"""

import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

from apiclient import discovery
import datetime

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Table Of Hours'


def get_timezone_string():
    now = datetime.datetime.now()
    utc_now = datetime.datetime.utcnow()
    timezone = utc_now.hour - now.hour
    timezone_string = '-0{0}00'.format(str(timezone))
    return timezone_string


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


def event_to_datetime_from_start(event):
    start = event['start'].get('dateTime', event['start'].get('date'))
    return event_start_to_datetime(start)


def event_start_to_datetime(event_time):
    """
    Returns a datetime object that represents the start time
    of a given event.
    """
    ugly_time = event_time[:-3] + event_time[-2:]
    return datetime.datetime.strptime(ugly_time, '%Y-%m-%dT%H:%M:%S%z')


def get_pretty_time(ugly_time):
    """
    Get the time out of an ugly ISO string
    """
    dt = event_start_to_datetime(ugly_time)
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


def get_timed_events(events):
    timed_events = []
    for event in events:
        try:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['start'].get('date'))
            pretty_range = get_pretty_time_range(start, end)
            event['pretty_range'] = pretty_range
            timed_events.append(event)
        except:
            pass
            # all day event
    return timed_events


def get_all_day_events(events):
    all_day_events = []
    for event in events:
        try:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['start'].get('date'))
            pretty_range = get_pretty_time_range(start, end)
        except:
            all_day_events.append(event)
    return all_day_events


def get_end_of_day_string():
    now = datetime.datetime.now()
    utc_now = datetime.datetime.utcnow()
    # TODO: fix that this only works in single-digit timezones
    end_of_day = datetime.datetime(now.year, now.month, now.day, 23, 59, 59, 999999)
    end_of_day_string = end_of_day.isoformat() + get_timezone_string()
    return end_of_day_string


def bucket_timed_events(timed_events):
    buckets = {}
    time_division = [0, 9, 12, 15, 18, 21]
    for time in time_division:
        buckets[time] = []

    for event in timed_events:
        dt = event_start_to_datetime(event['start'].get('dateTime', event['start'].get('date')))
        if dt.hour in [0, 8]:
            bucket = 0
        if dt.hour in [9, 11]:
            bucket = 9
        if dt.hour in [12, 14]:
            bucket = 12
        if dt.hour in [15, 17]:
            bucket = 15
        if dt.hour in [18, 20]:
            bucket = 18
        if dt.hour in [21, 23]:
            bucket = 21
        buckets[bucket].append(event)
    return buckets


def print_pretty_timed_events(timed_events):
    MIN_ENTRIES = 3
    MAX_ENTRIES = 6

    print('Schedule: ')
    day_buckets = bucket_timed_events(timed_events)
    max_bucket = day_buckets[list(day_buckets.keys())[0]]
    for bucket in day_buckets:
        if len(day_buckets[bucket]) > len(max_bucket):
            max_bucket = day_buckets[bucket]

    if len(max_bucket) < MIN_ENTRIES:
        number_of_entries = MIN_ENTRIES
    elif MAX_ENTRIES < len(max_bucket):
        number_of_entries = MAX_ENTRIES
    else:
        number_of_entries = len(max_bucket)

    for i in range(0, 23):
        if i in list(day_buckets.keys()):
            print(str(i) + ':00')
            bucket = day_buckets[i]
            for event in sorted(bucket, key=lambda e: e['start'].get('dateTime', e['start'].get('date'))):
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['start'].get('date'))
                pretty_range = get_pretty_time_range(start, end)
                print('---- ' + pretty_range + ' ' + event['summary'])
        else:
            print('----')


def list_daily_events():
    """
    Creates a Google Calendar API service object and outputs a list of the
    day's events on the user's calendar.
    """
    # initialize GCal Service
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # now and end_of_day in GCal format
    now_string = datetime.datetime.now().isoformat() + get_timezone_string()
    end_of_day_string = get_end_of_day_string()

    # Bulid list of calendars
    # incl. shared calendars from other accounts
    page_token = None
    calendars = []
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_entry in calendar_list['items']:
            calendars.append(calendar_entry['id'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    # get today's events from each calendar
    events = []
    for calendar in calendars:
        eventsResult = service.events().list(
            calendarId=calendar, timeMin=now_string, timeMax=end_of_day_string, maxResults=25, singleEvents=True,
            orderBy='startTime').execute()
        event_list = eventsResult.get('items', [])
        events.extend(event_list)

    # split into all day and timed events
    # timed events have a start and end time
    # TODO: handle events with only start time
    all_day_events = get_all_day_events(events)
    timed_events = sorted(get_timed_events(events), key=lambda e: e['start'].get('dateTime', e['start'].get('date')))

    # print out events
    if not all_day_events and not timed_events:
        print('No upcoming events found.')
    if all_day_events:
        print('All day events:')
        for event in all_day_events:
            print('---- ' + event['summary'])
    if timed_events:
        print_pretty_timed_events(timed_events)




