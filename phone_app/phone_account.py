import pjsua2 as pj
from log import logger
from phone_call import PhoneCall
from speaker import SpeakerOn
from voip_statistics import CallStatus, RegisterStatus


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
        self.cfg.regConfig.timeoutSec = self.app.cfg.register_expires

        cred = pj.AuthCredInfo("digest", "*", self.username, 0, self.password)
        self.cfg.sipConfig.authCreds.append(cred)

        self.create(self.cfg)
        self.app.stat.set_register_status(RegisterStatus.Registering)

    def onIncomingCall(self, call_prm: pj.OnIncomingCallParam):
        phone_call: PhoneCall = PhoneCall(account=self, call_id=call_prm.callId)
        logger.info("New incoming call")
        if self.app.cfg.auto_answer_enabled:
            if self.app.cfg.auto_answer_time > 0:
                self.app.play_in_ring()  # self.app.ring.start()
                phone_call.AutoAnswer(self.app.cfg.auto_answer_time)
            else:
                phone_call.Accept()
        else:
            self.app.play_in_ring()  # self.app.ring.start()
            phone_call.Ringing()

        self.add_call(phone_call)

    def onRegState(self, reg_prm: pj.OnRegStateParam):
        # logger.debug(f'{reg_prm.status=} {reg_prm.code=} {reg_prm.reason=} {reg_prm.rdata=} {reg_prm.expiration=}')

        ai: pj.AccountInfo = self.getInfo()
        # logger.debug(
        #     f"{ai.id=} {ai.isDefault=} {ai.uri=} {ai.regIsConfigured=} {ai.regIsActive=} {ai.regExpiresSec=} "
        #     f"{ai.regStatus=} {ai.regStatusText=} {ai.regLastErr=} {ai.onlineStatus=} {ai.onlineStatusText=}"
        # )
        logger.info(f"[{ai.uri}]: reg status = {ai.regStatus} {ai.regStatusText}")

        if ai.regStatus == 200:
            self.app.stat.set_register_status(RegisterStatus.Registered)
        else:
            self.app.stat.set_register_status(RegisterStatus.RegisterError)

        return super().onRegState(reg_prm)

    def make_call(self, number: str):
        logger.debug(f"[{self.username}{self.server}] New outgoing call to: {number}")
        phone_call = PhoneCall(self)
        prm = pj.CallOpParam(True)
        try:
            dest_uri = f"sip:{number}@{self.server}"
            SpeakerOn()
            phone_call.play_out_ring()
            phone_call.makeCall(dest_uri, prm)
            self.add_call(phone_call)
            self.app.stat.set_call_status(CallStatus.Calling)
            logger.info(f"New outgoing call to: {dest_uri}")
        except pj.Error as pjerr:
            logger.error(pjerr.info())

    def add_call(self, call: PhoneCall):
        try:
            self.calls.append(call)
            logger.debug(
                f"[{self.cfg.idUri}] CALL ADDED: {call.getInfo().remoteUri} CURRENT CALLS: {len(self.calls)}"
            )
        except Exception:
            logger.exception("Append call error")

    def remove_call(self, call: PhoneCall):
        try:
            self.calls.remove(call)
            logger.debug(
                f"[{self.cfg.idUri}] CALL REMOVED: {call.getInfo().remoteUri} CURRENT CALLS: {len(self.calls)}"
            )
        except Exception:
            logger.exception("Remove call error")
