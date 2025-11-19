"""
Q9: Distributed Key-Value Store with Eventual Consistency
3 replica nodes demonstrating eventual consistency vs strong consistency.
"""

import threading
import time
from collections import defaultdict

class KVReplica:
    def __init__(self, replica_id):
        self.replica_id = replica_id
        self.data = {}
        self.version = defaultdict(int)
        self.lock = threading.Lock()
        self.pending_updates = []
    
    def write(self, key, value, sync=False):
        """Write data (optionally synchronous)"""
        with self.lock:
            self.data[key] = value
            self.version[key] += 1
            timestamp = time.time()
        
        print(f"[Replica {self.replica_id}] WRITE: {key}={value} (v{self.version[key]})")
        
        if not sync:
            # Eventual consistency: queue for later propagation
            self.pending_updates.append({
                'key': key,
                'value': value,
                'version': self.version[key],
                'timestamp': timestamp
            })
        
        return self.version[key]
    
    def read(self, key):
        """Read data"""
        with self.lock:
            value = self.data.get(key, None)
            version = self.version.get(key, 0)
        
        print(f"[Replica {self.replica_id}] READ: {key}={value} (v{version})")
        return value, version
    
    def apply_update(self, key, value, version):
        """Apply update from another replica"""
        with self.lock:
            current_version = self.version.get(key, 0)
            
            # Only apply if it's a newer version
            if version > current_version:
                self.data[key] = value
                self.version[key] = version
                print(f"[Replica {self.replica_id}] UPDATE received: {key}={value} (v{version})")
                return True
            else:
                print(f"[Replica {self.replica_id}] IGNORED: {key} (old v{version}, current v{current_version})")
                return False
    
    def get_state(self):
        """Get current state"""
        with self.lock:
            return dict(self.data), dict(self.version)


class DistributedKVStore:
    def __init__(self, num_replicas=3):
        self.replicas = {i: KVReplica(i) for i in range(num_replicas)}
        self.num_replicas = num_replicas
    
    def write_strong_consistency(self, key, value):
        """Write with strong consistency (all replicas synchronous)"""
        print(f"\n--- STRONG CONSISTENCY WRITE: {key}={value} ---")
        for replica in self.replicas.values():
            replica.write(key, value, sync=True)
        print("✓ All replicas updated synchronously")
    
    def write_eventual_consistency(self, replica_id, key, value, delay=1.0):
        """Write with eventual consistency (async propagation)"""
        print(f"\n--- EVENTUAL CONSISTENCY WRITE: {key}={value} on Replica {replica_id} ---")
        
        # Write to primary
        version = self.replicas[replica_id].write(key, value, sync=False)
        
        # Propagate to other replicas after delay
        def propagate():
            time.sleep(delay)
            for rid, replica in self.replicas.items():
                if rid != replica_id:
                    replica.apply_update(key, value, version)
        
        threading.Thread(target=propagate, daemon=True).start()
    
    def read_all(self, key):
        """Read from all replicas"""
        print(f"\n--- READING {key} from all replicas ---")
        for replica in self.replicas.values():
            replica.read(key)
    
    def get_consistency_status(self):
        """Check if all replicas are consistent"""
        states = [self.replicas[i].get_state()[0] for i in range(self.num_replicas)]
        
        # Check if all have same data
        consistent = all(state == states[0] for state in states)
        return consistent, states


def simulate_kv_store():
    """Simulate KV store with consistency models"""
    print("=== DISTRIBUTED KEY-VALUE STORE ===\n")
    
    store = DistributedKVStore(3)
    
    print("Initial state: All replicas empty\n")
    
    # SCENARIO 1: Strong Consistency
    print("\n" + "="*60)
    print("SCENARIO 1: STRONG CONSISTENCY")
    print("="*60)
    
    store.write_strong_consistency('user:1', {'name': 'Alice', 'balance': 1000})
    time.sleep(0.5)
    
    store.read_all('user:1')
    consistent, states = store.get_consistency_status()
    print(f"\nConsistent across all replicas: {consistent}")
    
    # SCENARIO 2: Eventual Consistency
    print("\n" + "="*60)
    print("SCENARIO 2: EVENTUAL CONSISTENCY")
    print("="*60)
    
    print("\nStep 1: Write to Replica 0")
    store.write_eventual_consistency(0, 'user:2', {'name': 'Bob', 'balance': 500}, delay=2.0)
    
    print("\nStep 2: Read IMMEDIATELY after write (before propagation)")
    time.sleep(0.5)
    store.read_all('user:2')
    consistent, states = store.get_consistency_status()
    print(f"Consistent across all replicas: {consistent}")
    print("⚠ Replicas are INCONSISTENT - eventual consistency in progress")
    
    print("\nStep 3: Waiting for propagation (2 seconds)...")
    time.sleep(2.5)
    
    print("\nStep 4: Read AFTER propagation")
    store.read_all('user:2')
    consistent, states = store.get_consistency_status()
    print(f"Consistent across all replicas: {consistent}")
    print("✓ Replicas are now CONSISTENT")
    
    # SCENARIO 3: Concurrent Updates
    print("\n" + "="*60)
    print("SCENARIO 3: CONCURRENT UPDATES")
    print("="*60)
    
    print("\nUpdate 1: Write on Replica 0")
    store.write_eventual_consistency(0, 'counter', 100, delay=1.0)
    
    time.sleep(0.5)
    print("\nUpdate 2: Write on Replica 1 (before replication)")
    store.write_eventual_consistency(1, 'counter', 200, delay=1.0)
    
    print("\nWaiting for propagation...")
    time.sleep(1.5)
    
    print("\nFinal state:")
    consistent, states = store.get_consistency_status()
    for i, state in enumerate(states):
        print(f"  Replica {i}: {state}")
    
    print("\n=== SIMULATION COMPLETE ===")
    print("\nKEY DIFFERENCES:")
    print("• Strong Consistency: All reads return latest data, but slower")
    print("• Eventual Consistency: Faster writes, but temporary inconsistency")


if __name__ == '__main__':
    simulate_kv_store()
