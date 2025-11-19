import socket
import threading


def handle_client(conn, addr):
    print(f"[+] Client connected: {addr}")
    conn.sendall(
        b"Welcome to Text Processing Server.\nCommands: UPPER <text>, REVERSE <text>, COUNT <text>, EXIT\n"
    )

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            line = data.decode().strip()
            if not line:
                continue

            parts = line.split(maxsplit=1)
            cmd = parts[0].upper()

            if cmd == "UPPER":
                if len(parts) == 2:
                    conn.sendall((parts[1].upper() + "\n").encode())
                else:
                    conn.sendall(b"ERROR Usage: UPPER <text>\n")

            elif cmd == "REVERSE":
                if len(parts) == 2:
                    conn.sendall((parts[1][::-1] + "\n").encode())
                else:
                    conn.sendall(b"ERROR Usage: REVERSE <text>\n")

            elif cmd == "COUNT":
                if len(parts) == 2:
                    conn.sendall((str(len(parts[1])) + "\n").encode())
                else:
                    conn.sendall(b"ERROR Usage: COUNT <text>\n")

            elif cmd == "EXIT":
                conn.sendall(b"BYE\n")
                break

            else:
                conn.sendall(b"ERROR Unknown command\n")

    except Exception as e:
        print(f"Client error: {e}")

    print(f"[-] Client disconnected: {addr}")
    conn.close()


