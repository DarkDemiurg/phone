"""Main module."""

import atexit

import pjsua2 as pj  # type: ignore
from const import GPIO_SOCKET_PATH, HOST, LOG_LEVEL, USE_THREADS
from gpio_client import GpioClient
from icecream import install
from loguru import logger
from phone_account import PhoneAccount
from phone_call import PhoneCall
from tools import Action, Config, get_user_agent

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

        if USE_THREADS:
            self.ua_cfg.threadCnt = 1
            self.ua_cfg.mainThreadOnly = False
        else:
            self.ua_cfg.threadCnt = 0
            self.ua_cfg.mainThreadOnly = True

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
        self.accounts: list[PhoneAccount] = []
        acc = PhoneAccount(self, self.cfg.username, self.cfg.password, self.cfg.server)
        self.accounts.append(acc)

    @property
    def call_allowed(self):
        return True

    def MakeCall(self, number: str):
        logger.debug(f"[PHONE_APP] New outgoing call to: {number}")
        self.__choose_account(number).make_call(number)

    def __choose_account(self, number: str) -> PhoneAccount:
        return self.accounts[0]  # TODO: implement stub for multiple accounts

    def run(self):
        if HOST:
            socket_path = GPIO_SOCKET_PATH
        else:
            socket_path = self.cfg.gpio_server_socket

        self.gpio_client = GpioClient()
        self.gpio_client.serve_forever(socket_path, self.pin_callback)

    def print_audio_devs(self):
        for d in self.ep.audDevManager().enumDev2():
            p: pj.AudioDevInfo = d
            logger.debug(p.name)

    def pin_callback(self, pin_name: str) -> None:
        action = self.cfg.pin_action(pin_name)
        logger.debug(f"PIN handled: {pin_name}. {action}")

        if action is not None:
            self.process_pin_action(pin_name, action)

    def process_pin_action(self, pin_name: str, action: Action) -> None:
        try:
            match action:
                case Action.Call:
                    self.process_call(pin_name)
                case Action.Answer:
                    self.process_answer(pin_name)
                case Action.Mute:
                    self.process_mute(pin_name)
                case _:
                    logger.warning(f"Unknown Action: {action}")

        except Exception:
            logger.exception("PIN process error:")

    @property
    def current_call(self) -> None | PhoneCall:
        for acc in self.accounts:
            if len(acc.calls) > 0:
                return acc.calls[0]

        return None

    def process_call(self, pin_name):
        cc = self.current_call

        if cc is None:
            logger.debug(f"Call button pressed: {pin_name}. Current call is None")
            number = self.cfg.pin_number(pin_name)
            if number is not None and len(number) > 0:
                logger.info(
                    f'Make new call to number "{number}" because pin "{pin_name}" pressed.'
                )
                self.MakeCall(number)
            else:
                logger.info(f"Number for PIN = {pin_name} not found. Call skipped.")
        else:
            logger.info(
                f"Call button pressed: {pin_name}. Current call is not None. Terminate this call."
            )
            cc.Terminate()

    def process_answer(self, pin_name):
        cc = self.current_call

        if cc is None:
            logger.info(
                f"Answer button pressed: {pin_name}. Current call is None. Answer skipped."
            )
        else:
            logger.info(
                f"Answer button pressed: {pin_name}. Current call is not None. Answer this call."
            )
            cc.Accept()

    def process_mute(self, pin_name):
        cc = self.current_call

        if cc is None:
            logger.info(
                f"Mute button pressed: {pin_name}. Current call is None. Mute skipped."
            )
        else:
            logger.info(
                f"Mute button pressed: {pin_name}. Current call is not None. Toggle mute for this call."
            )
            cc.ToggleMute()


if __name__ == "__main__":
    app = PhoneApp()

    # app.print_audio_devs()

    # app.make_call("5006")

    # app.make_call("0036111")

    app.run()
