
import java.rmi.Naming;
import java.util.Scanner;

public class Client {

    public static void main(String[] args) {
        try {
            KeyService stub = (KeyService) Naming.lookup("rmi://localhost/KeyService");

            Scanner sc = new Scanner(System.in);
            while (true) {
                System.out.print("Menu -\n1. Create new key\n2. Get available key\n3. Keep alive a key\n4. Unblock a key\n5. View server state\n6. Exit\nEnter your choice: ");
                int choice = sc.nextInt();
                sc.nextLine();
                switch (choice) {
                    case 1:
                        String created = stub.createKey();
                        System.out.println("Created Key: " + created);
                        break;
                    case 2:
                        String assigned = stub.getKey();
                        if (assigned == null) {
                            System.out.println("No available keys at the moment.");
                        } else {
                            System.out.println("Assigned Key: " + assigned);
                        }
                        break;

                    case 3:
                        System.out.print("Enter key for keep-alive: ");
                        String kaKey = sc.nextLine().trim();
                        if (stub.keepAlive(kaKey)) {
                            System.out.println("Keep-alive successful.");
                        } else {
                            System.out.println("Keep-alive failed (expired/invalid).");
                        }
                        break;

                    case 4:
                        System.out.print("Enter key to unblock: ");
                        String ubKey = sc.nextLine().trim();
                        if (stub.unblockKey(ubKey)) {
                            System.out.println("Key unblocked.");
                        } else {
                            System.out.println("Unblock failed (invalid key or not blocked).");
                        }
                        break;

                    case 5:
                        System.out.println("Server State:");
                        System.out.println(stub.viewState());
                        break;

                    case 6:
                        System.out.println("Exiting client...");
                        sc.close();
                        return;

                    default:
                        System.out.println("Invalid choice. Try again.");
                }
            }
        } catch (Exception e) {
            System.out.println("Client Error: " + e.getMessage());
        }
    }
}
