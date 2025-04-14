"""Main module."""

import atexit

import pjsua2 as pj  # type: ignore
from const import LOG_LEVEL
from gpio_client import GpioClient
from icecream import install
from loguru import logger
from phone_account import PhoneAccount
from tools import Config, get_user_agent

install()

logger.add("/tmp/phone_app.log", rotation="1 MB")


class PhoneApp:
    def __init__(self):
        self.__init()
        atexit.register(self.__destroy)

    def __init(self):
        self.cfg = Config()
        self.__create_lib()
        self.__init_lib()
        self.__start_lib()

        self.__create_accounts()

    def __create_lib(self):
        self.ep = pj.Endpoint()
        self.ep.libCreate()

    def __init_lib(self):
        self.__create_endpoint_config()
        self.ep.libInit(self.ep_cfg)
        self.__create_transport()

    def __start_lib(self):
        self.ep.libStart()

    def __destroy(self):
        self.ep.libDestroy()

    def __create_media_config(self):
        self.med_cfg = pj.MediaConfig()

        self.ep_cfg.medConfig = self.med_cfg

    def __create_ua_config(self):
        self.ua_cfg = pj.UaConfig()
        self.ua_cfg.userAgent = get_user_agent()
        self.ep_cfg.uaConfig = self.ua_cfg

    def __create_log_config(self):
        self.log_cfg = pj.LogConfig()
        # self.log_cfg.filename = "/tmp/pjsip.log"
        self.log_cfg.level = LOG_LEVEL
        self.log_cfg.consoleLevel = LOG_LEVEL
        self.ep_cfg.logConfig = self.log_cfg

    def __create_endpoint_config(self):
        self.ep_cfg = pj.EpConfig()

        self.__create_log_config()
        self.__create_ua_config()
        self.__create_media_config()

    def __create_transport(self):
        self.tr = pj.TransportConfig()
        self.tr.port = self.cfg.proxy_server_port
        self.ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, self.tr)

    def __create_accounts(self):
        self.accounts = []
        acc = PhoneAccount(self, self.cfg.username, self.cfg.password, self.cfg.server)
        self.accounts.append(acc)

    @property
    def call_allowed(self):
        return True

    def make_call(self, number: str):
        logger.debug(f"[PHONE_APP] New outgoing call to: {number}")
        self.__choose_account(number).make_call(number)

    def __choose_account(self, number: str) -> PhoneAccount:
        return self.accounts[0]  # TODO: implement stub for multiple accounts


if __name__ == "__main__":
    app = PhoneApp()

    # for d in app.ep.audDevManager().enumDev2():
    #     p: pj.AudioDevInfo = d
    #     print(p.name)

    # app.make_call("5006")
    # app.make_call("0036111")

    for t in app.cfg.triggers_input:
        print(t)

    socket_path = "/tmp/gpio-server.socket"  # app.gpio_server_socket
    gpio_client = GpioClient()
    gpio_client.serve_forever(socket_path)
