class Message:
    def __init__(self, sender_id, text, vector_clock):
        self.sender_id = sender_id
        self.text = text
        self.vector_clock = vector_clock


class Node:
    def __init__(self, node_id, total_nodes):
        self.node_id = node_id
        self.vector_clock = [0] * total_nodes

    def internal_event(self):
        self.vector_clock[self.node_id] += 1
        print(f"Node {self.node_id}: INTERNAL EVENT")
        print(f"Updated vector clock: {self.vector_clock}\n")

    def send_message(self, receiver, message_text):
        self.vector_clock[self.node_id] += 1
        message = Message(self.node_id, message_text, list(self.vector_clock))
        print(f"Node {self.node_id}: SEND → Node {receiver.node_id}")
        print(f"Message clock: {self.vector_clock}\n")
        receiver.receive_message(message)

    def receive_message(self, message):
        # Merge clocks
        print(f"Vector Clock before updation: {self.vector_clock}")
        self.vector_clock = [
            max(local, received)
            for local, received in zip(self.vector_clock, message.vector_clock)
        ]

        # Increment receiver’s own entry
        self.vector_clock[self.node_id] += 1

        print(f"Node {self.node_id}: RECEIVE ← Node {message.sender_id}")
        print(f"Node {self.node_id} received message: {message.text}")
        print(f"Updated vector clock: {self.vector_clock}\n")

    def __str__(self):
        return f"Node {self.node_id} - Final Vector Clock: {self.vector_clock}"


class DistributedSystem:
    def __init__(self, num_nodes):
        self.nodes = [Node(i, num_nodes) for i in range(num_nodes)]

    def simulate(self):
        p0, p1, p2 = self.nodes

        # INTERNAL events
        p0.internal_event()
        p1.internal_event()

        # MESSAGE events
        p0.send_message(p1, "Hello from Node 0")
        p1.internal_event()
        p1.send_message(p2, "Hello from Node 1")

        # More internal events
        p2.internal_event()

        # More messages
        p2.send_message(p0, "Hello from Node 2")

        print("Final Vector Clocks: ")
        for node in self.nodes:
            print(node)


# Run simulation
system = DistributedSystem(3)
system.simulate()

"""Q1: What are Vector Clocks and why do we need them?

Ans:
Vector clocks are a logical time mechanism used in distributed systems to determine the causal ordering of events. They help answer whether event A happened before event B or whether two events are concurrent, without relying on physical time.

Q2: Difference between Lamport and Vector Clocks?
Lamport Clock	Vector Clock
Single integer clock	Array of integers
Captures partial ordering	Captures causality accurately
If LC(A)<LC(B) → does not guarantee A happened before B	VC(A)<VC(B) means A definitely happened before B
Does not detect concurrency	Can detect concurrency
Q3: When do we say events are concurrent?

Ans:
Two events are concurrent if neither vector timestamp is less than the other (i.e., they cannot be ordered causally).

Q4: How is a vector clock updated on send/receive?

Ans:
Send: increment own entry & attach vector
Receive: take element-wise maximum, then increment own entry.

Q5: What are real-world usages of vector clocks?

Ans:

Distributed debugging & monitoring

Amazon DynamoDB conflict resolution

Distributed version control (Git conceptually similar)

Event ordering in distributed logging & messaging systems
Short 1-minute viva explanation

I simulated Vector Clocks for logical time synchronization in a distributed environment with multiple processes. Each process maintains a vector timestamp that stores knowledge of events in all processes. When an internal event occurs, the local entry is incremented. When a message is sent, the vector is attached, and when a message is received, the receiving process performs an element-wise maximum merge and increments its own entry.
This enables determining event ordering: if VA < VB, event A happened before B, otherwise they are concurrent. Unlike Lamport clocks, vector clocks can detect concurrency accurately. This is essential in distributed debugging and conflict resolution in distributed storage systems like DynamoDB."""
