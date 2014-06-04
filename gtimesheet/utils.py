import gettext
import codecs

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

    delta = delta.total_seconds()
    perday = perday.total_seconds()
    sign = '-' if delta < 0 else '+'
    delta = abs(delta)
    days = delta // perday
    reminder = timedelta(seconds=(delta - perday*days))
    if days > 0:
        days_text = ngettext('day', 'days', days)
        return '%s %d %s %s' % (sign, days, days_text, reminder)
    else:
        return '%s %s' % (sign, reminder)


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
            files.append(codecs.open(filename, *args, **kwargs))
        yield files
    finally:
        for f in files:
            f.close()
