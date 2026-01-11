SentinelQueue, a Reliable Task Pipeline

I wanted to build a system that could handle background tasks without ever losing data. Whether it's sending thousands of emails or processing heavy data, I needed a way to ensure that even if a server crashes or an API fails, the task would eventually succeed. This was mostly from a conceptual standpoint, as I wanted to improve my understanding of Python from a backend perspective and how atomicity and concurrency can align.

Sentinel-Queue is a high-reliability task queue built with Python and Redis. It uses queueing patterns like atomic Lua scripting and exponential backoff to manage distributed workloads. It is designed to scale horizontally using Docker, allowing multiple workers to process a single shared queue safely.

Here's some features I implemented:

- Atomic Task Dequeueing:
Using Lua scripts inside Redis, the system ensures that grabbing a task is an "all-or-nothing" operation. This prevents "race conditions" where two workers accidentally grab the same task.

- Visibility Timeouts & Safety:
When a worker grabs a task, it's moved to an in_flight list. If the worker crashes, a "Watchdog" process automatically rescues the task and puts it back in the queue after a 30-second timeout.

- Exponential Backoff:
If a task fails, the system doesn't just retry immediately. It calculates a delay, giving failing services time to recover before trying again.

- Dead Letter Queue (DLQ):
To prevent "poison pills" from clogging the system, any task that fails more than 3 times is quarantined in a Dead Letter Queue for manual inspection.

- Live Monitoring Dashboard:
A dedicated monitoring script provides a real-time terminal view of the queue health, tracking "Waiting," "Active," and "Failed" tasks.

Here's the internal structure: 
* producer.py: The entry point, creating tasks with unique IDs and priority levels.
* worker.py: The engine of the program, processeing tasks, handling the Lua logic, and managing retries.
* monitor.py: A live dashboard for system observability.
* Dockerfile / Docker-compose: Configures the environment for horizontal scaling.

To run this... 
1. Start the infrastructure: docker-compose up -d redis
2. Launch the monitor: python monitor.py
3, Start the workers: docker-compose up --scale worker=3 (arbitrary; this runs 3 parallel workers)
4. Enqueue jobs: python producer.py

In the future, I'd like to add a web-based UI for the monitor and implement "Priority Groups" to ensure mission-critical tasks always jump to the front of the line regardless of when they were added.
