import os
import os.path
import sys
from datetime import datetime
import dataclasses
import paramiko
import scp


user = "root"
host = "192.168.1.1"
pswd = "LantronixFAE"


# Define progress callback that prints the current percentage completed for the file
def progress(filename, size, sent):
    sys.stdout.write(
        "%s's progress: %.2f%%   \r" % (filename, float(sent) / float(size) * 100)
    )


with paramiko.SSHClient() as ssh:
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.client.WarningPolicy)
    ssh.connect(hostname=host, username=user, password=pswd, look_for_keys=False)

    with scp.SCPClient(ssh.get_transport(), progress=progress) as scp:
        scp.get("/overlay/work/log", recursive=True, preserve_times=True)
