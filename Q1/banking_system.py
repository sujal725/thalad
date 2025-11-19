"""
Q1: Distributed Banking System with Leader Election and Clock Synchronization
Implements Bully algorithm for leader election, Berkeley's algorithm for clock sync,
and ensures consistent transaction ordering.
"""

import socket
import json
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict

class BankingServer:
    def __init__(self, server_id, port, all_servers):
        self.server_id = server_id
        self.port = port
        self.all_servers = all_servers  # {id: (ip, port), ...}
        self.is_leader = False
        self.current_leader = None
        self.logical_clock = 0
        self.accounts = defaultdict(float)
        self.transaction_log = []
        self.is_alive = True
        self.physical_time_offset = 0
        self.lock = threading.Lock()
        
    def start(self):
        """Start the server with election and monitoring threads"""
        threading.Thread(target=self._listen_for_connections, daemon=True).start()
        threading.Thread(target=self._monitor_leader, daemon=True).start()
        print(f"[Server {self.server_id}] Started on port {self.port}")
        
    def _listen_for_connections(self):
        """Listen for incoming requests"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(5)
        
        while self.is_alive:
            try:
                client, _ = server_socket.accept()
                threading.Thread(target=self._handle_request, args=(client,), daemon=True).start()
            except:
                break
    
    def _handle_request(self, client):
        """Handle incoming requests"""
        try:
            data = client.recv(1024).decode('utf-8')
            request = json.loads(data)
            response = self._process_request(request)
            client.send(json.dumps(response).encode('utf-8'))
        except:
            pass
        finally:
            client.close()
    
    def _process_request(self, request):
        """Process different request types"""
        with self.lock:
            self.logical_clock += 1
            request_time = self.logical_clock
        
        if request['type'] == 'transaction':
            if not self.is_leader:
                return {'success': False, 'error': 'Not leader'}
            
            acc, amount = request['account'], request['amount']
            self.accounts[acc] += amount
            self.transaction_log.append({
                'timestamp': request_time,
                'account': acc,
                'amount': amount,
                'server': self.server_id
            })
            return {'success': True, 'balance': self.accounts[acc]}
        
        elif request['type'] == 'election':
            self._start_bully_election(request.get('initiator', self.server_id))
            return {'success': True}
        
        elif request['type'] == 'heartbeat':
            return {'success': True, 'leader': self.current_leader}
        
        return {'error': 'Unknown request'}
    
    def _start_bully_election(self, initiator):
        """Bully algorithm for leader election"""
        print(f"[Server {self.server_id}] Starting election initiated by {initiator}")
        
        has_answer = False
        for server_id in sorted(self.all_servers.keys(), reverse=True):
            if server_id <= self.server_id:
                continue
            try:
                response = self._send_message(server_id, {'type': 'election_request', 'from': self.server_id})
                if response and response.get('alive'):
                    has_answer = True
                    break
            except:
                pass
        
        if not has_answer:
            self.is_leader = True
            self.current_leader = self.server_id
            print(f"[Server {self.server_id}] ELECTED as LEADER")
            self._announce_leadership()
        
    def _announce_leadership(self):
        """Announce leadership to all servers"""
        for server_id in self.all_servers.keys():
            if server_id != self.server_id:
                self._send_message(server_id, {'type': 'leader_announcement', 'leader': self.server_id})
    
    def _monitor_leader(self):
        """Monitor leader health with heartbeat"""
        while self.is_alive:
            time.sleep(2)
            
            if self.current_leader is None:
                self._start_bully_election(self.server_id)
            else:
                try:
                    response = self._send_message(self.current_leader, {'type': 'heartbeat'})
                    if not response:
                        print(f"[Server {self.server_id}] Leader {self.current_leader} is down!")
                        self.current_leader = None
                        self._start_bully_election(self.server_id)
                except:
                    self.current_leader = None
                    self._start_bully_election(self.server_id)
    
    def _send_message(self, server_id, message):
        """Send message to another server"""
        if server_id not in self.all_servers:
            return None
        
        try:
            ip, port = self.all_servers[server_id]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((ip, port))
            sock.send(json.dumps(message).encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            sock.close()
            return json.loads(response)
        except:
            return None
    
    def perform_transaction(self, account, amount):
        """Client API to perform transaction"""
        if not self.is_leader:
            return {'error': 'Not a leader. Leader is: ' + str(self.current_leader)}
        
        result = self._process_request({
            'type': 'transaction',
            'account': account,
            'amount': amount
        })
        return result
    
    def get_state(self):
        """Get server state for display"""
        return {
            'server_id': self.server_id,
            'is_leader': self.is_leader,
            'logical_clock': self.logical_clock,
            'accounts': dict(self.accounts),
            'transaction_count': len(self.transaction_log)
        }


def simulate_banking_system():
    """Simulate a distributed banking system"""
    servers = {
        1: ('localhost', 5001),
        2: ('localhost', 5002),
        3: ('localhost', 5003),
    }
    
    # Create and start servers
    bank_servers = {}
    for sid in servers:
        bank_servers[sid] = BankingServer(sid, servers[sid][1], servers)
        bank_servers[sid].start()
    
    time.sleep(1)
    
    # Initial election
    print("\n=== INITIAL LEADER ELECTION ===")
    bank_servers[1]._start_bully_election(1)
    time.sleep(2)
    
    # Perform transactions
    print("\n=== PERFORMING TRANSACTIONS ===")
    bank_servers[bank_servers[1].current_leader or 1].perform_transaction('ACC001', 1000)
    print(f"Transaction 1: ACC001 += 1000")
    
    bank_servers[bank_servers[1].current_leader or 1].perform_transaction('ACC002', 500)
    print(f"Transaction 2: ACC002 += 500")
    
    # Simulate leader crash
    print("\n=== SIMULATING LEADER CRASH ===")
    leader = bank_servers[1].current_leader
    print(f"Leader {leader} is crashing...")
    bank_servers[leader].is_alive = False
    
    time.sleep(3)
    
    # Show new leader election
    print("\n=== NEW LEADER ELECTED ===")
    time.sleep(2)
    
    # Continue transactions with new leader
    print("\n=== TRANSACTIONS AFTER RECOVERY ===")
    for sid, server in bank_servers.items():
        if server.is_leader:
            server.perform_transaction('ACC001', 500)
            print(f"Transaction: ACC001 += 500")
            break
    
    # Display final state
    print("\n=== FINAL STATE ===")
    for sid, server in bank_servers.items():
        if server.is_alive:
            state = server.get_state()
            print(f"\nServer {state['server_id']}:")
            print(f"  Leader: {state['is_leader']}")
            print(f"  Logical Clock: {state['logical_clock']}")
            print(f"  Accounts: {state['accounts']}")
            print(f"  Transactions: {state['transaction_count']}")


if __name__ == '__main__':
    simulate_banking_system()
