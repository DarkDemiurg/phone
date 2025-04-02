import pjsua2 as pj
from loguru import logger


class PhoneAccount(pj.Account):
    def __init__(self):
        pass

    def onIncomingCall(self, prm):
        # Call *call = new MyCall(*this, iprm.callId);
        # // Just hangup for now
        # CallOpParam op;
        # op.statusCode = PJSIP_SC_DECLINE;
        # call->hangup(op);
        # // And delete the call
        # delete call;

        return super().onIncomingCall(prm)

    def onRegState(self, prm: pj.OnRegStateParam):
        ai: pj.AccountInfo = self.getInfo()
        msg = f"{'*** Register: code=' if ai.regIsActive else '*** Unregister: code='} {prm.code}"
        logger.debug(msg)
        return super().onRegState(prm)
