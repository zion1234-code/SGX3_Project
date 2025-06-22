from flask import Flask, request, jsonify
import pandas as pd
import math
import uuid
import json
import redis
from hotqueue import HotQueue

app = Flask(__name__)

# ---------------------- Load and Prepare Dataset ------------------------

df = pd.read_csv('atxtraffic.csv', parse_dates=['Published Date'], low_memory=False)
df['Date'] = pd.to_datetime(df['Published Date'], errors='coerce')
df['Year'] = df['Date'].dt.year
df['Hour'] = df['Date'].dt.hour

# ---------------------- Redis + HotQueue Setup -------------------------

redis_conn = redis.Redis(host='localhost', port=6379, db=0)
job_queue = HotQueue("job_queue", host='localhost', port=6379, db=1)
job_results_key = "job_results"

# ---------------------- Haversine Distance Function ---------------------

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# ---------------------- Original Routes (for direct sync calls) ---------

@app.route('/')
def home():
    return "This is a new Flask app with job queue!"

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

    filtered = df[
        (df['Year'] == year) &
        (df[column_name].astype(str).str.contains(column_value, case=False, na=False))
    ]

    return jsonify(filtered.to_dict(orient='records'))

@app.route('/IncidentsByHourRange', methods=['GET'])
def incidents_by_hour_range():
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

# ---------------------- Job Queue Routes -------------------------------

@app.route('/submit-job', methods=['POST'])
def submit_job():
    """
    Submit a job to the queue.
    JSON format:
    {
        "method": "nearby_incidents",
        "params": {
            "latitude": 30.2672,
            "longitude": -97.7431
        }
    }
    """
    data = request.get_json(force=True)
    if not data or 'method' not in data or 'params' not in data:
        return jsonify({'error': 'JSON with "method" and "params" required'}), 400

    method = data['method']
    params = data['params']

    # Generate a unique job ID
    job_id = str(uuid.uuid4())

    # Enqueue the job as JSON string
    job_data = {
        'job_id': job_id,
        'method': method,
        'params': params
    }
    job_queue.put(json.dumps(job_data))

    # Initialize job status in Redis
    redis_conn.hset(job_results_key, job_id, json.dumps({'status': 'queued', 'result': None}))

    return jsonify({'job_id': job_id, 'status': 'queued'}), 202

@app.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    """
    Get the status and result of a job.
    """
    job_data = redis_conn.hget(job_results_key, job_id)
    if not job_data:
        return jsonify({'error': 'Job ID not found'}), 404

    job_info = json.loads(job_data)
    return jsonify(job_info)

# ---------------------- Helper: Call Method by Name ---------------------

def call_method(method_name, params):
    """
    Calls the method with the given name and params.
    Only allow predefined safe methods.
    """
    methods = {
        'filtered_incidents': filtered_incidents_job,
        'incidents_by_hour_range': incidents_by_hour_range_job,
        'nearby_incidents': nearby_incidents_job,
        'traffic_hazard_locations': traffic_hazard_locations_job
    }

    if method_name not in methods:
        return {'error': f'Method {method_name} not supported'}

    return methods[method_name](**params)

# ---------------------- Job Implementations (no request context) ---------

def filtered_incidents_job(ColumnName, ColumnValue, Year):
    try:
        year = int(Year)
    except Exception:
        return {'error': 'Year must be an integer'}

    filtered = df[
        (df['Year'] == year) &
        (df[ColumnName].astype(str).str.contains(ColumnValue, case=False, na=False))
    ]
    return filtered.to_dict(orient='records')

def incidents_by_hour_range_job(start, end):
    try:
        start = int(start)
        end = int(end)
    except Exception:
        return {'error': 'start and end must be integers'}

    filtered = df[(df['Hour'] >= start) & (df['Hour'] <= end)]
    return filtered.to_dict(orient='records')

def nearby_incidents_job(latitude, longitude):
    try:
        lat = float(latitude)
        lon = float(longitude)
    except Exception:
        return {'error': 'latitude and longitude must be numbers'}

    def is_within_1km(row):
        try:
            return haversine(lat, lon, float(row['Latitude']), float(row['Longitude'])) <= 1
        except:
            return False

    nearby = df[df.apply(is_within_1km, axis=1)]
    return nearby.to_dict(orient='records')

def traffic_hazard_locations_job(Year):
    try:
        year = int(Year)
    except Exception:
        return {'error': 'Year must be an integer'}

    hazards = df[
        (df['Issue Reported'].str.contains('Traffic Hazard', case=False, na=False)) &
        (df['Year'] == year)
    ]
    locations = hazards[['Location', 'Latitude', 'Longitude', 'Address']].drop_duplicates()
    return locations.to_dict(orient='records')

# ---------------------- Run App -----------------------------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8046)


