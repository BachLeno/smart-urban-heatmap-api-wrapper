import argparse
import json
import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

class SmartUrbanHeatMapClient:
    """
    Verantwortlich für HTTP-Kommunikation mit der Smart Urban Heat Map API.
    """
    def __init__(self, base_url: str = "https://smart-urban-heat-map.ch/api/v2"):
        self.base_url = base_url

    def fetch_latest(self) -> str:
        """Holt das rohe GeoJSON vom /latest-Endpoint als String."""
        url = f"{self.base_url}/latest"
        response = requests.get(url)
        response.raise_for_status()
        return response.text

class GeoDataLoader:
    """
    Verantwortlich für das Einlesen und Vorverarbeiten von GeoJSON-Strings in ein GeoDataFrame.
    """
    def load(self, geojson_str: str) -> gpd.GeoDataFrame:
        data = json.loads(geojson_str)
        crs = data.get('crs', {}).get('properties', {}).get('name', None)
        gdf = gpd.GeoDataFrame.from_features(data, crs=crs)
        return gdf

class ThingBuilder:
    """
    Baut die "Things"-Entitäten aus den Daten.
    """
    def build(self, df: pd.DataFrame) -> list:
        things = []
        for _, row in df.iterrows():
            things.append({
                "@iot.id": row.get("stationId"),
                "name": row.get("name", ""),
                "description": "Sensor station measuring temperature and humidity",
                "properties": {
                    "outdated": row.get("outdated"),
                    "measurementsPlausible": row.get("measurementsPlausible")
                }
            })
        return things

class LocationBuilder:
    """
    Baut die "Locations"-Entitäten aus geometrischen Daten.
    """
    def build(self, df: pd.DataFrame) -> list:
        locations = []
        for _, row in df.iterrows():
            geom = row.get("geometry")
            if not isinstance(geom, Point):
                continue
            coords = [geom.x, geom.y]
            locations.append({
                "@iot.id": row.get("stationId"),
                "name": row.get("name", ""),
                "description": "Geographic location of the sensor",
                "encodingType": "application/vnd.geo+json",
                "location": {"type": "Point", "coordinates": coords}
            })
        return locations

class DataStreamBuilder:
    """
    Baut die "Datastreams"-Entitäten für Temperatur und Feuchte.
    """
    def build(self, df: pd.DataFrame) -> list:
        dstreams = []
        for _, row in df.iterrows():
            sid = row.get("stationId")
            name = row.get("name", "")
            # Temperatur-Datastream
            dstreams.append({
                "@iot.id": f"{sid}-temperature",
                "name": f"Temperature Datastream for {name}",
                "description": "Temperature measurements",
                "unitOfMeasurement": {"symbol": "°C", "name": "Degree Celsius", "definition": "http://unitsofmeasure.org/ucum.html#para-30"},
                "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
                "Thing": {"@iot.id": sid},
                "ObservedProperty": {"name": "Temperature", "definition": "http://sensorthings.org/Temperature"},
                "Sensor": {"name": "Temperature Sensor", "description": "Measures air temperature"}
            })
            # Feuchte-Datastream
            dstreams.append({
                "@iot.id": f"{sid}-humidity",
                "name": f"Humidity Datastream for {name}",
                "description": "Humidity measurements",
                "unitOfMeasurement": {"symbol": "%", "name": "Percentage", "definition": "http://unitsofmeasure.org/ucum.html#para-30"},
                "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
                "Thing": {"@iot.id": sid},
                "ObservedProperty": {"name": "Humidity", "definition": "http://sensorthings.org/Humidity"},
                "Sensor": {"name": "Humidity Sensor", "description": "Measures relative humidity"}
            })
        return dstreams

class ObservationBuilder:
    """
    Erstellt die "Observations"-Einträge mit Zeitstempeln und Ergebnissen.
    """
    def build(self, df: pd.DataFrame) -> list:
        observations = []
        for _, row in df.iterrows():
            sid = row.get("stationId")
            ts = row.get("dateObserved")
            ts_iso = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)
            # Temperatur-Observation
            observations.append({
                "Datastream": {"@iot.id": f"{sid}-temperature"},
                "phenomenonTime": ts_iso,
                "resultTime": ts_iso,
                "result": row.get("temperature")
            })
            # Feuchte-Observation
            observations.append({
                "Datastream": {"@iot.id": f"{sid}-humidity"},
                "phenomenonTime": ts_iso,
                "resultTime": ts_iso,
                "result": row.get("relativeHumidity")
            })
        return observations

class SensorThingsConverter:
    """
    Fassade, die alle Komponenten orchestriert: Ruft Daten von der SmartUrbanHeatMapClient ab und erzeugt SensorThings-konforme Objekte.
    """
    def __init__(self, base_url: str = None):
        client_url = base_url if base_url else "https://smart-urban-heat-map.ch/api/v2"
        self.client = SmartUrbanHeatMapClient(client_url)
        self.loader = GeoDataLoader()
        self.thing_builder = ThingBuilder()
        self.location_builder = LocationBuilder()
        self.datastream_builder = DataStreamBuilder()
        self.observation_builder = ObservationBuilder()

    def convert(self) -> dict:
        raw = self.client.fetch_latest()
        df = self.loader.load(raw)
        return {
            "Things": self.thing_builder.build(df),
            "Locations": self.location_builder.build(df),
            "Datastreams": self.datastream_builder.build(df),
            "Observations": self.observation_builder.build(df)
        }

    def save_to_json(self, filename="sensor_things_output.json"):
        payload = self.convert()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)
        print(f"SensorThings-Daten wurden erfolgreich in {filename} gespeichert.")

# Optionaler direkter Aufruf für Tests oder interaktive Nutzung
if __name__ == "__main__":
    converter = SensorThingsConverter()
    converter.save_to_json("sensor_things_output.json")
