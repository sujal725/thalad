"""
RING ELECTION ALGORITHM (FIXED)
Leader selected = node with highest ID
"""

import threading
import time

class RingNode:
    def __init__(self, node_id, num_nodes):
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.next_node_id = (node_id + 1) % num_nodes
        self.is_alive = True
        self.is_coordinator = False
        self.all_nodes = {}
        self.lock = threading.Lock()

    def crash(self):
        with self.lock:
            self.is_alive = False
            self.is_coordinator = False
        print(f"[Node {self.node_id}] CRASHED")

    def recover(self):
        with self.lock:
            self.is_alive = True
        print(f"[Node {self.node_id}] RECOVERED")

    def start_election(self):
        if not self.is_alive:
            return

        print(f"\n[Node {self.node_id}] Starting RING ELECTION")
        msg = [self.node_id]
        self._pass_message(msg)

    def _pass_message(self, message_list):
        next_id = self.next_node_id

        for _ in range(self.num_nodes):
            if next_id in self.all_nodes and self.all_nodes[next_id].is_alive:
                break
            next_id = (next_id + 1) % self.num_nodes
        else:
            return

        next_node = self.all_nodes[next_id]
        print(f"[Node {self.node_id}] → Passing {message_list} to Node {next_id}")

        threading.Thread(
            target=next_node._receive_message,
            args=(message_list,),
            daemon=True
        ).start()

    def _receive_message(self, message_list):
        if not self.is_alive:
            return

        time.sleep(0.1)
        print(f"[Node {self.node_id}] Received {message_list}")

        if message_list[0] == self.node_id:
            coordinator_id = max(message_list)
            print(f"\n[Node {self.node_id}] ELECTION COMPLETE. Coordinator = Node {coordinator_id}\n")
            self._announce_coordinator(coordinator_id)
            return

        if self.node_id not in message_list:
            new_list = message_list + [self.node_id]
        else:
            new_list = message_list

        self._pass_message(new_list)

    def _announce_coordinator(self, coord_id):
        for node in self.all_nodes.values():
            if node.is_alive:
                node.is_coordinator = (node.node_id == coord_id)
                print(f"[Node {node.node_id}] Acknowledged Node {coord_id} as COORDINATOR")


def simulate_ring_election():
    print("=== RING ELECTION ALGORITHM ===\n")

    num_nodes = 5
    nodes = {i: RingNode(i, num_nodes) for i in range(num_nodes)}

    for node in nodes.values():
        node.all_nodes = nodes

    print("Ring: 0 → 1 → 2 → 3 → 4 → 0")

    print("\n--- SCENARIO 1: Initial Election ---")
    nodes[0].start_election()
    time.sleep(3)

    coord = next((n for n in nodes.values() if n.is_coordinator), None)
    print(f"Coordinator: Node {coord.node_id if coord else 'None'}")

    print("\n--- SCENARIO 2: Coordinator Crash ---")
    coord.crash()
    time.sleep(1)

    for n in nodes.values():
        n.is_coordinator = False

    print("\n--- SCENARIO 3: New Election After Crash ---")
    nodes[1].start_election()
    time.sleep(3)

    coord = next((n for n in nodes.values() if n.is_coordinator), None)
    print(f"New Coordinator: Node {coord.node_id if coord else 'None'}")

    print("\n--- SCENARIO 4: Multiple Node Failures ---")
    crashed = coord.node_id
    coord.crash()
    nodes[(crashed + 2) % num_nodes].crash()
    time.sleep(1)

    for n in nodes.values():
        n.is_coordinator = False

    print("\n--- SCENARIO 5: Election with Node Down ---")
    nodes[(crashed + 3) % num_nodes].start_election()
    time.sleep(3)

    coord = next((n for n in nodes.values() if n.is_coordinator), None)
    print(f"Final Coordinator: Node {coord.node_id if coord else 'None'}")

    print("\n=== SIMULATION COMPLETE ===")


if __name__ == "__main__":
    simulate_ring_election()
