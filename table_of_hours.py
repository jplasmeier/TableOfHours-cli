"""
Entry point of TableOfHours
"""

import datetime


def get_part_of_day(current_time):
    """
    Returns a string representing what part of the day it is.
    :return:
    """
    current_hour = current_time.hour

    if current_hour < 5:
        return "night"
    if current_hour >= 5 and current_hour < 12:
        return "morning"
    if current_hour >= 12 and current_hour < 18:
        return "afternoon"
    if current_hour >= 18:
        return "evening"
    # this shouldn't happen, but should return a general
    # message in case it does
    else:
        return "tidings"


def get_username():
    return "J"


def main():
    dt = datetime.datetime.now()
    part_of_day = get_part_of_day(dt)
    username = get_username()
    print("Good {0}, {1}.".format(part_of_day, username))
    print(dt.strftime("Today is %A, %B %d %Y."))
    print("Your schedule for the day is:")


if __name__ == '__main__':
    main()