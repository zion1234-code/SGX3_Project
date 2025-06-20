from flask import Flask, request, jsonify
import pandas as pd
import math

app = Flask(__name__)

# ---------------------- Load and Prepare Dataset ------------------------

# Load the CSV and parse dates
df = pd.read_csv('atxtraffic.csv', parse_dates=['Published Date'], low_memory=False)

# Add useful columns for filtering
df['Date'] = pd.to_datetime(df['Published Date'], errors='coerce')
df['Year'] = df['Date'].dt.year
df['Hour'] = df['Date'].dt.hour  # For hour-based filtering

# ---------------------- Haversine Distance Function ---------------------

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the distance in kilometers between two lat/lon points using the Haversine formula.
    """
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# ------------------------ Routes ----------------------------------------

@app.route('/')
def home():
    return "This is a new Flask app!"

@app.route('/FilteredIncidents', methods=['GET'])
def filtered_incidents():
    """
    Filters incidents based on column name, value, and year.
    """
    column_name = request.args.get('ColumnName')
    column_value = request.args.get('ColumnValue')
    year = request.args.get('Year')

    if not column_name or not column_value or not year:
        return jsonify({'error': 'Missing query parameter: ColumnName, ColumnValue, or Year'}), 400

    try:
        year = int(year)
    except ValueError:
        return jsonify({'error': 'Year must be an integer'}), 400

    filtered = df[
        (df['Year'] == year) &
        (df[column_name].astype(str).str.contains(column_value, case=False, na=False))
    ]

    return jsonify(filtered.to_dict(orient='records'))

@app.route('/IncidentsByHourRange', methods=['GET'])
def incidents_by_hour_range():
    """
    Returns all incidents that occurred between two hours (0-23).
    """
    start_hour = request.args.get('start')
    end_hour = request.args.get('end')

    if not start_hour or not end_hour:
        return jsonify({'error': 'Missing query parameters: start and end'}), 400

    try:
        start_hour = int(start_hour)
        end_hour = int(end_hour)
    except ValueError:
        return jsonify({'error': 'start and end must be integers'}), 400

    if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
        return jsonify({'error': 'Hours must be between 0 and 23'}), 400

    filtered = df[(df['Hour'] >= start_hour) & (df['Hour'] <= end_hour)]

    return jsonify(filtered.to_dict(orient='records'))

@app.route('/NearbyIncidents', methods=['GET'])
def nearby_incidents():
    """
    Returns incidents within 1 km of the provided latitude and longitude.
    """
    lat = request.args.get('latitude')
    lon = request.args.get('longitude')

    if not lat or not lon:
        return jsonify({'error': 'Missing latitude or longitude parameters'}), 400

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return jsonify({'error': 'Latitude and longitude must be valid numbers'}), 400

    def is_within_1km(row):
        try:
            return haversine(lat, lon, float(row['Latitude']), float(row['Longitude'])) <= 1
        except:
            return False

    nearby = df[df.apply(is_within_1km, axis=1)]

    return jsonify(nearby.to_dict(orient='records'))

# ------------------------- Run App --------------------------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8046)

