import json
import os
import select
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

    def serve_forever(
        self,
        gpio_socket_path: str,
        gpio_callback: Callable[[str], None],
        config_socket_path: str,
        config_callback: Callable[[str, str], None],
    ):
        self.__is_shut_down.clear()

        try:
            config_server_socket = self._setup_config_socket(config_socket_path)

            while not self.__shutdown_request:
                try:
                    with socket.socket(
                        socket.AF_UNIX, socket.SOCK_SEQPACKET, 0
                    ) as gpio_socket:
                        gpio_socket.connect(gpio_socket_path)
                        logger.debug(f"Connected to GPIO socket: {gpio_socket_path}")

                        sockets_to_monitor = [gpio_socket, config_server_socket]

                        while not self.__shutdown_request:
                            readable, _, _ = select.select(
                                sockets_to_monitor, [], [], 1.0
                            )

                            for sock in readable:
                                if sock == gpio_socket:
                                    self._handle_gpio_socket(gpio_socket, gpio_callback)
                                elif sock == config_server_socket:
                                    self._handle_config_socket(
                                        config_server_socket, config_callback
                                    )
                except Exception:
                    logger.exception("GpioClient error:")
                    if not self.__shutdown_request:
                        threading.Event().wait(1)
        finally:
            self._cleanup_config_socket(config_socket_path)
            self.__shutdown_request = False
            self.__is_shut_down.set()
            logger.debug("GpioClient terminated")

    def _setup_config_socket(self, socket_path: str) -> socket.socket:
        """Создание серверного сокета для конфигурации"""
        if os.path.exists(socket_path):
            os.remove(socket_path)

        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.bind(socket_path)
        server_socket.listen(1)
        server_socket.setblocking(False)
        logger.debug(f"Config socket server started: {socket_path}")
        return server_socket

    def _handle_gpio_socket(
        self, gpio_socket: socket.socket, callback: Callable[[str], None]
    ):
        """Обработка данных от GPIO сокета"""
        try:
            res = gpio_socket.recv(14)
            if self.__shutdown_request:
                return

            if len(res) >= 4:
                msg = res.decode("ASCII").strip("\x00")
                parts = msg.split("=")
                if len(parts) == 2:
                    pin = parts[0]
                    state = parts[1]
                    if state == "1" and callback is not None:
                        callback(pin)
        except socket.error:
            raise  # GPIO сокет отключился

    def _handle_config_socket(
        self, server_socket: socket.socket, callback: Callable[[str, str], None]
    ):
        try:
            conn, addr = server_socket.accept()
            try:
                data = conn.recv(1024).decode("utf-8").strip()
                if data:
                    self._process_config_data(data, callback)
            finally:
                conn.close()
        except BlockingIOError:
            pass  # Нет ожидающих подключений
        except Exception as e:
            logger.error(f"Error handling config connection: {e}")

    def _process_config_data(self, data: str, callback: Callable[[str, str], None]):
        try:
            config = json.loads(data)
            param = config.get("param")
            value = config.get("value")

            if param and value is not None:
                logger.debug(f"Received new config value: {param}={value}")
                callback(param, value)
            else:
                logger.warning(f"Invalid config value: {value}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {data}")
        except Exception as e:
            logger.error(f"Error processing config: {e}")

    def _cleanup_config_socket(self, socket_path: str):
        if os.path.exists(socket_path):
            try:
                os.remove(socket_path)
            except Exception as e:
                logger.error(f"Error cleaning up config socket: {e}")

    def shutdown(self):
        self.__shutdown_request = True
        self.__is_shut_down.wait()
