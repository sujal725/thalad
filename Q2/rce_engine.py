"""
Q2: Remote Code Execution Engine using Socket RPC with Multithreading
Client sends code snippets to server, server executes and returns results.
"""

import socket
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

class RCEServer:
    def __init__(self, host='localhost', port=6001):
        self.host = host
        self.port = port
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def start(self):
        """Start the RCE server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)
        print(f"[RCE Server] Listening on {self.host}:{self.port}")
        
        try:
            while True:
                client, addr = server_socket.accept()
                print(f"[RCE Server] Client connected from {addr}")
                self.executor.submit(self._handle_client, client, addr)
        except KeyboardInterrupt:
            print("\n[RCE Server] Shutting down...")
        finally:
            server_socket.close()
    
    def _handle_client(self, client, addr):
        """Handle individual client requests"""
        try:
            # Receive code
            data = client.recv(1024).decode('utf-8')
            request = json.loads(data)
            
            print(f"[RCE Server] Processing request from {addr}: {request['type']}")
            
            # Execute code
            if request['type'] == 'arithmetic':
                result = self._execute_arithmetic(request['operation'], request['operands'])
            elif request['type'] == 'sort':
                result = self._execute_sort(request['data'])
            elif request['type'] == 'string':
                result = self._execute_string(request['operation'], request['text'])
            else:
                result = {'error': 'Unknown operation'}
            
            # Send response
            response = {'success': True, 'result': result}
            client.send(json.dumps(response).encode('utf-8'))
            print(f"[RCE Server] Response sent to {addr}")
            
        except Exception as e:
            client.send(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
        finally:
            client.close()
    
    def _execute_arithmetic(self, operation, operands):
        """Execute arithmetic operations"""
        a, b = operands[0], operands[1]
        if operation == 'add':
            return a + b
        elif operation == 'subtract':
            return a - b
        elif operation == 'multiply':
            return a * b
        elif operation == 'divide':
            return a / b if b != 0 else 'Error: Division by zero'
        return 'Unknown operation'
    
    def _execute_sort(self, data):
        """Execute sorting operations"""
        time.sleep(0.1)  # Simulate processing
        return sorted(data)
    
    def _execute_string(self, operation, text):
        """Execute string operations"""
        if operation == 'reverse':
            return text[::-1]
        elif operation == 'uppercase':
            return text.upper()
        elif operation == 'lowercase':
            return text.lower()
        elif operation == 'length':
            return len(text)
        return 'Unknown operation'


class RCEClient:
    def __init__(self, host='localhost', port=6001):
        self.host = host
        self.port = port
    
    def execute_arithmetic(self, operation, operands):
        """Execute arithmetic on remote server"""
        request = {
            'type': 'arithmetic',
            'operation': operation,
            'operands': operands
        }
        return self._send_request(request)
    
    def execute_sort(self, data):
        """Execute sort on remote server"""
        request = {
            'type': 'sort',
            'data': data
        }
        return self._send_request(request)
    
    def execute_string(self, operation, text):
        """Execute string operation on remote server"""
        request = {
            'type': 'string',
            'operation': operation,
            'text': text
        }
        return self._send_request(request)
    
    def _send_request(self, request):
        """Send request and receive response"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            sock.send(json.dumps(request).encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            sock.close()
            return json.loads(response)
        except Exception as e:
            return {'success': False, 'error': str(e)}


def simulate_rce():
    """Simulate RCE system"""
    # Start server in background
    server = RCEServer()
    threading.Thread(target=server.start, daemon=True).start()
    time.sleep(1)
    
    # Create client
    client = RCEClient()
    
    print("\n=== RCE CLIENT REQUESTS ===\n")
    
    # Test arithmetic
    print("1. Arithmetic Operations:")
    result = client.execute_arithmetic('add', [15, 25])
    print(f"   15 + 25 = {result['result']}")
    
    result = client.execute_arithmetic('multiply', [7, 8])
    print(f"   7 * 8 = {result['result']}")
    
    # Test sorting
    print("\n2. Sorting Operations:")
    result = client.execute_sort([5, 2, 9, 1, 7])
    print(f"   Sort [5,2,9,1,7] = {result['result']}")
    
    # Test string operations
    print("\n3. String Operations:")
    result = client.execute_string('reverse', 'HELLO')
    print(f"   Reverse 'HELLO' = {result['result']}")
    
    result = client.execute_string('uppercase', 'python')
    print(f"   Uppercase 'python' = {result['result']}")
    
    print("\n=== TESTS COMPLETED ===")
    time.sleep(1)


if __name__ == '__main__':
    simulate_rce()
