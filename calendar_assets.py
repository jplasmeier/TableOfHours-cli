"""
Classes for things that go on your calendar,
e.g. Events, Tasks, Errands, and Goals.
"""

import datetime

def get_timezone_string():
    now = datetime.datetime.now()
    utc_now = datetime.datetime.utcnow()
    timezone = utc_now.hour - now.hour
    if timezone < 0:
        timezone += 24
    timezone_string = '-0{0}00'.format(str(timezone))
    return timezone_string


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
    end_of_day_string = datetime_to_google_string(end_of_day)
    return end_of_day_string


def datetime_to_google_string(dt):
    return dt.isoformat() + get_timezone_string()


def new_event(service):
    print("Creating new event.")
    summary = input("Please enter the name/title of the event:")

    start_date_raw = input("Please enter the date (or none to use today's date). The format is: 01/31/1970")
    if start_date_raw == '':
        start_date = datetime.date.today()
    else:
        start_date = datetime.datetime.strptime(start_date_raw, "%m/%d/%Y")
    start_time_string = input("Please enter the start time in the format 11:59.")
    start_time = datetime.datetime.strptime(start_time_string, "%H:%M")
    start_dt = datetime.datetime.combine(start_date, start_time.time())

    end_date_raw = input("Please enter the end date (or none to use today's date). The format is: 01/31/1970")
    if end_date_raw == '':
        end_date = datetime.date.today()
    else:
        end_date = datetime.datetime.strptime(end_date_raw, "%m/%d/%Y")
    end_time_string = input("Please enter the end time in the format 11:59")
    end_time = datetime.datetime.strptime(end_time_string, "%H:%M")
    end_dt = datetime.datetime.combine(end_date, end_time.time())

    location = input("Please enter the location of the event:")

    # TODO: create valid Google Datetime format from supplied date and time
    # TODO: Especially time
    start = datetime_to_google_string(start_dt)
    end = datetime_to_google_string(end_dt)
    event = {'summary': summary, 'start': {'dateTime': start}, 'end': {'dateTime': end}, 'location': location}
    event = service.events().insert(calendarId='primary', body=event).execute()

    print('Event created: %s' % (event.get('htmlLink')))


def bucket_timed_events(timed_events):
    buckets = {}
    time_division = [0, 9, 12, 15, 18, 21]
    for time in time_division:
        buckets[time] = []

    for event in timed_events:
        dt = event_start_to_datetime(event['start'].get('dateTime', event['start'].get('date')))
        if dt.hour in range(0, 8):
            bucket = 0
        elif dt.hour in range(9, 11):
            bucket = 9
        elif dt.hour in range(12, 14):
            bucket = 12
        elif dt.hour in range(15, 17):
            bucket = 15
        elif dt.hour in range(18, 20):
            bucket = 18
        elif dt.hour in range(21, 23):
            bucket = 21
        else:
            bucket = 0

        buckets[bucket].append(event)

    return buckets


def print_pretty_timed_events(timed_events):
    print('Schedule: ')
    day_buckets = bucket_timed_events(timed_events)
    max_bucket = day_buckets[list(day_buckets.keys())[0]]
    for bucket in day_buckets:
        if len(day_buckets[bucket]) > len(max_bucket):
            max_bucket = day_buckets[bucket]

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


def list_daily_events(service):
    """
    Creates a Google Calendar API service object and outputs a list of the
    day's events on the user's calendar.
    """

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




