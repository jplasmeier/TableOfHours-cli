"""
Entry point of TableOfHours
"""

import calendar_assets
import datetime


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
    # this shouldn't happen, but should return a general
    # message in case it does
    else:
        return "tidings"


def get_username():
    return "J"


def main_menu():
    print("Please choose an option (by number):")
    print("1. Create new event")
    print("2. Edit existing event")
    print("3. List goals")
    print("4. Create new goal")
    print("5. Edit existing goal")
    choice = input()
    if choice == 1:
        pass
    if choice == 2:
        pass
    if choice == 3:
        pass
    if choice == 4:
        pass
    if choice == 5:
        pass


def main():
    dt = datetime.datetime.now()
    part_of_day = get_part_of_day(dt)
    username = get_username()
    print("Good {0}, {1}.".format(part_of_day, username))
    print(dt.strftime("Today is %A, %B %d %Y."))
    calendar_assets.list_daily_events()
    main_menu()


if __name__ == '__main__':
    main()