import socket
import os

from loguru import logger

from tools import Config

socket_path = Config().cfg.gpio_server_socket


class GpioClient:
    def __init__(self, socket_path: str):
        self.socket_path = socket_path
    
    def set_output_pin(pin_name: str, val: bool):
        pass

with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET, 0) as s:
    s.connect(socket_path)
    while True:
        res = s.recv(4)
        print(res)
