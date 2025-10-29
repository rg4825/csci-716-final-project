# file:         open_sky.py
# description:  contains the functions for interacting with the OpenSky API

import pandas as pd

from pyopensky.rest import REST
from geopy import Point
from geopy.distance import geodesic

DEFAULT_AIRPORT = "Dallas Fort Worth International Airport"
AIRPORTS_DF = pd.read_csv("../common/data/airports.csv")


def get_flights(airport=DEFAULT_AIRPORT, radius=50):
    row = AIRPORTS_DF.loc[AIRPORTS_DF["name"] == airport]
    lat, lng = row.iloc[0]["latitude_deg"], row.iloc[0]["longitude_deg"]
    bbox = get_bbox(lat, lng, radius)

    api = REST()
    data = api.states(bounds=tuple(bbox))
    return data


def get_bbox(lat, lng, miles):
    # sw, ne
    bearings = [225, 45]
    origin = Point(lat, lng)
    l = []

    for bearing in bearings:
        destination = geodesic(miles=miles).destination(origin, bearing)
        coords = destination.longitude, destination.latitude
        l.extend(coords)

    return l
