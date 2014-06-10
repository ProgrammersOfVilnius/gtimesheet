import gettext
import codecs
import itertools

from pathlib import Path
from contextlib import contextmanager
from datetime import timedelta

ngettext = gettext.NullTranslations().ngettext


def format_timedelta(delta, perday=timedelta(hours=24)):
    """Format timedelta by given working hours per day.

        >>> workday = timedelta(hours=7)

        >>> format_timedelta(timedelta(hours=14), workday)
        '+ 2 days 0:00:00'

        >>> format_timedelta(timedelta(hours=-14), workday)
        '- 2 days 0:00:00'

        >>> format_timedelta(timedelta(hours=17), workday)
        '+ 2 days 3:00:00'

        >>> format_timedelta(timedelta(hours=8), workday)
        '+ 1 day 1:00:00'

    """
    perday = perday.total_seconds()
    sign = '-' if delta < timedelta() else '+'
    delta = abs(delta)
    delta = delta.total_seconds()
    days = delta // perday
    reminder = timedelta(seconds=(delta - perday*days))
    if days > 0:
        days_text = ngettext('day', 'days', days)
        return '%s %d %s %s' % (sign, days, days_text, reminder)
    else:
        return '%s %s' % (sign, reminder)


def format_hours(delta):
    """

        >>> print format_hours(timedelta(days=1))
        24:00

        >>> print format_hours(timedelta(days=1, minutes=30))
        24:30

        >>> print format_hours(timedelta(days=1, minutes=30, seconds=5))
        24:30

        >>> print format_hours(timedelta(seconds=200))
        0:03

        >>> print format_hours(timedelta(days=10))
        240:00

        >>> print format_hours(-timedelta(hours=1, minutes=10))
        -1:10

    """
    if delta >= timedelta():
        sign = ''
    else:
        sign = '-'
        delta = abs(delta)
    delta = delta.total_seconds()
    hours, delta = divmod(delta, 60*60)
    minutes = delta // 60
    return '%s%d:%02d' % (sign, hours, minutes)



@contextmanager
def open_files(filenames, *args, **kwargs):
    """Context for opening many files.

        >>> import os
        >>> from tempfile import NamedTemporaryFile
        >>> f1 = NamedTemporaryFile(delete=False)
        >>> f2 = NamedTemporaryFile(delete=False)

        >>> with open_files([f1.name, f2.name]) as files:
        ...     print [isinstance(f, file) for f in files]
        [True, True]

        >>> os.unlink(f1.name)
        >>> os.unlink(f2.name)

    """
    files = []
    try:
        for filename in filenames:
            if isinstance(filename, Path):
                filename = str(filename)
            files.append(codecs.open(filename, *args, **kwargs))
        yield files
    finally:
        for f in files:
            f.close()


def is_empty_iterable(iterable):
    iterable = iter(iterable)
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return itertools.chain([first], iterable)
