import java.io.Serializable;

public interface TaskCode<T> extends Serializable {
    T run();
}
