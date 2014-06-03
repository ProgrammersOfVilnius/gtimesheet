import arrow
import datetime

from .constants import VIRTUAL_MIDNIGHT


def woty(d):
    """woty - week of the year"""
    return d.isocalendar()[1]


def schedule(entries, virtual_midnight=VIRTUAL_MIDNIGHT, now=None):
    """Generates reports shedule.

    Setup tests.

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

        >>> entries = [
        ...     {'date1': '2014-02-03 01:01'},
        ... ]
        >>> pp(list(schedule(entries, now=now)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [('daily', '2014-02-02'), ('weekly', '2014/05'),
         ('monthly', '2014-02')]

    """
    reports = set()
    now = now or datetime.datetime.now()
    now = arrow.get(now).floor('day').naive
    now_week = '%d/%02d' % (now.year, woty(now))
    now_month = now.strftime('%Y-%m')
    last_month = last_week = None

    can_yield = lambda last, current, now: (
        last is not None and last != current and
        last not in reports and now > last
    )

    for entry in entries:
        day = arrow.get(entry['date1'], 'YYYY-MM-DD HH:mm')

        if day.naive.time() > virtual_midnight:
            day = day.floor('day').naive
        else:
            day = day.floor('day').replace(days=-1).naive

        week = '%d/%02d' % (day.year, woty(day))
        if can_yield(last_week, week, now_week):
            yield 'weekly', last_week
            reports.add(last_week)
        last_week = week

        month = day.strftime('%Y-%m')
        if can_yield(last_month, month, now_month):
            yield 'monthly', last_month
            reports.add(last_month)
        last_month = month

        if day not in reports and now > day:
            yield 'daily', day.strftime('%Y-%m-%d')
            reports.add(day)


    if can_yield(last_week, None, now_week):
        yield 'weekly', last_week

    if can_yield(last_month, None, now_month):
        yield 'monthly', last_month
