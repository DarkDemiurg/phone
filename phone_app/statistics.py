import json

from const import VOIP_RUNTIME_DATA
from log import logger


class Statistics:
    _instance = None
    _cfg: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Statistics, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._load_config()
        self._initialized = True

    def _load_config(self):
        try:
            with open(VOIP_RUNTIME_DATA) as f:
                self._cfg = json.load(f)
        except Exception:
            logger.exception("Load statistics error:")

    def update(self):
        try:
            with open(VOIP_RUNTIME_DATA) as f:
                json.dump(self._cfg, f, indent=4)
        except Exception:
            logger.exception("Update statistics error:")
