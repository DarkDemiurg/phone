HOST = True
if HOST:
    GENERAL_CONFIG = 'cfg/general_config.json'
    OS_RELEASE = 'cfg/os-release'
    MCAST_DATA = 'cfg/mcast_data.json'
else:
    GENERAL_CONFIG = '/tmp/etc/general_config.json'
    OS_RELEASE = '/usr/lib/os-release'
    MCAST_DATA = '/tmp/mcast_data.json'