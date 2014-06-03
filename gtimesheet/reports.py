import arrow
import datetime

from StringIO import StringIO

from gtimelog.timelog import Reports
from gtimelog.timelog import TimeWindow


def daily_report(filename, min_date, max_date, virtual_midnight='06:00'):
    """

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

    >>> print daily_report(f.name, '2014-03-01', '2014-04-01')
    To: sirex@pov.lt
    Subject: 2014-03-01 report for Mantas (Sat, week 09)
    <BLANKLINE>
    Start at 14:15
    <BLANKLINE>
    Project: task 1                                                 3 hours 59 min
    Start                                                           0 min
    Project: task 2                                                 2 hours 35 min
    Project: task 3                                                 28 min
    <BLANKLINE>
    Total work done: 7 hours 2 min
    <BLANKLINE>
    By category:
    <BLANKLINE>
    Project                                                         7 hours 2 min
    (none)                                                          0 min
    <BLANKLINE>
    Slacking:
    <BLANKLINE>
    Time spent slacking: 0 min
    <BLANKLINE>

    >>> os.unlink(f.name)

    """
    virtual_midnight = datetime.time(*map(int, virtual_midnight.split(':')))
    min_date = arrow.get(min_date).naive
    max_date = arrow.get(max_date).naive
    window = TimeWindow(filename, min_date, max_date, virtual_midnight)
    output = StringIO()
    reports = Reports(window)
    email = 'sirex@pov.lt'
    who = 'Mantas'
    reports.daily_report(output, email, who)
    report = output.getvalue()
    return report
