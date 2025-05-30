import os
import socket

SOCKET_PATH = "/tmp/gpio-server.socket"


def main():
    while True:
        # Удаляем существующий сокет
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)

        try:
            # Создаём и настраиваем сокет
            with socket.socket(
                socket.AF_UNIX, socket.SOCK_SEQPACKET, 0
            ) as server_socket:
                server_socket.bind(SOCKET_PATH)
                server_socket.listen(1)

                while True:
                    connection, _ = server_socket.accept()

                    print(f"New connection: {connection=}")

                    with connection:
                        while True:
                            cmd = input("Enter button num. 'q' to exit.\n")

                            if cmd == "q":
                                os._exit(0)

                            num = -1
                            try:
                                num = int(cmd)
                            except Exception:
                                pass

                            if 2 <= num <= 13:
                                msg = f"Q{num}=1"
                                bts = msg.encode("ASCII")
                                connection.send(bts)
                                print(f"Sended: {msg}")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
