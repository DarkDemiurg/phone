import platform

HOST = platform.machine() != "armv7l"

if HOST:
    # GENERAL_CONFIG = "cfg/general_config.json"
    # OS_RELEASE = "cfg/os-release"
    # MCAST_DATA = "cfg/mcast_data.json"
    # VOIP_RUNTIME_DATA = "cfg/voip_runtime_data.json"
    GENERAL_CONFIG = "/tmp/etc/general_config.json"
    OS_RELEASE = "/tmp/etc/os-release"
    MCAST_DATA = "/tmp/etc/mcast_data.json"
    VOIP_RUNTIME_DATA = "/tmp/etc/voip_runtime_data.json"
    LOG_LEVEL = 2
    GPIO_SOCKET_PATH = "/tmp/gpio-server.socket"
    PHONE_SOCKET_PATH = "/tmp/phone-server.socket"
    USE_THREADS = True
    RING_OUT = "sound/ringing.wav"
    RING_IN = "sound/ring.wav"
else:
    GENERAL_CONFIG = "/tmp/etc/general_config.json"
    OS_RELEASE = "/usr/lib/os-release"
    MCAST_DATA = "/tmp/mcast_data.json"
    VOIP_RUNTIME_DATA = "/var/run/voip_runtime_data.json"
    LOG_LEVEL = 3
    GPIO_SOCKET_PATH = "/var/run/gpio-server.socket"
    PHONE_SOCKET_PATH = "/var/run/phone-server.socket"
    USE_THREADS = True
    RING_OUT = "/opt/phone_app/sound/ringing.wav"
    RING_IN = "/opt/phone_app/sound/ring.wav"
