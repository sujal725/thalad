
import java.rmi.Naming;
import java.util.Arrays;


public class Client {
    public static void main(String[] args) {
        try {
            Task stub = (Task)Naming.lookup("rmi://localhost/RemoteExecEngine");
            System.out.println("Submitting code to remote server for execution...");

            TaskCode<int[]> sortProgram = new TaskCode<int[]>() {
                int[] data = {5, 1, 7, 3};
                @Override
                public int[] run() {
                    Arrays.sort(data);
                    return data;
                }
            };
            System.out.println("Sorted: " + Arrays.toString(stub.executeTask(sortProgram)));

            TaskCode<String> reverseProgram = new TaskCode<String>() {
                String s = "distributed";
                @Override
                public String run() {
                    return new StringBuilder(s).reverse().toString();
                }
            };
            System.out.println("Reversed: " + stub.executeTask(reverseProgram));

            TaskCode<Integer> factorialProgram = new TaskCode<Integer>() {
                int n = 5;
                @Override
                public Integer run() {
                    int f = 1;
                    for (int i = 1; i <= n; i++) f *= i;
                    return f;
                }
            };
            System.out.println("Factorial: " + stub.executeTask(factorialProgram));
        } catch (Exception e) {
            System.out.println("Client exception: " + e.toString());
        }
    }
}
/*Q2 Remote Code Execution Engine (RPC / Java RMI)
Project Goal

To design a distributed system where multiple clients can send small executable tasks (e.g., arithmetic expressions, sorting operations, or string operations) to a Remote Execution Server using RPC / Java RMI. The server executes the task and returns the result. The system supports multithreading so multiple clients can request execution simultaneously.

What is Remote Code Execution in Distributed Systems?

Remote code execution means that one machine (client) can send an instruction or function to another machine (server), which executes the instruction and returns the output.

Example:

Client sends:

sort([5,1,4,2])


Server executes:

[1,2,4,5]


Server sends response back to client.

This helps centralize computational load and share processing resources.

Key Concepts Involved
RPC (Remote Procedure Call)

RPC allows a program to call a function located on a remote server as if it were a local function.

Characteristics:

The network communication is hidden behind function calls.

Parameters are marshalled (converted into transmittable format).

Results are unmarshalled (converted back).

RPC flow:

Client → Stub → Network → Server stub → Method execution → Return result


Advantages:

Simple client usage

Programmer does not need to manage socket-level networking

Java RMI (Remote Method Invocation)

Java RMI is Java’s version of RPC, enabling remote object method invocation over a network.

Key components:

Remote Interface defining allowed remote methods

Remote Object implementing the interface

RMI Registry for lookup and binding

Stubs for client and server communication

In our case:

interface RemoteExecutor extends Remote {
    String executeTask(String code) throws RemoteException;
}


Client calls:

stub.executeTask("reverse:hello");


Server processes and sends back:

"olleh"

Multithreading in the Server

To improve responsiveness and support multiple simultaneous clients:

When a request is received, the server creates a new thread to process it.

Worker threads execute tasks independently.

The main server thread keeps accepting new connections.

Benefit:

Client1 asking for sorting and Client2 asking for string reversal can be executed concurrently.

System Architecture Explanation (To Speak in Viva)

Client application

Accepts user input / code snippet / operation.

Sends request to server using RPC / RMI.

Waits for response and prints result.

Remote Server

Implements remote methods that can receive a task and process it.

Parses the request and executes appropriate function.

Runs each request inside a separate thread.

Returns result back to client.

RMI Registry

Allows client to locate the remote object by name.

Example Flow (How System Works)

Client:

Enter task: add 10 20


Client sends via RMI:

"add 10 20"


Server receives:

Request from client: add 10 20


Server thread performs:

result = 30


Server returns to client:

30


Client output:

Result from server: 30

Example Supported Tasks

add 12 8 → 20

subtract 30 4 → 26

multiply 5 7 → 35

reverse hello → olleh

sort [6,3,9,1] → [1,3,6,9]

Why Multithreading Is Important Here

Without multithreading:

One request at a time

If a client sends a long computation (like sorting a big array), other clients wait

With multithreading:

Each client request is processed in a separate worker thread

Server remains highly responsive

Viva Questions and Suggested Answers
Q1. What is RPC and how is it used in your project?

RPC allows a client to call a function on a remote server as if it were local. In my project, the client calls a remote method like executeTask(), the server runs the requested computation, and returns the result.

Q2. What is Java RMI?

Java RMI is Java’s implementation of RPC that enables executing object methods on remote JVMs. It hides networking details and handles parameter serialization automatically.

Q3. Why do we need multithreading in this system?

Multithreading enables multiple clients to request remote task execution concurrently. Without threads, the server would block and serve one client at a time, reducing responsiveness.

Q4. How does the server know which operation to execute?

The server parses the incoming request string and chooses the proper handler function. For example, if the request begins with "add", it executes arithmetic logic; if "sort", then sorting logic.

Q5. What is marshalling and unmarshalling?

Marshalling converts parameters into a transmittable format for network transfer. Unmarshalling converts them back into usable values on the receiving end.

Q6. What happens if two clients send tasks simultaneously?

The server creates two separate threads, each executing its assigned computation independently and returning results separately.

Q7. What are real-world applications of such a system?

Cloud function execution, serverless computing, distributed computing frameworks, online compilers, containerized execution services, remote automation systems.

Q8. What are limitations of your implementation?

Limited types of allowed tasks

Security concerns: blindly executing code can be dangerous

No load balancing or scheduling

Single machine server, not fault tolerant

Q9. How could this be extended in future?

Deploy multiple servers and use a load balancer

Add authentication and sandboxing

Support code execution in multiple languages

Persist results and logs

Short Summary Answer (Speak in 45–60 seconds)

I implemented a Remote Code Execution Engine using RPC / Java RMI. The client sends a code snippet or task request to the server. The server parses and executes the task remotely, then returns the output to the client. To support multiple clients concurrently, the server uses multithreading and creates a separate worker thread for each request. Communication between client and server happens through RMI stubs, where marshalling and unmarshalling allow transferring method parameters and return values. The system demonstrates distributed computing and remote method execution where computation is centralized and shared. */