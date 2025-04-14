import pjsua2 as pj
from loguru import logger

ROLE_STR = {
    pj.PJSIP_ROLE_UAC: "outgoing",
    pj.PJSIP_ROLE_UAS: "incoming",
    pj.PJSIP_UAC_ROLE: "outgoing",
    pj.PJSIP_UAS_ROLE: "incoming",
}


class PhoneCall(pj.Call):
    def __init__(self, account, call_id=pj.PJSUA_INVALID_ID):
        pj.Call.__init__(self, account, call_id)
        self.account = account
        self.connected = False
        self.onhold = False
        self.call_id = call_id
        self._muted = False

    def onCallState(self, cs_prm: pj.OnCallStateParam):
        # sip_event: pj.SipEvent = cs_prm.e
        # logger.debug(f"{sip_event.type=} {sip_event.body=} {sip_event.pjEvent=}")
        try:
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
                self.account.remove_call(self)
        except Exception as e:
            logger.error(f"State error: {str(e)}")

    def onCallMediaState(self, med_prm: pj.OnCallMediaStateParam):
        try:
            ci = self.getInfo()
            for mi in ci.media:
                if mi.type == pj.PJMEDIA_TYPE_AUDIO and (
                    mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE
                    or mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD
                ):
                    m = self.getMedia(mi.index)
                    am = pj.AudioMedia.typecastFromMedia(m)
                    # connect ports
                    self.account.app.ep.audDevManager().getCaptureDevMedia().startTransmit(
                        am
                    )
                    am.startTransmit(
                        self.account.app.ep.audDevManager().getPlaybackDevMedia()
                    )

                    if mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD and not self.onhold:
                        logger.info(f"[{self.peerUri}] sets call onhold")
                        self.onhold = True
                    elif mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE and self.onhold:
                        logger.info(f"[{self.peerUri}] sets call active")
                        self.onhold = False
        except Exception:
            logger.exception("Media error:")

    def Accept(self):
        try:
            prm = pj.CallOpParam()
            prm.statusCode = 200
            self.answer(prm)
            ci: pj.CallInfo = self.getInfo()
            logger.debug(
                f"[{self.call_id}] accepted: {ROLE_STR[ci.role]} acc={ci.accId} "
                f"local={ci.localUri} remote={ci.remoteUri} {ci.stateText}"
            )
        except Exception as e:
            logger.error(f"[{self.call_id}] Call answer error: {str(e)}")

    def Decline(self):
        try:
            ci: pj.CallInfo = self.getInfo()
            logger.debug(
                f"[{self.call_id}] declined: {ROLE_STR[ci.role]} acc={ci.accId} "
                f"local={ci.localUri} remote={ci.remoteUri} {ci.stateText}"
            )
            op: pj.CallOpParam = pj.CallOpParam()
            op.statusCode = pj.PJSIP_SC_DECLINE
            super().hangup(op)
        except Exception as e:
            logger.error(f"[{self.call_id}] Call decline error: {str(e)}")

    def Terminate(self):
        try:
            ci: pj.CallInfo = self.getInfo()
            logger.debug(
                f"[{self.call_id}] terminated: {ROLE_STR[ci.role]} acc={ci.accId} "
                f"local={ci.localUri} remote={ci.remoteUri} {ci.stateText}"
            )
            op: pj.CallOpParam = pj.CallOpParam()
            op.statusCode = pj.PJSIP_SC_REQUEST_TERMINATED
            super().hangup(op)
        except Exception as e:
            logger.error(f"[{self.call_id}] Call terminate error: {str(e)}")

    def TxMute(self, mute: bool):
        try:
            am = None
            ci = self.getInfo()
            for mi in ci.media:
                if mi.type == pj.PJMEDIA_TYPE_AUDIO and (
                    mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE
                    or mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD
                ):
                    m = self.getMedia(mi.index)
                    am = pj.AudioMedia.typecastFromMedia(m)

            if am is None:
                logger.error("AudioMedia not found")
                return

            if mute:
                self.account.app.ep.audDevManager().getCaptureDevMedia().stopTransmit(
                    am
                )
                self._muted = True
            else:
                self.account.app.ep.audDevManager().getCaptureDevMedia().startTransmit(
                    am
                )
                self._muted = False

            logger.debug(
                f"[{self.call_id}] mute = {mute}: {ROLE_STR[ci.role]} acc={ci.accId} "
                f"local={ci.localUri} remote={ci.remoteUri} {ci.stateText}"
            )
        except Exception:
            logger.exception("TxMute error:")

    def ToggleMute(self) -> None:
        self.TxMute(not self._muted)
