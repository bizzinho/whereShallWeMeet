import datetime
import plotly.express as px
import plotly.graph_objects as go
from scipy.spatial import ConvexHull
import numpy as np
from shapely.geometry import Polygon
import pointpats 

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

def plotAddresses(lon, lat, show=True):
    fig = px.scatter_mapbox(lat=lat, lon=lon,
                        mapbox_style="carto-positron")
    if show:
        fig.show()
    else:
        return fig

def plotConvexHull(polygon, bbox=False, samples = None):
    fig = go.Figure(go.Scattermapbox(
        fill = "toself",
        lon = [p[0] for p in polygon], lat = [p[1] for p in polygon],
        marker = { 'size': 10, 'color': "orange" }))
    if bbox:
        box = getBbox(lon, lat)
        fig.add_trace(px.line_mapbox(
            lon = [b[0] for b in box],
            lat = [b[1] for b in box]
        ).data[0])
    if samples is not None:
        f2=plotAddresses([s[0] for s in samples], [s[1] for s in samples], show=False)
        fig.add_trace(f2.data[0])
    fig.update_layout(
        mapbox = {
            'style': "carto-positron",
            "center": go.layout.mapbox.Center(lon=np.mean(lon), 
            lat=np.mean(lat)),
            "zoom":8},
        showlegend = False)
    fig.show()

def sampleWithinPoly(polygon, n=50):
    pgon = Polygon(polygon)
    return pointpats.random.poisson(pgon, size=n)

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

def closestCity(samples):
    # df_cities = pd.read_csv("geoInfo/ch.csv")
    df_cities = pd.read_csv("geoInfo/swisstopo_towns.csv").rename(columns={"Ortschaftsname":"city","N":"lat", "E":"lng"})
    cities = list(zip(df_cities.lng, df_cities.lat))
    closest = [np.argmin(np.linalg.norm(s-cities, axis=1)) for s in samples]
    return set([df_cities.iloc[c]["city"] for c in closest])