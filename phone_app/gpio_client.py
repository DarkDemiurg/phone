import socket
import threading
from typing import Callable, Optional

from log import logger


class GpioClient:
    _instance: Optional["GpioClient"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GpioClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.__is_shut_down = threading.Event()
        self.__shutdown_request = False

        self._initialized: bool = True

    def serve_forever(self, socket_path: str, callback: Callable[[str], None]):
        self.__is_shut_down.clear()

        try:
            while not self.__shutdown_request:
                try:
                    logger.debug(f"Trying connect to socket: {socket_path}")
                    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET, 0) as s:
                        s.connect(socket_path)

                        logger.debug(f"Connected to socket: {socket_path}")

                        while not self.__shutdown_request:
                            res = s.recv(14)
                            if self.__shutdown_request:
                                break

                            if len(res) >= 4:
                                try:
                                    msg = res.decode("ASCII").strip("\x00")
                                    parts = msg.split("=")
                                    if len(parts) == 2:
                                        pin = parts[0]
                                        state = parts[1]

                                        if state == "1":
                                            if callback is not None:
                                                callback(pin)
                                except Exception:
                                    pass
                except Exception:
                    logger.exception("GpioClient error:")
        finally:
            self.__shutdown_request = False
            self.__is_shut_down.set()
            logger.debug("GpioClient terminated")

    def shutdown(self):
        self.__shutdown_request = True
        self.__is_shut_down.wait()
