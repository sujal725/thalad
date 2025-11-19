import socket
import threading
import time
import uuid

KEY_TTL_SECONDS = 300  # 5 minutes
BLOCK_TIMEOUT_SECONDS = 60  # 60 seconds

# key_store structure:
# {
#   "key_string": {
#       "status": "available" / "blocked",
#       "expiry": <timestamp>,
#       "blocked_since": <timestamp or None>
#   },
#   ...
# }

key_store = {}
store_lock = threading.Lock()


def create_key():
    with store_lock:
        key = str(uuid.uuid4())
        key_store[key] = {
            "status": "available",
            "expiry": time.time() + KEY_TTL_SECONDS,
            "blocked_since": None,
        }
    return key


def get_available_key():
    with store_lock:
        now = time.time()
        for k, info in key_store.items():
            if info["status"] == "available" and info["expiry"] > now:
                info["status"] = "blocked"
                info["blocked_since"] = now
                return k
    return None


def unblock_key(key):
    with store_lock:
        if key in key_store:
            info = key_store[key]
            if info["status"] == "blocked":
                info["status"] = "available"
                info["blocked_since"] = None
                return True
    return False


def keep_alive_key(key):
    with store_lock:
        if key in key_store:
            info = key_store[key]
            # Only extend if not expired already
            if info["expiry"] > time.time():
                info["expiry"] = time.time() + KEY_TTL_SECONDS
                return True
    return False


def cleanup_worker():
    """Background thread to delete expired keys and release blocked ones."""
    while True:
        now = time.time()
        with store_lock:
            # Delete expired keys
            to_delete = []
            for k, info in key_store.items():
                if info["expiry"] <= now:
                    to_delete.append(k)
            for k in to_delete:
                del key_store[k]

            # Release blocked keys that are blocked for too long
            for k, info in key_store.items():
                if info["status"] == "blocked" and info["blocked_since"] is not None:
                    if now - info["blocked_since"] >= BLOCK_TIMEOUT_SECONDS:
                        info["status"] = "available"
                        info["blocked_since"] = None
        time.sleep(5)  # run every 5 seconds


def handle_client(conn, addr):
    print(f"[+] Connected: {addr}")
    conn.sendall(
        b"Welcome to API Key Server. Commands: CREATE, GET, UNBLOCK <key>, KEEPALIVE <key>, EXIT\n"
    )

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            cmd_line = data.decode().strip()
            if not cmd_line:
                continue

            parts = cmd_line.split()
            cmd = parts[0].upper()

            if cmd == "CREATE":
                key = create_key()
                conn.sendall(f"CREATED {key}\n".encode())

            elif cmd == "GET":
                key = get_available_key()
                if key:
                    conn.sendall(f"ASSIGNED {key}\n".encode())
                else:
                    conn.sendall(b"NO_KEY_AVAILABLE\n")

            elif cmd == "UNBLOCK":
                if len(parts) != 2:
                    conn.sendall(b"ERROR Usage: UNBLOCK <key>\n")
                    continue
                key = parts[1]
                if unblock_key(key):
                    conn.sendall(b"UNBLOCKED\n")
                else:
                    conn.sendall(b"ERROR Cannot unblock (invalid key or not blocked)\n")

            elif cmd == "KEEPALIVE":
                if len(parts) != 2:
                    conn.sendall(b"ERROR Usage: KEEPALIVE <key>\n")
                    continue
                key = parts[1]
                if keep_alive_key(key):
                    conn.sendall(b"ALIVE\n")
                else:
                    conn.sendall(b"ERROR Keepalive failed (invalid/expired key)\n")

            elif cmd == "EXIT":
                conn.sendall(b"BYE\n")
                break

            else:
                conn.sendall(b"ERROR Unknown command\n")

    finally:
        print(f"[-] Disconnected: {addr}")
        conn.close()


def start_server(host="127.0.0.1", port=5000):
    cleaner = threading.Thread(target=cleanup_worker, daemon=True)
    cleaner.start()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[SERVER] Listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()


if __name__ == "__main__":
    start_server()
