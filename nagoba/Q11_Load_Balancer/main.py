import time
import random


class Server:
    def __init__(self, sid):
        self.id = sid
        self.load = 0  # number of active requests

    def add_request(self):
        self.load += 1

    def finish_request(self):
        if self.load > 0:
            self.load -= 1


class LoadBalancer:
    def __init__(self, num_servers, strategy="round_robin"):
        self.servers = [Server(i) for i in range(1, num_servers + 1)]
        self.strategy = strategy
        self.rr_index = 0

    def assign_request(self, req_id):
        if self.strategy == "round_robin":
            server = self.servers[self.rr_index]
            self.rr_index = (self.rr_index + 1) % len(self.servers)

        elif self.strategy == "least_connections":
            server = min(self.servers, key=lambda s: s.load)

        server.add_request()
        print(f"[LB] Request {req_id} → Server {server.id}")
        return server

    def show_loads(self):
        print("Current Loads: ", end="")
        for s in self.servers:
            print(f"S{s.id}:{s.load} ", end="")
        print("\n")


def simulate(lb, num_requests=10):
    for req in range(1, num_requests + 1):
        server = lb.assign_request(req)
        lb.show_loads()

        # simulate task finishing
        if random.random() < 0.4:
            server.finish_request()
            print(f"[Server {server.id}] Finished 1 request.")
            lb.show_loads()

        time.sleep(0.5)


if __name__ == "__main__":
    while True:
        n = input("Number of servers: ")
        if n.isdigit() and int(n) > 0:
            n = int(n)
            break
        print("Please enter a positive integer.")

    choice = input(
        "Choose Load Balancing Strategy: \n1. Round Robin\n2. Least Connections\n Enter choice (1/2): "
    )
    if choice == "1":
        strategy = "round_robin"
    elif choice == "2":
        strategy = "least_connections"
    else:
        print("Invalid choice, defaulting to Round Robin.")
        strategy = "round_robin"

    lb = LoadBalancer(n, strategy=strategy)
    simulate(lb)
