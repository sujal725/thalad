"""
Q10: Multithreaded Server Handling Multiple Client Requests
Server spawns a thread for each client, processes requests independently.
"""

import socket
import threading
import time
import json

class MultithreadedServer:
    def __init__(self, host='localhost', port=8001):
        self.host = host
        self.port = port
        self.client_count = 0
        self.lock = threading.Lock()
    
    def start(self):
        """Start multithreaded server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)
        print(f"[Server] Listening on {self.host}:{self.port}")
        print("[Server] Accepting connections...\n")
        
        try:
            while True:
                client, addr = server_socket.accept()
                
                with self.lock:
                    self.client_count += 1
                    client_id = self.client_count
                
                print(f"[Server] Client #{client_id} connected from {addr}")
                
                # Spawn new thread for this client
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client, addr, client_id),
                    daemon=True
                )
                thread.start()
        
        except KeyboardInterrupt:
            print("\n[Server] Shutting down...")
        finally:
            server_socket.close()
    
    def _handle_client(self, client, addr, client_id):
        """Handle individual client in separate thread"""
        try:
            print(f"[Thread-{client_id}] Started processing client {addr}")
            
            while True:
                # Receive request
                data = client.recv(1024).decode('utf-8')
                if not data:
                    break
                
                request = json.loads(data)
                print(f"[Thread-{client_id}] Processing: {request}")
                
                # Process request
                if request['type'] == 'text_process':
                    result = self._process_text(request['text'], request['operation'])
                elif request['type'] == 'compute':
                    result = self._compute(request['value'])
                else:
                    result = 'Unknown request'
                
                # Send response
                response = {'success': True, 'result': result}
                client.send(json.dumps(response).encode('utf-8'))
                print(f"[Thread-{client_id}] Response sent to {addr}")
        
        except Exception as e:
            print(f"[Thread-{client_id}] Error: {e}")
        finally:
            client.close()
            print(f"[Thread-{client_id}] Client disconnected")
    
    def _process_text(self, text, operation):
        """Process text operations"""
        time.sleep(0.5)  # Simulate processing
        
        if operation == 'reverse':
            return text[::-1]
        elif operation == 'uppercase':
            return text.upper()
        elif operation == 'lowercase':
            return text.lower()
        elif operation == 'words':
            return len(text.split())
        return 'Unknown operation'
    
    def _compute(self, value):
        """Perform computation"""
        time.sleep(0.2)  # Simulate computation
        return value * value


class ClientSimulator:
    def __init__(self, client_id, host='localhost', port=8001):
        self.client_id = client_id
        self.host = host
        self.port = port
    
    def send_request(self, request):
        """Send request to server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            sock.send(json.dumps(request).encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            sock.close()
            return json.loads(response)
        except Exception as e:
            return {'success': False, 'error': str(e)}


def simulate_multithreaded_server():
    """Simulate multithreaded server"""
    # Start server
    server = MultithreadedServer()
    threading.Thread(target=server.start, daemon=True).start()
    time.sleep(1)
    
    print("="*60)
    print("CLIENT REQUESTS")
    print("="*60 + "\n")
    
    # Simulate multiple clients sending requests concurrently
    def client_requests(client_num):
        client = ClientSimulator(client_num)
        
        # Send multiple requests
        requests = [
            {
                'type': 'text_process',
                'text': f'Hello from Client {client_num}',
                'operation': 'uppercase'
            },
            {
                'type': 'compute',
                'value': 5 + client_num
            },
            {
                'type': 'text_process',
                'text': 'Processing concurrently',
                'operation': 'reverse'
            }
        ]
        
        for req in requests:
            result = client.send_request(req)
            print(f"[Client-{client_num}] Response: {result}")
            time.sleep(0.2)
    
    # Create multiple clients
    clients = []
    for i in range(1, 4):
        thread = threading.Thread(target=client_requests, args=(i,), daemon=True)
        thread.start()
        clients.append(thread)
        time.sleep(0.3)  # Stagger client connections
    
    # Wait for all clients to finish
    for thread in clients:
        thread.join()
    
    time.sleep(1)
    print("\n" + "="*60)
    print("All clients processed independently by separate threads")
    print("="*60)


if __name__ == '__main__':
    simulate_multithreaded_server()
