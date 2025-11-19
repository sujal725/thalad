import java.rmi.Naming;

public class Client {
    public static void main(String[] args) {
        try {
            Arithmetic stub = (Arithmetic) Naming.lookup("rmi://localhost/ArithmeticServer");
            System.out.println("Addition: " + stub.add(10, 5));
            System.out.println("Subtraction: " + stub.sub(10, 5));
            System.out.println("Multiplication: " + stub.mul(10, 5));
            System.out.println("Division: " + stub.div(10, 5));
        } catch (Exception e) {
            System.out.println("Client exception: " + e.toString());
        }
    }
}
