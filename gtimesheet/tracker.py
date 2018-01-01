import arrow
import datetime

from pathlib import Path

from .constants import VIRTUAL_MIDNIGHT


def schedule(entries, replog=None, virtual_midnight=VIRTUAL_MIDNIGHT,
             now=None):
    """Generates reports shedule.

    Setup tests.

        >>> from io import StringIO
        >>> from pprint import pprint as pp
        >>> now = datetime.datetime(2014, 3, 31, 9)

    Shedule for three days in one week, where last day is today.

        >>> entries = [
        ...     {'date1': '2014-03-25 15:48'},
        ...     {'date1': '2014-03-30 15:48'},
        ...     {'date1': '2014-03-31 15:48'},
        ... ]
        >>> pp(list(schedule(entries, now=now)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [('daily', '2014-03-25'), ('daily', '2014-03-30'),
         ('weekly', '2014/13')]

    One day that is today. Report for today can only be sent next day.

        >>> entries = [
        ...     {'date1': '2014-03-31 15:48'},
        ... ]
        >>> pp(list(schedule(entries, now=now)))
        []

    One day that is today, but before virtual midnight. If an entry is recorded
    on next day, but before midnight, it will be assigned to previous day
    report.

        >>> entries = [
        ...     {'date1': '2014-03-31 01:01'},
        ... ]
        >>> pp(list(schedule(entries, now=now)))
        [('daily', '2014-03-30'), ('weekly', '2014/13')]

    One day from previous month.

        >>> replog = ReportsLog(log=StringIO(), now=now)
        >>> entries = [
        ...     {'date1': '2014-02-03 01:01'},
        ... ]
        >>> pp(list(schedule(entries, replog, now=now)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [('daily', '2014-02-02'), ('weekly', '2014/05'),
         ('monthly', '2014-02')]

    Last week of year:

        >>> now = datetime.datetime(2016, 1, 4, 9, 30)
        >>> replog = ReportsLog(log=StringIO(), now=now)
        >>> entries = [
        ...     {'date1': '2015-12-31 09:00'},
        ...     {'date1': '2016-01-01 09:00'},
        ... ]
        >>> pp(list(schedule(entries, replog, now=now)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [('daily', '2015-12-31'),
         ('monthly', '2015-12'),
         ('daily', '2016-01-01'),
         ('weekly', '2015/53')]

        >>> now = datetime.datetime(2016, 1, 11, 9, 30)
        >>> replog = ReportsLog(log=StringIO(), now=now)
        >>> entries = [
        ...     {'date1': '2016-01-04 09:00'},
        ...     {'date1': '2016-01-05 09:00'},
        ...     {'date1': '2016-01-06 09:00'},
        ...     {'date1': '2016-01-07 09:00'},
        ...     {'date1': '2016-01-08 09:00'},
        ... ]
        >>> pp(list(schedule(entries, replog, now=now)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [('daily', '2016-01-04'),
         ('daily', '2016-01-05'),
         ('daily', '2016-01-06'),
         ('daily', '2016-01-07'),
         ('daily', '2016-01-08'),
         ('weekly', '2016/01')]


    """
    now = now or datetime.datetime.now()
    replog = replog or ReportsLog(now=now)
    now = arrow.get(now).floor('day').naive
    now_week = '%d/%02d' % tuple(now.isocalendar()[:2])
    now_month = now.strftime('%Y-%m')
    last_month = last_week = None

    can_yield = lambda last, current, now: (
        last is not None and last != current and
        last not in replog and now > last
    )

    for entry in entries:
        day = arrow.get(entry['date1'], 'YYYY-MM-DD HH:mm')

        if day.naive.time() > virtual_midnight:
            day = day.floor('day').naive
        else:
            day = day.floor('day').replace(days=-1).naive

        week = '%d/%02d' % tuple(day.isocalendar()[:2])
        if can_yield(last_week, week, now_week):
            yield replog.add('weekly', last_week)
        last_week = week

        month = day.strftime('%Y-%m')
        if can_yield(last_month, month, now_month):
            yield replog.add('monthly', last_month)
        last_month = month

        f_day = day.strftime('%Y-%m-%d')
        if f_day not in replog and now > day:
            yield replog.add('daily', f_day)

    if can_yield(last_week, None, now_week):
        yield replog.add('weekly', last_week)

    if can_yield(last_month, None, now_month):
        yield replog.add('monthly', last_month)


def read_sent_reports(f):
    """Read sent reports log file and retur set of sent reports.

        >>> from io import StringIO
        >>> sentreports = StringIO('''
        ... 2014-06-04 15:18:59,monthly,2014-05
        ... ''')

        >>> read_sent_reports(sentreports)
        set(['2014-05'])

    """
    reports = set()
    for line in f:
        line = line.strip()
        if line:
            created, report, date = line.strip().split(',')
            reports.add(date)
    return reports


def get_sent_reports(filename):
    path = Path(filename)
    if path.exists():
        with path.open() as f:
            return read_sent_reports(f)
    else:
        return set()


class ReportsLog(object):
    def __init__(self, dates=None, log=None, now=None):
        self.dates = dates or set()
        self.log = log
        self.now = now or datetime.datetime.now()
        self.now = self.now.strftime('%Y-%m-%d %H:%M:%S')

    def __contains__(self, date):
        return date in self.dates

    def add(self, report, date):
        self.dates.add(date)
        return report, date

    def write(self, report, date):
        if self.log is not None:
            self.log.write(u'%s,%s,%s\n' % (self.now, report, date))
