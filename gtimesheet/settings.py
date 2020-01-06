import os
import datetime

from datetime import timedelta
from pathlib import Path
from configparser import RawConfigParser
from os.path import expanduser


def resolve_path_if_exists(path):
    path = Path(expanduser(path))
    if path.exists():
        return path.resolve()
    else:
        return path


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


def resolve_time(s):
    h, m = map(str.strip, s.split(':', 1))
    h, m = map(int, (h, m))
    return datetime.time(h, m)


def resolve_bool(s):
    if s is True or s == 1 or s.lower() in ('yes', 'true', 'on'):
        return True
    else:
        False


def resolve_list(*apply):
    def _resolve_list(s):
        items = map(str.strip, s.split(','))
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
            apply=resolve_path_if_exists,
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

        self.set('virtual_midnight',
            glog.get('virtual_midnight'),
            datetime.time(3, 0),
            apply=resolve_time,
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
        self.set('editor', glog.get('editor'), os.environ.get('EDITOR', 'vi'))

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
