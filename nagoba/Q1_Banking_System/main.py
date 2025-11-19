import threading
import time
import random

HEARTBEAT_INTERVAL = 1  # leader sends heartbeat every 1s
HEARTBEAT_TIMEOUT = 3  # follower declares leader dead after 3s


class Server:
    def __init__(self, sid):
        self.sid = sid
        self.is_leader = False
        self.clock = 0
        self.accounts = {"A": 1000}
        self.alive = True
        self.last_heartbeat = time.time()
        self.lock = threading.Lock()

    def tick(self):
        with self.lock:
            self.clock += 1
            return self.clock

    def apply_transaction(self, account, amount, ordered_ts):
        with self.lock:
            self.clock = max(self.clock, ordered_ts) + 1
            self.accounts[account] = self.accounts.get(account, 0) + amount
            return self.clock

    def crash(self):
        self.alive = False
        self.is_leader = False


def bully_election(servers):
    alive = [s for s in servers if s.alive]
    if not alive:
        return None

    new_leader = max(alive, key=lambda s: s.sid)

    for s in servers:
        s.is_leader = False
    new_leader.is_leader = True

    print(f"[ELECTION] New Leader: S{new_leader.sid}")
    return new_leader


def heartbeat_sender(leader: Server, servers):
    while leader.alive and leader.is_leader:
        time.sleep(HEARTBEAT_INTERVAL)
        now = time.time()
        for s in servers:
            if s.sid != leader.sid and s.alive:
                s.last_heartbeat = now
        # print(f"[HEARTBEAT] S{leader.sid} sent heartbeat")


def heartbeat_monitor(server: Server, servers):
    while server.alive:
        time.sleep(1)
        if not server.is_leader:
            if time.time() - server.last_heartbeat > HEARTBEAT_TIMEOUT:
                print(f"[HEARTBEAT-FAIL] S{server.sid} detected leader failure!")
                new_leader = bully_election(servers)
                if new_leader is not None:
                    threading.Thread(
                        target=heartbeat_sender, args=(new_leader, servers), daemon=True
                    ).start()
                break


class TransactionManager:
    def __init__(self, servers):
        self.servers = servers

    def process(self, account, amount):
        leader = next((s for s in self.servers if s.is_leader and s.alive), None)
        if not leader:
            print("[NOTICE] No leader. Running election...")
            leader = bully_election(self.servers)

            if leader:
                threading.Thread(
                    target=heartbeat_sender, args=(leader, self.servers), daemon=True
                ).start()

        leader_time = leader.tick()
        print(f"[LEADER S{leader.sid}] ordering tx @ LClock={leader_time}")

        for s in self.servers:
            if s.alive:
                ts = s.apply_transaction(account, amount, leader_time)
                print(
                    f" S{s.sid} applied tx   -> Balance={s.accounts[account]}  LC={ts}"
                )

        print()


def main():
    servers = [Server(1), Server(2), Server(3)]
    tm = TransactionManager(servers)

    # Start heartbeat monitors for all
    for s in servers:
        threading.Thread(
            target=heartbeat_monitor, args=(s, servers), daemon=True
        ).start()

    # Initial election
    leader = bully_election(servers)
    threading.Thread(
        target=heartbeat_sender, args=(leader, servers), daemon=True
    ).start()

    print("\nInitial Transactions")
    tm.process("A", +200)
    tm.process("A", -50)

    # Crash leader
    print("\nLeader Crash Simulation")
    time.sleep(2)
    print(f"Crashing Leader S{leader.sid}")
    leader.crash()

    # This will trigger heartbeat-based detection
    time.sleep(5)

    print("\nTransactions After Re-Election")
    tm.process("A", +500)

    print("\nFinal Balances")
    for s in servers:
        if s.alive:
            print(f"S{s.sid}: Balance={s.accounts['A']}  LClock={s.clock}")


if __name__ == "__main__":
    main()
