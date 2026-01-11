import redis
import time
import os

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def print_dashboard():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        queued = r.zcard("job_queue")
        in_flight = r.zcard("in_flight")
        dead = r.zcard("dead_letter_queue")

        print("SentinelQueue Live Monitor")
        print(f"Waiting in Queue:  {queued}")
        print(f"Currently Active:  {in_flight}")
        print(f"Failed (DLQ):      {dead}")
        print("************************")
        print("Press Ctrl+C to exit")

        time.sleep(1)

if __name__ == "__main__":
    print_dashboard()