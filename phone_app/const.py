HOST = True

if HOST:
    GENERAL_CONFIG = "cfg/general_config.json"
    OS_RELEASE = "cfg/os-release"
    MCAST_DATA = "cfg/mcast_data.json"
    LOG_LEVEL = 4
    GPIO_SOCKET_PATH = "/tmp/gpio-server.socket"
    USE_THREADS = True
else:
    GENERAL_CONFIG = "/tmp/etc/general_config.json"
    OS_RELEASE = "/usr/lib/os-release"
    MCAST_DATA = "/tmp/mcast_data.json"
    LOG_LEVEL = 3
    GPIO_SOCKET_PATH = "/var/run/gpio-server.socket"
    USE_THREADS = True
