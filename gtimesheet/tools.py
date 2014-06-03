"""Timesheet and gTimeLog synchronisation tool.

Usage:
  gtimesheet [--dry-run] <timesheet> <timelog>
  gtimesheet (-h | --help)
  gtimesheet --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --dry-run     Just show what will be done without doing anything.

"""

import dataset

from docopt import docopt
from gtimesheet import __version__
from pathlib import Path

from .sync import sync
from .sync import sync_to_timesheet
from .timelog import timesheets_to_timelog


def gtimesheet():
    args = docopt(__doc__, version=__version__)

    path = Path(args['<timesheet>'])
    db = dataset.connect('sqlite:///%s' % path.resolve())

    keys = ('clientName', 'projectName', 'notes')

    entries = sync(db, args['<timelog>'])
    entries = sync_to_timesheet(db, entries)

    if args['--dry-run']:
        for source, entry in entries:
            notes = ': '.join(filter(None, [entry[k] for k in keys]))
            print u'{source:>9}: {date1} -- {date2}: {notes_}'.format(
                    source=source, notes_=notes, **entry
            )
    else:
        entries = (entry for source, entry in entries)
        for line in timesheets_to_timelog(entries):
            print line
