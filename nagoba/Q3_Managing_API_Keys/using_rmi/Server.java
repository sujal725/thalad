import java.rmi.Naming;

public class Server {
    public static void main(String[] args) {
        try {
            KeyServiceImpl obj = new KeyServiceImpl();
            Naming.rebind("KeyService", obj);
            System.out.println("API Key Manager Server is running...");
        } catch (Exception e) {
            System.out.println("Server error: " + e.toString());
        }
    }
}
