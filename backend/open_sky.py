# file:         open_sky.py
# description:  contains the functions for interacting with the OpenSky API

from opensky_api import OpenSkyApi

def test_api():
    api = OpenSkyApi()
    states = api.get_states()
    for s in states.states:
        print(s)
