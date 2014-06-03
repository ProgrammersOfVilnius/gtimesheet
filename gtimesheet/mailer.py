import datetime

from .tracker import schedule
from .reports import ReportsFacade


def send_reports(filename, entries):
    reports = ReportsFacade(filename)
    now = datetime.datetime.now()
    for report, date in schedule(entries):
        print '\t'.join([str(now), report, date])
        report = getattr(reports, report)
        print report(date)
        print
        print '-' * 72
