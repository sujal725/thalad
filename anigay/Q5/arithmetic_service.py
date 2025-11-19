"""
Q5: Distributed Arithmetic Service using Socket RPC
Server exposes arithmetic operations, client invokes them remotely.
"""

import socket
import json
import threading
import time

class ArithmeticServer:
    def __init__(self, host='localhost', port=7001):
        self.host = host
        self.port = port
    
    def start(self):
        """Start arithmetic server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"[Arithmetic Server] Listening on {self.host}:{self.port}")
        
        try:
            while True:
                client, addr = server_socket.accept()
                threading.Thread(target=self._handle_client, args=(client, addr), daemon=True).start()
        except KeyboardInterrupt:
            pass
        finally:
            server_socket.close()
    
    def _handle_client(self, client, addr):
        """Handle client request"""
        try:
            # Receive request (marshalling)
            data = client.recv(1024).decode('utf-8')
            request = json.loads(data)
            
            print(f"[Server] Request from {addr}: {request}")
            
            # Execute operation
            operation = request['operation']
            operands = request['operands']
            
            if operation == 'add':
                result = operands[0] + operands[1]
            elif operation == 'subtract':
                result = operands[0] - operands[1]
            elif operation == 'multiply':
                result = operands[0] * operands[1]
            elif operation == 'divide':
                result = operands[0] / operands[1] if operands[1] != 0 else 'Error'
            else:
                result = 'Unknown operation'
            
            # Send response (unmarshalling)
            response = {'success': True, 'result': result}
            client.send(json.dumps(response).encode('utf-8'))
            print(f"[Server] Response sent: {result}")
            
        except Exception as e:
            client.send(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
        finally:
            client.close()


class ArithmeticClient:
    def __init__(self, host='localhost', port=7001):
        self.host = host
        self.port = port
    
    def call_remote(self, operation, operands):
        """Call remote arithmetic function"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            
            # Marshal request
            request = {
                'operation': operation,
                'operands': operands
            }
            sock.send(json.dumps(request).encode('utf-8'))
            
            # Unmarshal response
            response = sock.recv(1024).decode('utf-8')
            result = json.loads(response)
            
            sock.close()
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add(self, a, b):
        return self.call_remote('add', [a, b])
    
    def subtract(self, a, b):
        return self.call_remote('subtract', [a, b])
    
    def multiply(self, a, b):
        return self.call_remote('multiply', [a, b])
    
    def divide(self, a, b):
        return self.call_remote('divide', [a, b])


def simulate_arithmetic_service():
    """Simulate distributed arithmetic service"""
    # Start server
    server = ArithmeticServer()
    threading.Thread(target=server.start, daemon=True).start()
    time.sleep(1)
    
    # Create client
    client = ArithmeticClient()
    
    print("\n=== DISTRIBUTED ARITHMETIC SERVICE ===\n")
    
    print("Remote Invocations:")
    
    # Test operations
    result = client.add(10, 20)
    print(f"add(10, 20) = {result['result']}")
    
    result = client.subtract(50, 15)
    print(f"subtract(50, 15) = {result['result']}")
    
    result = client.multiply(7, 8)
    print(f"multiply(7, 8) = {result['result']}")
    
    result = client.divide(100, 4)
    print(f"divide(100, 4) = {result['result']}")
    
    print("\n=== MARSHALLING/UNMARSHALLING DEMO ===")
    print("Request marshalled to JSON, transmitted, then unmarshalled on server")
    print("Server computes result and marshals response back to client")
    print("\n=== SIMULATION COMPLETE ===")
    
    time.sleep(1)


if __name__ == '__main__':
    simulate_arithmetic_service()
