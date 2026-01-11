import redis
import json
import uuid

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def enqueue_job(task_name, payload, priority=5):
    job_id = str(uuid.uuid4())
    job_data = {
        "id": job_id,
        "task": task_name,
        "payload": payload,
        "retries": 0
    }
    serialized_job = json.dumps(job_data)
    r.zadd("job_queue", {serialized_job: priority})
    print(f"✅ Enqueued {task_name} (ID: {job_id}) with priority {priority}")


if __name__ == "__main__":
    for i in range(30):
        enqueue_job(f"task_{i}", {"data": i}, priority=5)
    enqueue_job("process_payment", {"amount": 100, "currency": "USD"}, priority=1)
    enqueue_job("send_welcome_email", {"email": "test@example.com"}, priority=10)