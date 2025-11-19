"""
Q11: Load Balancer with Round Robin Distribution
Distributes requests to backend servers using Round Robin algorithm.
"""

import threading
import time
import json
from collections import deque

class BackendServer:
    def __init__(self, server_id, processing_time=0.1):
        self.server_id = server_id
        self.processing_time = processing_time
        self.request_count = 0
        self.total_time = 0
        self.lock = threading.Lock()
    
    def process_request(self, request):
        """Process request"""
        with self.lock:
            self.request_count += 1
        
        print(f"  [Backend {self.server_id}] Processing request: {request}")
        time.sleep(self.processing_time)
        
        with self.lock:
            self.total_time += self.processing_time
        
        return f"Processed by Server {self.server_id}: {request}"
    
    def get_stats(self):
        """Get server statistics"""
        with self.lock:
            return {
                'server_id': self.server_id,
                'request_count': self.request_count,
                'avg_time': self.total_time / max(1, self.request_count)
            }


class RoundRobinLoadBalancer:
    def __init__(self, backend_servers):
        self.backends = backend_servers
        self.current_index = 0
        self.lock = threading.Lock()
    
    def distribute_request(self, request):
        """Distribute request using Round Robin"""
        with self.lock:
            server = self.backends[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.backends)
        
        print(f"[LoadBalancer] Routing to Backend {server.server_id}")
        result = server.process_request(request)
        return result


class LeastConnectionsLoadBalancer:
    def __init__(self, backend_servers):
        self.backends = backend_servers
        self.lock = threading.Lock()
    
    def distribute_request(self, request):
        """Distribute request using Least Connections"""
        with self.lock:
            # Find backend with least connections
            min_connections = min(b.request_count for b in self.backends)
            server = next(b for b in self.backends if b.request_count == min_connections)
        
        print(f"[LoadBalancer] Routing to Backend {server.server_id} (connections: {server.request_count})")
        result = server.process_request(request)
        return result


def simulate_load_balancer():
    """Simulate load balancer"""
    print("=== LOAD BALANCER SIMULATION ===\n")
    
    # Create backend servers
    backends = [
        BackendServer(1, processing_time=0.1),
        BackendServer(2, processing_time=0.15),
        BackendServer(3, processing_time=0.12),
    ]
    
    print("Backend servers created: 3\n")
    
    # Test Round Robin
    print("="*60)
    print("ROUND ROBIN LOAD BALANCING")
    print("="*60 + "\n")
    
    lb_rr = RoundRobinLoadBalancer(backends)
    
    print("[Client] Sending 9 requests to Round Robin LB\n")
    for i in range(1, 10):
        request = f"Request-{i}"
        print(f"[Request {i}]")
        result = lb_rr.distribute_request(request)
        print(f"  Response: {result}\n")
    
    print("\nRound Robin Distribution:")
    for backend in backends:
        stats = backend.get_stats()
        print(f"  Backend {stats['server_id']}: {stats['request_count']} requests")
    
    # Reset for Least Connections test
    print("\n" + "="*60)
    print("LEAST CONNECTIONS LOAD BALANCING")
    print("="*60 + "\n")
    
    backends = [
        BackendServer(1, processing_time=0.08),
        BackendServer(2, processing_time=0.2),
        BackendServer(3, processing_time=0.1),
    ]
    
    lb_lc = LeastConnectionsLoadBalancer(backends)
    
    print("[Client] Sending 9 requests to Least Connections LB\n")
    
    # Use threading to show concurrent requests
    def send_request(req_id):
        request = f"Request-{req_id}"
        print(f"[Request {req_id}]")
        result = lb_lc.distribute_request(request)
        print(f"  Response: {result}\n")
    
    threads = []
    for i in range(1, 10):
        t = threading.Thread(target=send_request, args=(i,), daemon=True)
        threads.append(t)
        t.start()
        time.sleep(0.05)  # Stagger requests
    
    for t in threads:
        t.join()
    
    print("\nLeast Connections Distribution:")
    for backend in backends:
        stats = backend.get_stats()
        print(f"  Backend {stats['server_id']}: {stats['request_count']} requests, " +
              f"avg_time: {stats['avg_time']:.3f}s")
    
    print("\n=== SIMULATION COMPLETE ===")
    print("\nKEY DIFFERENCES:")
    print("• Round Robin: Equal distribution regardless of load")
    print("• Least Connections: Dynamic distribution based on active connections")


if __name__ == '__main__':
    simulate_load_balancer()
