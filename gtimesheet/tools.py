"""Timesheet and gTimeLog synchronisation tool.

Usage:
  gtimesheet [--dry-run] <timesheet> <timelog>
  gtimesheet send-reports [--dry-run] <timesheet> <timelog>
  gtimesheet stats <timesheet> <timelog>
  gtimesheet overtime [--holidays=<filename>...] <ratio> <timesheet> <timelog>
  gtimesheet (-h | --help)
  gtimesheet --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --dry-run     Just show what will be done without doing anything.
  <ratio>       Hourse per day with given total hours per day, example: 3.5/7

"""

import dataset

from docopt import docopt
from gtimesheet import __version__
from pathlib import Path
from datetime import timedelta

from .sync import sync
from .sync import sync_to_timesheet
from .timelog import timesheets_to_timelog
from .timelog import timelog_file
from .mailer import send_reports
from .stats import stats_by_day
from .stats import get_overtime
from .holidays import Holidays
from .utils import format_timedelta
from .utils import open_files


def gtimesheet():
    args = docopt(__doc__, version=__version__)

    path = Path(args['<timesheet>'])
    db = dataset.connect('sqlite:///%s' % path.resolve())

    keys = ('clientName', 'projectName', 'notes')

    entries = sync(db, args['<timelog>'])
    entries = sync_to_timesheet(db, entries)

    if args['--dry-run'] and args['send-reports']:
        entries = [entry for source, entry in entries]
        with timelog_file(entries) as filename:
            send_reports(filename, entries)
    elif args['stats']:
        entries = [entry for source, entry in entries]
        for date, time in stats_by_day(entries):
            print '%s: %8s' % (date.strftime('%Y-%m-%d'), str(time))
    elif args['overtime']:
        with open_files(args['--holidays']) as files:
            holidays = Holidays(files)
        h_perday, h_total = map(float, args['<ratio>'].split('/'))
        entries = [entry for source, entry in entries]
        overtime = get_overtime(entries, h_perday, holidays)
        print format_timedelta(overtime, timedelta(hours=h_total))
    elif args['--dry-run']:
        for source, entry in entries:
            notes = ': '.join(filter(None, [entry[k] for k in keys]))
            print u'{source:>9}: {date1} -- {date2}: {notes_}'.format(
                    source=source, notes_=notes, **entry
            )
    else:
        entries = (entry for source, entry in entries)
        for line in timesheets_to_timelog(entries):
            print line
