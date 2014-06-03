"""
This module provides ReportsFacade class, that is facade for gTimeLog reports
implementation.

Setup tests.

    >>> import os
    >>> from tempfile import NamedTemporaryFile
    >>> f = NamedTemporaryFile(delete=False)
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
    >>> f.close()


Daily report test.

    >>> reports = ReportsFacade(f.name)
    >>> print reports.daily('2014-03-31') # doctest: +ELLIPSIS
    To: me@example.com
    ...
    Total work done: 3 hours 3 min
    ...
    <BLANKLINE>


Weekly report test.

    >>> reports = ReportsFacade(f.name)
    >>> print reports.weekly('2014/13') # doctest: +ELLIPSIS
    To: me@example.com
    ...
    Total work done this week: 3 hours 3 min
    ...
    <BLANKLINE>


Monthly report test.

    >>> reports = ReportsFacade(f.name)
    >>> print reports.monthly('2014-03') # doctest: +ELLIPSIS
    To: me@example.com
    ...
    Total work done this month: 7 hours 2 min
    ...
    <BLANKLINE>


Tear down tests.

    >>> os.unlink(f.name)

"""

import arrow
import datetime

from StringIO import StringIO

from gtimelog.timelog import Reports
from gtimelog.timelog import TimeWindow


class ReportsFacade(object):
    def __init__(self, filename, virtual_midnight=datetime.time(6, 0)):
        self.filename = filename
        self.virtual_midnight = virtual_midnight
        self.email = 'me@example.com'
        self.who = 'Name'

    def window(self, min_dt, max_dt):
        return TimeWindow(self.filename, min_dt, max_dt, self.virtual_midnight)

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
        window = self.window(day, day+oneday)
        return self.report('daily_report', window)

    def weekly(self, week):
        day = datetime.datetime.strptime('%s/1' % week, '%Y/%W/%w')
        day = datetime.datetime.combine(day, self.virtual_midnight)
        day = arrow.get(day)
        window = self.window(day.naive, day.replace(weeks=+1).naive)
        return self.report('weekly_report_plain', window)

    def monthly(self, month):
        day = datetime.datetime.strptime(month, '%Y-%m')
        day = datetime.datetime.combine(day, self.virtual_midnight)
        day = arrow.get(day)
        window = self.window(day.naive, day.replace(months=+1).naive)
        return self.report('monthly_report_plain', window)
