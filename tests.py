import unittest
import datetime
import pytz

from timezone import ordinal_day_of_month
from timezone import to_datetime
from timezone import local_weekday
from timezone import is_weekday_last_of_month

class DateTimeTests(unittest.TestCase):
    def test_ordinal_day_of_month(self):
        day1 = "2019-09-08T04:00:00+00:00"
        date = to_datetime(day1)
        ordinal = ordinal_day_of_month(date, 3600, 'America/Santiago')
        print(ordinal)
        assert(ordinal < 6)
    def test_weekday(self):
        day1 = "2019-11-10T00:32:11+00:00"
        date = to_datetime(day1)
        wd   = local_weekday(date, 'Australia/Sydney')
        print(wd)
        sunday = 6
        assert(wd == sunday)  

    def test_is_last(self):
        day1 = "2019-11-10T00:32:11+00:00"
        date = to_datetime(day1)
        wd   = is_weekday_last_of_month(date)
        print(wd)
        assert(wd == False) 

if __name__ == '__main__':
    unittest.main()