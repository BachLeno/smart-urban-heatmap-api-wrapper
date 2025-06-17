# Smart Urban Heat Map – SensorThings API Wrapper

Dieses Repository enthält ein Python-basiertes Wrapper-Projekt für die [Smart Urban Heat Map API](https://smart-urban-heat-map.ch) ([GitHub Dokumentation](https://meteotest.github.io/urban-heat-API-docs/de/)), mit Fokus auf die Umwandlung der Daten in das [OGC SensorThings](https://www.ogc.org/standards/sensorthings) Datenmodell. Das Projekt wurde im Rahmen eines Praxisprojekts an der Berner Fachhochschule (BFH) entwickelt.

## Inhalte

Das Repository ist strukturiert in drei Hauptbereiche:

- **`latest/`** – Code zur Abfrage und Konvertierung von aktuellen Stationsdaten über den `/latest` API-Endpunkt
- **`timeseries/`** – Code zur Verarbeitung von Zeitreihendaten über den `/timeseries` API-Endpunkt
- **`old_code/`** – Archivierter, veralteter Code zur Nachvollziehbarkeit der Entwicklung

#### Zusätzlich enthält das Repository ein interaktives Notebook zur kombinierten Auswertung und Visualisierung von /latest und /timeseries API-Abfragen.

## Funktionen

- Abruf von Temperatur- und Feuchtigkeitsdaten für definierte Stationen
- Konvertierung in das SensorThings-Format mit:
  - Things
  - Locations
  - Datastreams
  - Observations
- Speicherung als JSON-Datei
- Visualisierung von Temperatur und Luftfeuchtigkeit aktuell & über die Zeit

## Dateien

| Datei/Ordner                        | Beschreibung |
|------------------------------------|--------------|
| `latest/`                          | Code zur Verarbeitung von `/latest` API-Abfrage |
| `timeseries/`                      | Code zur Verarbeitung von Zeitreihen `/timeseries` API-Abfragen |
| `old_code/`                        | Veraltete, aber dokumentierte Skripte |
| `SensorThingsConverter_Notebook.ipynb` | Notebook zur Konvertierung & Visualisierung von `/latest` & `/timeseries` API-Abfragen |
| `sensor_things_output.json`       | JSON-Ausgabe für `/latest` |
| `timeseries_11117.json`           | JSON-Ausgabe für eine bestimmte Zeitreihenabfrage`/timeseries` |

## Nutzung

1. Klone das Repository:
   ```bash
   git clone https://github.com/BachLeno/smart-urban-heatmap-api-wrapper.git
   cd smart-urban-heatmap-api-wrapper


## Gehostete API & neues Demo-Notebook

Nach Abgabe des Praxisprojekts wurde die SensorThings API online gehostet via [PythonAnywhere](https://www.pythonanywhere.com/).

### Öffentliche Endpunkte

- [`/latest`](https://lenobach.pythonanywhere.com/latest) – Aktuelle Stationsdaten im SensorThings-Format
- [`/timeseries`](https://lenobach.pythonanywhere.com/timeseries?stationId=11117&timeFrom=2024-11-01T00:00:00Z&timeTo=2024-11-05T00:00:00Z) – Zeitreihendaten für eine bestimmte Station und Zeitraum

### Neue Dateien

| Datei                           | Beschreibung |
|--------------------------------|--------------|
| `SensorThings_API_Demo_Notebook.ipynb` | Neues interaktives Notebook zur Abfrage der live-API über PythonAnywhere |
| `flask_app.py`                 | Flask-basierte Bereitstellung der API-Endpunkte für `/latest` und `/timeseries` |

Das Notebook ersetzt die lokale JSON-basierte Lösung und greift direkt auf die gehosteten REST-Endpunkte zu.

