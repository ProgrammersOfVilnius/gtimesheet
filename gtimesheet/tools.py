"""Timesheet and gTimeLog synchronisation tool.

Usage:
  gtimesheet [--config=<filename>] [--dry-run] [--timesheet=<filename>]
             [--timelog=<filename>]
  gtimesheet send [--config=<filename>] [--dry-run] [--fake]
             [--sent-reports=<filename>] [--timesheet=<filename>]
             [--timelog=<filename>]
  gtimesheet stats [--config=<filename>] [--timesheet=<filename>]
             [--timelog=<filename>]
  gtimesheet overtime [--config=<filename>] [--holidays=<filename>...]
             [--work-hours=<hrs-per-day>] [--timesheet=<filename>]
             [--timelog=<filename>]
  gtimesheet (-h | --help)
  gtimesheet --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  -c <filename> --config=<filename>
                Configuration file. [default: ~/.gtimelog/gtimelogrc]
  --dry-run     Just show what will be done without doing anything.
  --fake        Fill sent reports state file, without sending any report.
  --holidays=<filename...>
                Configuration files for holidays. You can use this parameter
                more than once to include more holiday files.
  --sent-reports=<filename>
                Sent reports log file.
  --timesheet=<filename>
                Timesheet Sqlite3 database file 
  --timelog=<filename>
                gTimeLog timelog.txt file.
  --work-hours=<hrs-per-day>
                Hours per day with given total hours per day, example: 3.5/7

"""

import dataset

from docopt import docopt
from gtimesheet import __version__
from pathlib import Path
from datetime import timedelta
from contextlib import contextmanager

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
from .tracker import get_sent_reports
from .tracker import ReportsLog
from .settings import Settings


@contextmanager
def _replog(args):
    if not args['--dry-run'] and args['--sent-reports']:
        with open(args['--sent-reports'], 'a') as f:
            yield f
    else:
        yield None


def gtimesheet():
    args = docopt(__doc__, version=__version__)
    cfg = Settings(args)

    db = dataset.connect('sqlite:///%s' % cfg.timesheet.resolve())

    entries = sync(db, args['<timelog>'])
    entries = sync_to_timesheet(db, entries)

    if args['send-reports']:
        entries = [entry for source, entry in entries]
        reports = get_sent_reports(args['--sent-reports'])
        with timelog_file(entries) as filename, _replog(args) as log:
            replog = ReportsLog(reports, log)
            dontsend = args['--fake'] or args['--dry-run']
            send_reports(filename, entries, replog, dontsend)

    elif args['stats']:
        entries = (entry for source, entry in entries)
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
        keys = ('clientName', 'projectName', 'notes')
        for source, entry in entries:
            notes = ': '.join(filter(None, [entry[k] for k in keys]))
            print u'{source:>9}: {date1} -- {date2}: {notes_}'.format(
                source=source, notes_=notes, **entry
            )

    else:
        entries = (entry for source, entry in entries)
        for line in timesheets_to_timelog(entries):
            print line
