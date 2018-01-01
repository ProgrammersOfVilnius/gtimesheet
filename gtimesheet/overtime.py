import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import gtimesheet.stats


def get_overtime(entries, perday, holidays):
    totaltime = datetime.timedelta()
    worktime = datetime.timedelta()
    overtime = datetime.timedelta()
    for date, time in gtimesheet.stats.stats_by_day(entries):
        totaltime += perday
        worktime += time
        if holidays.is_holiday(date):
            overtime += time
            continue

        if time > perday:
            overtime += time - perday
        else:
            overtime -= perday - time

    return totaltime, worktime, overtime

def td_to_hours(delta):
    delta = delta.total_seconds()
    hours, delta = divmod(delta, 60*60)
    return hours



def overtime_graph(entries, perday, holidays):
    x = []
    y = []

    overtime = datetime.timedelta()
    for date, time in gtimesheet.stats.stats_by_day(entries):
        x.append(date.date())
        if holidays.is_holiday(date):
            overtime += time
        else:
            if time > perday:
                overtime += time - perday
            else:
                overtime -= perday - time

        print('%s: %6s %6s %6s %s' % (
            date.date(),
            td_to_hours(overtime),
            td_to_hours(time),
            td_to_hours(perday),
            'holiday' if holidays.is_holiday(date) else '',
        ))
        y.append(td_to_hours(overtime))

    fig, ax = plt.subplots(1)
    ax.plot(x, [0] * len(x), 'k')
    ax.plot(x, y, 'k')
    ax.fill_between(x, 0, y)
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    fig.autofmt_xdate()
    plt.grid()
    plt.show()
