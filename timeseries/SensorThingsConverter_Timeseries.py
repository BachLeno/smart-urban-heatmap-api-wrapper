import argparse
import json
import requests
import pandas as pd

class SmartUrbanHeatMapClient:
    def __init__(self, base_url: str = "https://smart-urban-heat-map.ch/api/v2"):
        self.base_url = base_url

    def fetch_timeseries(self, station_id: str, time_from: str = None, time_to: str = None) -> list:
        """
        Fragt Zeitreihendaten für eine bestimmte Station und optionalen Zeitbereich ab.
        Gibt eine Liste der Messwerte zurück.
        """
        url = f"{self.base_url}/timeseries?stationId={station_id}"
        if time_from:
            url += f"&timeFrom={time_from}"
        if time_to:
            url += f"&timeTo={time_to}"

        response = requests.get(url)
        if response.status_code == 204 or not response.content.strip():
            return []

        try:
            return response.json()
        except json.JSONDecodeError:
            print(f"WARNUNG: Antwort von Station {station_id} ist kein gültiges JSON.")
            return []

class TimeSeriesObservationBuilder:
    """
    Erstellt SensorThings-konforme "Observations" aus Zeitreihendaten.
    """
    def build(self, station_id: str, timeseries_data: list) -> list:
        observations = []
        for entry in timeseries_data:
            ts = pd.to_datetime(entry.get("dateObserved"))
            ts_iso = ts.isoformat()

            if "temperature" in entry:
                observations.append({
                    "Datastream": {"@iot.id": f"{station_id}-temperature"},
                    "phenomenonTime": ts_iso,
                    "resultTime": ts_iso,
                    "result": entry["temperature"]
                })

            if "relativeHumidity" in entry:
                observations.append({
                    "Datastream": {"@iot.id": f"{station_id}-humidity"},
                    "phenomenonTime": ts_iso,
                    "resultTime": ts_iso,
                    "result": entry["relativeHumidity"]
                })
        return observations

class SensorThingsConverter:
    """
    Hauptklasse zur Umwandlung der Zeitreihendaten in SensorThings-konforme JSON-Strukturen.
    """
    def __init__(self, base_url: str = None):
        client_url = base_url if base_url else "https://smart-urban-heat-map.ch/api/v2"
        self.client = SmartUrbanHeatMapClient(client_url)
        self.observation_builder = TimeSeriesObservationBuilder()

    def convert_timeseries(self, station_id: str, time_from: str = None, time_to: str = None) -> dict:
        """
        Konvertiert Zeitreihendaten für eine Station in ein SensorThings-kompatibles Format.
        """
        if not station_id:
            raise ValueError("Bitte gib eine gültige stationId mit --stationId an.")

        try:
            ts_data = self.client.fetch_timeseries(station_id, time_from, time_to)
            values = ts_data.get("values", []) if isinstance(ts_data, dict) else ts_data

            if not values:
                print(f"Keine Zeitreihen-Daten für Station {station_id}")
                return {"Observations": []}

            observations = self.observation_builder.build(station_id, values)
            return {"Observations": observations}

        except Exception as e:
            print(f"Fehler beim Abrufen der Zeitreihe für Station {station_id}: {e}")
            return {"Observations": []}

    def save_timeseries_to_json(self, station_id: str, filename="sensor_things_timeseries.json", time_from=None, time_to=None):
        """
        Speichert die konvertierten Zeitreihendaten in eine JSON-Datei.
        """
        payload = self.convert_timeseries(station_id, time_from, time_to)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)
        print(f"Zeitreihen-Daten für Station {station_id} wurden erfolgreich in {filename} gespeichert.")

if __name__ == "__main__":
    # Kommandozeilenparser für stationId und optionale Zeitfilter
    parser = argparse.ArgumentParser(description="Convert Smart Urban Heat Map Timeseries to SensorThings Observations.")
    parser.add_argument("--stationId", type=str, required=True, help="Station ID für die Timeseries-Abfrage (z.B. 11117)")
    parser.add_argument("--timeFrom", type=str, help="Startzeitpunkt im ISO-Format, z.B. 2024-11-01T00:00:00Z")
    parser.add_argument("--timeTo", type=str, help="Endzeitpunkt im ISO-Format, z.B. 2024-11-05T00:00:00Z")
    args = parser.parse_args()

    # Konvertierung und Speichern der Daten
    converter = SensorThingsConverter()
    filename = f"timeseries_{args.stationId}.json"
    converter.save_timeseries_to_json(
        station_id=args.stationId,
        filename=filename,
        time_from=args.timeFrom,
        time_to=args.timeTo
    )

# Beispiel zum Ausführen in der Kommandozeilenparser:
# python timeseries/SensorThingsConverter_Timeseries.py --stationId=11117 --timeFrom=2024-11-01T00:00:00Z --timeTo=2024-11-05T00:00:00Z
