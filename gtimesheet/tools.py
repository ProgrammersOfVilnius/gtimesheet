"""Timesheet and gTimeLog synchronisation tool.

Usage:
  gtimesheet [--config=<filename>] [--dry-run] [--timesheet=<filename>]
             [--timelog=<filename>]
  gtimesheet send [--config=<filename>] [--dry-run] [--fake]
             [--sent-reports=<filename>] [--timesheet=<filename>]
             [--timelog=<filename>] [--email=<email>] [--name=<name>]
             [--from-email=<email>]
  gtimesheet stats [--config=<filename>] [--timesheet=<filename>]
             [--timelog=<filename>]
  gtimesheet overtime [--config=<filename>] [--holidays=<filename>...]
             [--work-hours=<hrs-per-day>] [--timesheet=<filename>]
             [--timelog=<filename>]
  gtimesheet overtime-graph [--config=<filename>] [--holidays=<filename>...]
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

import datetime
import dataset

from docopt import docopt
from gtimesheet import __version__
from datetime import timedelta
from contextlib import contextmanager

from .sync import sync
from .sync import sync_to_timesheet
from .timelog import timesheets_to_timelog
from .timelog import timelog_file
from .mailer import send_reports
from .stats import stats_by_day
from .overtime import get_overtime
from .overtime import overtime_graph
from .holidays import Holidays
from .utils import format_timedelta
from .utils import format_hours
from .utils import open_files
from .tracker import get_sent_reports
from .tracker import ReportsLog
from .settings import Settings


@contextmanager
def _replog(cfg):
    if not cfg.dry_run and cfg.sent_reports:
        with cfg.sent_reports.open('a') as f:
            yield f
    else:
        yield None


def gtimesheet():
    args = docopt(__doc__, version=__version__)
    cfg = Settings()
    cfg.load(args)

    db = dataset.connect('sqlite:///%s' % cfg.timesheet)

    entries = sync(db, str(cfg.timelog))
    entries = sync_to_timesheet(db, entries)

    if args['send']:
        entries = [entry for source, entry in entries]
        reports = get_sent_reports(cfg.sent_reports)
        with timelog_file(entries) as filename, _replog(cfg) as log:
            replog = ReportsLog(reports, log)
            dontsend = cfg.fake or cfg.dry_run
            send_reports(cfg, filename, entries, replog, dontsend)

    elif args['stats']:
        with open_files(cfg.holidays) as files:
            holidays = Holidays(files)
        entries = (entry for source, entry in entries)
        overtime = datetime.timedelta()
        perday = cfg.part_time
        for date, time in stats_by_day(entries):
            if holidays.is_holiday(date):
                holiday = '(holiday)'
                overtime += time
            else:
                holiday = ''
                if time > perday:
                    overtime += time - perday
                else:
                    overtime -= perday - time

            print('%s: %8s [%8s] %s' % (
                date.strftime('%Y-%m-%d'), str(time), format_hours(overtime),
                holiday
            ))

    elif args['overtime']:
        with open_files(cfg.holidays) as files:
            holidays = Holidays(files)
        h_total = cfg.hours
        h_perday = cfg.part_time
        entries = [entry for source, entry in entries]
        totaltime, worktime, overtime = get_overtime(entries, h_perday, holidays)
        print()
        print('Work time:     %8s' % format_hours(worktime))
        print('Total time:    %8s' % format_hours(totaltime))
        print('Overtime:      %8s' % format_hours(overtime))
        print()
        print('Overtime in fulltime working days (%s h/day):' % h_total)
        print('  %s' % format_timedelta(overtime, timedelta(hours=h_total)))
        print()
        print('Overtime in fulltime working days (%s h/day):' % (h_perday.total_seconds() / 3600))
        print('  %s' % format_timedelta(overtime, h_perday))

    elif args['overtime-graph']:
        with open_files(cfg.holidays) as files:
            holidays = Holidays(files)
        h_total = cfg.hours
        h_perday = cfg.part_time
        entries = [entry for source, entry in entries]
        overtime_graph(entries, h_perday, holidays)

    elif cfg.dry_run:
        spt = lambda o: datetime.datetime.strptime(o, '%Y-%m-%d %H:%M')
        keys = ('clientName', 'projectName', 'notes')
        for source, entry in entries:
            delta = spt(entry['date2']) - spt(entry['date1'])
            notes = ': '.join(filter(None, [entry[k] for k in keys]))
            print('{source:>9}: {date1} -- {date2} ({delta:>8}): {notes_}'.format(
                source=source, notes_=notes, delta=delta, **entry
            ))

    else:
        entries = (entry for source, entry in entries)
        for line in timesheets_to_timelog(entries):
            print(line)
