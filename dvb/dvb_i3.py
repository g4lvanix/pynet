#!/usr/bin/env python3

import requests,json

base_url = "http://widgets.vvo-online.de/abfahrtsmonitor/"

station_endpoint = "Haltestelle.do"
departure_endpoint = "Abfahrten.do"

with open("config.json") as f:
    config = json.loads(f.read())


r = requests.get(base_url+station_endpoint,params={"ort": config["location"], "hst": config["station"]})

if r.status_code != 200:
    print("DVB server error")
else:   
    stations = r.json()
    station = stations[1][0][0]

    r = requests.get(base_url+departure_endpoint,
             params={"ort": config["location"], "hst": station})

print("Station:",station)
print("Number | Destination | Minutes")

for i in r.json():
    print(" | ".join(i))
