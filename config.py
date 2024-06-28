SSH_CONFIG = {"USER": "root", "HOST": "192.168.1.1", "PASSWORD": "LantronixFAE"}

REMOTE_DIR_PATHS = ["/overlay/work/log/Refresh/", "/opt/Refresh/Database/"]
REMOTE_FILE_PATHS = []

CMD_GROUPS = {
    "system": [
        "cat /etc/os-release",
        "uname -a",
        "uname -n",
        "set",
        "crontab -l",
        "ubus call system board",
        "ubus call system info",
        "ubus call service list",
    ],
    "uci": [
        "uci export",
        "uci show",
    ],
    "filesystems": [
        "cat /proc/mtd",
        "cat /proc/mounts",
        "cat /proc/partitions",
        "mount",
        "df",
    ],
    "systemlogs": ["dmesg", "logread"],
    "ifconfig": ["ifconfig"],
    "ip": [
        "ip -d -s -h link show",
        "ip neigh show",
        "ip -d addr show",
        "ip route show",
        "ip rule show",
        "ip route list table all",
    ],
    "processes": [
        "ps -lw",
        "cat /proc/meminfo",
        "free",
        "cat /proc/uptime",
        "netstat -anlpeW",
        "top -b -n 3 -d 1",
    ],
    "ubus_network": [
        "ubus call router_info getRouterinfo",
        "ubus call dnsmasq metrics",
        "ubus call network.device status",
        "ubus call network.interface dump",
        "ubus call network.wireless status",
        "ubus call network.interface.cellular status",
        "ubus call serviceaction getCellulardata",
        "ubus call mwan3 status",
    ],
    "ubus_wifi": [
        """ubus call iwinfo info '{"device":"wlan0"}'""",
        """ubus call iwinfo info '{"device":"wlan1"}'""",
        """ubus call iwinfo scan '{"device":"wlan0"}'""",
        """ubus call iwinfo scan '{"device":"wlan1"}'""",
        """ubus call iwinfo assoclist '{"device":"wlan0"}'""",
        """ubus call iwinfo freqlist '{"device":"wlan0"}'""",
        """ubus call iwinfo freqlist '{"device":"wlan1"}'""",
        """ubus call iwinfo txpowerlist '{"device":"wlan0"}'""",
        """ubus call iwinfo txpowerlist '{"device":"wlan1"}'""",
    ],
    "sendat_cellular": [
        "sendat ATI",
        "sendat AT+GSN",
        "sendat AT+CIMI",
        "sendat AT+QCCID",
        "sendat AT+CSQ",
        "sendat AT+QCSQ",
        "sendat AT+QNWINFO",
        """sendat 'AT+QCSCON?'""",
    ],
}
