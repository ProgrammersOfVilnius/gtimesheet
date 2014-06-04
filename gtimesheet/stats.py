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
        >>> pp(list(format_stats(stats_by('day', entries))))
        [('2014-03-31', '2:30:00')]

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
            xday = last

    if last is not None:
        while xday <= last:
            yield xday, datetime.timedelta()
            xday += datetime.timedelta(days=1)
        yield last, time



def get_overtime(entries, h_perday, holidays):
    overtime = datetime.timedelta()
    perday = datetime.timedelta(hours=h_perday)
    for date, time in stats_by_day(entries):
        if holidays.is_holiday(date):
            overtime += time
            continue

        if time > perday:
            overtime += time - perday
        else:
            overtime -= perday - time

    return overtime
