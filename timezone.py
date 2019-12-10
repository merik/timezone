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
    # returns: 1 = monday, 7 = sunday
    timezone = pytz.timezone(timezone_string)  
    wd = date.astimezone(timezone).isoweekday() ## monday = 1, sunday = 7
    return wd
def local_weekday_with_sunday_is_zero(date, timezone_string):
    wd = local_weekday(date, timezone_string)
    if wd == 7: #sunday
        wd = 0
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
    raw_offset = timezone_json["raw_offset"]
    if timezone_json["dst_offset"] and timezone_json["dst_from"] and timezone_json["dst_until"]:
        dst_offset = timezone_json["dst_offset"]
        dst_from = timezone_json["dst_from"]
        dst_until = timezone_json["dst_until"]

        hik_timezone_string = build_hikvision_timezone_string(
                timezone_identifier = timezone_string, 
                raw_offset = raw_offset, 
                dst_offset = dst_offset, 
                dst_string_from = dst_from, 
                dst_string_to = dst_until)

        json_string += spaces + spaces + '"hik_timezone": "' + hik_timezone_string + '",\n' 
        json_string += spaces + spaces + '"dh_timezone": {},\n'.format(build_dahua_timezone(raw_offset))
        json_string += spaces + spaces + '"gmt_timezone": "' + raw_offset_to_gmt_offset(raw_offset) + '",\n'
        json_string += spaces + spaces + '"dst_offset": {}'.format(timezone_json["dst_offset"]) + ',\n'
        json_string += spaces + spaces + '"dst_from": {\n'
        json_string += build_dst_json(timezone_json["dst_from"], timezone_string, indent * 3, timezone_json["dst_offset"])
        json_string += spaces + spaces + "},\n"
        json_string += spaces + spaces + '"dst_until": {\n'
        json_string += build_dst_json(timezone_json["dst_until"], timezone_string, indent * 3, timezone_json["dst_offset"])
        json_string += spaces + spaces + "},\n"
    else:
        hik_timezone_string = build_hikvision_timezone_string(
                timezone_identifier = timezone_string,
                raw_offset = raw_offset,
                dst_offset = 0,
                dst_string_from = "",
                dst_string_to = "")

        json_string += spaces + spaces + '"hik_timezone": "' + hik_timezone_string + '",\n' 
        json_string += spaces + spaces + '"dh_timezone": {},\n'.format(build_dahua_timezone(raw_offset))
        json_string += spaces + spaces + '"gmt_timezone": "' + raw_offset_to_gmt_offset(raw_offset) + '",\n'
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
    #dst_string: 2020-04-04T16:00:00+00:00
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

def build_hikvision_timezone_string(timezone_identifier, raw_offset, dst_offset, dst_string_from, dst_string_to):
    #-7200 -> #CST 2:00:00DST01:00:00,M10.1.0/03:00:00,M4.1.0/02:00:00
    timezone_string = raw_offset_to_cst_string(raw_offset)
    if dst_offset != 0:
        timezone_string += 'DST' + seconds_to_time(dst_offset, True)
        timezone_string += ',' + dst_string_to_posix(dst_string = dst_string_from, timezone_string = timezone_identifier, dst_offset = dst_offset)
        timezone_string += ',' + dst_string_to_posix(dst_string = dst_string_to, timezone_string = timezone_identifier, dst_offset = dst_offset)
    return timezone_string

def build_dahua_timezone(raw_offset):
    #0: "GMT+00:00" 1: "GMT+01:00" 2: "GMT+02:00" 3: "GMT+03:00" 
    #4: "GMT+03:30" 5: "GMT+04:00" 6: "GMT+04:30" 7: "GMT+05:00" 
    #8: "GMT+05:30" 9: "GMT+05:45" 10: "GMT+06:00" 11: "GMT+06:30" 
    #12: "GMT+07:00"
    #13: "GMT+08:00" 14: "GMT+09:00" 15: "GMT+09:30" 16: "GMT+10:00" 
    #17: "GMT+11:00" 18: "GMT+12:00" 19: "GMT+13:00" 20: "GMT-01:00" 
    #21: "GMT-02:00" 22: "GMT-03:00" 23: "GMT-03:30" 24: "GMT-04:00" 
    #25: "GMT-05:00" 26: "GMT-06:00" 27: "GMT-07:00" 28: "GMT-08:00" 
    #29: "GMT-09:00" 30: "GMT-10:00" 31: "GMT-11:00" 32: "GMT-12:00"
    gmtMinutes = [0, 60, 120, 180, 210, 240, 270, 300, 330, 345,
                    360, 390, 420, 480, 540, 570, 600, 660, 720, 780,
                    -60, -120, -180, -210, -240, -300, -360, -420, -480
                    -540, -600, -660, -720]
    timezone_index = -1
    for index, offset in enumerate(gmtMinutes, start=0):
        if offset * 60 == raw_offset:
            timezone_index = index
            break
    return timezone_index
        

def dst_string_to_posix(dst_string, timezone_string, dst_offset):
    #dst_string: 2020-04-04T16:00:00+00:00
    #posix_string: M4.1.0/02:00:00
    date = to_datetime(dst_string)
    month = local_month(date, timezone_string)
    hour = local_hour(date, timezone_string)
    minute = local_minute(date, timezone_string)
    ordinal = ordinal_day_of_month(date, dst_offset, timezone_string)
    wd = local_weekday_with_sunday_is_zero(date, timezone_string)
    ret = 'M{}.{}.{}/{:02d}:{:02d}:00'.format(month, ordinal, wd, hour, minute)
    return ret

def seconds_to_time(seconds, zeroed_hour):
    #3600: 01:00:00
    #36000: 10:00:00
    (minutes, second) = divmod(seconds, 60)
    (hour, minute) = divmod(minutes, 60)
    if zeroed_hour:
        return "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
    else:
        return "{}:{:02d}:{:02d}".format(hour, minute, second)

def raw_offset_to_cst_string(raw_offset):
    #-7200 -> CST 2:00:00
    #36000 -> CST-10:00:00
    #0 -> CST 0:00:00
    prefix = 'CST'
    if raw_offset > 0:
        prefix = prefix + '-'
    else:
        prefix = prefix + ' '
    return prefix + seconds_to_time(abs(raw_offset), False)

def raw_offset_to_gmt_offset(raw_offset):
    #3600 -> GMT+10:00
    (minutes, _) = divmod(raw_offset, 60)
    (hour, minute) = divmod(minutes, 60)
    if raw_offset >=0:
        return "GMT+{:02d}:{:02d}".format(hour, minute)
    else:
        return "GMT-{:02d}:{:02d}".format(hour, minute)

def save_to_file(filename, json_string):
    file = open(filename, "w")
    file.write(json_string)
    file.close()

if __name__ == '__main__':
    timezone_string = get_timezone_list()
    print(timezone_string)
    save_to_file('timezones.json', timezone_string)
    