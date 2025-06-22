import redis
import json
from hotqueue import HotQueue
from app import call_method  # Uses the helper function in your app.py

# Redis setup
redis_conn = redis.Redis(host='localhost', port=6379, db=0)
job_queue = HotQueue("job_queue", host='localhost', port=6379, db=1)
job_results_key = "job_results"

print("👷 Worker is running. Waiting for jobs...")

for job_data_json in job_queue.consume():
    try:
        job_data = json.loads(job_data_json)
        job_id = job_data['job_id']
        method = job_data['method']
        params = job_data['params']

        print(f"🔧 Processing job {job_id} — method: {method}")

        # Mark as running
        redis_conn.hset(job_results_key, job_id, json.dumps({'status': 'running', 'result': None}))

        # Call the method from your app
        result = call_method(method, params)

        # Save result
        redis_conn.hset(job_results_key, job_id, json.dumps({'status': 'completed', 'result': result}))
        print(f"✅ Job {job_id} completed.")

    except Exception as e:
        print(f"❌ Job failed: {e}")
        redis_conn.hset(job_results_key, job_id, json.dumps({'status': 'failed', 'result': str(e)}))

