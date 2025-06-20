from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load dataset and parse date column
df = pd.read_csv('atxtraffic.csv', parse_dates=['Published Date'], low_memory=False)
df['Date'] = pd.to_datetime(df['Published Date'], errors='coerce')
df['Year'] = df['Date'].dt.year

@app.route('/')
def home():
    return "This is a new Flask app!"

@app.route('/FilteredIncidents', methods=['GET'])
def filtered_incidents():
    column_name = request.args.get('ColumnName')
    column_value = request.args.get('ColumnValue')
    year = request.args.get('Year')

    if not column_name or not column_value or not year:
        return jsonify({'error': 'Missing query parameter: ColumnName, ColumnValue, or Year'}), 400

    try:
        year = int(year)
    except ValueError:
        return jsonify({'error': 'Year must be an integer'}), 400

    # Filter the dataframe based on inputs
    filtered = df[
        (df['Year'] == year) &
        (df[column_name].astype(str).str.contains(column_value, case=False, na=False))
    ]

    return jsonify(filtered.to_dict(orient='records'))

@app.route('/TrafficHazardLocations', methods=['GET'])
def traffic_hazard_locations():
    year = request.args.get('Year')

    if not year:
        return jsonify({'error': 'Year parameter is required'}), 400

    try:
        year = int(year)
    except ValueError:
        return jsonify({'error': 'Year must be an integer'}), 400

    hazards = df[
        (df['Issue Reported'].str.contains('Traffic Hazard', case=False, na=False)) &
        (df['Year'] == year)
    ]

    locations = hazards[['Location', 'Latitude', 'Longitude', 'Address']].drop_duplicates()

    return jsonify(locations.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8046)





