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

def ordinal_day_of_month(date, dst_offset, timezone_string):
    #return 1, 2... (first, second (sunday) day of month)
    month = local_month(date, timezone_string)
    index = 1
    newdate = date - timedelta(days = 7) - timedelta(seconds = dst_offset)
    print(dst_offset)
    while (local_month(newdate, timezone_string) == month):
        index = index + 1
        newdate = newdate - timedelta(days = 7)
    return index

def local_month(date, timezone_string):
    timezone = pytz.timezone(timezone_string)  
    month = date.astimezone(timezone).month
    return month

def local_hour(date, timezone_string):
    timezone = pytz.timezone(timezone_string)  
    hour = date.astimezone(timezone).hour
    return hour
def local_minute(date, timezone_string):
    timezone = pytz.timezone(timezone_string)  
    minute = date.astimezone(timezone).minute
    return minute

def local_weekday(date, timezone_string):
    # returns: 1 = sunday, 2 = monday, 7 = saturday
    timezone = pytz.timezone(timezone_string)  
    wd = date.astimezone(timezone).isoweekday() ## monday = 1, sunday = 7
    wd = wd + 1
    if wd == 8:  # sunday
        wd = 1
    return wd

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
    json_string = build_timezone_json_pretty_string(timezone, data, json_data, 4)
    return json_string

def build_timezone_json_pretty_string(timezone_string, timezone_json, timezone_json_string, indent):
    spaces = " " * indent
    json_string = spaces + '"' + timezone_string + '": {\n'
    if timezone_json["dst_offset"] and timezone_json["dst_from"] and timezone_json["dst_until"]:
        json_string += spaces + spaces + '"dst_offset": {}'.format(timezone_json["dst_offset"]) + ',\n'
        json_string += spaces + spaces + '"dst_from": {\n'
        json_string += build_dst_json(timezone_json["dst_from"], timezone_string, indent * 3, timezone_json["dst_offset"])
        json_string += spaces + spaces + "},\n"
        json_string += spaces + spaces + '"dst_until": {\n'
        json_string += build_dst_json(timezone_json["dst_until"], timezone_string, indent * 3, timezone_json["dst_offset"])
        json_string += spaces + spaces + "},\n"
    else:
        json_string += spaces + spaces + '"dst_offset": null,' + '\n'
        json_string += spaces + spaces + '"dst_from": null,' + '\n'
        json_string += spaces + spaces + '"dst_until": null,' + '\n'
        
    json_string += spaces + spaces + '"raw": {\n'
    lines = timezone_json_string.splitlines()
    for line in lines:
        if len(line) > 0:
            if line == "{" or line == "}":
                continue
            json_string += spaces + spaces + spaces + line + "\n"
    json_string += spaces + spaces + "}\n"
    json_string += spaces + "}"
    return json_string

def build_dst_json(dst_string, timezone_string, indent, dst_offset):
    spaces = " " * indent
    date = to_datetime(dst_string)
    month = local_month(date, timezone_string)
    hour = local_hour(date, timezone_string)
    minute = local_minute(date, timezone_string)
    ordinal = ordinal_day_of_month(date, dst_offset, timezone_string)
    wd = local_weekday(date, timezone_string)
    json_string = ""
    json_string += spaces + '"month": {},\n'.format(month)
    json_string += spaces + '"weekday_ordinal": {},\n'.format(ordinal)
    json_string += spaces + '"weekday": {},\n'.format(wd)
    json_string += spaces + '"hour": {},\n'.format(hour)
    json_string += spaces + '"minute": {}\n'.format(minute)
    return json_string

def save_to_file(filename, json_string):
    file = open(filename, "w")
    file.write(json_string)
    file.close()

if __name__ == '__main__':
    timezone_string = get_timezone_list()
    print(timezone_string)
    save_to_file('timezone2.json', timezone_string)
    