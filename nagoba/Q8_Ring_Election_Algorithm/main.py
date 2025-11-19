class Process:
    def __init__(self, pid):
        self.id = pid
        self.alive = True

    def __repr__(self):
        return f"Process({self.id}, alive={self.alive})"


class RingElectionSystem:
    def __init__(self, process_ids):
        self.processes = [Process(pid) for pid in process_ids]
        self.n = len(self.processes)
        self.coordinator = max(process_ids)  # initially highest ID

    def fail_process(self, pid):
        for p in self.processes:
            if p.id == pid:
                p.alive = False
        print(f"[FAIL] Process {pid} has failed.\n")

    def get_next_alive(self, index):
        """Return the next alive process index in ring."""
        i = (index + 1) % self.n
        while not self.processes[i].alive:
            i = (i + 1) % self.n
        return i

    def start_election(self, starter_id):
        print(f"[ELECTION] Process {starter_id} starts a ring election.")

        # Find index of starter in the list
        idx = next(i for i, p in enumerate(self.processes) if p.id == starter_id)

        # Election message initially contains its own id
        election_msg = [starter_id]

        # Pass message clockwise
        current = idx
        while True:
            next_i = self.get_next_alive(current)
            next_pid = self.processes[next_i].id

            print(f"[PASS] Election message {election_msg} → Process {next_pid}")

            if next_pid in election_msg:
                # Message returned to starter -> election complete
                break

            election_msg.append(next_pid)
            current = next_i

        # New leader = highest alive id in the message
        new_leader = max(election_msg)
        self.coordinator = new_leader

        print(f"\n[COORDINATOR] New leader elected: Process {new_leader}\n")

    def show_status(self):
        print("Current Process States:")
        for p in self.processes:
            print(f"  Process {p.id}: {'Alive' if p.alive else 'Dead'}")
        print(f"Current Coordinator: Process {self.coordinator}\n")


# Example Simulation
if __name__ == "__main__":
    # Create ring of 5 processes
    system = RingElectionSystem([1, 2, 3, 4, 5])
    system.show_status()

    # Fail the current leader (5)
    system.fail_process(5)

    # Process 2 detects failure → starts election
    system.start_election(2)

    system.show_status()
"""
Ring Algorithm vs Bully Algorithm
Feature	Ring Algorithm	Bully Algorithm
Topology	Logical ring	Fully connected
Knows about others	Only neighbor	Knows all higher nodes
Message cost	O(n)	O(n²) worst
Winner	Highest ID	Highest ID
Fairness	All nodes participate equally	High-ID dominates
🧾 Viva Questions & Best Answers
Q1. Why do we use Election Algorithms?

Election algorithms choose a new leader when the current coordinator fails, ensuring system continuity.

Q2. What is the Ring Election Algorithm?

It is an algorithm where distributed processes arranged in a ring pass an election message containing candidate IDs. Each node appends its ID and relays the message. When it returns to initiator, the highest ID becomes the new leader and a coordinator message is broadcast.

Q3. Why is the message passed in a ring?

To simplify communication: each process talks only to the next, reducing network complexity and overhead.

Q4. What happens when multiple nodes start elections at same time?

Messages merge naturally; final message still contains all IDs, so highest ID always wins.

Q5. Why does the highest ID become leader?

Assumption: higher ID node has more resources, more computing power, more reliability.

Q6. What is the complexity of the Ring Algorithm?

O(n), because the election message goes around the ring once.

Q7. Real-world uses?

Token ring networks

Distributed databases

Cluster resource managers

Multi-node lock systems

Cloud container orchestration

📝 1-Minute Spoken Explanation (Exam-ready)

I implemented the Ring Election Algorithm for leader selection in distributed systems. The processes are arranged logically in a circular ring, where each process only knows the address of its next neighbor. When the current leader fails, the detecting process starts an election by sending an ELECTION message with its ID. Each process receiving the message appends its ID and forwards it clockwise. When the message returns to the initiator, it contains all alive process IDs. The highest ID is selected as the new leader. Then a COORDINATOR message is circulated to announce the new leader. The algorithm guarantees fairness and requires only O(n) message complexity. It is simpler than the Bully Algorithm and suitable for ring-structured systems."""