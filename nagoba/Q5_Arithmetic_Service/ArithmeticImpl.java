import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;

public class ArithmeticImpl extends UnicastRemoteObject implements Arithmetic {
    public ArithmeticImpl() throws RemoteException {
        super();
    }

    @Override
    public int add(int a, int b) throws RemoteException {
        return a + b;
    }

    @Override
    public int sub(int a, int b) throws RemoteException {
        return a - b;
    }

    @Override
    public int mul(int a, int b) throws RemoteException {
        return a * b;
    }

    @Override
    public int div(int a, int b) throws RemoteException {
        if (b == 0)
            throw new RemoteException("Division by zero aint possible");
        return a / b;
    }
}
