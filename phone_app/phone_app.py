"""Main module."""

import atexit

import pjsua2 as pj  # type: ignore
from loguru import logger

logger.add("/tmp/phone_app.log", rotation="1 MB")


class PhoneApp:
    def __init__(self):
        self.__init()
        atexit.register(self.__destroy)

    def __init(self):
        self.__create_lib()
        self.__init_lib()
        self.__start_lib()

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

        self.ep_cfg.uaConfig = self.ua_cfg

    def __create_log_config(self):
        self.log_cfg = pj.LogConfig()
        self.ep_cfg.logConfig = self.log_cfg

    def __create_endpoint_config(self):
        self.ep_cfg = pj.EpConfig()

        self.__create_log_config()
        self.__create_ua_config()
        self.__create_media_config()

    def __create_transport(self):
        self.tr = pj.TransportConfig()
        self.tr.port = 5060
        self.ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, self.tr)


if __name__ == "__main__":
    pa = PhoneApp()
    pass
