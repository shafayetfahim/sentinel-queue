Title: SentinelQueue

Description: A Distributed, fault-tolerant task orchestrator.

Tech Stack: Python, Redis, Docker, Lua.

How to Run: docker-compose up --scale worker=n, 
where n is some integer value of workers that falls
below your resource ceiling, which might be
defined by CPU/Memory limits or API rate
limits. Resource usage will grow linearly until this ceiling.