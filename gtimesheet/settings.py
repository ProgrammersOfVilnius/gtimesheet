from pathlib import Path
from ConfigParser import SafeConfigParser


class Settings(object):
    def __init__(self, args):
        config = SafeConfigParser()
        config.read(args['--config'])
        glog = dict(config.items('gtimelog'))
        gsheet = dict(config.items('gtimesheet'))

        self.set('timesheet', args['<timesheet>'], gsheet.get('timesheet-db'),
                              '~/.gtimelog/timesheet.db')

    def set(self, key, *values):
        for value in values:
            if value:
                setattr(self, key, value)
