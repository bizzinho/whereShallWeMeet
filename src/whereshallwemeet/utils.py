import datetime
import plotly.express as px
import plotly.graph_objects as go
from scipy.spatial import ConvexHull
import numpy as np

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

def plotConvexHull(polygon, bbox=False):
    fig = go.Figure(go.Scattermapbox(
        fill = "toself",
        lon = [p[0] for p in polygon], lat = [p[1] for p in polygon],
        marker = { 'size': 10, 'color': "orange" }))
    if bbox:
        box = getBbox(lon, lat)
        fig.add_trace(px.line_mapbox(
            lon = [b[0] for b in box],
            lat = [b[1] for b in box]
        ))
    fig.update_layout(
        mapbox = {
            'style': "carto-positron"},
        showlegend = False)
    fig.show()

def convexArea(lon, lat):
    h = ConvexHull(list(zip(lon, lat)))

    polygon = [(lon[s], lat[s]) for s in h.vertices]

    return polygon

def getBbox(lon, lat):
    return [(min(lon), min(lat)),
    (max(lon), min(lat)),
    (max(lon), max(lat)),
    (min(lon), max(lat)),
    (min(lon), min(lat))]