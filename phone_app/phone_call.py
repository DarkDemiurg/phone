import pjsua2 as pj
from loguru import logger


class PhoneCall(pj.Call):
    def __init__(self):
        pass

    def onCallState(self, prm: pj.OnCallStateParam):
        try:
            ci: pj.CallInfo = self.getInfo()
            logger.info(f"Call state: {ci.stateText}")
            # if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            #     self.app.calls.remove(self)
        except Exception as e:
            logger.error(f"State error: {str(e)}")

        return super().onCallState(prm)

    def onCallMediaState(self, prm):
        return super().onCallMediaState(prm)

    def answer(self, prm):
        try:
            prm = pj.CallOpParam()
            prm.statusCode = 200
            super().answer(prm)
        except Exception as e:
            self.app.logger.error(f"Answer error: {str(e)}")
