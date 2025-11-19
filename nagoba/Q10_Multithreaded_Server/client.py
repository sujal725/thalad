import socket


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 9000))

    print(s.recv(1024).decode(), end="")

    try:
        while True:
            cmd = input(">>> ")
            s.sendall((cmd + "\n").encode())
            resp = s.recv(1024)
            if not resp:
                break
            print(resp.decode(), end="")
            if cmd.strip().upper() == "EXIT":
                break
    finally:
        s.close()


if __name__ == "__main__":
    main()