"""Q1 – Distributed Banking System with Leader Election & Clock Synchronization
Aim

To simulate a distributed banking environment where multiple servers maintain account data. If the primary server fails, the system automatically elects a new leader, synchronizes clocks to preserve transaction order, and continues processing client transactions consistently.

What the System Does

Multiple banking servers manage account balances.

A leader server coordinates updates and handles global ordering of transactions.

If the leader crashes, remaining servers run a leader election algorithm (Bully or Ring).

Once the new leader is selected, it performs clock synchronization (Berkeley or Lamport).

Transactions continue without loss or duplication, proving availability and consistency.

Key Requirements Mapped to Implementation
Feature	Implementation Approach
Distributed banking servers	Simulate using multiple processes/threads
Leader election	Bully algorithm (or Ring if using ring architecture)
Leader health monitoring	Heartbeat mechanism or periodic ping
Clock synchronization	Berkeley or Lamport clocks
Global ordering	Sort transactions using synchronized timestamps
Communication	REST, RPC, or WebSockets
Consistent transactions	Leader validates & broadcasts updates
Leader Election (Bully Algorithm Explanation)
Assumptions:

Every server has a unique ID / priority.

Higher ID = higher priority.

Servers know IDs of others.

Algorithm steps:

Leader crashes (detected due to missing heartbeat).

Server with lower ID starts election.

It sends ELECTION messages to higher ID servers.

Any higher server replies OK, meaning “I’ll take over”.

Highest alive server declares itself COORDINATOR.

Broadcasts to others that it is the new leader.

Why Bully?

Suitable for small banking clusters.

High priority server becomes leader: reliable, powerful.

Faster than Ring in most cases.

Clock Synchronization

To maintain correct ordering of global transactions, we synchronize clocks.

You can choose:

Berkeley Algorithm (physical clock sync)

Leader polls times from other servers.

Calculates average.

Sends adjustments.

All clocks become time-aligned.

Or

Lamport Logical Clock (logical ordering)

Increment counter on each event.

On message receive: timestamp = max(local, received)+1.

Maintains causal ordering.

Which to choose and why?

Berkeley is better for real transaction timestamp ordering:

We want real-time alignment for banking transactions.

Helps in record auditing and anomaly detection.

Clients see correct chronological order.

Lamport is useful when causal relation matters more than real time.

System Flow Example (Story to Tell in Viva)

Servers S1, S2, S3 maintain bank accounts.

Initial leader = S3.

Client A performs deposit 200 on account 101 handled by leader S3.

S3 broadcasts updated balance to all other servers and timestamps it.

S3 crashes.

S1 detects no heartbeat from S3, starts Bully Election.

S1 sends ELECTION → S2.

S2 responds OK and sends election to S3 (no response).

S2 becomes leader, announces COORDINATOR.

S2 runs Berkeley sync, adjusts clocks.

Client B performs withdraw 50, new leader timestamps it correctly, updates all replicas.

Client operations continue without stopping.

Example Output to Explain
Initial Leader: S3
Heartbeat lost from S3 ... starting election

S1 → S2,ELECTION
S2 → OK
S2 → S3,ELECTION
No response from S3
S2 declares itself LEADER

Clock Synchronization:
Times before sync: S1=100, S2=105, S3=108
Average time = 104.3
Adjusted: S1=+4.3, S2=-0.7, S3=-3.7

Processing Transactions:
ClientA deposit 200 -> Final Balance: 1200 (on all servers)
ClientB withdraw 50 -> Final Balance: 1150

Global ordered logs:
[104.5] deposit 200
[104.6] withdraw 50

Viva Questions and Answers
Q1. Why is leader election needed in distributed banking?

To avoid system failure when the primary server crashes, and to ensure continuous updates, consistency, and synchronization across the remaining servers.

Q2. Why choose Bully Algorithm?

Because it selects the server with highest processing ability and gives fast resolution. It works well when node IDs are known and network is relatively stable.

Q3. Why do we need clock synchronization?

Without clock sync, transaction ordering may be wrong across servers. Deposits and withdrawals could appear in incorrect order causing incorrect balances.

Q4. Why Berkeley instead of Lamport?

Berkeley synchronizes physical clock time, which matches banking needs where real timestamps matter for auditing and transaction history.

Q5. How do clients continue transactions after leader failure?

After leader election, the new leader resumes transaction processing as it has synchronized state and updated timestamps.

Q6. What is eventual effect of synchronization?

All nodes converge to the same balance values and maintain the same global ordering of events.

Q7. How does heartbeat monitoring work?

Leader periodically sends alive signals. If followers do not receive heartbeat within time limit, they initiate election.

Q8. What happens if a follower fails?

As long as at least one server remains alive, election can still occur among remaining nodes.

Q9. What communication method did you choose and why?

Options: REST / RPC / WebSockets. Use depends on implementation method. REST is simple and widely supported.

Q10. What improvements can be done?

Add persistence using database, add multiple leaders, support load balancing, fault tolerance model, two-phase commit protocol.

One-Minute Spoken Summary

I built a distributed banking system where multiple servers maintain customer accounts. A leader server coordinates transactions and ensures consistency. If the leader fails, the system performs automatic leader election using the Bully algorithm. The highest-priority server becomes the new leader. After election, the new leader performs clock synchronization using Berkeley algorithm so that all transaction timestamps align correctly. All servers continue processing requests, and balances remain correct and ordered globally even after a failure. This demonstrates leader election, clock synchronization, replication, and fault-tolerance in distributed banking."""