# raft-guang

a really minimal implementation of leader election using the raft consensus algorithm in python. 
mostly built for learning purposes, so it's stripped down to just the basics.

## how it works

it spins up a cluster of 3 nodes (expecting ports 5001, 5002, 5003). each node runs a background thread with an election timer. if a follower doesn't receive a heartbeat within the randomized timeout window (4-8s), it transitions to a candidate, bumps its term, and requests votes from the other peers.

if a candidate gets a majority of votes (2 or more here), it becomes the leader.

right now, it just implements the leader election phase. fully fledged log replication isn't here.

## running it

you need 3 terminal windows to run the full cluster.

first, install the dependencies (can just spin up a venv):
```bash
pip install fastapi uvicorn requests pydantic
```

then start each node:

**node 1:**
```bash
PORT=5001 uvicorn node:app --port 5001
```

**node 2:**
```bash
PORT=5002 uvicorn node:app --port 5002
```

**node 3:**
```bash
PORT=5003 uvicorn node:app --port 5003
```

watch the console logs. you'll see nodes timing out, starting elections, and voting. if you kill the current leader, you'll see one of the remaining nodes start a new election and take over.

## endpoints

- `GET /` - check current node state (role, current term, who it voted for, etc)
- `POST /request_vote` - internal rpc endpoint used by nodes during elections
