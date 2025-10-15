# file:         open_sky.py
# description:  contains the functions for interacting with the OpenSky API

import matplotlib.pyplot as plt

from pyopensky.rest import REST
from geopy import Point
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# TODO define some kind of dictionary for all valid airports

def test_api():
    geolocator = Nominatim(user_agent="testApp")
    location = geolocator.geocode("Dallas Fort Worth International Airport, Dallas, TX")
    bbox = get_bbox(location.latitude, location.longitude, 1000)

    print((location.latitude, location.longitude))
    print(tuple(bbox))
    print(geodesic((bbox[0], bbox[1]), (bbox[2], bbox[3])).miles)

    # plt.scatter(location.latitude, location.longitude)
    # plt.plot([bbox[0], bbox[0]], [bbox[1], bbox[3]], 'r-')
    # plt.plot([bbox[2], bbox[2]], [bbox[1], bbox[3]], 'r-')
    # plt.plot([bbox[0], bbox[2]], [bbox[1], bbox[1]], 'r-')
    # plt.plot([bbox[0], bbox[2]], [bbox[3], bbox[3]], 'r-')
    # plt.show()

    api = REST()
    data = api.states() # TODO fixme to use bounds
    for flight in data.itertuples():
        print(flight)

def get_bbox(lat, lng, miles):
    # sw, ne
    bearings = [225, 45]
    origin = Point(lat, lng)
    l = []

    for bearing in bearings:
        destination = geodesic(miles=miles).destination(origin, bearing)
        coords = destination.latitude, destination.longitude
        l.extend(coords)
    # xmin, ymin, xmax, ymax
    return l
