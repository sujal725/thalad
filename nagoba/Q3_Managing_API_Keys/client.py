import socket


def main():
    host = "127.0.0.1"
    port = 5000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    print(s.recv(1024).decode(), end="")

    try:
        while True:
            cmd = input(">>> ")
            if not cmd:
                continue
            s.sendall((cmd + "\n").encode())
            data = s.recv(1024)
            if not data:
                print("Server closed connection.")
                break
            print(data.decode(), end="")
            if cmd.strip().upper() == "EXIT":
                break
    finally:
        s.close()


if __name__ == "__main__":
    main()
