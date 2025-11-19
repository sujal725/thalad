
import java.rmi.Naming;

public class Server {
    public static void main(String[] args) {
        try {
            ArithmeticImpl obj = new ArithmeticImpl();
            Naming.rebind("ArithmeticServer", obj);
            System.out.println("Arithmetic Server is ready & object is bound to registry...");
        } catch (Exception e) {
            System.out.println("Server exception: " + e.toString());
        }
    }
}
/*
 * Q1. What is the goal of your distributed arithmetic service?

Ans:
The goal is to demonstrate remote method invocation using RPC/RMI. Instead of computing arithmetic locally, the client sends arithmetic requests (add/sub/mul) to a remote server, which performs the computation and returns the result. This shows how functions can be executed on another machine in a transparent way.

Q2. What is RPC? How is it used in your project?

Ans:
RPC stands for Remote Procedure Call. It allows a program to call a function on a remote server as if it were a local function.

In my project, the client uses RPC to call remote arithmetic functions such as add(a, b), sub(a, b), and mul(a, b) on the server. Parameters and return values are marshalled into a network format and sent over a socket or RMI infrastructure.

Q3. What is Java RMI and how is it different from generic RPC?

Ans:
Java RMI (Remote Method Invocation) is Java’s implementation of RPC for objects. It allows a Java program to invoke methods on remote Java objects.

Differences:

Generic RPC works with procedures/functions, often language-independent.

RMI is Java-specific and supports full object-oriented features and object serialization.

In RMI, you work with interfaces and remote objects instead of just functions.

Q4. What is marshalling? What is unmarshalling? Where do they occur in your system?

Ans:

Marshalling is the process of converting parameters or objects into a format suitable for transmission over a network (like converting int a=10, b=20 into a byte stream or JSON).

Unmarshalling is the reverse: converting the received network data back into language-level types or objects.

In my system:

On the client side, arguments to remote functions are marshalled before sending.

On the server side, requests are unmarshalled, the operation is performed, then the result is marshalled and sent back.

The client finally unmarshals the response to get the actual result value.

Q5. How does the client know which server function to call?

Ans:
The client encodes the operation in the request:

For a manual RPC using sockets, the client might send something like:

"ADD 10 20" or {"op": "add", "a": 10, "b": 20}.

The server parses the message and decides which function to execute.

For Java RMI, the client invokes stub.add(10, 20) directly on a remote interface, and RMI internally routes the call to the correct method on the server.

Q6. What are the main components in RMI architecture? (If you used Java)

Ans:

Remote Interface – declares the methods that can be called remotely.

Remote Object Implementation – class that implements the interface.

Stub – client-side proxy that forwards calls to the remote object.

RMI Registry – name service where remote objects are registered and looked up.

Skeleton (older RMI) – server-side entity that receives requests from stub (in newer versions, skeleton is generated internally).

Q7. What are the advantages of using RPC/RMI for such a service?

Ans:

Hides low-level networking details.

Client code looks like normal function/method calls.

Encourages clean separation of interface (what is offered) from implementation (how it is done).

Makes it easier to scale or relocate services, since clients just call remote methods.

Q8. How would you test that your distributed arithmetic service works properly?

Ans:

Start the server process (listening on a port / RMI registry).

Start the client process and call:

add(2, 3) → expect 5

sub(10, 4) → expect 6

mul(7, 8) → expect 56

Try invalid inputs or operations (if implemented) to see error handling.

Optionally, run multiple clients and observe that the server can handle several requests sequentially (or concurrently if multithreading is added).

Q9. What are some limitations or challenges in RPC/RMI?

Ans:

Network failures: calls can fail due to disconnects, timeouts.

Performance overhead: marshalling and network latency make remote calls slower than local calls.

Versioning & compatibility: client and server must agree on interface and data format.

Error handling is more complex; must handle remote exceptions.

Q10. If the server is written in Python and the client is in Java, can you directly use RMI?

Ans:
No. Java RMI is Java-specific. To support cross-language RPC, we’d use something language-neutral like gRPC, Thrift, JSON-RPC, or a custom protocol over sockets/HTTP. RMI works best in a pure Java ecosystem.
 */