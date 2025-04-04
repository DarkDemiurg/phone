import pjsua2 as pj
from loguru import logger

ROLE_STR = {
    pj.PJSIP_ROLE_UAC: "outgoing",
    pj.PJSIP_ROLE_UAS: "incoming",
    pj.PJSIP_UAC_ROLE: "outgoing",
    pj.PJSIP_UAS_ROLE: "incoming",
}


class PhoneCall(pj.Call):
    def __init__(self, account, call_id):
        super().__init__(account, call_id)
        self.account = account
        self.call_id = call_id

    def onCallState(self, cs_prm: pj.OnCallStateParam):
        # sip_event: pj.SipEvent = cs_prm.e
        # logger.debug(f"{sip_event.type=} {sip_event.body=} {sip_event.pjEvent=}")
        try:
            breakpoint()
            ci: pj.CallInfo = self.getInfo()
            # logger.debug(
            #     f"{ci.id=} {ci.role=} {ci.accId=} {ci.localUri=} {ci.localContact=} {ci.remoteUri=} "
            #     f"{ci.remoteContact=} {ci.callIdString=} {ci.setting=} {ci.state=} {ci.stateText=} "
            #     f"{ci.lastStatusCode=} {ci.lastReason=} {ci.media=} {ci.provMedia=} {ci.connectDuration=} "
            #     f"{ci.totalDuration=} {ci.remOfferer=} {ci.remAudioCount=} {ci.remVideoCount=}"
            # )
            logger.debug(
                f"[{self.call_id}] {ROLE_STR[ci.role]} acc={ci.accId} "
                f"local={ci.localUri} remote={ci.remoteUri} {ci.stateText}"
            )
            if ci.state == pj.PJSIP_INV_STATE_NULL:  # Before INVITE is sent or received
                pass
            if ci.state == pj.PJSIP_INV_STATE_CALLING:  # After INVITE is sent
                pass
            if ci.state == pj.PJSIP_INV_STATE_INCOMING:  # After INVITE is received.
                pass
            if ci.state == pj.PJSIP_INV_STATE_EARLY:  # After response with To tag.
                pass
            if ci.state == pj.PJSIP_INV_STATE_CONNECTING:  # After 2xx is sent/received.
                pass
            if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:  # After ACK is sent/received.
                pass
            if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:  # Session is terminated.
                # self.app.calls.remove(self)
                pass
        except Exception as e:
            logger.error(f"State error: {str(e)}")

        return super().onCallState(cs_prm)

    def onCallMediaState(self, med_prm: pj.OnCallMediaStateParam):
        return super().onCallMediaState(med_prm)

    def accept(self):
        try:
            prm = pj.CallOpParam()
            prm.statusCode = 200
            super().answer(prm)
            ci: pj.CallInfo = self.getInfo()
            logger.debug(
                f"[{self.call_id}] accepted: {ROLE_STR[ci.role]} acc={ci.accId} "
                f"local={ci.localUri} remote={ci.remoteUri} {ci.stateText}"
            )
        except Exception as e:
            logger.error(f"[{self.call_id}] Answer error: {str(e)}")

    def decline(self):
        try:
            op: pj.CallOpParam = pj.CallOpParam()
            op.statusCode = pj.PJSIP_SC_BUSY_HERE
            super().hangup(op)
            ci: pj.CallInfo = self.getInfo()
            logger.debug(
                f"[{self.call_id}] declined: {ROLE_STR[ci.role]} acc={ci.accId} "
                f"local={ci.localUri} remote={ci.remoteUri} {ci.stateText}"
            )
        except Exception as e:
            logger.error(f"[{self.call_id}] Answer error: {str(e)}")
