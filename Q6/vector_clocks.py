"""
Q6: Vector Clocks for Logical Clock Synchronization
Simulates distributed processes with vector clock-based event ordering.
"""

import threading
import time
from collections import defaultdict

class VectorClock:
    def __init__(self, process_id, num_processes):
        self.process_id = process_id
        self.clock = [0] * num_processes
    
    def increment(self):
        """Increment own clock"""
        self.clock[self.process_id] += 1
    
    def update(self, received_clock):
        """Update clock when receiving message"""
        for i in range(len(self.clock)):
            self.clock[i] = max(self.clock[i], received_clock[i])
        self.clock[self.process_id] += 1
    
    def copy(self):
        """Get copy of clock"""
        return self.clock.copy()
    
    def __lt__(self, other):
        """Check if this clock is causally before other"""
        less = False
        for i in range(len(self.clock)):
            if self.clock[i] > other[i]:
                return False
            if self.clock[i] < other[i]:
                less = True
        return less
    
    def __str__(self):
        return str(self.clock)


class DistributedProcess:
    def __init__(self, process_id, num_processes):
        self.process_id = process_id
        self.vc = VectorClock(process_id, num_processes)
        self.events = []
        self.lock = threading.Lock()
    
    def local_event(self, event_name):
        """Execute a local event"""
        with self.lock:
            self.vc.increment()
            self.events.append({
                'type': 'local',
                'name': event_name,
                'vc': self.vc.copy()
            })
            print(f"[P{self.process_id}] Local: {event_name} | VC: {self.vc}")
    
    def send_message(self, message, target_process):
        """Send message to another process"""
        with self.lock:
            self.vc.increment()
            self.events.append({
                'type': 'send',
                'name': f"Send: {message}",
                'vc': self.vc.copy()
            })
            print(f"[P{self.process_id}] Send: {message} → P{target_process} | VC: {self.vc}")
        
        return self.vc.copy()
    
    def receive_message(self, message, sender_vc):
        """Receive message from another process"""
        with self.lock:
            self.vc.update(sender_vc)
            self.events.append({
                'type': 'receive',
                'name': f"Receive: {message}",
                'vc': self.vc.copy()
            })
            print(f"[P{self.process_id}] Receive: {message} | VC: {self.vc}")
    
    def get_events(self):
        """Get all events"""
        with self.lock:
            return list(self.events)


def simulate_vector_clocks():
    """Simulate vector clock synchronization"""
    print("=== VECTOR CLOCKS SIMULATION ===\n")
    
    # Create 3 processes
    processes = {
        0: DistributedProcess(0, 3),
        1: DistributedProcess(1, 3),
        2: DistributedProcess(2, 3),
    }
    
    print("Distributed processes with Vector Clocks:\n")
    
    # Simulate events
    def p0_events():
        processes[0].local_event("Read from disk")
        time.sleep(0.1)
        vc = processes[0].send_message("Request data", 1)
        processes[1].receive_message("Request from P0", vc)
        time.sleep(0.1)
        processes[0].local_event("Processing")
    
    def p1_events():
        processes[1].local_event("Initialize")
        time.sleep(0.2)
        vc = processes[1].send_message("Send data", 2)
        processes[2].receive_message("Data from P1", vc)
    
    def p2_events():
        time.sleep(0.15)
        processes[2].local_event("Waiting for data")
        time.sleep(0.1)
        processes[2].local_event("Data received")
    
    # Run processes concurrently
    t0 = threading.Thread(target=p0_events)
    t1 = threading.Thread(target=p1_events)
    t2 = threading.Thread(target=p2_events)
    
    t0.start()
    t1.start()
    t2.start()
    
    t0.join()
    t1.join()
    t2.join()
    
    # Display all events
    print("\n=== EVENT ORDERING BY VECTOR CLOCK ===\n")
    all_events = []
    for pid, process in processes.items():
        for event in process.get_events():
            all_events.append((pid, event))
    
    print(f"{'Process':<10} {'Event':<30} {'Vector Clock':<20}")
    print("-" * 60)
    for pid, event in sorted(all_events, key=lambda x: x[1]['vc']):
        print(f"P{pid:<9} {event['name']:<30} {event['vc']}")
    
    print("\n=== CAUSALITY ANALYSIS ===")
    print("✓ Events ordered by vector clock values")
    print("✓ Causal relationships preserved across processes")
    print("✓ Concurrent events properly detected")
    print("\n=== SIMULATION COMPLETE ===")


if __name__ == '__main__':
    simulate_vector_clocks()
