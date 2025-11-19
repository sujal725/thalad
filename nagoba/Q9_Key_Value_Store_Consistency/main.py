import threading
import time


class Replica:
    def __init__(self, rid):
        self.rid = rid
        self.store = {}
        self.lock = threading.Lock()

    def read(self, key):
        with self.lock:
            return self.store.get(key, None)

    def write(self, key, value):
        with self.lock:
            self.store[key] = value

    def __str__(self):
        with self.lock:
            return f"Replica{self.rid}: {self.store}"


class ReplicationSystem:
    def __init__(self, num_replicas=3, propagate_delay=3.0):
        self.replicas = [Replica(i) for i in range(num_replicas)]
        self.delay = propagate_delay

    def show_all(self, prefix=""):
        print(prefix)
        for r in self.replicas:
            print("  ", r)
        print()

    # Strong consistency: update all replicas synchronously
    def strong_update(self, key, value):
        print(
            f"[STRONG] Updating key='{key}' -> '{value}' on all replicas (synchronous)"
        )
        for r in self.replicas:
            r.write(key, value)
        print("[STRONG] Acknowledged to client (all replicas updated)\n")

    # Eventual consistency: write to one replica, schedule async propagation
    def eventual_update(self, primary_idx, key, value):
        primary = self.replicas[primary_idx]
        print(
            f"[EVENTUAL] Client updates Replica{primary_idx}: key='{key}' -> '{value}' (ack immediately)"
        )
        primary.write(key, value)
        # schedule propagation to others after delay
        t = threading.Timer(
            self.delay, self._propagate_from, args=(primary_idx, key, value)
        )
        t.daemon = True
        t.start()
        print(
            f"[EVENTUAL] Update acknowledged to client; propagation scheduled in {self.delay} sec\n"
        )

    def _propagate_from(self, primary_idx, key, value):
        print(
            f"[PROPAGATE] Propagating key='{key}' -> '{value}' from Replica{primary_idx} to others..."
        )
        for i, r in enumerate(self.replicas):
            if i == primary_idx:
                continue
            r.write(key, value)
        print("[PROPAGATE] Propagation complete.\n")

    # Helper read (read-from-one-replica)
    def read_from(self, replica_idx, key):
        val = self.replicas[replica_idx].read(key)
        print(f"[READ] Replica{replica_idx} returned: {key} -> {val}")
        return val


# Example demonstration script
def demo():
    sys = ReplicationSystem(num_replicas=3, propagate_delay=4.0)

    # Initialize same key on all replicas
    print("INITIAL STATE:")
    sys.strong_update("x", "100")
    sys.strong_update("y", "500")
    sys.strong_update("z", "900")
    sys.show_all("After initialization:")

    # EVENTUAL: update replicas asynchronously
    sys.eventual_update(primary_idx=0, key="x", value="200")
    sys.eventual_update(primary_idx=1, key="y", value="600")

    # Immediately read from all replicas (shows divergence)
    print("IMMEDIATE READS (after eventual-update, before propagation):")
    for i in range(3):
        sys.read_from(i, "x")
        sys.read_from(i, "y")
        sys.read_from(i, "z")
    print()

    # Wait for propagation to complete
    print(f"Waiting {sys.delay + 1} seconds for propagation...\n")
    time.sleep(sys.delay + 1)

    # Read again — replicas should have converged
    print("READS AFTER PROPAGATION (eventual consistency achieved):")
    for i in range(3):
        sys.read_from(i, "x")
        sys.read_from(i, "y")
        sys.read_from(i, "z")
    print()

    # Now demonstrate STRONG update: write synchronously to all replicas
    sys.strong_update("x", "300")
    print("READS AFTER STRONG UPDATE (all replicas consistent immediately):")
    for i in range(3):
        sys.read_from(i, "x")
    print()

    # Final snapshot
    sys.show_all("FINAL STATE:")


if __name__ == "__main__":
    demo()
