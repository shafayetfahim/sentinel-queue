import redis
import json
import uuid


# Connect to the Redis instance running in Docker
# Note: From your laptop, it's 'localhost'. Inside Docker, it would be 'redis_queue'.
r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def enqueue_job(task_name, payload, priority=5):
    """
    Creates a unique job and adds it to the Priority Queue (Sorted Set).
    """
    job_id = str(uuid.uuid4())
    job_data = {
        "id": job_id,
        "task": task_name,
        "payload": payload,
        "retries": 0
    }

    # Convert dictionary to a JSON string so Redis can store it
    serialized_job = json.dumps(job_data)

    # ZADD: Key is 'job_queue', Score is 'priority', Value is 'serialized_job'
    r.zadd("job_queue", {serialized_job: priority})
    print(f"✅ Enqueued {task_name} (ID: {job_id}) with priority {priority}")


if __name__ == "__main__":
    # Let's create a high-priority payment job and a low-priority email job
    for i in range(30):
        enqueue_job(f"task_{i}", {"data": i}, priority=5)
    enqueue_job("process_payment", {"amount": 100, "currency": "USD"}, priority=1)
    enqueue_job("send_welcome_email", {"email": "test@example.com"}, priority=10)