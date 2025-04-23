import os

from tools import Config


def SpeakerOn():
    pin = Config().voice_pin_name
    os.system(f"gpio_set -u /var/run/gpio-server.socket -p {pin} -v 1")


def SpeakerOff():
    pin = Config().voice_pin_name
    os.system(f"gpio_set -u /var/run/gpio-server.socket -p {pin} -v 1")
