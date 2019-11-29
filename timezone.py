import requests
import time
import json
from datetime import datetime
from datetime import timedelta
import pytz

base_url = "http://worldtimeapi.org/api/"
datetime_format = "%Y-%m-%dT%H:%M:%S%z"

def to_datetime(date_string):
    #timezone = pytz.timezone(timezone_string)
    date = datetime.strptime(date_string, datetime_format)
    return date

def ordinal_day_of_month(date):
    #return 1, 2... (first, second (sunday) day of month)
    month = date.month
    index = 0
    newdate = date - timedelta(days = 7)
    while (newdate.month == month):
        index = index + 1
        newdate = newdate - timedelta(days = 7)
    return index

def weekday(date, timezone_string):
    # monday = 0, sunday = 6
    timezone = pytz.timezone(timezone_string)
    return date.astimezone(timezone).weekday()

def is_weekday_last_of_month(date):
    month = date.month
    newdate = date + timedelta(days = 7)
    return month != newdate.month

def get_timezone_list():
    timezoneJsonString = "{\n"
    r = requests.get(url = "%stimezone" %(base_url))
    json = r.json()
    counter = 0
    for timezone in json:
        timezoneJson = get_timezone_detail(timezone)
        if counter > 0:
            timezoneJsonString += ",\n"
        timezoneJsonString += timezoneJson 
        counter = counter + 1
        if counter == 2:
            break
        if counter % 10 == 0:
            time.sleep(10)
        else:
            time.sleep(1)
    timezoneJsonString += "\n}"
    return timezoneJsonString
       
def get_timezone_detail(timezone):
    print(timezone)
    r = requests.get(url = "%stimezone/%s" %(base_url, timezone))
    data = r.json()
    json_data = json.dumps(data, indent = 0)
    json_string = build_timezone_json_pretty_string(timezone, json_data, 4)
    #return json.dumps(data, indent = 8)
    return json_string

def build_timezone_json_pretty_string(timezone_string, timezone_json, indent):
    begin_indent = " " * indent
    json_string = begin_indent + '"' + timezone_string + '": {\n'
    lines = timezone_json.splitlines()
    for line in lines:
        if len(line) > 0:
            if line == "{" or line == "}":
                continue
            json_string += begin_indent + begin_indent + line + "\n"
    json_string += begin_indent + "}"
    return json_string
timezoneString = get_timezone_list()
print(timezoneString)
#file = open("timezone.json", "w")
#file.write(timezoneString)
#file.close()

