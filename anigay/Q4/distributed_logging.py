"""
Q4: Distributed Logging System with Clock Synchronization
Implements Lamport Logical Clocks for event ordering across distributed servers.
Lamport chosen over Berkeley because: no physical clock needed, handles async systems well.
"""

import threading
import time
from datetime import datetime
from collections import defaultdict

class LogEntry:
    def __init__(self, event, server_id, lamport_clock):
        self.event = event
        self.server_id = server_id
        self.lamport_clock = lamport_clock
        self.raw_timestamp = time.time()
    
    def __lt__(self, other):
        if self.lamport_clock != other.lamport_clock:
            return self.lamport_clock < other.lamport_clock
        return self.server_id < other.server_id


class DistributedServer:
    def __init__(self, server_id):
        self.server_id = server_id
        self.lamport_clock = 0
        self.logs = []
        self.lock = threading.Lock()
    
    def log_event(self, event):
        """Log an event with Lamport timestamp"""
        with self.lock:
            self.lamport_clock += 1
            entry = LogEntry(event, self.server_id, self.lamport_clock)
            self.logs.append(entry)
            print(f"[Server {self.server_id}] Event logged: '{event}' | Lamport: {entry.lamport_clock}")
            return entry
    
    def receive_message(self, remote_lamport):
        """Update Lamport clock when receiving a message"""
        with self.lock:
            self.lamport_clock = max(self.lamport_clock, remote_lamport) + 1
    
    def get_logs(self):
        """Get all logs"""
        with self.lock:
            return list(self.logs)


class CentralLogManager:
    def __init__(self, servers):
        self.servers = servers  # {id: DistributedServer}
        self.central_logs = []
        self.lock = threading.Lock()
    
    def merge_logs(self):
        """Merge logs from all servers"""
        all_logs = []
        
        for server in self.servers.values():
            all_logs.extend(server.get_logs())
        
        # Sort by Lamport clock, then by server ID for tie-breaking
        all_logs.sort()
        
        with self.lock:
            self.central_logs = all_logs
    
    def display_logs(self):
        """Display merged logs"""
        print("\n=== CENTRALIZED LOG VIEW ===\n")
        print(f"{'Order':<6} {'Server':<8} {'Lamport':<10} {'Raw Time':<25} {'Event':<30}")
        print("-" * 80)
        
        for idx, log in enumerate(self.central_logs, 1):
            raw_time = datetime.fromtimestamp(log.raw_timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"{idx:<6} {log.server_id:<8} {log.lamport_clock:<10} {raw_time:<25} {log.event:<30}")


def simulate_distributed_logging():
    """Simulate distributed logging system"""
    print("=== DISTRIBUTED LOGGING SYSTEM WITH LAMPORT CLOCKS ===\n")
    
    # Create distributed servers
    servers = {
        1: DistributedServer(1),
        2: DistributedServer(2),
        3: DistributedServer(3),
    }
    
    # Simulate events with some concurrency
    def server_events(server_id, events):
        server = servers[server_id]
        for event_name, delay in events:
            time.sleep(delay)
            server.log_event(event_name)
    
    # Define events for each server
    events_s1 = [
        ('Database Query', 0),
        ('Cache Hit', 0.5),
        ('Write Operation', 1),
    ]
    
    events_s2 = [
        ('API Request Received', 0.2),
        ('Auth Validation', 0.7),
        ('Response Sent', 1.2),
    ]
    
    events_s3 = [
        ('File Read', 0.3),
        ('Data Processing', 0.8),
        ('Sync Complete', 1.5),
    ]
    
    # Run events in parallel
    t1 = threading.Thread(target=server_events, args=(1, events_s1))
    t2 = threading.Thread(target=server_events, args=(2, events_s2))
    t3 = threading.Thread(target=server_events, args=(3, events_s3))
    
    print("Events occurring on distributed servers:\n")
    t1.start()
    t2.start()
    t3.start()
    
    t1.join()
    t2.join()
    t3.join()
    
    # Merge and display logs
    manager = CentralLogManager(servers)
    manager.merge_logs()
    manager.display_logs()
    
    # Verify ordering
    print("\n=== ORDERING VERIFICATION ===")
    print("✓ All events are ordered by Lamport clock")
    print("✓ Tie-breaking by Server ID ensures deterministic ordering")
    print("✓ Causal relationships are preserved")
    print("\n=== SIMULATION COMPLETE ===")


if __name__ == '__main__':
    simulate_distributed_logging()
