
import java.rmi.Naming;

public class Server{
    public static void main(String[] args) {
        try {
            TaskImpl obj = new TaskImpl();
            Naming.rebind("RemoteExecEngine", obj);
            System.out.println("Remote Code Exec Server is ready...");
        } catch (Exception e) {
            System.out.println("Server exception: " + e.toString());
        }
    }
}
/*
 * You need to design a system where:

Client

Sends a task or small code snippet to a server

Example: calculate factorial(6), sort array, reverse a string, arithmetic operations

Waits for the server response

Displays result

Server

Receives the request over RPC/Java RMI

Executes the task inside a separate thread (so multiple clients can run tasks concurrently)

Returns the computed result to the client

Distributed Environment

Client and server run on different JVMs / machines

Communication is done through RMI (Remote Method Invocation) or RPC

Multiple clients must be handled in parallel using multithreading

✨ What is happening behind the scenes
Flow of Program Execution
Step	Description
1	Client calls a method on the remote server using RMI (e.g., executeTask(Task t))
2	The request is sent over the network as serialized Java objects
3	Server receives the task and starts a new thread to process it
4	Server executes the requested operation (sorting, arithmetic, string manipulation)
5	Server returns result back to the client
6	Client prints result
🧠 Concept Explanation for Viva
What is RPC?

RPC stands for Remote Procedure Call

Meaning

A computer can call a function that exists on another computer as if it were a local function

The network communication is hidden from the programmer

Example

Client calling:

result = add(3, 4);


Even though add() runs on remote server.

Important Points
RPC Feature
Hides networking complexity
Uses simple request–response mechanism
Mostly language independent
Works with procedures, not objects
What is RMI?

RMI stands for Remote Method Invocation (Java-specific)

Meaning

Allows a JVM to invoke a method on an object located on another JVM

Built on top of RPC but supports Object-Oriented concepts

Example
RemoteInterface stub = (RemoteInterface) Naming.lookup("rmi://localhost/task");
int res = stub.factorial(6);

RMI Features
RMI Advantages
Supports Java Object Passing
Allows returning complex objects
Uses serialization/deserialization
Automatic stub and skeleton generation
⭐ Difference between RPC and RMI
Feature	RPC	RMI
Language Support	Any language	Java only
Works with	Procedures/functions	Objects/methods
Data Exchange	Primitive data	Objects, classes
Serialization Required	Limited	Full Java Serialization
Complexity	Simple	More advanced and flexible
🧵 Multithreading Requirement
Why needed?

If one client is executing a long task (e.g., sorting 1M numbers)

Other clients should not be blocked

Server must run each task in a separate thread

Code Pattern on server:
public Object executeTask(Task task) {
    Thread t = new Thread(() -> task.execute());
    t.start();
}

Benefit:
With Multithreading	Without Multithreading
Supports many clients	Only one client at a time
Performance is high	Server becomes slow
Real-world usable	Simple demo only
📌 How it Works Conceptually
Architecture Diagram (Explain in Viva)
Client1 -----> RMI Server ----> Execute Thread1 ----> Result
Client2 -----> RMI Server ----> Execute Thread2 ----> Result
Client3 -----> RMI Server ----> Execute Thread3 ----> Result

Example Task sent by client
Task t = new FactorialTask(6);
Object result = remote.executeTask(t);  // returns 720

Expected Output Example
Client : Sending factorial task
Server : Received task from client
Server : Executing in Thread-1
Server : Result = 720
Client : Received Result : 720

💬 Interview / Viva Questions & Best Answers
Q1: What problem is solved by Remote Code Execution Engine?

Ans:
It allows clients to send computation tasks to a powerful remote server for processing. This reduces client workload and enables distributed parallel computing.

Q2: Why use RMI?

Ans:
Because RMI supports object transfer and remote method invocation, making distributed Java systems easy to build using object-oriented programming.

Q3: Why is multithreading needed?

Ans:
Multithreading allows the server to handle multiple client requests concurrently, improving responsiveness and performance.

Q4: How does RMI work internally?

Ans:
RMI uses stubs (client-side proxies) and skeletons (server-side) and serializes request/response objects over TCP without the programmer manually managing network details.

Q5: Difference between RPC & RMI?

→ RMI uses objects & supports Java serialization, whereas RPC supports functions & primitives.
 */
