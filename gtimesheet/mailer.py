import os
import codecs

from subprocess import call
from tempfile import NamedTemporaryFile

from .tracker import schedule
from .reports import ReportsFacade

def print_email_preview(body):
    print
    print '*'*35 + '8<' + '*'*35
    print body
    print '*'*35 + '>8' + '*'*35
    print


def send_reports(filename, entries, replog, dontsend=False):
    editor = os.environ.get('EDITOR', 'vi')
    reports = ReportsFacade(filename)
    for report, date in schedule(entries, replog):
        genreport = getattr(reports, report)
        body = genreport(date)
        print_email_preview(body)

        while True:
            answer = raw_input('Do you want to send this report? [Yne?]: ')
            answer = answer.lower()
            if answer == '' or answer == 'y':
                print
                print 'Sending ...',
                print '  DONE'
                replog.write(report, date)
                break
            elif answer == 'e':
                print 'Opening editor (%s) ...' % editor
                f = NamedTemporaryFile('w', suffix='.eml', delete=False)
                f.write(body.encode('utf-8'))
                f.close()
                print f.name
                retcode = call([editor, f.name])
                if retcode != 0:
                    print 'Editor exited with %d return code.' % retcode
                else:
                    with codecs.open(f.name, encoding='utf-8') as temp:
                        body = temp.read()
                    print_email_preview(body)
                os.unlink(f.name)
            elif answer == 'n':
                print 'Skipping this report.'
                replog.write(report, date)
                break
            elif answer == 'q':
                return
            else:
                if answer != '?':
                    print 'ERROR: incorrect choice.'
                    print

                print
                print 'Possible choices are:'
                print '  y - yes, send this report'
                print '  n - no, don\'t send this report'
                print '  e - open this report in editor and send edited version'
                print '  q - stop sending report and quit'
                print '  ? - show all possible choices'
                print
