# file:         open_sky.py
# description:  contains the functions for interacting with the OpenSky API

import matplotlib.pyplot as plt

from pyopensky.rest import REST
from geopy import Point
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

DEFAULT_AIRPORT="Dallas Fort Worth International Airport, Dallas, TX"

def get_flights(airport=DEFAULT_AIRPORT, radius=50):
    geolocator = Nominatim(user_agent="testApp")
    location = geolocator.geocode(airport)
    bbox = get_bbox(location.latitude, location.longitude, radius)

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
