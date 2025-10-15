# file:         open_sky.py
# description:  contains the functions for interacting with the OpenSky API

from pyopensky.rest import REST

def test_api():
    api = REST()
    data = api.states()
    for flight in data.itertuples():
        if flight.origin_country == "Norway":
            print(flight)
