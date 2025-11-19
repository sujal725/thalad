"""
Q7: Bully Algorithm for Leader Election
Simulates node priorities, node failures, and election process.
"""

import threading
import time
from collections import defaultdict

class Node:
    def __init__(self, node_id, all_nodes):
        self.node_id = node_id
        self.priority = node_id  
        self.is_alive = True
        self.is_coordinator = False
        self.all_nodes = all_nodes
        self.lock = threading.Lock()
    
    def crash(self):
        """Simulate node crash"""
        with self.lock:
            self.is_alive = False
            self.is_coordinator = False
        print(f"[Node {self.node_id}] CRASHED")
    
    def recover(self):
        """Recover from crash"""
        with self.lock:
            self.is_alive = True
        print(f"[Node {self.node_id}] RECOVERED")
    
    def start_election(self):
        """Start bully election"""
        print(f"\n[Node {self.node_id}] Starting BULLY ELECTION")
        
        with self.lock:
            self.is_coordinator = False
        
        # Step 1: Send election message to higher priority nodes
        higher_nodes = [n for n in self.all_nodes if n.node_id > self.node_id and n.is_alive]
        
        if not higher_nodes:
            # No higher nodes, this node becomes coordinator
            with self.lock:
                self.is_coordinator = True
            print(f"[Node {self.node_id}] ELECTED as COORDINATOR")
            self._announce_coordinator()
            return
        
        print(f"[Node {self.node_id}] Sending election messages to: {[n.node_id for n in higher_nodes]}")
        
        # Send election messages
        for node in higher_nodes:
            node._receive_election_message(self.node_id)
        
        # Wait for responses
        time.sleep(1)
        
        # If no higher node became coordinator, this node wins
        if not any(n.is_coordinator for n in higher_nodes):
            with self.lock:
                self.is_coordinator = True
            print(f"[Node {self.node_id}] ELECTED as COORDINATOR")
            self._announce_coordinator()
    
    def _receive_election_message(self, sender_id):
        """Receive election message"""
        if not self.is_alive:
            return
        
        print(f"[Node {self.node_id}] Received election from Node {sender_id}")
        
        # Node must respond to sender
        time.sleep(0.1)
        
        # Start own election if not already coordinator
        if not self.is_coordinator:
            threading.Thread(target=self.start_election, daemon=True).start()
    
    def _announce_coordinator(self):
        """Announce this node as coordinator to all"""
        print(f"[Node {self.node_id}] Announcing leadership to all nodes")
        for node in self.all_nodes:
            if node.node_id != self.node_id and node.is_alive:
                node._set_coordinator(self.node_id)
    
    def _set_coordinator(self, coordinator_id):
        """Set coordinator"""
        with self.lock:
            if self.is_alive:
                print(f"[Node {self.node_id}] Acknowledged Node {coordinator_id} as coordinator")


def simulate_bully_election():
    """Simulate bully algorithm"""
    print("=== BULLY ELECTION ALGORITHM ===\n")
    
    # Create nodes with priorities
    print("Creating nodes with priorities (higher ID = higher priority):")
    nodes = [Node(i, None) for i in range(1, 6)]
    for node in nodes:
        node.all_nodes = nodes
        print(f"  Node {node.node_id}: Priority {node.priority}")
    
    print("\n--- SCENARIO 1: Initial Election ---")
    nodes[4].start_election()  # Node 5 starts election
    time.sleep(2)
    
    print(f"\nCoordinator after election: {next((n.node_id for n in nodes if n.is_coordinator), 'None')}")
    
    print("\n--- SCENARIO 2: Coordinator Crash ---")
    coordinator_id = next(n.node_id for n in nodes if n.is_coordinator)
    nodes[coordinator_id - 1].crash()
    time.sleep(1)
    
    print("\n--- SCENARIO 3: New Election After Crash ---")
    nodes[2].start_election()  # Next lower node initiates
    time.sleep(2)
    
    new_coordinator = next((n.node_id for n in nodes if n.is_coordinator), 'None')
    print(f"\nNew Coordinator: {new_coordinator}")
    
    print("\n--- SCENARIO 4: Node Recovery ---")
    nodes[coordinator_id - 1].recover()
    time.sleep(1)
    nodes[coordinator_id - 1].start_election()
    time.sleep(2)
    
    final_coordinator = next(n.node_id for n in nodes if n.is_coordinator)
    print(f"\nFinal Coordinator: {final_coordinator}")
    
    print("\n=== SIMULATION COMPLETE ===")


if __name__ == '__main__':
    simulate_bully_election()
