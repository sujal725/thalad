"""
Q3: API Key Management Server with Multi-threading
Features: Key generation, retrieval, blocking, keep-alive, auto-expiry
"""

import threading
import time
import uuid
from datetime import datetime, timedelta
from collections import defaultdict
import json

class APIKeyManager:
    def __init__(self):
        self.keys = {}  # {key: {'created': time, 'blocked': bool, 'last_keepalive': time}}
        self.key_ttl = 5 * 60  # 5 minutes
        self.blocked_ttl = 60  # 60 seconds
        self.lock = threading.Lock()
    
    def create_key(self):
        """Create a new API key"""
        with self.lock:
            key = str(uuid.uuid4())[:16]
            self.keys[key] = {
                'created': time.time(),
                'blocked': False,
                'last_keepalive': time.time(),
                'status': 'active'
            }
            print(f"[Manager] Created key: {key}")
            return key
    
    def get_available_key(self):
        """Get an available key and block it"""
        with self.lock:
            for key, data in self.keys.items():
                if data['status'] == 'active' and not data['blocked']:
                    data['blocked'] = True
                    data['blocked_time'] = time.time()
                    print(f"[Manager] Assigned key: {key} (blocked)")
                    return key
        return None
    
    def unblock_key(self, key):
        """Unblock a previously assigned key"""
        with self.lock:
            if key in self.keys:
                self.keys[key]['blocked'] = False
                print(f"[Manager] Unblocked key: {key}")
                return True
        return False
    
    def keepalive(self, key):
        """Signal keep-alive for a key"""
        with self.lock:
            if key in self.keys:
                self.keys[key]['last_keepalive'] = time.time()
                print(f"[Manager] Keep-alive received for: {key}")
                return True
        return False
    
    def start_cleanup(self):
        """Start background cleanup thread"""
        threading.Thread(target=self._cleanup_expired_keys, daemon=True).start()
        threading.Thread(target=self._cleanup_blocked_keys, daemon=True).start()
    
    def _cleanup_expired_keys(self):
        """Remove expired keys (no keep-alive for TTL seconds)"""
        while True:
            time.sleep(10)  # Check every 10 seconds
            with self.lock:
                current_time = time.time()
                expired = []
                
                for key, data in self.keys.items():
                    if data['status'] == 'active':
                        if current_time - data['last_keepalive'] > self.key_ttl:
                            expired.append(key)
                
                for key in expired:
                    del self.keys[key]
                    print(f"[Manager] EXPIRED key: {key}")
    
    def _cleanup_blocked_keys(self):
        """Auto-unblock keys after TTL if not explicitly unblocked"""
        while True:
            time.sleep(5)  # Check every 5 seconds
            with self.lock:
                current_time = time.time()
                
                for key, data in self.keys.items():
                    if data['blocked'] and 'blocked_time' in data:
                        if current_time - data['blocked_time'] > self.blocked_ttl:
                            data['blocked'] = False
                            print(f"[Manager] Auto-unblocked key: {key}")
    
    def get_all_keys(self):
        """Get all keys with their status"""
        with self.lock:
            status = {}
            for key, data in self.keys.items():
                status[key] = {
                    'blocked': data['blocked'],
                    'status': data['status'],
                    'age_seconds': int(time.time() - data['created'])
                }
            return status


class APIKeyServer:
    def __init__(self):
        self.manager = APIKeyManager()
        self.manager.start_cleanup()
    
    def handle_request(self, request):
        """Handle API requests"""
        req_type = request.get('type')
        
        if req_type == 'create':
            key = self.manager.create_key()
            return {'success': True, 'key': key}
        
        elif req_type == 'get':
            key = self.manager.get_available_key()
            if key:
                return {'success': True, 'key': key}
            return {'success': False, 'error': 'No available keys'}
        
        elif req_type == 'unblock':
            success = self.manager.unblock_key(request.get('key'))
            return {'success': success}
        
        elif req_type == 'keepalive':
            success = self.manager.keepalive(request.get('key'))
            return {'success': success}
        
        elif req_type == 'status':
            status = self.manager.get_all_keys()
            return {'success': True, 'keys': status}
        
        return {'success': False, 'error': 'Unknown request'}


def simulate_api_key_system():
    """Simulate API key management system"""
    server = APIKeyServer()
    
    print("=== API KEY MANAGEMENT SYSTEM ===\n")
    
    # Create keys
    print("1. Creating API keys...")
    key1 = server.handle_request({'type': 'create'})['key']
    key2 = server.handle_request({'type': 'create'})['key']
    key3 = server.handle_request({'type': 'create'})['key']
    
    # Get available keys
    print("\n2. Getting available keys...")
    assigned_key = server.handle_request({'type': 'get'})
    print(f"   Assigned: {assigned_key}")
    
    # Check status
    print("\n3. Current status:")
    status = server.handle_request({'type': 'status'})
    for key, data in status['keys'].items():
        print(f"   {key}: blocked={data['blocked']}, age={data['age_seconds']}s")
    
    # Keep-alive
    print("\n4. Sending keep-alive signals...")
    server.handle_request({'type': 'keepalive', 'key': key1})
    server.handle_request({'type': 'keepalive', 'key': key2})
    
    # Unblock a key
    print("\n5. Unblocking key...")
    server.handle_request({'type': 'unblock', 'key': key1})
    
    # Simulate passage of time and auto-expiry
    print("\n6. Waiting for auto-expiry (this is simulated)...")
    print("   (In production, keys expire after 5 minutes without keep-alive)")
    
    print("\n7. Final status:")
    status = server.handle_request({'type': 'status'})
    for key, data in status['keys'].items():
        print(f"   {key}: blocked={data['blocked']}, age={data['age_seconds']}s")
    
    print("\n=== SIMULATION COMPLETE ===")


if __name__ == '__main__':
    simulate_api_key_system()
