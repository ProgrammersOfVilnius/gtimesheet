import os
import datetime
import string

from contextlib import contextmanager
from tempfile import NamedTemporaryFile


def read_timelog(f, midnight='06:00'):
    """

    >>> from pprint import pprint as pp
    >>> from StringIO import StringIO

    >>> f = StringIO('''
    ... 2014-03-24 14:15: start
    ... 2014-03-24 18:14: project: t1
    ... ''')
    >>> pp(list(read_timelog(f)))
    [{'date1': datetime.datetime(2014, 3, 24, 14, 15),
      'date2': datetime.datetime(2014, 3, 24, 18, 14),
      'notes': 'project: t1'}]

    >>> f = StringIO('')
    >>> pp(list(read_timelog(f)))
    []

    >>> f = StringIO('''
    ... 2014-03-24 18:14: project: t1
    ... ''')
    >>> pp(list(read_timelog(f)))
    []

    >>> f = StringIO('''
    ... 2014-03-24 18:14: project: t1
    ... 2014-03-25 18:14: project: t1
    ... ''')
    >>> pp(list(read_timelog(f)))
    []

    >>> f = StringIO('''
    ... 2014-03-24 18:14: project: t1
    ... 2014-03-25 17:14: project: t1
    ... 2014-03-25 18:14: project: t1
    ... ''')
    >>> pp(list(read_timelog(f)))
    [{'date1': datetime.datetime(2014, 3, 25, 17, 14),
      'date2': datetime.datetime(2014, 3, 25, 18, 14),
      'notes': 'project: t1'}]

    >>> f = StringIO('''
    ... 2014-03-24 14:15: start
    ... 2014-03-24 18:14: project: t1
    ...
    ... 2014-03-25 09:40: start
    ...
    ... 2014-03-31 15:48: start
    ... 2014-03-31 17:10: project: t2
    ... 2014-03-31 17:38: project: t3
    ... 2014-03-31 18:51: project: t4
    ... 2014-04-16 15:22: launch: **
    ... 2014-04-16 16:04: mail ***
    ... 2014-04-16 18:01: project: t4
    ... 2014-04-16 18:47: project: t5
    ... ''')
    >>> pp(list(read_timelog(f)))
    [{'date1': datetime.datetime(2014, 3, 24, 14, 15),
      'date2': datetime.datetime(2014, 3, 24, 18, 14),
      'notes': 'project: t1'},
     {'date1': datetime.datetime(2014, 3, 31, 15, 48),
      'date2': datetime.datetime(2014, 3, 31, 17, 10),
      'notes': 'project: t2'},
     {'date1': datetime.datetime(2014, 3, 31, 17, 10),
      'date2': datetime.datetime(2014, 3, 31, 17, 38),
      'notes': 'project: t3'},
     {'date1': datetime.datetime(2014, 3, 31, 17, 38),
      'date2': datetime.datetime(2014, 3, 31, 18, 51),
      'notes': 'project: t4'},
     {'date1': datetime.datetime(2014, 4, 16, 15, 22),
      'date2': datetime.datetime(2014, 4, 16, 16, 4),
      'notes': 'mail ***'},
     {'date1': datetime.datetime(2014, 4, 16, 16, 4),
      'date2': datetime.datetime(2014, 4, 16, 18, 1),
      'notes': 'project: t4'},
     {'date1': datetime.datetime(2014, 4, 16, 18, 1),
      'date2': datetime.datetime(2014, 4, 16, 18, 47),
      'notes': 'project: t5'}]

    """
    last = None
    nextday = None
    hour, minute = map(int, midnight.split(':'))
    midnight = dict(hour=hour, minute=minute)
    day = datetime.timedelta(days=1)
    for line in f:
        line = line.strip()
        if line == '': continue

        time, note = line.split(': ', 1)
        time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')

        if nextday is None or time >= nextday:
            last = time
            nextday = time.replace(**midnight)
            if time >= nextday:
                nextday += day
            continue

        yield {
            'date1': last,
            'date2': time,
            'notes': note,
        }

        last = time


def resolvekw(key, mapping, default=KeyError):
    """Recursively find last key and value where value is not in d.

    Test single nesting level.

    >>> resolvekw('project', {'project': 1})
    ('project', 1)

    Test two nesting levels.

    >>> resolvekw('project', {'my project': 'project', 'project': 1})
    ('project', 1)

    Test recusive mapping.

    >>> resolvekw('a', {'a': 'b', 'b': 'a'})
    ('b', 'a')

    Test KeyError.

    >>> resolvekw('c', {'a': 'b'}) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    KeyError: 'Key "c" is not in given mapping.'

    """
    val = key
    keys = set()
    while val in mapping and val not in keys:
        key, val = val, mapping[val]
        keys.add(key)
    if keys:
        return key, val
    elif default is not KeyError:
        return key, default
    else:
        raise KeyError('Key "%s" is not in given mapping.' % key)


