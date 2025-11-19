class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.alive = True

    def __repr__(self):
        return f"Node({self.id}, alive={self.alive})"


class BullySystem:
    def __init__(self, node_ids):
        self.nodes = {nid: Node(nid) for nid in node_ids}
        self.coordinator = max(node_ids)

    def fail_node(self, nid):
        self.nodes[nid].alive = False
        print(f"[FAIL] Node {nid} has failed.")

        if nid == self.coordinator:
            print("[INFO] Coordinator failed! Election required.\n")

    def start_election(self, starter_id):
        print(f"[ELECTION] Node {starter_id} starts election.")
        starter = self.nodes[starter_id]

        higher_nodes = [n for n in self.nodes.values() if n.id > starter_id and n.alive]

        if not higher_nodes:
            # No higher alive nodes → starter becomes coordinator
            self.coordinator = starter_id
            print(f"[COORDINATOR] Node {starter_id} becomes the new coordinator!\n")
            return

        print(
            f"[SEND] Node {starter_id} → Election message → {', '.join(str(n.id) for n in higher_nodes)}"
        )

        # Higher node responds and starts its own election
        for h in higher_nodes:
            print(f"[OK] Node {h.id} responds to Node {starter_id}.")
            self.start_election(h.id)  # recursive cascade
            return  # Only first alive higher node handles next

    def show_status(self):
        print("Current Nodes:")
        for n in self.nodes.values():
            print(f"  Node {n.id}: {'Alive' if n.alive else 'Dead'}")
        print(f"Current Coordinator: Node {self.coordinator}\n")


# Example Simulation
if __name__ == "__main__":
    system = BullySystem([1, 2, 3, 4, 5])

    system.show_status()

    # Fail the coordinator (5)
    system.fail_node(5)

    # Node 2 detects failure and starts election
    system.start_election(2)

    system.show_status()
"""Concept Explanation
Why do we need Leader Election?

In distributed systems, many tasks (such as synchronization, replication, transaction ordering) need a coordinator.
If the coordinator fails, a new leader must be chosen automatically — without shutting down the system.

Bully Algorithm

Used in distributed systems for leader election. Works based on priority.

Assumptions

Each node has a unique ID

Higher ID → higher power

Nodes know IDs of all others

Communication is reliable

🛠 How the Bully Algorithm Works (Steps)
1. Normal Operation

The highest-ID node is the leader.

2. Leader Failure

A lower-priority node detects leader failure (e.g., missing heartbeat).

It initiates an election.

3. Election Message

Node N sends ELECTION message to all nodes with higher ID.
Example:

Node 2 → Node 3, Node 4, Node 5: ELECTION?

4. Response

If any higher-ID node is alive, it replies:

OK


Meaning: “I am alive, I will take over the election.”

5. Higher node continues the election

The highest node among alive continues election steps repeating the same process.

6. New Leader is Announced

The highest-ID alive node declares itself as:

COORDINATOR


Broadcasts to all nodes: "I am the new leader".

🧾 Example Scenario (Explain in Viva)

Nodes with priorities:

Nodes: 1, 2, 3, 4, 5

Current leader = Node 5
Node failure: Node 5 crashes

Node 3 detects failure → starts election:

3 -> 4,5 : ELECTION?


Node 4 responds:

4 -> 3 : OK
4 -> 5 : ELECTION?


No reply from 5, so 4 becomes leader.

Node 4 broadcasts:

4 -> ALL : COORDINATOR

📌 Result:
New Leader: Node 4

📦 Output Example Explanation (Typical Console Output)
Nodes: [1,2,3,4,5]
Initial Leader: 5

Simulating failure: Node 5 down

Node 3 initiates election
3 -> 4,5 : ELECTION
Reply from 4: OK

Node 4 initiates election
4 -> 5 : ELECTION
(no response)

Node 4 declares itself leader
Broadcast: 4 is the new COORDINATOR

📍 Interpretation:

Leader failure detected

Election request sent to higher priority nodes

Node with highest alive ID wins

System continues without downtime

👨‍🏫 Viva Questions & Best Answers
Q1. What is leader election in distributed systems?

Leader election selects a single coordinator among distributed nodes to manage tasks like synchronization and controlling access to shared resources. If the leader fails, a new one must take over.

Q2. Why do we use the Bully Algorithm?

Because it is simple, fast, and ensures that the highest-priority node becomes the leader, preventing conflicts and guaranteeing strong leadership.

Q3. Why does the highest ID node win?

Because:

It has the highest capability (assumed strongest hardware)

Guarantees deterministic result

Prevents two leaders at the same time

Q4. What happens if two nodes start an election simultaneously?

Both send election messages, but ultimately the highest priority alive node wins since it continues eliminating lower-priority nodes.

Q5. What is the communication complexity of the Bully Algorithm?

Worst case: O(n²) — because each node may contact all higher nodes multiple times.

Q6. What are limitations of the Bully Algorithm?
Limitation	Reason
High message overhead	Especially with many nodes
Assumes reliable communication	No network packet loss
Assumes known node list	Static topology only
Q7. Difference between Bully vs Ring Election Algorithm
Bully Algorithm	Ring Algorithm
Highest-ID wins	Highest-ID after ring cycle wins
Fully connected network	Logical ring topology
Faster	More message passing
Needs knowing all nodes	Only neighbors need to be known
Q8. Real-world uses

Distributed databases

Kafka cluster controllers

Hadoop NameNode HA

Zookeeper coordination

📝 1-Minute Viva Summary (Speak like this)

In my project, I simulated a distributed system with 5 nodes, each assigned a priority ID. The Bully Algorithm is used for leader election: the highest priority node becomes the coordinator. When the leader fails, a lower-priority node detects it and starts an election by sending election messages to higher-priority nodes. Any alive higher node responds and continues the election process. Eventually, the highest-priority alive node declares itself the leader and broadcasts a coordinator message. This ensures continued system operation with no downtime. The algorithm is simple, deterministic, and efficient for small systems."""