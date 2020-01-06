import os
import codecs
import smtplib
import email

from getpass import getpass
from subprocess import call
from tempfile import NamedTemporaryFile
from email.charset import Charset
from email.charset import QP
from contextlib import contextmanager

from .tracker import schedule
from .reports import ReportsFacade
from .utils import is_empty_iterable


def sendmail(server, from_, to, message):
    if not isinstance(to, list):
        to = [to]

    charset = Charset('UTF-8')
    charset.header_encoding = QP
    charset.body_encoding = QP

    msg = email.message_from_string(message)
    msg.set_charset(charset)

    server.sendmail(from_, to, msg.as_string())


@contextmanager
def smtp(cfg):

    server = smtplib.SMTP(cfg.smtp_server, cfg.smtp_port)
    server.ehlo()
    server.starttls()

    if cfg.smtp_ask_password:
        for i in range(3):
            password = getpass('Enter SMTP password for %s: ' %
                               cfg.smtp_username)
            try:
                server.login(cfg.smtp_username, password)
            except smtplib.SMTPAuthenticationError:
                print()
                print('Incorrect password, try again...')
            else:
                break
    else:
        server.login(cfg.smtp_username, cfg.smtp_password)

    yield server

    server.close()


def print_email_preview(body):
    print()
    print('*'*35 + '8<' + '*'*35)
    print(body)
    print('*'*35 + '>8' + '*'*35)
    print()


def _send_reports(cfg, server, entries, reports, replog):
    for report, date in entries:
        genreport = getattr(reports, report)
        body = genreport(date)
        print_email_preview(body)

        while True:
            answer = input('Do you want to send this report? [Yneq?]: ')
            answer = answer.lower()
            if answer == '' or answer == 'y':
                print()
                print('Sending ...', end='')
                if cfg.dry_run:
                    print('  DONE (dry-run)')
                    break
                try:
                    sendmail(server, cfg.from_email, cfg.email, body)
                except Exception as e:
                    print('FAILED.')
                    print('Failed to send email: %s' % e)
                    raise
                else:
                    print('  DONE')
                    replog.write(report, date)
                break

            elif answer == 'e':
                print('Opening editor (%s) ...' % cfg.editor)
                f = NamedTemporaryFile('w', suffix='.eml', delete=False)
                f.write(body.encode('utf-8'))
                f.close()
                print(f.name)
                retcode = call([cfg.editor, f.name])
                if retcode != 0:
                    print('Editor exited with %d return code.' % retcode)
                else:
                    with codecs.open(f.name, encoding='utf-8') as temp:
                        body = temp.read()
                    print_email_preview(body)
                os.unlink(f.name)

            elif answer == 'n':
                print('Skipping this report.')
                replog.write(report, date)
                break

            elif answer == 'q':
                return

            else:
                if answer != '?':
                    print('ERROR: incorrect choice.')
                    print()

                print()
                print('Possible choices are:')
                print('  y - yes, send this report')
                print('  n - no, don\'t send this report')
                print('  e - open this report in editor and send edited version')
                print('  q - stop sending report and quit')
                print('  ? - show all possible choices')
                print()


def send_reports(cfg, filename, entries, replog, dontsend=False):
    reports = ReportsFacade(cfg, filename, cfg.virtual_midnight)
    entries = schedule(entries, replog)
    entries = is_empty_iterable(entries)
    if entries is None:
        print('No reports to be sent.')
    else:
        if cfg.dry_run:
            server = None
            _send_reports(cfg, server, entries, reports, replog)
        else:
            with smtp(cfg) as server:
                _send_reports(cfg, server, entries, reports, replog)
