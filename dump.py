import os
import os.path
import sys
from datetime import datetime
import dataclasses
import fabric
import invoke
import paramiko
import scp

from config import SSH_CONFIG, CMD_GROUPS


def execute_cmdgroup(conn, groupname, cmds, fobj=sys.stdout):
    def fpr(s):
        print(s, file=fobj)

    def fpr_flush(s):
        print(s, file=fobj, flush=True)

    cmd_group_dt = datetime.utcnow()
    fpr("\nBEGIN COMMANDGROUP {}".format(groupname))

    for cmd in cmds:
        cmd_dt = datetime.utcnow()
        fpr("\n{} ########### BEGIN COMMAND ##########".format(cmd_dt.isoformat()))
        fpr("\nCOMMAND:\n'{}'".format(cmd))
        try:
            result = conn.run(cmd, hide=True)
        except invoke.exceptions.UnexpectedExit as ex:
            fpr("\nUNEXPECTEDEXIT:\n'{}'".format(ex))
        except invoke.exceptions.Failure as ex:
            fpr("\nFAILURE:\n'{}'".format(ex))
        except invoke.exceptions.ThreadException as ex:
            fpr("\nTHREADEXCEPTION:\n'{}'".format(ex))
        except Exception as ex:
            fpr("\nUNKNOWN EXCEPTION:\n'{}'".format(ex))
        else:
            fpr("\nEXITCODE:\n'{}'".format(result.exited))
            fpr("\nSTDOUT:\n'{}'".format(result.stdout))
            fpr("\nSTDERR:\n'{}'".format(result.stderr))
        finally:
            cmd_dt_end = datetime.utcnow()
            fpr(
                "\nDURATION:\n'{} seconds'".format(
                    (cmd_dt_end - cmd_dt).total_seconds()
                )
            )
            fpr_flush(
                "\n{} ########### END COMMAND ############".format(
                    cmd_dt_end.isoformat()
                )
            )

    fpr_flush(
        "\nEND COMMANDGROUP {} {} seconds".format(
            groupname, (datetime.utcnow() - cmd_group_dt).total_seconds()
        )
    )


if __name__ == "__main__":
    # Create directory in cwd

    dump_dirname = "dumpx303-" + datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    p = os.path.join(os.getcwd(), dump_dirname)
    # print(p)
    # TODO

    # os._exit(0)

    user_host = SSH_CONFIG["USER"] + "@" + SSH_CONFIG["HOST"]
    connect_kwargs = {"password": SSH_CONFIG["PASSWORD"]}

    cmds = ["uname -a", "uname -n"]
    with fabric.connection.Connection(user_host, connect_kwargs=connect_kwargs) as conn:
        execute_cmdgroup(conn, "test", cmds)
