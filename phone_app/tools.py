import json
from enum import StrEnum
from typing import Optional

from const import GENERAL_CONFIG, OS_RELEASE


def get_user_agent():
    model = "UNIV"
    build_time = "20250413"
    try:
        with open(OS_RELEASE) as f:
            lines = f.readlines()
            model = "UNIV"
            for line in lines:
                parts = line.split("=")
                if len(parts) == 2:
                    if parts[0] == "MODEL":
                        model = parts[1].strip('"\n')
                    if parts[0] == "BUILD_TIME":
                        build_time = parts[1].strip('"\n')
    except Exception:
        pass

    return f"{model}/{build_time}"


class Action(StrEnum):
    Call = "Call"
    Answer = "Answer"
    Mute = "Mute"


class TriggerInput:
    def __init__(self, idx: str, number: str, pin_name: str, action: str):
        self.idx: str = idx  # = "1"
        # self.annotation: str #= "телефон 1",
        # self.audio_interface_link: str #= "Device.Voip.AudioInterfaces.1."
        # self.duration: int #= 0
        # self.line_link: str #= "Device.Voip.VoiceProfile.1.Line.1."
        self.number: str = number  # = "tel1"
        self.pin_name: str = pin_name  # = "Q2"
        self.action: Action = Action[action]  # = "Call"

    def __str__(self):
        return f"[{self.idx}] {self.pin_name=} {self.number=} {self.action=}"


class Config:
    _instance = None
    _cfg: dict = {}
    _triggers_input: list[TriggerInput]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._load_config()
        self._initialized = True

    def _load_triggers_input(self):
        self._triggers_input = []

        for idx in self._cfg["Device"]["Voip"]["TriggersInput"]:
            v = self._cfg["Device"]["Voip"]["TriggersInput"][idx]
            tr = TriggerInput(
                idx=idx, number=v["Number"], pin_name=v["PinName"], action=v["Action"]
            )
            self._triggers_input.append(tr)

    def _load_config(self):
        with open(GENERAL_CONFIG) as f:
            self._cfg = json.load(f)
        self._load_triggers_input()

    def reload_config(self):
        self._load_config()

    @property  # +
    def gpio_server_socket(self) -> str:
        return self._cfg["Device"]["Voip"]["GPIOServerSocket"]  # noqa

    @property  # +
    def server(self) -> str:
        return self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["SIP"]["ProxyServer"]

    @property  # +
    def username(self) -> str:
        return self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["Line"]["1"]["SIP"][
            "AuthUserName"
        ]

    @property  # +
    def password(self) -> str:
        return self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["Line"]["1"]["SIP"][
            "AuthPassword"
        ]

    @property
    def voice_pin_name(self) -> str:
        return self._cfg["Device"]["Voip"]["AudioInterfaces"]["1"]["VoicePinName"]

    @property
    def register_expires(self) -> int:
        return self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["SIP"][
            "RegisterExpires"
        ]

    @property  # +
    def auto_answer_enabled(self) -> bool:
        return self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["Line"]["1"][
            "AutoAnswerEnable"
        ]

    @property  # +
    def auto_answer_time(self) -> int:
        return self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["Line"]["1"][
            "AutoAnswerTime"
        ]

    @property  # +
    def proxy_server_port(self) -> int:
        return self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["SIP"][
            "ProxyServerPort"
        ]

    @property  # +
    def triggers_input(self) -> list[TriggerInput]:
        return self._triggers_input

    def pin_action(self, pin_name: str) -> Optional[Action]:
        for ti in self._triggers_input:
            if ti.pin_name == pin_name:
                return ti.action

        return None

    def pin_number(self, pin_name: str) -> Optional[str]:
        for ti in self._triggers_input:
            if ti.pin_name == pin_name:
                return ti.number.strip()

        return None