def timelog_to_timesheet(timelog, projects):
    """Convert single timelog record returned by ``read_timelog``.

    :timelog: item returned by ``read_timelog``

    >>> from pprint import pprint as pp
    >>> pp(timelog_to_timesheet({
    ...     'date1': datetime.datetime(2014, 3, 31, 15, 48),
    ...     'date2': datetime.datetime(2014, 3, 31, 17, 10),
    ...     'notes': 'project: t2',
    ... }, {'my project': 'project', 'project': 1}))
    {'amount': 0.0,
     'amountperhour': 0.0,
     'breaks': 0,
     'clientName': '',
     'date1': '2014-03-31 15:48',
     'date2': '2014-03-31 17:10',
     'methodid': 0,
     'notes': 't2',
     'overtime': 0,
     'project': '1',
     'projectName': 'project',
     'status': 0,
     'working': 82}

    """
    d1 = timelog['date1']
    d2 = timelog['date2']
    notes = map(string.strip, timelog['notes'].split(':', 2))
    client, project, notes = ['']*(3-len(notes)) + notes
    project, project_id = resolvekw(project, projects, default=0)
    return {
        'clientName': client,
        'projectName': project,
        'project': '%d' % project_id,
        'amountperhour': 0.0,
        'date1': d1.strftime('%Y-%m-%d %H:%M'),
        'date2': d2.strftime('%Y-%m-%d %H:%M'),
        'working': (d2 - d1).seconds // 60,
        'breaks': 0,
        'overtime': 0,
        'amount': 0.0,
        'notes': notes,
        'methodid': 0,
        'status': 0,
    }


def timesheets_to_timelog(timesheets, midnight='06:00'):
    """Convert list of timesheet records to timelog.txt format.

    This function yields timelog line one be one.

    :timesheets: list of timesheet records

    >>> from pprint import pprint as pp

    >>> timesheets = [
    ...     {'amount': 0.0,
    ...      'amountperhour': 0.0,
    ...      'breaks': 0,
    ...      'clientName': '',
    ...      'date1': '2014-03-31 15:48',
    ...      'date2': '2014-03-31 17:10',
    ...      'methodid': 0,
    ...      'notes': 't2',
    ...      'overtime': 0,
    ...      'project': '1',
    ...      'projectName': 'project',
    ...      'status': 0,
    ...      'working': 82},
    ... ]
    >>> pp(list(timesheets_to_timelog(timesheets)))
    ['2014-03-31 15:48: start', '2014-03-31 17:10: project: t2']

    >>> timesheets = [
    ...     {'amount': 0.0,
    ...      'amountperhour': 0.0,
    ...      'breaks': 0,
    ...      'clientName': '',
    ...      'date1': '2014-03-31 15:48',
    ...      'date2': '2014-03-31 17:10',
    ...      'methodid': 0,
    ...      'notes': 't2',
    ...      'overtime': 0,
    ...      'project': '1',
    ...      'projectName': 'project',
    ...      'status': 0,
    ...      'working': 82},
    ...     {'amount': 0.0,
    ...      'amountperhour': 0.0,
    ...      'breaks': 0,
    ...      'clientName': '',
    ...      'date1': '2014-03-31 17:10',
    ...      'date2': '2014-03-31 18:10',
    ...      'methodid': 0,
    ...      'notes': 't2',
    ...      'overtime': 0,
    ...      'project': '1',
    ...      'projectName': 'project',
    ...      'status': 0,
    ...      'working': 82},
    ...     {'amount': 0.0,
    ...      'amountperhour': 0.0,
    ...      'breaks': 0,
    ...      'clientName': '',
    ...      'date1': '2014-04-01 09:00',
    ...      'date2': '2014-04-01 12:50',
    ...      'methodid': 0,
    ...      'notes': 't2',
    ...      'overtime': 0,
    ...      'project': '1',
    ...      'projectName': 'project',
    ...      'status': 0,
    ...      'working': 82},
    ...     {'amount': 0.0,
    ...      'amountperhour': 0.0,
    ...      'breaks': 0,
    ...      'clientName': 'client',
    ...      'date1': '2014-04-01 14:30',
    ...      'date2': '2014-04-01 18:00',
    ...      'methodid': 0,
    ...      'notes': 'a task',
    ...      'overtime': 0,
    ...      'project': '1',
    ...      'projectName': 'project',
    ...      'status': 0,
    ...      'working': 82},
    ... ]
    >>> pp(list(timesheets_to_timelog(timesheets)))
    ['2014-03-31 15:48: start',
     '2014-03-31 17:10: project: t2',
     '2014-03-31 18:10: project: t2',
     '',
     '2014-04-01 09:00: start',
     '2014-04-01 12:50: project: t2',
     '2014-04-01 14:30: slack ***',
     '2014-04-01 18:00: client: project: a task']

    """
    fmt = '%Y-%m-%d %H:%M'
    last = None
    nextday = None
    day = datetime.timedelta(days=1)
    hour, minute = map(int, midnight.split(':'))
    midnight = dict(hour=hour, minute=minute)
    for ts in timesheets:
        time = datetime.datetime.strptime(ts['date1'], fmt)

        if nextday is not None and time >= nextday:
            yield ''

        if nextday is None or time >= nextday:
            last = None
            nextday = time.replace(**midnight)
            if time >= nextday:
                nextday += day

        notes = ts['notes'] if ts['notes'] else '(empty note)'
        if ts['projectName']:
            notes = '%s: %s' % (ts['projectName'], notes)
        else:
            notes = '%s' % notes

        if last is None:
            yield '%s: start' % ts['date1']
        elif last != ts['date1']:
            yield '%s: break ***' % ts['date1']

        if ts['breaks']:
            date2 = datetime.datetime.strptime(ts['date2'], fmt)
            date2 -= datetime.timedelta(minutes=ts['breaks'])
            date2 = date2.strftime(fmt)
        else:
            date2 = ts['date2']
        yield '%s: %s' % (date2, notes)

        last = ts['date2']


@contextmanager
def timelog_file(entries):
    f = NamedTemporaryFile(delete=False)
    for line in timesheets_to_timelog(entries):
        f.write(line.encode('utf-8') + '\n')
    f.close()
    yield f.name
    os.unlink(f.name)