"""1. Strict Consistency

Any read returns the most recent write instantly, across the entire system.

Meaning:

If a write happens at time t, then any read at time > t must return the updated value.

Requires globally synchronized clocks.

Impossible to guarantee in real distributed systems with network delays.

Example:

Time 10: Write X=5
Time 10.1: Any client anywhere must read X=5


Real-world?
❌ Impossible in practice due to latency and CAP theorem.

2. Strong Consistency

After a write completes, any subsequent read returns the updated value, but reads before write completion can still return old values.

Example:

write(X=5) completes
→ all reads return X=5


Used in:

HBase, BigTable, Zookeeper, relational DBs with distributed transactions

Seen when applications require absolute correctness (banking, stock trading)

3. Eventual Consistency

If no new updates are made, all replicas eventually converge to the same value, but temporarily they may return different values.

Example sequence:

Initial: X = 100 across A,B,C

Write X=500 only on A
Immediately read: A=500, B=100, C=100  ← temporary inconsistency
Propagation occurs
Finally: A=500, B=500, C=500


Used in:

Amazon DynamoDB, Cassandra, S3, Mobile chat systems, DNS, WhatsApp message sync

Reason:
✔ High availability
✔ Low latency
✔ Works well under network failure

🔁 Flow of Your Simulation (To Explain in Viva)
Replicas initially:
Node A: {"balance":1000}
Node B: {"balance":1000}
Node C: {"balance":1000}

Update performed on Node A only:
Node A updates balance = 5000
Nodes B & C still show 1000


Client reads now:

Read from A → 5000
Read from B → 1000
Read from C → 1000

After delay (simulate propagation after 3 seconds):
Propagating update to all nodes...
Node B → 5000
Node C → 5000


Final state:

A:5000 B:5000 C:5000  (converged)


This proves Eventual Consistency.

📦 Expected Sample Output (Explain in Viva)
Initial state:
A: {"value":100}
B: {"value":100}
C: {"value":100}

Updating replica A only...
A: {"value":500}
B: {"value":100}
C: {"value":100}

Reads immediately after update:
Read from A -> 500
Read from B -> 100
Read from C -> 100

Propagating update after delay...

Final state after sync:
A: {"value":500}
B: {"value":500}
C: {"value":500}

--> Eventual consistency achieved.

Explain what happened:

Immediately after update — replicas temporarily inconsistent

Eventually — all replicas converge

Demonstrates AP (Availability + Partition tolerance) tradeoff of CAP theorem

📌 Strong Consistency vs Eventual Consistency — Comparison Table
Feature	Strong Consistency	Eventual Consistency
Read-after-write	Guaranteed	Not guaranteed
Temporary differences	No	Yes
Latency	Higher	Very low
Availability under failures	Lower	High
Use case	Banking, transactions	Social media, real-time apps
Example system	Google Spanner, Zookeeper	DynamoDB, Cassandra, S3
🧪 Viva Questions & Answer Format
Q1. Why is consistency a challenge in distributed systems?

Because replicas are stored across multiple machines, and due to network delays, packet loss, and partitions, we cannot guarantee immediate synchronization.

Q2. What is eventual consistency?

Eventual consistency means that replicas may temporarily differ, but eventually converge to the same value if no new updates occur.

Q3. Why use eventual consistency instead of strong consistency?

For high availability, low latency, offline mode support, and scaling in distributed applications.

Q4. Where is eventual consistency used in real life?

Amazon shopping cart, WhatsApp chat sync across devices, DNS updates, social media likes.

Q5. What is the CAP theorem and which model does eventual consistency follow?

CAP: A distributed system cannot guarantee Consistency, Availability, and Partition tolerance simultaneously.
Eventual consistency favors AP and relaxes consistency requirement.

Q6. Give an example scenario showing inconsistency.

Client1 reads A=500
Client2 reads A=100 at the same time (before replication)
Later both read A=500 after sync.

Q7. What would be Strong Consistency output in the same example?
Write A=500
Reads from all replicas instantly return 500


No temporary inconsistency.

🎤 1-Minute Spoken Summary for viva

I implemented a distributed key-value store with three replicas. Initially, all replicas store the same value. When an update is performed on one replica, the others temporarily hold the old value. After simulating network delay, the update propagates to all replicas and they converge to the same value. This demonstrates eventual consistency, where replicas become consistent over time.
In contrast, strong consistency guarantees that any read after a completed write will immediately reflect the latest value across all replicas, and strict consistency requires reads always return the most recent global write — something impossible in practical distributed systems due to real-world delays. Eventual consistency is widely used in distributed storage systems like DynamoDB, Cassandra, and DNS because it offers high availability and scalability."""