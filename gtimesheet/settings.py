import string

from datetime import timedelta
from pathlib import Path
from ConfigParser import RawConfigParser
from os.path import expanduser


def resolve_path(path):
    return Path(expanduser(path)).resolve()


def resolve_float(s):
    if s is None:
        return None
    else:
        return float(s)

def resolve_hours(s):
    s = resolve_float(s)
    if s is None:
        return None
    else:
        return timedelta(hours=s)


def resolve_bool(s):
    if s is True or s == 1 or s.lower() in ('yes', 'true', 'on'):
        return True
    else:
        False


def resolve_list(*apply):
    def _resolve_list(s):
        items = map(string.strip, s.split(','))
        for fn in apply:
            items = map(fn, items)
        return items
    return _resolve_list


class Settings(object):
    def load(self, args):
        config = RawConfigParser()
        config_path = self.set('config_path',
            args['--config'],
            '~/.gtimelog/gtimelogrc',
            apply=resolve_path,
        )
        config.read(str(config_path))

        glog = dict(config.items('gtimelog'))
        gsheet = dict(config.items('gtimesheet'))

        self.set('timesheet',
            args['--timesheet'],
            gsheet.get('timesheet-db'),
            '~/.gtimelog/timesheet.db',
            apply=resolve_path,
        )

        self.set('timelog',
            args['--timelog'],
            gsheet.get('timelog'),
            '~/.gtimelog/timelog.txt',
            apply=resolve_path,
        )

        self.set('sent_reports',
            args['--sent-reports'],
            gsheet.get('sent-reports'),
            '~/.gtimelog/sentreports.log',
            apply=resolve_path,
        )

        self.set('holidays',
            args['--holidays'],
            gsheet.get('holidays'),
            '~/.gtimelog/holidays.cfg',
            apply=resolve_list(resolve_path),
        )

        if args['--work-hours']:
            hours, part_time = map(float, args['--work-hours'].split('/', 1))
        else:
            hours = part_time = None

        self.set('hours',
            hours,
            glog.get('hours'),
            7,
            apply=resolve_float,
        )

        self.set('part_time',
            part_time,
            gsheet.get('part-time'),
            self.hours,
            apply=resolve_hours,
        )

        self.set('dry_run', args['--dry-run'], apply=bool)
        self.set('fake', args['--fake'], apply=bool)
        self.set('email', args['--email'], glog.get('list-email'))
        self.set('from_email', args['--from-email'], gsheet.get('from-email'))
        self.set('name', args['--name'], glog.get('name'))

        self.set('smtp_username', gsheet.get('smtp-username'), self.from_email)
        self.set('smtp_password', gsheet.get('smtp-password'))
        self.set('smtp_server', gsheet.get('smtp-server'), 'smtp.gmail.com')
        self.set('smtp_port', gsheet.get('smtp-port'), 587, apply=int)
        self.set('smtp_ask_password',
            gsheet.get('smtp-ask-password'),
            False,
            apply=resolve_bool,
        )

    def set(self, key, *values, **kwargs):
        n = len(values)
        for i, value in enumerate(values, 1):
            if value or i == n:
                apply = kwargs.get('apply', ())
                apply = apply if isinstance(apply, tuple) else (apply,)
                for fn in apply:
                    value = fn(value)
                setattr(self, key, value)
                return value
