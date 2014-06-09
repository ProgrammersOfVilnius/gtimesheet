import codecs
import datetime

from .timelog import read_timelog
from .timelog import timelog_to_timesheet
from .timesheet import get_project_mapping


def iter_sync(ts1, ts2):
    """Synchronize ts1 with ts2 and update both in place.

    :ts1: timesheet log
    :ts2: gtimelog log

    ts1 and ts2 are qual

    >>> from pprint import pprint as pp
    >>> d = lambda d: datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')

    >>> ts1 = [{'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42',
    ...         'breaks': 0}]
    >>> ts2 = [{'date1': d('2014-05-07 09:55'), 'date2': d('2014-05-07 12:42')}]
    >>> pp(list(iter_sync(ts1, ts2)))
    [({'breaks': 0, 'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42'},
      {'date1': datetime.datetime(2014, 5, 7, 9, 55),
       'date2': datetime.datetime(2014, 5, 7, 12, 42)})]

    ts1 and ts2 does not overlap

    >>> ts1 = [{'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42',
    ...         'breaks': 0}]
    >>> ts2 = [{'date1': d('2014-05-07 12:42'), 'date2': d('2014-05-07 13:40')}]
    >>> pp(list(iter_sync(ts1, ts2)))
    [({'breaks': 0, 'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42'},
      None),
     (None,
      {'date1': datetime.datetime(2014, 5, 7, 12, 42),
       'date2': datetime.datetime(2014, 5, 7, 13, 40)})]

    ts1 with 10 minutes break and ts2 starts 10 minutes later.

    >>> ts1 = [{'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42',
    ...         'breaks': 10}]
    >>> ts2 = [{'date1': d('2014-05-07 10:05'), 'date2': d('2014-05-07 12:42')}]
    >>> pp(list(iter_sync(ts1, ts2)))
    [({'breaks': 10, 'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42'},
      {'date1': datetime.datetime(2014, 5, 7, 10, 5),
       'date2': datetime.datetime(2014, 5, 7, 12, 42)})]

    ts1 with 10 minutes break and ts2 ends 10 minutes earlier.

    >>> ts1 = [{'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42',
    ...         'breaks': 10}]
    >>> ts2 = [{'date1': d('2014-05-07 09:55'), 'date2': d('2014-05-07 12:32')}]
    >>> pp(list(iter_sync(ts1, ts2)))
    [({'breaks': 10, 'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42'},
      {'date1': datetime.datetime(2014, 5, 7, 9, 55),
       'date2': datetime.datetime(2014, 5, 7, 12, 32)})]

    Currently overlapping entries are not supported.

    >>> ts1 = [{'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42',
    ...         'breaks': 10, 'clientName': '', 'projectName': '',
    ...         'notes': ''}]
    >>> ts2 = [{'date1': d('2014-05-07 09:58'), 'date2': d('2014-05-07 12:30'),
    ...         'notes': ''}]
    >>> pp(list(iter_sync(ts1, ts2))) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    Exception: Timesheet (2014-05-07 09:55 -- 2014-05-07 12:42: ) and
               gTimeLog (2014-05-07 09:58 -- 2014-05-07 12:30: ) entries
               overlap.

    Check wrong order.

    >>> ts1 = []
    >>> ts2 = [{'date1': d('2014-05-07 09:58'), 'date2': d('2014-05-07 12:30'),
    ...         'notes': ''},
    ...        {'date1': d('2014-05-06 09:58'), 'date2': d('2014-05-06 12:30'),
    ...         'notes': ''}]
    >>> pp(list(iter_sync(ts1, ts2))) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    AssertionError: assert (datetime.datetime(2014, 5, 7, 9, 58) is None or
                            datetime.datetime(2014, 5, 7, 9, 58) <
                            datetime.datetime(2014, 5, 6, 9, 58))

    """
    fmt = '%Y-%m-%d %H:%M'
    ts1 = iter(ts1)
    ts2 = iter(ts2)
    t1 = next(ts1, None)
    t2 = next(ts2, None)
    last_t1d1 = last_t2d1 = None
    while t1 or t2:
        t1d1 = t1d2 = t2d1 = t2d2 = None

        if t1:
            t1d1 = datetime.datetime.strptime(t1['date1'], fmt)
            t1d2 = datetime.datetime.strptime(t1['date2'], fmt)

            # Sanity checks
            assert last_t1d1 is None or last_t1d1 < t1d1
            assert t1d1 <= t1d2

        if t2:
            t2d1 = t2['date1']
            t2d2 = t2['date2']
            breaks = datetime.timedelta(minutes=(t1['breaks'] if t1 else 0))
            t2d1b = t2d1 - breaks
            t2d2b = t2d2 + breaks

            # Sanity checks
            assert last_t2d1 is None or last_t2d1 < t2d1
            assert t2d1 <= t2d2

        if t1 is None:
            yield None, t2
            last_t2d1 = t2d1
            t2 = next(ts2, None)

        elif t2 is None:
            yield t1, None
            last_t1d1 = t1d1
            t1 = next(ts1, None)

        elif (
            (t1d1 == t2d1  and t1d2 == t2d2 ) or
            (t1d1 == t2d1b and t1d2 == t2d2 ) or
            (t1d1 == t2d1  and t1d2 == t2d2b)
        ):
            yield t1, t2
            last_t1d1 = t1d1
            last_t2d1 = t2d1
            t1 = next(ts1, None)
            t2 = next(ts2, None)

        elif t1d1 >= t2d2:
            yield None, t2
            t2 = next(ts2, None)

        elif t2d1 >= t1d2:
            yield t1, None
            t1 = next(ts1, None)

        else:
            sft = lambda o: o.strftime(fmt)
            keys = ('clientName', 'projectName', 'notes')
            notes = ': '.join(filter(None, [t1[k] for k in keys]))
            ts = '%s -- %s: %s' % (sft(t1d1), sft(t1d2), notes)
            tl = '%s -- %s: %s' % (sft(t2d1), sft(t2d2), t2['notes'])
            raise Exception(
                'Timesheet (%s) and gTimeLog (%s) entries overlap.' % (ts, tl)
            )


def sync(timesheet_db, timelog_path):
    """Yields merged tuples of ordered timesheet and timelog files."""

    with codecs.open(timelog_path, 'r', encoding='utf-8') as f:
        ts1 = timesheet_db['times'].find(order_by=['date1'])
        ts2 = read_timelog(f)
        for timesheet, timelog in iter_sync(ts1, ts2):
            yield timesheet, timelog


def sync_to_timesheet(db, entries):
    projects = get_project_mapping(db)
    for timesheet, timelog in entries:
        if timesheet and timelog:
            entry = timelog_to_timesheet(timelog, projects)
            entry = dict(entry, **timesheet)
            source = 'BOTH'
        elif timesheet:
            entry = timesheet
            source = 'TIMESHEET'
        elif timelog:
            entry = timelog_to_timesheet(timelog, projects)
            source = 'TIMELOG'
        yield source, entry
