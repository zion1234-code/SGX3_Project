from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

def LoadData():
    df = pd.read_csv('atxtraffic.csv')  # Your dataset file

    # Convert Date column to datetime, drop bad rows
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date', 'Latitude', 'Longitude'])

    # Extract useful columns
    df['Hour'] = df['Date'].dt.hour
    df['Year'] = df['Date'].dt.year

    # Make sure Lat/Lon are floats
    df['Latitude'] = df['Latitude'].astype(float)
    df['Longitude'] = df['Longitude'].astype(float)

    return df

@app.route('/filter_by_hour')
def filter_by_hour():
    hour = request.args.get('hour', type=int)
    if hour is None:
        return jsonify({"error": "Missing 'hour' parameter"}), 400

    df = LoadData()
    filtered = df[df['Hour'] == hour]

    return filtered.to_json(orient='records')

@app.route('/filter_by_location')
def filter_by_location():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius = request.args.get('radius', default=0.01, type=float)

    if None in (lat, lon):
        return jsonify({"error": "Missing 'lat' or 'lon' parameter"}), 400

    df = LoadData()
    filtered = df[
        (df['Latitude'] >= lat - radius) & (df['Latitude'] <= lat + radius) &
        (df['Longitude'] >= lon - radius) & (df['Longitude'] <= lon + radius)
    ]

    return filtered.to_json(orient='records')

if __name__ == '__main__':
    # Listen on all interfaces so consumer.py can connect remotely
    app.run(host='0.0.0.0', port=8046, debug=True)



