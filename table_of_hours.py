"""
Entry point of TableOfHours
"""

import calendar_assets

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


def get_part_of_day(current_time):
    """
    Returns a string representing what part of the day it is.
    :return:
    """
    current_hour = current_time.hour

    if current_hour < 5:
        return "night"
    if 5 <= current_hour < 12:
        return "morning"
    if 12 <= current_hour < 18:
        return "afternoon"
    if current_hour >= 18:
        return "evening"
    # this shouldn't happen, but should return a general message in case it does
    else:
        return "tidings"


def get_username():
    return "J"


def main_menu(service):
    print("Please choose an option (by number):")
    print("1. Create new event")
    print("2. Edit existing event")
    print("3. List goals")
    print("4. Create new goal")
    print("5. Edit existing goal")
    choice = int(input())
    if choice == 1:
        # Create new event
        calendar_assets.new_event(service)
    if choice == 2:
        pass
    if choice == 3:
        pass
    if choice == 4:
        pass
    if choice == 5:
        pass


def main():
    # initialize GCal Service
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    dt = datetime.datetime.now()
    part_of_day = get_part_of_day(dt)
    username = get_username()
    print("Good {0}, {1}.".format(part_of_day, username))
    print(dt.strftime("Today is %A, %B %d %Y."))
    calendar_assets.list_daily_events(service)
    main_menu(service)


if __name__ == '__main__':
    main()