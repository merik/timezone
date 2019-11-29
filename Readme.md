# TimeZone Database Generator
Python script to extract timezone data from worldtimeapi.org and save to a json file
- Two apis are used:
    * GET https://worldtimeapi.org/api/timezone
    * GET http://worldtimeapi.org/api/timezone/area/location
- outputs a json file with format of:
```
    "Australia/Sydney": {
        "dst_offset": 3600,
        "dst_from": {
            "month": 10,
            "ordinal": 1,
            "weekday": 1,
            "hour": 3,
            "minute": 0
        },
        "dst_until": {
            "month": 4,
            "ordinal": 1,
            "weekday": 1,
            "hour": 2,
            "minute": 0
        },
        "raw": {
            "week_number": 48,
            "utc_offset": "+11:00",
            "utc_datetime": "2019-11-29T07:02:48.721875+00:00",
            "unixtime": 1575010968,
            "timezone": "Australia/Sydney",
            "raw_offset": 36000,
            "dst_until": "2020-04-04T16:00:00+00:00",
            "dst_offset": 3600,
            "dst_from": "2019-10-05T16:00:00+00:00",
            "dst": true,
            "day_of_year": 333,
            "day_of_week": 5,
            "datetime": "2019-11-29T18:02:48.721875+11:00",
            "client_ip": "220.233.199.48",
            "abbreviation": "AEDT"
        }
    },
```