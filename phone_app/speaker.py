import os

from log import logger
from tools import Config

LED_PIN = "Q0"


def SpeakerOn():
    pin = Config().voice_pin_name
    cmd = f"gpio_set -u /var/run/gpio-server.socket -p {pin} -v 1"
    os.system(cmd)
    logger.debug(f"Try {cmd=}")


def SpeakerOff():
    pin = Config().voice_pin_name
    cmd = f"gpio_set -u /var/run/gpio-server.socket -p {pin} -v 0"
    os.system(cmd)
    logger.debug(f"Try {cmd=}")


def LedOn():
    cmd = f"gpio_set -u /var/run/gpio-server.socket -p {LED_PIN} -v 0"
    os.system(cmd)
    logger.debug(f"Try {cmd=}")


def LedOff():
    cmd = f"gpio_set -u /var/run/gpio-server.socket -p {LED_PIN} -v 1"
    os.system(cmd)
    logger.debug(f"Try {cmd=}")
