import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;

public class TaskImpl extends UnicastRemoteObject implements Task {

    public TaskImpl() throws RemoteException {
        super();
    }

    @Override
    public <T> T executeTask(TaskCode<T> code) throws RemoteException {
        System.out.println("Executing client-submitted code...");
        return code.run();
    }
}
