# file:         open_sky.py
# description:  contains the functions for interacting with the OpenSky API
from http.client import HTTPException

import pandas as pd
from httpx import HTTPStatusError

from pyopensky.rest import REST
from geopy import Point
from geopy.distance import geodesic

DEFAULT_AIRPORT = "Dallas Fort Worth International Airport"
#AIRPORTS_DF = pd.read_csv("../common/data/airports.csv")
API = REST()

'''
def get_flights_airport(airport=DEFAULT_AIRPORT, radius=50):
    """
    Gets all flights within a certain radius around some airport.
    :param airport: the official name of some airport
    :param radius:  the (square) radius around that airport to get the flights from
    :return:        dataframe containing flight information
    """
    lat, lng = _get_lat_lng(airport)
    return get_flights_lat_lng(lat, lng, radius)
'''

def get_flights_lat_lng(lat, lng, radius=50):
    """
    Gets all flights within a certain radius around some latitude, longitude point.
    :param lat:     latitude of the center point
    :param lng:     longitude of the center point
    :param radius:  the (square) radius around that airport to get the flights from
    :return:        dataframe containing flight information, bounding box of the flights
    """
    bbox = _get_bbox(lat, lng, radius)
    data = API.states(bounds=tuple(bbox))
    return data, bbox


def get_flight_trajectories(flights):
    """
    Gets the trajectory for all flights given.
    :param flights:     dataframe of flights
    :return:            list of dataframes, one per flight
    """
    trajectories = []
    for flight in flights.itertuples():
        icao24 = flight.icao24
        try:
            trajectories.append(API.tracks(icao24))
        except HTTPStatusError:
            print(f"skipping flight {icao24} due to invalid endpoint")
    return trajectories


def _get_bbox(lat, lng, miles):
    # sw, ne
    bearings = [225, 45]
    origin = Point(lat, lng)
    l = []

    for bearing in bearings:
        destination = geodesic(miles=miles).destination(origin, bearing)
        coords = destination.longitude, destination.latitude
        l.extend(coords)

    return l

'''
def _get_lat_lng(airport):
    row = AIRPORTS_DF.loc[AIRPORTS_DF["name"] == airport]
    lat, lng = row.iloc[0]["latitude_deg"], row.iloc[0]["longitude_deg"]
    return lat, lng
'''