def start_server(host="0.0.0.0", port=9000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[SERVER] Listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
"""What is this question asking?

You need to:

Create a server that:

Listens on some port (e.g., TCP socket / HTTP endpoint).

Accepts multiple client connections.

For each client, spawns a new thread to handle it.

Simulate multiple clients:

Separate client.py files, or

Use curl / Postman if it's a REST API.

Clients send simple text requests:

e.g., uppercase conversion, length, reversing string, word count.

The server processes each request independently and concurrently.

So the focus is: multi-threaded server + concurrency.

2. Core Concepts You MUST Know
2.1 Concurrency vs Parallelism

Concurrency: Ability to handle multiple tasks at (logically) the same time – interleaving them.
Example: server handles many clients, switching between them.

Parallelism: Tasks running literally at the same time on multiple CPU cores.
Example: one thread on core1, another on core2.

In your context:
You’re showing concurrent handling of multiple clients using threads.

2.2 What is a Thread?

A thread is a lightweight unit of execution inside a process.

Multiple threads share:

Memory

File descriptors

Global variables

But each thread has its own:

Stack

Program counter

Local variables

In your server:

Main thread: accepts new connections.

For each client: you create a new thread that handles that client without blocking others.

2.3 Why Multithreaded Server?

Imagine a single-threaded server:

Client A connects and sends a request that takes 5 seconds.

During these 5 sec, the server can’t handle Client B.

So Client B must wait → bad responsiveness.

With a multithreaded server:

Client A handled in Thread-1.

Client B handled in Thread-2.

Both requests can be processed almost simultaneously.

Benefits:

Better responsiveness.

Can serve many clients like chat servers, web servers, APIs, etc.

2.4 Typical Architecture

For a socket-based server (e.g., Python):

Create a server socket (TCP).

Bind to host:port (e.g., 127.0.0.1:5000).

Start listening.

Loop:

accept() new client → returns conn, addr.

Create a thread: Thread(target=handle_client, args=(conn, addr)).

Start thread.

handle_client function:

Reads request from socket.

Processes string (e.g., uppercase / reverse).

Sends back response to client.

Closes connection.

For REST/HTTP server, frameworks (Flask, Django, FastAPI, Java Spring, etc.) often handle threading / multiprocessing internally.

3. Example Flow You Can Explain in Viva

Assume server does uppercase conversion of text.

Server side (high-level steps)

Start server on port 5000.

Print: Server listening on port 5000.

Client 1 connects → Server prints:

[+] Connected: ('127.0.0.1', 50110)


Server starts Thread-1 to handle Client 1.

Client 2 connects → Server prints:

[+] Connected: ('127.0.0.1', 50111)


Server starts Thread-2 to handle Client 2.

Both Thread-1 and Thread-2 run independently.

Client side (simulation)

Client 1 sends:

hello server


Server replies:

HELLO SERVER


Client 2 sends:

this is client 2


Server replies:

THIS IS CLIENT 2


If Client 1 sleeps for 5 seconds (simulate heavy work), Client 2 is still served immediately by its own thread.

4. What kind of output might you see?
On server console:
[SERVER] Listening on 127.0.0.1:5000
[+] Connected: ('127.0.0.1', 50110)
[THREAD-1] Received from ('127.0.0.1', 50110): hello server
[THREAD-1] Sent: HELLO SERVER
[+] Connected: ('127.0.0.1', 50111)
[THREAD-2] Received from ('127.0.0.1', 50111): this is client 2
[THREAD-2] Sent: THIS IS CLIENT 2
[-] Disconnected: ('127.0.0.1', 50110)
[-] Disconnected: ('127.0.0.1', 50111)

On client1 console:
Connected to server
Enter message: hello server
Response: HELLO SERVER

On client2 console:
Connected to server
Enter message: this is client 2
Response: THIS IS CLIENT 2


You can explain:

Each client has its own handler thread, so both requests are processed concurrently. The main server thread continues accepting new connections while worker threads handle logic.

5. Important Viva Questions & Answers
Q1. What is the purpose of a multithreaded server?

Ans:
To handle multiple client requests simultaneously. Each client connection is managed by a separate thread so that slow or long-running requests do not block others.

Q2. How does your server handle multiple clients?

Ans:
The main thread listens for incoming connections. When a client connects, the server calls accept(), then spawns a new thread passing the client socket to a handler function. This handler runs independently and processes the client’s request, while the main thread continues accepting other clients.

Q3. What happens inside the client handler thread?

Ans:
The handler thread receives the client’s request message, processes it (e.g., text transformation like uppercase, reverse, word count), sends back the response, and finally closes the connection. This is done independently for each client.

Q4. What is the difference between single-threaded and multithreaded server behavior?

Ans:

Single-threaded:

One client at a time.

A long request blocks all others.

Multithreaded:

Multiple clients at once.

Slow client does not affect others.

Better performance & responsiveness.

Q5. Are there any issues with multithreading?

Ans:

Yes, potential issues include:

Race conditions: if multiple threads modify shared data without synchronization.

Deadlocks: circular waits for locks.

Context switching overhead: too many threads can slow down system.

But in simple request-per-connection server where threads don’t share mutable global state, these issues are minimal.

Q6. What kind of tasks did your clients send?

Ans:
Simple text-processing tasks such as:

Converting input string to uppercase.

Counting number of characters/words.

Reversing the string.

This proves the server can receive a request, process it, and send back a response concurrently for multiple clients.

Q7. How did you simulate multiple clients?

Ans:
I used multiple client scripts (e.g., client1.py, client2.py), or opened multiple terminals running the same client program. Alternatively, if using HTTP/REST, I could send multiple requests from Postman or curl simultaneously.

Q8. Is your implementation thread-safe?

Ans:
Yes, because each client connection uses a separate socket and the server does not share mutable global data across threads (or if shared, it’s protected with locks). Thus, threads do not interfere with each other.

Q9. Could we use processes instead of threads?

Ans:
Yes, using multiprocessing (e.g., fork() or Python’s multiprocessing module) is another option, providing true parallelism on multi-core CPUs. But threads are lighter-weight and easier to use for I/O-bound network servers, which is why multithreading is common.

6. 1-Minute Viva Summary (You can speak this as is)

In this assignment, I designed a multithreaded server that can handle multiple client requests simultaneously. The server listens on a TCP port and, whenever a client connects, it spawns a new thread dedicated to that client. Each handler thread receives the client’s message, performs a simple text-processing task such as converting to uppercase, and sends the response back. While one thread is processing a client’s request, the main server thread continues accepting new connections, and other client threads run in parallel. This demonstrates concurrency in a distributed environment and shows how multithreading improves responsiveness compared to a single-threaded server."""