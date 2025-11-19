import java.rmi.Remote;
import java.rmi.RemoteException;

public interface KeyService extends Remote {

    public String createKey() throws RemoteException;

    public String getKey() throws RemoteException;

    public boolean unblockKey(String key) throws RemoteException;

    public boolean keepAlive(String key) throws RemoteException;

    public String viewState() throws RemoteException;
}