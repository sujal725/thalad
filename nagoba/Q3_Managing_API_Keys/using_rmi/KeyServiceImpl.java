import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class KeyServiceImpl extends UnicastRemoteObject implements KeyService {
    private static final long KEY_TTL_MS = 5 * 60 * 1000;
    private static final long BLOCK_TIMEOUT_MS = 60 * 1000;

    private final Map<String, KeyInfo> store = new HashMap<>();

    private static class KeyInfo {
        String status;
        long expiryTime;
        long blockedSince;
    }

    public KeyServiceImpl() throws RemoteException {
        super();
    }

    @Override
    public String createKey() throws RemoteException {
        String key = UUID.randomUUID().toString();
        KeyInfo info = new KeyInfo();
        info.status = "active";
        info.expiryTime = System.currentTimeMillis() + KEY_TTL_MS;
        info.blockedSince = 0;
        store.put(key, info);
        return key;
    }

    @Override
    public String getKey() throws RemoteException {
        long now = System.currentTimeMillis();
        for (Map.Entry<String, KeyInfo> entry : store.entrySet()) {
            KeyInfo info = entry.getValue();
            if (info.status.equals("available") && info.expiryTime > now) {
                info.status = "blocked";
                info.blockedSince = now;
                return entry.getKey();
            }
        }
        return null;
    }

    @Override
    public synchronized boolean unblockKey(String key) throws RemoteException {
        if (!store.containsKey(key)) {
            return false;
        }

        KeyInfo info = store.get(key);
        if (info.status.equals("blocked")) {
            info.status = "available";
            info.blockedSince = 0;
            return true;
        }
        return false;
    }

    @Override
    public synchronized boolean keepAlive(String key) throws RemoteException {
        if (!store.containsKey(key)) {
            return false;
        }

        long now = System.currentTimeMillis();
        KeyInfo info = store.get(key);
        if (info.expiryTime > now) {
            info.expiryTime = now + KEY_TTL_MS;
            return true;
        }
        return false;
    }

    @Override
    public synchronized String viewState() throws RemoteException {
        return store.toString();
    }
}
