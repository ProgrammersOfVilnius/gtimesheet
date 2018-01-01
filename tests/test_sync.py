import datetime
from pprint import pprint as pp

import pytest

from gtimesheet.sync import iter_sync

d = lambda d: datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')


def test_ts1_and_ts2_are_equal():

    ts1 = [{'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42',
            'breaks': 0}]
    ts2 = [{'date1': d('2014-05-07 09:55'), 'date2': d('2014-05-07 12:42')}]
    assert list(iter_sync(ts1, ts2)) == [
        (
            {'breaks': 0, 'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42'},
            {'date1': datetime.datetime(2014, 5, 7, 9, 55), 'date2': datetime.datetime(2014, 5, 7, 12, 42)},
        )
    ]


def test_ts1_and_ts2_does_not_overlap():
    ts1 = [{'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42',
            'breaks': 0}]
    ts2 = [{'date1': d('2014-05-07 12:42'), 'date2': d('2014-05-07 13:40')}]
    assert list(iter_sync(ts1, ts2)) == [
        (
            {'breaks': 0, 'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42'},
            None,
        ),
        (
            None,
            {'date1': datetime.datetime(2014, 5, 7, 12, 42), 'date2': datetime.datetime(2014, 5, 7, 13, 40)},
        ),
    ]


def test_ts1_with_10_minutes_break_and_ts2_starts_10_minutes_later():
    ts1 = [{'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42',
            'breaks': 10}]
    ts2 = [{'date1': d('2014-05-07 10:05'), 'date2': d('2014-05-07 12:42')}]
    assert list(iter_sync(ts1, ts2)) == [
        (
            {'breaks': 10, 'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42'},
            {'date1': datetime.datetime(2014, 5, 7, 10, 5), 'date2': datetime.datetime(2014, 5, 7, 12, 42)},
        ),
    ]


def test_ts1_with_10_minutes_break_and_ts2_ends_10_minutes_earlier():
    ts1 = [{'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42',
            'breaks': 10}]
    ts2 = [{'date1': d('2014-05-07 09:55'), 'date2': d('2014-05-07 12:32')}]
    assert list(iter_sync(ts1, ts2)) == [
        (
            {'breaks': 10, 'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42'},
            {'date1': datetime.datetime(2014, 5, 7, 9, 55), 'date2': datetime.datetime(2014, 5, 7, 12, 32)},
        ),
    ]


def test_currently_overlapping_entries_are_not_supported():
    ts1 = [{'date1': '2014-05-07 09:55', 'date2': '2014-05-07 12:42',
            'breaks': 10, 'clientName': '', 'projectName': '',
            'notes': ''}]
    ts2 = [{'date1': d('2014-05-07 09:58'), 'date2': d('2014-05-07 12:30'),
            'notes': ''}]
    with pytest.raises(Exception):
        list(iter_sync(ts1, ts2))


def test_check_wrong_order():
    ts1 = []
    ts2 = [{'date1': d('2014-05-07 09:58'), 'date2': d('2014-05-07 12:30'),
            'notes': ''},
           {'date1': d('2014-05-06 09:58'), 'date2': d('2014-05-06 12:30'),
            'notes': ''}]
    with pytest.raises(AssertionError):
        list(iter_sync(ts1, ts2))
