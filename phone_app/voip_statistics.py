import json
from enum import StrEnum

from const import VOIP_RUNTIME_DATA
from log import logger


class CallStatus(StrEnum):
    Unknown = "Unknown"
    Idle = "Idle"
    Busy = "Busy"
    Calling = "Calling"
    Ringing = "Ringing"


class RegisterStatus(StrEnum):
    Unknown = "Unknown"
    Up = "Up"
    Initializing = "Initializing"
    Registering = "Registering"
    Registered = "Registered"
    RegistrationOff = "RegistrationOff"
    Unregistering = "Unregistering"
    RegisterError = "RegisterError"
    RegisterServerUnavailable = "RegisterServerUnavailable"
    Disabled = "Disabled"


class Statistics:
    _instance = None
    _cfg: dict = {
        "Device": {
            "Voip": {
                "VoiceProfile": {
                    "1": {
                        "Line": {
                            "1": {
                                "CallStatus": "Idle",
                                "RegisterStatus": "Unknown",
                                "BackupRegisterStatus": "Unknown",
                            }
                        }
                    }
                }
            }
        }
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Statistics, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.__update()
        self._initialized = True

    def __update(self):
        try:
            with open(VOIP_RUNTIME_DATA, "w") as f:
                json.dump(self._cfg, f, indent=4)
        except Exception:
            logger.exception("Update statistics error:")

    def set_call_status(self, call_status: CallStatus):
        self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["Line"]["1"]["CallStatus"] = (
            call_status.value
        )
        self.__update()

    def set_register_status(self, register_status: RegisterStatus):
        self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["Line"]["1"][
            "RegisterStatus"
        ] = register_status.value
        self.__update()
