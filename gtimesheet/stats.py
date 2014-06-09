import datetime

from .constants import VIRTUAL_MIDNIGHT

combine = datetime.datetime.combine


def format_stats(stats):
    fmt = '%Y-%m-%d'
    for date, time in stats:
        yield date.strftime(fmt), str(time)


def stats_by_day(entries, virtual_midnight=VIRTUAL_MIDNIGHT):
    """

        >>> from pprint import pprint as pp

        >>> entries = [
        ...     {'date1': '2014-03-31 09:00', 'date2': '2014-03-31 10:30'},
        ...     {'date1': '2014-03-31 14:00', 'date2': '2014-03-31 15:00'},
        ... ]
        >>> entries = [dict(d, notes='', breaks=0) for d in entries]
        >>> pp(list(format_stats(stats_by_day(entries))))
        [('2014-03-31', '2:30:00')]

        >>> entries = [
        ...     {'date1': '2014-03-24 14:15', 'date2': '2014-03-24 18:14'},
        ...     {'date1': '2014-03-31 17:10', 'date2': '2014-03-31 17:38'},
        ...     {'date1': '2014-04-01 13:54', 'date2': '2014-04-01 15:41'},
        ...     {'date1': '2014-04-01 16:04', 'date2': '2014-04-01 18:00'},
        ...     {'date1': '2014-04-04 11:25', 'date2': '2014-04-04 12:33'},
        ... ]
        >>> entries = [dict(d, notes='', breaks=0) for d in entries]
        >>> pp(list(format_stats(stats_by_day(entries))))
        [('2014-03-24', '3:59:00'),
         ('2014-03-25', '0:00:00'),
         ('2014-03-26', '0:00:00'),
         ('2014-03-27', '0:00:00'),
         ('2014-03-28', '0:00:00'),
         ('2014-03-29', '0:00:00'),
         ('2014-03-30', '0:00:00'),
         ('2014-03-31', '0:28:00'),
         ('2014-04-01', '3:43:00'),
         ('2014-04-02', '0:00:00'),
         ('2014-04-03', '0:00:00'),
         ('2014-04-04', '1:08:00')]


    """
    fmt = '%Y-%m-%d %H:%M'
    xday = last = None
    time = datetime.timedelta()
    for entry in entries:
        if entry['notes'].endswith('*'): continue

        date1 = datetime.datetime.strptime(entry['date1'], fmt)
        date2 = datetime.datetime.strptime(entry['date2'], fmt)

        if entry['breaks']:
            date2 -= datetime.timedelta(minutes=entry['breaks'])

        day = combine(date1, datetime.time())
        if date1.time() <= virtual_midnight:
            day = day - datetime.timedelta(days=1)

        if last is not None and last != day:
            while xday < last:
                yield xday, datetime.timedelta()
                xday += datetime.timedelta(days=1)
            yield last, time
            time = datetime.timedelta()
            xday = last + datetime.timedelta(days=1)

        time += date2 - date1
        last = day
        if xday is None:
            xday = last + datetime.timedelta(days=1)

    if last is not None:
        while xday < last:
            yield xday, datetime.timedelta()
            xday += datetime.timedelta(days=1)
        yield last, time



def get_overtime(entries, perday, holidays):
    totaltime = datetime.timedelta()
    worktime = datetime.timedelta()
    overtime = datetime.timedelta()
    for date, time in stats_by_day(entries):
        totaltime += perday
        worktime += time
        if holidays.is_holiday(date):
            overtime += time
            continue

        if time > perday:
            overtime += time - perday
        else:
            overtime -= perday - time

    return totaltime, worktime, overtime
