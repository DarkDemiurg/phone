import pjsua2 as pj
from const import RING_OUT
from log import logger
from voip_statistics import CallStatus

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
        self.on_hold = False
        self.call_id = call_id
        self._muted = False
        self.delay = -1
        self.delayed = False
        self.player: pj.AudioMediaPlayer | None = None

    def onDtmfDigit(self, prm: pj.OnDtmfDigitParam):
        logger.info(f"DTMF DIGIT: {prm.digit}")

    def play_out_ring(self):
        try:
            if self.player is None:
                self.player = pj.AudioMediaPlayer()
                self.player.createPlayer(RING_OUT)
                self.player.startTransmit(
                    self.account.app.ep.audDevManager().getPlaybackDevMedia()
                )
            else:
                logger.warning("Player is not None")
        except Exception as e:
            logger.exception(f"Start player error: {str(e)}")

    def stop_out_ring(self):
        try:
            if self.player is not None:
                self.player.stopTransmit(
                    self.account.app.ep.audDevManager().getPlaybackDevMedia()
                )
                self.player = None
            else:
                logger.warning("Player is not None")
        except Exception as e:
            logger.exception(f"Stop player error: {str(e)}")

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
                self.account.app.stat.set_call_status(self.account.id, CallStatus.Busy)
                self.account.app.stop_in_ring()  # self.account.app.ring.kill(speaker_off=False)
                self.stop_out_ring()

            if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:  # Session is terminated.
                self.account.remove_call(self)
                self.account.app.stat.set_call_status(self.account.id, CallStatus.Idle)
                self.account.app.stop_in_ring()  # self.account.app.ring.kill()
                self.stop_out_ring()
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

                    info = self.getStreamInfo(mi.index)
                    codec = f"{info.codecName}/{info.codecClockRate}"

                    logger.debug(f"Codec: {codec}")

                    self.account.app.stat.set_call_codec(codec)

                    mic: pj.AudioMedia = (
                        self.account.app.ep.audDevManager().getCaptureDevMedia()
                    )
                    mic.adjustTxLevel(3.0)
                    mic.startTransmit(am)
                    am.startTransmit(
                        self.account.app.ep.audDevManager().getPlaybackDevMedia()
                    )

                    if (
                        mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD
                        and not self.on_hold
                    ):
                        logger.info(f"[{self.call_id}] sets call on hold")
                        self.on_hold = True
                    elif mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE and self.on_hold:
                        logger.info(f"[{self.call_id}] sets call active")
                        self.on_hold = False
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
            logger.exception(f"[{self.call_id}] Call terminate error: {str(e)}")

    def Ringing(self):
        try:
            ci: pj.CallInfo = self.getInfo()
            logger.debug(
                f"[{self.call_id}] ringing: {ROLE_STR[ci.role]} acc={ci.accId} "
                f"local={ci.localUri} remote={ci.remoteUri} {ci.stateText}"
            )
            op: pj.CallOpParam = pj.CallOpParam()
            op.statusCode = pj.PJSIP_SC_RINGING
            super().answer(op)
            self.account.app.stat.set_call_status(self.account.id, CallStatus.Ringing)
        except Exception as e:
            logger.error(f"[{self.call_id}] Call terminate error: {str(e)}")

    def AutoAnswer(self, auto_answer_time: int):
        try:
            ci: pj.CallInfo = self.getInfo()
            logger.debug(
                f"[{self.call_id}] auto answer: {ROLE_STR[ci.role]} acc={ci.accId} "
                f"local={ci.localUri} remote={ci.remoteUri} {ci.stateText}"
            )
            self.delayed = True
            self.delay = auto_answer_time
            self.account.app.stat.set_call_status(self.account.id, CallStatus.Ringing)
        except Exception as e:
            logger.error(f"[{self.call_id}] Auto answer error: {str(e)}")

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

    def Active(self) -> bool:
        try:
            ci: pj.CallInfo = self.getInfo()
            return ci.state == pj.PJSIP_INV_STATE_CONFIRMED
        except Exception:
            logger.exception("Active error:")

        return False
