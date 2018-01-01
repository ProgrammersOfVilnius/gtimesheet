An add-on to gtimelog_.

Features
========

- Can remember already sent daily, weekly and monthly time reports.

- Has integrated SMTP client for sending mails.

- Can send all not yet sent time logs with one command (interactively). Allows
  to edit report before sending, using your favorite text editor.

- Can track overtime by specified working hours, with holiday support.

- Integrates with Timesheet_ Android app (experimental). This allows to track
  time with both, gtimelog_ and Timesheet_.

Install
=======

Currently the only available options is to grab it from git repo::

    virtualenv --system-site-packages env
    env/bin/pip install -e git+https://github.com/ProgrammersOfVilnius/gtimesheet.git#egg=gtimesheet

Setup your ``~/.gtimelog/gtimelogrc``::

    [gtimelog]
    ...

    [gtimesheet]
    from-email = me@example.com
    sent-reports =  ~/.gtimelog/sentreports.log
    timesheet-db = ~/Dropbox/Apps/AadhkTimeTracker Lite/timetracker.db
    timelog = ~/.gtimelog/timelog.txt
    holidays = ~/.gtimelog/holidays.cfg
    part-time = 4.2
    smtp-username = # If not specified takes value from from-email
    smtp-password = # You can specify password here in plain text or use smtp-ask-password
    smtp-server = smtp.gmail.com
    smtp-port = 587
    smtp-ask-password = true

If you where using gtimelog_ before, for the first time, flag all previous
reports as already sent (information will be added to
``~/.gtimelog/sentreports.log`` file)::

    gtimesheet send --fake

Usage
=====

Use, gtimelog_ as before. Only, do not sent logs using gtimelog_, but instead
use this command::

    gtimesheet send --fake
    
This command detects all missing log reports to be sent, and interactively asks
for your approval before sending each report.

Using Timesheet
---------------

In order to use Timesheet_, you need to specify path to Timesheet's SQLite
database using ``timesheet-db`` parameter in ``~/.gtimelog/gtimelogrc``. Timesheet_
allows to export all data to SQLite format.

It is up to you, how you synchronize this database file between you mobile
phone and you computer. One of ways to do it, is to use Dropbox_.

When SQLite database from Timesheet_ is in place, you can run::

    gtimesheet send

Time log entries from gtimelog_ and Timesheet_ will be merged and time reports
will be sent.


.. _gtimelog: https://mg.pov.lt/gtimelog/
.. _Timesheet: https://play.google.com/store/apps/details?id=com.aadhk.time
.. _Dropbox: https://www.dropbox.com/
