import datetime
import plotly.express as px

def onDay(date, day=2, hour=18):
    """
    Returns the date of the next given weekday after
    the given date. For example, the date of next Monday.

    NB: if it IS the day we're looking for, this returns 0.
    consider then doing onDay(foo, day + 1).
    """
    days = (day - date.weekday() + 7) % 7

    newdate = date + datetime.timedelta(days=days)

    return newdate.replace(hour=hour, minute=0, second=0, microsecond=0)


def argmin(a):
    return min(range(len(a)), key=lambda x: a[x])

def plotAddresses(lon, lat):
    fig = px.scatter_mapbox(lat, lon,
                        mapbox_style="carto-positron")
    fig.show()