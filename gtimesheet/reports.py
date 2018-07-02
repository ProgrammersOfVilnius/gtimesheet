"""
This module provides ReportsFacade class, that is facade for gTimeLog reports
implementation.

Setup tests.

    >>> import os
    >>> import io
    >>> from tempfile import NamedTemporaryFile
    >>> from .settings import Settings
    >>> f = NamedTemporaryFile('w', delete=False, encoding='utf-8')
    >>> f.write('''
    ... 2014-03-24 14:15: start
    ... 2014-03-24 18:14: project: task 1
    ...
    ... 2014-03-25 09:40: start
    ...
    ... 2014-03-31 15:48: start
    ... 2014-03-31 17:10: project: task 2
    ... 2014-03-31 17:38: project: task 3
    ... 2014-03-31 18:51: project: task 2
    ... ''')
    211
    >>> f.close()
    >>> cfg = Settings()
    >>> _ = cfg.set('email', 'me@example.com')
    >>> _ = cfg.set('name', 'Name')


Daily report test.

    >>> reports = ReportsFacade(cfg, f.name)
    >>> print(reports.daily('2014-03-31')) # doctest: +ELLIPSIS
    To: me@example.com
    ...
    Total work done: 3 hours 3 min
    ...
    <BLANKLINE>


Weekly report test.

    >>> reports = ReportsFacade(cfg, f.name)
    >>> print(reports.weekly('2014/13')) # doctest: +ELLIPSIS
    To: me@example.com
    Subject: Weekly report for Name (week 13)
    ...
    Total work done this week: 3:59
    ...
    <BLANKLINE>


Monthly report test.

    >>> reports = ReportsFacade(cfg, f.name)
    >>> print(reports.monthly('2014-03')) # doctest: +ELLIPSIS
    To: me@example.com
    ...
    Total work done this month: 7:02
    ...
    <BLANKLINE>


Tear down tests.

    >>> os.unlink(f.name)

Test weekly report issue on first week of the year, caused by:

    >>> data = io.StringIO('''
    ... 2016-01-04 09:00: start **
    ... 2016-01-04 09:14: gtimelog: write some tests
    ... 2016-01-04 09:10: gtimelog: whoops clock got all confused
    ... 2016-01-04 09:10: gtimelog: so this will need to be fixed
    ... ''')
    >>> reports = ReportsFacade(cfg, data)
    >>> print(reports.weekly('2016/01'))
    To: me@example.com
    Subject: Weekly report for Name (week 01)
    ...
    <BLANKLINE>

"""

import arrow
import datetime
import isoweek

from io import StringIO

from gtimelog.timelog import Reports
from gtimelog.timelog import TimeLog
from gtimelog.timelog import TimeWindow


class ReportsFacade(object):

    def __init__(self, cfg, filename, virtual_midnight=datetime.time(6, 0)):
        self.filename = filename
        self.virtual_midnight = virtual_midnight
        self.email = cfg.email
        self.who = cfg.name

    def window(self, min_dt, max_dt):
        tl = TimeLog(self.filename, self.virtual_midnight)
        return TimeWindow(tl, min_dt, max_dt, )

    def report(self, method, window):
        output = StringIO()
        reports = Reports(window)
        report = getattr(reports, method)
        report(output, self.email, self.who)
        return output.getvalue()

    def daily(self, day):
        oneday = datetime.timedelta(days=1)
        day = arrow.get(day).floor('day').naive
        day = datetime.datetime.combine(day, self.virtual_midnight)
        window = self.window(day, day + oneday)
        return self.report('daily_report', window)

    def weekly(self, week):
        day = isoweek.Week(*map(int, week.split('/', 2))).monday()
        day = datetime.datetime.combine(day, self.virtual_midnight)
        day = arrow.get(day)
        window = self.window(day.naive, day.replace(weeks=+1).naive)
        return self.report('weekly_report_categorized', window)

    def monthly(self, month):
        day = datetime.datetime.strptime(month, '%Y-%m')
        day = datetime.datetime.combine(day, self.virtual_midnight)
        day = arrow.get(day)
        window = self.window(day.naive, day.replace(months=+1).naive)
        return self.report('monthly_report_categorized', window)
