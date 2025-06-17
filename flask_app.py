from flask import Flask, jsonify
from flask import request
from SensorThingsConverter_Latest import SensorThingsConverter as LatestConverter
from SensorThingsConverter_Timeseries import SensorThingsConverter as TimeseriesConverter

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'SensorThings API Wrapper is running!'

@app.route('/latest', methods=['GET'])
def latest():
    try:
        converter = LatestConverter()
        data = converter.convert()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/timeseries', methods=['GET'])
def timeseries():
    try:
        station_id = request.args.get("stationId")
        time_from = request.args.get("timeFrom")
        time_to = request.args.get("timeTo")

        if not station_id:
            return jsonify({'error': 'stationId is required'}), 400

        converter = TimeseriesConverter()
        data = converter.convert_timeseries(station_id, time_from, time_to)
        return jsonify(data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()