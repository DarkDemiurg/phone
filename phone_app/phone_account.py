import pjsua2 as pj
from loguru import logger
from phone_call import PhoneCall


class PhoneAccount(pj.Account):
    def __init__(self, app, username: str, password: str, server: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.username = username
        self.password = password
        self.server = server
        self.calls: list[PhoneCall] = []
        self.__create()

    def __create(self):
        self.cfg = pj.AccountConfig()
        self.cfg.idUri = f"sip:{self.username}@{self.server}"
        self.cfg.regConfig.registrarUri = f"sip:{self.server}"

        cred = pj.AuthCredInfo("digest", "*", self.username, 0, self.password)
        self.cfg.sipConfig.authCreds.append(cred)

        self.create(self.cfg)

    def onIncomingCall(self, call_prm: pj.OnIncomingCallParam):
        # logger.debug(f'{call_prm.callId=} {call_prm.rdata=}')

        phone_call: PhoneCall = PhoneCall(account=self, call_id=call_prm.callId)

        if not self.app.call_allowed:
            phone_call.Decline()
        else:
            phone_call.Accept()
            self.add_call(phone_call)

    def onRegState(self, reg_prm: pj.OnRegStateParam):
        # logger.debug(f'{reg_prm.status=} {reg_prm.code=} {reg_prm.reason=} {reg_prm.rdata=} {reg_prm.expiration=}')

        ai: pj.AccountInfo = self.getInfo()
        # logger.debug(
        #     f"{ai.id=} {ai.isDefault=} {ai.uri=} {ai.regIsConfigured=} {ai.regIsActive=} {ai.regExpiresSec=} "
        #     f"{ai.regStatus=} {ai.regStatusText=} {ai.regLastErr=} {ai.onlineStatus=} {ai.onlineStatusText=}"
        # )
        logger.debug(f"[{ai.uri}]: reg status = {ai.regStatus} {ai.regStatusText}")

        return super().onRegState(reg_prm)

    def make_call(self, number: str):
        logger.debug(f"[{self.username}{self.server}] New outgoing call to: {number}")
        phone_call = PhoneCall(self)
        prm = pj.CallOpParam(True)
        try:
            dest_uri = f"sip:{number}@{self.server}"
            phone_call.makeCall(dest_uri, prm)
            self.add_call(phone_call)
        except pj.Error as pjerr:
            logger.error(pjerr.info())

    def add_call(self, call: PhoneCall):
        self.calls.append(call)
        logger.debug(
            f"[{self.cfg.idUri}] CALL ADDED: {call.getInfo().remoteUri} CURRENT CALLS: {len(self.calls)}"
        )

    def remove_call(self, call: PhoneCall):
        self.calls.remove(call)
        logger.debug(
            f"[{self.cfg.idUri}] CALL REMOVED: {call.getInfo().remoteUri} CURRENT CALLS: {len(self.calls)}"
        )
