import java.rmi.Remote;
import java.rmi.RemoteException;

public interface Task extends Remote {
    <T> T executeTask(TaskCode<T> code) throws RemoteException;
}