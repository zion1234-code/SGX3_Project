from hotqueue import HotQueue
import time

# Connect to Redis and create a queue named 'job_queue'
q = HotQueue("job_queue", host="localhost", port=8047)  # Replace 6379 if needed

def producer():
    # Put some sample jobs on the queue
    for i in range(5):
        job_data = {"type": "print", "msg": f"Hello {i}"}
        print(f"Producer: Adding job {job_data}")
        q.put(job_data)
        time.sleep(1)

def consumer():
    print("Consumer: Waiting for jobs...")
    for job in q.consume():
        print(f"Consumer: Got job: {job}")
        if job["type"] == "print":
            print(f"Message: {job['msg']}")
        else:
            print("Unknown job type")

if __name__ == "__main__":
    import threading

    # Run producer and consumer in separate threads for demo
    t_producer = threading.Thread(target=producer)
    t_consumer = threading.Thread(target=consumer)

    t_consumer.start()
    t_producer.start()

    t_producer.join()
    # Note: consumer runs infinitely waiting for jobs,
    # so we won't join it here to keep demo simple