"""1. What is this question asking?

You need to simulate a load balancer that:

Accepts incoming client requests.

Distributes them to multiple backend servers.

Uses one strategy:

Round Robin OR

Least Connections

Backend servers can be simulated as:

Threads

Functions / objects

You must print how the load is distributed, e.g.:

Request 1 → Server 1
Request 2 → Server 2
Request 3 → Server 3
Request 4 → Server 1
...


So the main focus is: load balancing strategy + basic concurrency understanding.

2. Core Concepts for Viva
2.1 What is a Load Balancer?

A load balancer is a component that:

Sits between clients and backend servers.

Receives all incoming requests.

Decides which backend server should handle each request.

Purpose:

Prevent any single server from overloading.

Improve performance & reliability.

Enable horizontal scaling.

Real-world examples: Nginx, HAProxy, AWS ELB, Kubernetes Service.

2.2 Why do we need Load Balancing?

Without load balancing:

All clients might accidentally hit one server.

That server becomes slow / overloaded.

Other servers remain under-utilized.

With load balancing:

Requests are distributed across multiple backend instances.

System can handle more traffic.

If one backend fails, load balancer can skip it → fault tolerance.

3. Load Balancing Algorithms

You need at least one. Let’s cover both for viva.

3.1 Round Robin

Idea:
Distribute requests in order, one by one, cycling through servers.

Example: 3 servers → S1, S2, S3

Request sequence:

Req1 → S1

Req2 → S2

Req3 → S3

Req4 → S1

Req5 → S2

Req6 → S3
… and so on.

Implementation concept:

Maintain an index:

index = (index + 1) % N


Use servers[index] for current request.

Advantages:

Very simple

Good when all servers have similar capacity and request cost

Disadvantages:

Doesn’t consider if a server is slower or currently overloaded.

3.2 Least Connections

Idea:
Assign the next request to the server that currently has the fewest active connections.

You maintain something like:

connections = {
  "S1": 3,
  "S2": 1,
  "S3": 5
}


Next request → goes to S2 (only 1 active connection).

Used when:

Requests are long-running.

Servers may have different load / capacity.

Advantages:

More intelligent

Better for varying request durations

Disadvantages:

Requires tracking live connections (more complex).

Needs locking if multithreaded.

4. Backend Simulation (Threads / Functions)

You’ll likely do something like:

Represent backend servers as functions or classes:

def handle_request(server_id, request_id):
    # Simulate some processing
    time.sleep(random_processing_time)
    print(f"Server {server_id} finished request {request_id}")


Or use threads:

t = Thread(target=handle_request, args=(server_id, request_id))
t.start()


This simulates parallel processing by backend servers.

5. Typical Flow of Your Simulation (Story for Viva)

Create N servers, e.g.:

Servers: S0, S1, S2


Implement load balancer object:

load_balancer = RoundRobinLB(servers)


Generate M requests (e.g., 10 fake requests).

For each request:

Load balancer chooses a server using:

Round Robin, or

Least Connections

Print mapping:

Request 0 assigned to S0
Request 1 assigned to S1
Request 2 assigned to S2
Request 3 assigned to S0
...


Optionally start a thread to simulate each request being processed.

6. Sample Output & How to Explain It
Example: Round Robin with 3 servers

Printed output:

Servers: [S0, S1, S2]

Incoming Requests:
Request 1 -> S0
Request 2 -> S1
Request 3 -> S2
Request 4 -> S0
Request 5 -> S1
Request 6 -> S2
Request 7 -> S0
Request 8 -> S1
Request 9 -> S2


You explain:

The load balancer cycles through servers sequentially. Each request is assigned to the next server in the list, wrapping back to the first after the last server. This ensures a fair and equal distribution of requests when server capacities are similar.

Example: Least Connections

Imagine this log:

Initial active connections: S0=0, S1=0, S2=0

Request 1 -> S0 (S0:1, S1:0, S2:0)
Request 2 -> S1 (S0:1, S1:1, S2:0)
Request 3 -> S2 (S0:1, S1:1, S2:1)
Request 4 -> S1 (S0:1, S1:2, S2:1)
Request 5 -> S2 (S0:1, S1:2, S2:2)
Request 6 -> S0 (S0:2, S1:2, S2:2)
...
Server S1 finished a request (S1:1)
Request 7 -> S1 (S0:2, S1:2, S2:2)


You explain:

For every new request, the load balancer checks which server has the fewest active connections and sends the request there. When a server finishes a request, its active count decreases. This keeps the load balanced even if some servers finish faster than others.

7. Viva Questions & Suggested Answers
Q1. What is a load balancer?

Ans:
A load balancer is a component that distributes incoming client requests across multiple backend servers to improve performance, availability, and scalability.

Q2. Which algorithm did you implement and why?

If Round Robin:

I implemented the Round Robin algorithm because it is simple and effective when all backend servers have similar capacity and request duration. It cycles through servers in a fixed order, ensuring each gets an equal number of requests.

If Least Connections:

I implemented the Least Connections algorithm because it dynamically considers the current load on each server. Requests are always routed to the server with the fewest active requests, which balances load better when request sizes or processing times vary.

Q3. Compare Round Robin and Least Connections.
Aspect	Round Robin	Least Connections
Info used	Just server list	Active connection count
Complexity	Simple	More complex
Good when	All servers similar, equal request time	Request durations vary
Adaptivity	Static	Dynamic
Q4. How did you simulate backend servers?

Ans:
I simulated backend servers as separate functions (or threads). For each incoming request, the load balancer chooses a server ID and calls a handler function (or spawns a thread) that “processes” the request, possibly using a short sleep to simulate computation time.

Q5. How do you prove that your load is balanced?

Ans:
My program prints the mapping of each request to a server. At the end, I can count how many requests each server received:

In Round Robin, counts are nearly equal.

In Least Connections, no server gets significantly more requests than others, especially under varying processing times.

Q6. What real-world systems use load balancers?

Ans:

Web servers behind Nginx or HAProxy

Cloud load balancers like AWS ELB, GCP Load Balancing

Microservices in Kubernetes (Services & Ingress)

API gateways

Q7. Are there other load balancing strategies?

Ans:
Yes, examples:

Random choice

Weighted Round Robin

Weighted Least Connections

IP Hash

Response-time–based

8. 1-Minute Viva Summary (You Can Speak This)

In this assignment, I simulated a load balancer that distributes incoming client requests to multiple backend servers. The load balancer receives requests and uses a [Round Robin / Least Connections] strategy to decide which server should handle each one. In Round Robin, it cycles through the servers in order, giving each server an equal share of requests. In Least Connections, it always picks the server with the fewest current active requests, which balances load better when some requests take longer than others.
The backend servers are simulated as functions or threads that process the requests independently. The program prints which server each request is assigned to, showing that the distribution is balanced and demonstrating how a real-world load balancer improves scalability and availability."""