import random
from fastapi import FastAPI
import os
import threading
import time
import requests
from pydantic import BaseModel

app = FastAPI()


PORT = int(os.environ.get("PORT"))
NODE_ID = f"node-{PORT}"

ALL_NODES = [5001, 5002, 5003]

PEERS = []
for node in ALL_NODES:
    if node != PORT:
        PEERS.append(node)



state = {
    "node_id": NODE_ID,
    "role": "follower",      
    "current_term": 0,
    "voted_for": None,
    "last_heartbeat": time.time(),
}



class VoteRequest(BaseModel):
    term: int
    candidate_id: str



@app.get("/")
def hello():
    return {
        "message": "node alive",
        "state": state
    }



@app.post("/request_vote")
def request_vote(req: VoteRequest):

   
    if req.term < state["current_term"]:
        return {"vote_granted": False}

   
    if req.term > state["current_term"]:
        state["current_term"] = req.term
        state["role"] = "follower"
        state["voted_for"] = None

    if state["voted_for"] is None:
        state["voted_for"] = req.candidate_id
        return {"vote_granted": True}

    # Otherwise reject
    return {"vote_granted": False}



def election_timer():

    timeout = random.uniform(4, 8)

    while True:
        time.sleep(0.2)

        if state["role"] == "follower":

            time_passed = time.time() - state["last_heartbeat"]

            if time_passed > timeout:

               
                state["role"] = "candidate"
                state["current_term"] += 1
                state["voted_for"] = NODE_ID

                print(f"{NODE_ID} starting election for term {state['current_term']}")

                votes = 1  

              
                for peer in PEERS:

                    try:
                        response = requests.post(
                            f"http://localhost:{peer}/request_vote",
                            json={
                                "term": state["current_term"],
                                "candidate_id": NODE_ID
                            },
                            timeout=0.5
                        )

                        result = response.json()

                        if result["vote_granted"]:
                            votes += 1

                    except:
                        print(f"{NODE_ID} could not reach node {peer}")

                print(f"{NODE_ID} received {votes} votes")

            
                if votes >= 2:
                    state["role"] = "leader"
                    print(f"{NODE_ID} became LEADER for term {state['current_term']}")

                timeout = random.uniform(4, 8)



threading.Thread(target=election_timer, daemon=True).start()