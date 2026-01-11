import redis
import time
import json

r = redis.Redis(host='redis_queue', port=6379, decode_responses=True)

LUA_DEQUEUE_SCRIPT = """
local job = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
if #job > 0 then
    local job_data = job[1]
    local scheduled_time = tonumber(job[2])
    local current_time = tonumber(ARGV[2])

    if scheduled_time <= current_time then
        redis.call('ZREM', KEYS[1], job_data)
        -- Move to in_flight with the visibility timeout (ARGV[1])
        redis.call('ZADD', KEYS[2], ARGV[1], job_data)
        return job_data
    end
end
return nil
"""

def reclaim_stale_jobs():
    now = time.time()
    stale_jobs = r.zrangebyscore("in_flight", 0, now)
    for job_data in stale_jobs:
        print(f"Rescuing stale job...")
        pipe = r.pipeline()
        pipe.zrem("in_flight", job_data)
        pipe.zadd("job_queue", {job_data: time.time()})
        pipe.execute()


def handle_failure(job_data, max_retries=3):
    data = json.loads(job_data)
    data['retries'] += 1
    new_job_json = json.dumps(data)

    r.zrem("in_flight", job_data)

    if data['retries'] > max_retries:
        print(f"DLQ: Job {data['id']} failed {max_retries}x. Quarantined.")
        r.zadd("dead_letter_queue", {new_job_json: time.time()})
    else:
        delay = 2 ** data['retries']
        print(f"RETRY: Job {data['id']} failed. Backing off {delay}s...")
        r.zadd("job_queue", {new_job_json: time.time() + delay})


def process_job(job_data):
    data = json.loads(job_data)
    if "payment" in data['task'].lower(): return False
    print(f"Working on {data['task']}...")
    time.sleep(2)
    return True


def worker_loop():
    print("Worker Active")
    while True:
        reclaim_stale_jobs()
        timeout = time.time() + 30
        job_data = r.eval(LUA_DEQUEUE_SCRIPT, 2, "job_queue", "in_flight", timeout, time.time())

        if job_data:
            if process_job(job_data):
                r.zrem("in_flight", job_data)
                print("Success!")
            else: handle_failure(job_data)
        else: time.sleep(1)


if __name__ == "__main__":
    worker_loop()