"""1. Overall idea of the project

You are designing a multi-threaded API key management server.

The server:

Generates API keys.

Assigns keys to clients.

Tracks each key’s:

status: available / blocked

expiry time

how long it has been blocked

Automatically:

deletes keys if they are not kept alive every 5 minutes,

releases blocked keys after 60 seconds if not explicitly unblocked.

Clients talk to the server using simple commands/endpoints like:

CREATE

GET

UNBLOCK <key>

KEEPALIVE <key>

The important topics for viva are:

multithreading,

shared state and locks,

time-based expiry,

status transitions (available ↔ blocked),

automatic background cleanup.

2. Multithreading in your server
2.1 Why multithreading?

The server must handle multiple clients at once. Without threads:

One client’s request would block others.

If a client is slow or idle, other clients get delayed.

With multithreading:

The main thread only accepts new connections.

Each client gets its own handler thread.

A separate background thread performs periodic key cleanup.

Result: many clients can work concurrently, and maintenance happens in parallel.

2.2 Thread roles

You typically have three kinds of threads:

Main thread

Starts the server socket.

Calls accept() in a loop.

For every new client, spawns a client handler thread.

Client handler threads

One per client connection.

Read text commands from the client (CREATE, GET, etc.).

Execute the requested operation on the shared key store.

Send back a response.

Terminate when the client disconnects.

Cleanup thread

Runs in the background.

Wakes up periodically (for example, every 5 seconds).

Deletes expired keys.

Releases keys that have been blocked for more than 60 seconds.

This combination shows a typical server-side multithreaded design.

3. Shared data: key store and locking

You keep all keys and their metadata in a shared in-memory structure, for example:

key_store = {
    "key1": {
        "status": "available" / "blocked",
        "expiry": <timestamp>,
        "blocked_since": <timestamp or None>
    },
    ...
}


Because multiple threads access key_store at the same time (client threads plus cleanup thread), you must protect it with a lock (e.g., threading.Lock in Python).

Pattern:

with store_lock:
    # safe read or write on key_store


This prevents race conditions like:

Two clients getting the same key via GET.

Cleanup thread deleting a key while a client handler is updating it.

In viva, emphasize:

I used a mutex lock around all operations that modify or read from the key store to ensure thread safety.

4. The endpoints and their semantics

You can describe each command like an API endpoint.

4.1 CREATE – generate new key

Purpose:

Create a new API key with a time-to-live of 5 minutes.

Initially mark it as available.

Typical steps:

Generate a unique key (for example, using UUID).

Under the lock, insert into key_store:

status = "available"

expiry = current_time + 5 minutes

blocked_since = None

Return the key to the client, e.g.: CREATED <key>.

Conceptually:

CREATE is used by an admin or provisioning system to add fresh keys into the pool of available keys.

4.2 GET – retrieve an available key

Purpose:

Give a client one key that is free to use.

Ensure this key is not given to another client at the same time.

Typical steps:

Under the lock, iterate over key_store and find:

a key with status == "available",

whose expiry is still in the future.

If found:

set status = "blocked",

set blocked_since = current_time,

return ASSIGNED <key>.

If no such key:

return NO_KEY_AVAILABLE.

The word “blocked” here means:

This key is currently assigned to a client and must not be handed out again until it is unblocked or automatically released.

4.3 UNBLOCK <key> – make a key reusable (optional but implemented)

Purpose:

Manually release a key that was assigned, so another client can use it.

Typical steps:

Under the lock, check if:

the key exists,

its status is "blocked".

If yes:

set status = "available",

set blocked_since = None,

return UNBLOCKED.

Otherwise:

return an error such as ERROR Cannot unblock (invalid key or not blocked).

You can explain:

UNBLOCK is used when a client finishes using an API key and explicitly releases it back into the pool.

4.4 KEEPALIVE <key> – prevent deletion

Purpose:

Extend the lifetime of a key so it is not deleted after 5 minutes.

Typical steps:

Under the lock, check if the key exists and is not already expired.

If valid:

set expiry = current_time + 5 minutes (reset the TTL).

return ALIVE.

If invalid or already expired:

return a message like ERROR Keepalive failed (invalid/expired key).

This implements the rule:

“Each generated key has a life of 5 minutes after which it gets deleted automatically if keep-alive operation is not run for that key.”

In viva words:

A client that wants to hold a key longer than 5 minutes must periodically send KEEPALIVE for that key. If it does not, the key expires and is removed by the cleanup thread.

5. Automatic behaviors handled by the cleanup thread

This is important to highlight because it shows you understand background processing and timing.

5.1 Automatic deletion of expired keys

Every few seconds, the cleanup thread:

Gets current time.

Under the lock, iterates over key_store.

For any key where expiry <= now:

deletes it from key_store.

This implements the 5-minute life rule.

5.2 Automatic release of blocked keys after 60 seconds (optional requirement)

For keys with status == "blocked":

Compute now - blocked_since.

If this difference is greater than 60 seconds:

set status = "available",

set blocked_since = None.

This satisfies:

Automatically release blocked keys within 60 seconds if not unblocked explicitly.

In viva, you can say:

If a client crashes or forgets to UNBLOCK, the system still recovers because the cleanup thread will automatically release the blocked key after 60 seconds.

6. Example scenario you can narrate in viva

You can walk the examiner through a simple story.

Start with empty key store.

Client 1 sends CREATE:

Server creates key K1, expiry = now + 5 min, status = available.

Client 2 sends GET:

Server finds K1, sets it blocked, returns ASSIGNED K1.

Immediately after:

Key store has K1: status = blocked, blocked_since = t0.

Client 2 sends KEEPALIVE K1 every few minutes:

Each time expiry is pushed forward by 5 minutes.

If Client 2 sends UNBLOCK K1:

Server marks K1 available again.

Another client’s GET can now assign K1.

If Client 2 disappears and does not send UNBLOCK or KEEPALIVE:

After 60 seconds, cleanup thread makes K1 available again (automatic release).

If even longer passes without KEEPALIVE, and expiry passes, cleanup deletes K1.

This shows that your design supports:

controlled key lifetime,

prevention of double-use,

automatic recovery from client crashes.

7. Viva-style questions and sample answers

You can memorize or adapt these.

Q1. What is the main goal of this project?

The main goal is to design a multi-threaded server that generates and manages API keys safely. It must support key creation, assignment, keep-alive, unblocking, and automatic expiration, while handling multiple clients concurrently.

Q2. Why do you use multithreading in the server?

I use multithreading so that multiple clients can interact with the server at the same time. Each client connection is handled by a separate thread, which prevents one slow client from blocking others. I also use a background cleanup thread to perform periodic tasks like deleting expired keys and releasing blocked keys.

Q3. How do you manage concurrency on the shared key data?

All keys are stored in a shared key_store. Since multiple threads read and write this structure, I use a mutex lock. Before reading or modifying key_store, I acquire the lock using a context (for example, with store_lock:). This ensures thread safety and avoids race conditions.

Q4. What does it mean when a key is in “blocked” state?

A blocked key means it has been assigned to a client and must not be given to another client via GET. It is reserved. The key can either be unblocked manually, automatically released after 60 seconds if no action is taken, or eventually deleted when its TTL expires.

Q5. How are keys automatically deleted after 5 minutes?

Each key has an expiry timestamp set to creation time plus 5 minutes (or plus 5 minutes every time KEEPALIVE is called). The cleanup thread regularly scans the key_store and deletes keys whose expiry time is less than or equal to the current time.

Q6. How does KEEPALIVE affect the key’s lifetime?

KEEPALIVE resets the expiry time to current time plus 5 minutes. As long as a client calls KEEPALIVE before expiry, the key will remain in the system. If KEEPALIVE stops, the key eventually expires and is deleted.

Q7. What happens if a client holds a key but crashes without unblocking it?

Because the key is blocked and the client never sends UNBLOCK, it might remain blocked forever. To prevent this, the cleanup thread monitors blocked keys and automatically releases them after 60 seconds. This ensures that keys cannot be permanently stuck due to client failures.

Q8. What are some limitations of your current design?

A few limitations are:

All data is in memory, so if the server restarts, keys are lost.

Time-based checks depend on system clock and cleanup interval granularity.

There is no authentication; any client can ask for keys.

It does not scale to multiple server instances because the key_store is local to one process.

You can mention these to show you understand trade-offs.

Q9. How would you extend this system in the future?

Possible extensions:

Persist keys in a database.

Add authentication or per-user quotas.

Expose endpoints via HTTP/REST instead of raw sockets.

Deploy multiple instances using a shared datastore or distributed lock."""