import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import json

class SensorThingsConverter:

    def __init__(self, base_url="https://smart-urban-heat-map.ch/api/v2"):
        self.base_url = base_url

    def fetch_latest(self):
        url = f"{self.base_url}/latest"
        response = requests.get(url)

        if response.status_code == 200:
            data = gpd.read_file(response.text)
            return data
        else:
            print(f"Error: Request failed with status code {response.status_code}")
            return None

    def convert_to_sensorthings(self, data):
        if data is None:
            print("No data available for conversion.")
            return None
        
        things, locations, datastreams, observations = [], [], [], []
        
        for _, row in data.iterrows():
            thing_id = row["stationId"]
            location_geometry = row["geometry"]

            # SensorThings "Thing"
            thing = {
                "@iot.id": thing_id,
                "name": row["name"],
                "description": "Sensor measuring temperature and humidity",
                "properties": {"outdated": row["outdated"], "measurementsPlausible": row["measurementsPlausible"]}
            }
            things.append(thing)

            # SensorThings "Location"
            location = {
                "@iot.id": thing_id,
                "name": row["name"],
                "description": "Geographic location of the sensor",
                "encodingType": "application/vnd.geo+json",
                "location": {
                    "type": "Point",
                    "coordinates": [location_geometry.x, location_geometry.y]
                }
            }
            locations.append(location)

            # SensorThings "Datastreams"
            datastream_temp = {
                "@iot.id": f"{thing_id}-temperature",
                "name": f"Temperature Datastream for {row['name']}",
                "description": "Temperature measurements",
                "unitOfMeasurement": {"symbol": "°C", "name": "Degree Celsius", "definition": "http://unitsofmeasure.org/ucum.html#para-30"},
                "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
                "Thing": {"@iot.id": thing_id},
                "ObservedProperty": {"name": "Temperature", "definition": "http://sensorthings.org/Temperature"},
                "Sensor": {"name": "Temperature Sensor", "description": "Measures air temperature"}
            }

            datastream_hum = {
                "@iot.id": f"{thing_id}-humidity",
                "name": f"Humidity Datastream for {row['name']}",
                "description": "Humidity measurements",
                "unitOfMeasurement": {"symbol": "%", "name": "Percentage", "definition": "http://unitsofmeasure.org/ucum.html#para-30"},
                "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
                "Thing": {"@iot.id": thing_id},
                "ObservedProperty": {"name": "Humidity", "definition": "http://sensorthings.org/Humidity"},
                "Sensor": {"name": "Humidity Sensor", "description": "Measures relative humidity"}
            }

            datastreams.append(datastream_temp)
            datastreams.append(datastream_hum)

            # SensorThings "Observations" (Ensure Timestamps are in ISO 8601 format)
            observation_temp = {
                "Datastream": {"@iot.id": f"{thing_id}-temperature"},
                "phenomenonTime": row["dateObserved"].isoformat() if isinstance(row["dateObserved"], pd.Timestamp) else str(row["dateObserved"]),
                "resultTime": row["dateObserved"].isoformat() if isinstance(row["dateObserved"], pd.Timestamp) else str(row["dateObserved"]),
                "result": row["temperature"]
            }
            observation_hum = {
                "Datastream": {"@iot.id": f"{thing_id}-humidity"},
                "phenomenonTime": row["dateObserved"].isoformat() if isinstance(row["dateObserved"], pd.Timestamp) else str(row["dateObserved"]),
                "resultTime": row["dateObserved"].isoformat() if isinstance(row["dateObserved"], pd.Timestamp) else str(row["dateObserved"]),
                "result": row["relativeHumidity"]
            }

            observations.append(observation_temp)
            observations.append(observation_hum)

        # Construct the SensorThings API JSON structure
        sensorthings_data = {
            "Things": things,
            "Locations": locations,
            "Datastreams": datastreams,
            "Observations": observations
        }

        return sensorthings_data

    def fetch_and_convert(self):
        
        latest_data = self.fetch_latest()
        if latest_data is not None:
            return self.convert_to_sensorthings(latest_data)
        return None

    def save_to_json(self, filename="sensor_data.json"):
        
        sensorthings_data = self.fetch_and_convert()
        if sensorthings_data:
            with open(filename, "w") as json_file:
                json.dump(sensorthings_data, json_file, indent=4)
            print(f"Data saved to {filename} successfully!")

# Usage Example:
wrapper = SensorThingsConverter()

# Fetch latest sensor data and convert it
sensorthings_data = wrapper.fetch_and_convert()

# Print JSON output
if sensorthings_data:
    print(json.dumps(sensorthings_data, indent=4))

# Save JSON output to a file
wrapper.save_to_json("sensor_things_output.json")