"""A tool for holidays.

Setup test case.

    >>> d = datetime.date
    >>> from StringIO import StringIO
    >>> holidays_f = StringIO('''
    ... 2014-02-16    event 1
    ... 2014-04-20/2  event 2
    ... # 2014-06-23    event 3
    ...
    ... 2014-06-24    event 4
    ... ''')

    >>> holidays = Holidays([holidays_f])

Check weekday:

    >>> holidays.is_holiday(d(2014, 2, 1))
    True

Check non weekday and non holiday:

    >>> holidays.is_holiday(d(2014, 2, 3))
    False

Check holiday event:

    >>> holidays.is_holiday(d(2014, 2, 16))
    True

Check holiday spaning few days:

    >>> holidays.is_holiday(d(2014, 4, 20))
    True
    >>> holidays.is_holiday(d(2014, 4, 21))
    True

Check commented linke:

    >>> holidays.is_holiday(d(2014, 6, 23))
    False

"""

import datetime

strptime = datetime.datetime.strptime
DAY = datetime.timedelta(days=1)


class Holidays(object):
    DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, files):
        self.holidays = set()
        for f in files:
            self.from_file(f)

    def parse_date_spec(self, spec):
        if '/' in spec:
            date, times = spec.split('/', 1)
            date = strptime(date, self.DATE_FORMAT).date()
            times = int(times)
            return [date + DAY*i for i in range(times)]
        else:
            date = strptime(spec, self.DATE_FORMAT).date()
            return [date]

    def from_file(self, f):
        for line in f:
            line = line.strip()
            if line.startswith('#') or line == '': continue
            date_spec, comment = line.split(None, 1)
            dates = self.parse_date_spec(date_spec)
            self.holidays.update(dates)

    def is_weekday(self, date):
        return date.isoweekday() in (6, 7)

    def is_holiday(self, date):
        date = date.date() if isinstance(date, datetime.datetime) else date
        return self.is_weekday(date) or date in self.holidays
