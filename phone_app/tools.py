import json

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


class Config:
    _instance = None
    _cfg: dict = {}

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

    def _load_config(self):
        with open(GENERAL_CONFIG) as f:
            self._cfg = json.load(f)

    def reload_config(self):
        self._load_config()

    @property
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

    @property
    def auto_answer_enabled(self) -> bool:
        return self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["Line"]["1"][
            "AutoAnswerEnable"
        ]

    @property
    def auto_answer_time(self) -> int:
        return self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["Line"]["1"][
            "AutoAnswerTime"
        ]

    @property  # +
    def proxy_server_port(self) -> int:
        return self._cfg["Device"]["Voip"]["VoiceProfile"]["1"]["SIP"][
            "ProxyServerPort"
        ]
