import os
import os.path
import sys
import datetime
import fabric
import invoke
import paramiko
from paramiko import AuthenticationException, SSHException
import paramiko.ssh_exception
import scp
from scp import SCPException
import argparse

from config_gklee import SSH_CONFIG, CMD_GROUPS, REMOTE_DIR_PATHS


def fpr(s, log_file):
    print(s, file=log_file)


def fpr_flush(s, log_file):
    print(s, file=log_file, flush=True)


def execute_cmdgroup(conn, groupname, cmds, dir_path):

    cmd_group_dt = datetime.datetime.now(datetime.UTC)
    with open(f"{dir_path}\\{groupname}_cg.txt", "w") as log_file:
        fpr("\nBEGIN COMMANDGROUP {}".format(groupname), log_file)

        for cmd in cmds:
            cmd_dt = datetime.datetime.now(datetime.UTC)
            fpr(
                "\n{} ########### BEGIN COMMAND ##########".format(cmd_dt.isoformat()),
                log_file,
            )
            fpr("\nCOMMAND:\n'{}'".format(cmd), log_file)
            try:
                result = conn.run(cmd, hide=True)
            except invoke.exceptions.UnexpectedExit as ex:
                fpr("\nUNEXPECTEDEXIT:\n'{}'".format(ex), log_file)
            except invoke.exceptions.Failure as ex:
                fpr("\nFAILURE:\n'{}'".format(ex), log_file)
            except invoke.exceptions.ThreadException as ex:
                fpr("\nTHREADEXCEPTION:\n'{}'".format(ex), log_file)
            except Exception as ex:
                fpr("\nUNKNOWN EXCEPTION:\n'{}'".format(ex), log_file)
            else:
                fpr("\nEXITCODE:\n'{}'".format(result.exited), log_file)
                fpr("\nSTDOUT:\n'{}'".format(result.stdout), log_file)
                fpr("\nSTDERR:\n'{}'".format(result.stderr), log_file)
            finally:
                cmd_dt_end = datetime.datetime.now(datetime.UTC)
                fpr(
                    "\nDURATION:\n'{} seconds'".format(
                        (cmd_dt_end - cmd_dt).total_seconds()
                    ),
                    log_file,
                )
                fpr_flush(
                    "\n{} ########### END COMMAND ############".format(
                        cmd_dt_end.isoformat()
                    ),
                    log_file,
                )

        fpr_flush(
            "\nEND COMMANDGROUP {} {} seconds".format(
                groupname,
                (datetime.datetime.now(datetime.UTC) - cmd_group_dt).total_seconds(),
            ),
            log_file,
        )


def progress(filename, size, sent):
    sys.stdout.write(
        "\n%s's progress: %.2f%%   \r\n" % (filename, float(sent) / float(size) * 100)
    )


# Establish connection with remote machine
def client_connect(ssh):
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.client.WarningPolicy)
    ssh.connect(
        hostname=SSH_CONFIG["HOST"],
        username=SSH_CONFIG["USER"],
        password=SSH_CONFIG["PASSWORD"],
        look_for_keys=False,
    )


# Copy file/directory from remote machine to local machine
def copy_log(log_path, dir_path):

    cpy_dt = datetime.datetime.now(datetime.UTC)
    with open(f"{dir_path}\\copy.txt", "a") as log_file:

        fpr("\nCOPY FROM {}".format(log_path), log_file)
        fpr(
            "\n{} ########### BEGIN COPY ##########\n".format(cpy_dt.isoformat()),
            log_file,
        )

        try:
            with paramiko.SSHClient() as ssh:
                client_connect(ssh)
                with scp.SCPClient(ssh.get_transport(), progress=progress) as scp1:
                    scp1.get(
                        remote_path=log_path,
                        recursive=True,
                        preserve_times=True,
                        local_path=dir_path,
                    )
        except AuthenticationException as ex:
            fpr("\nAUTHENTICATION EXCEPTION:\n'{}'".format(ex), log_file)
        except SSHException as ex:
            fpr("\nSSH EXCEPTION:\n'{}'".format(ex), log_file)
        except SCPException as ex:
            fpr("\nSCP EXCEPTION:\n'{}'".format(ex), log_file)
        except FileNotFoundError as ex:
            fpr("\nFILE NOT FOUND ERROR:\n'{}'".format(ex), log_file)
        except Exception as ex:
            fpr("\nUNKNOWN EXCEPTION:\n'{}'".format(ex), log_file)
        else:
            fpr("\nCOPIED SUCCESSFULLY\n ", log_file)
        finally:
            cpy_dt_end = datetime.datetime.now(datetime.UTC)

            fpr(
                "\nDURATION:\n'{} seconds'".format(
                    (cpy_dt_end - cpy_dt).total_seconds()
                ),
                log_file,
            )

            fpr_flush(
                "\n{} ########### END COPY ############\n".format(
                    cpy_dt_end.isoformat()
                ),
                log_file,
            )


# Test if connection is established
def test_uname(conn, fobj=sys.stdout):
    try:
        conn.run("uname -a", hide=True)
    except paramiko.ssh_exception.AuthenticationException as ex:
        fpr(
            "\nCOULD NOT ESTABLISH CONNECTION:\n AUTHENTICATION EXCEPTION\n".format(ex),
            fobj,
        )
        sys.exit()
    except paramiko.ssh_exception.BadHostKeyException as ex:
        fpr(
            "\nCOULD NOT ESTABLISH CONNECTION:\n BAD HOST KEY EXCEPTION\n".format(ex),
            fobj,
        )
        sys.exit()
    except Exception as ex:
        fpr("\nCOULD NOT ESTABLISH CONNECTION: \n UNKNOWN EXCEPTION\n".format(ex), fobj)
        sys.exit()
    else:
        fpr("\nCONNECTION ESTABLISHED\n", fobj)
        return True


if __name__ == "__main__":
    # Create directory for every execution of code
    dump_dirname = "dumpx303-" + datetime.datetime.now(datetime.UTC).strftime(
        "%Y%m%dT%H%M%S"
    )
    # Path for files to be copied to

    # Parse argument for path leading to dump directory
    parser = argparse.ArgumentParser(description="Optional arguments to specify")
    parser.add_argument(
        "-dp",
        "-dump_path",
        dest="user_path",
        type=str,
        help="Enter the path to create the dump directory.",
        nargs="?",
        required=False,
        default=os.getcwd(),  # If no path is entered, default to current directory
    )

    # Parse argument for selecting a command group
    parser.add_argument(
        "-cg",
        "-command_group",
        dest="select_cg",
        type=str,
        help="Enter specific command group(s) to execute.",
        nargs="*",
        required=False,
    )

    # Parse argument to choose to copy nothing
    parser.add_argument(
        "-cp",
        "-copy",
        dest="choose_copy",
        type=bool,
        help="Choose whether to copy the directories or not: True or False.",
        nargs="?",
        required=False,
    )

    # Parse argument for choosing a directory path to copy from
    parser.add_argument(
        "-cp_d",
        "-copy_directory",
        dest="copy_dir",
        type=str,
        help="Provide the path to the directory you wish to copy.",
        nargs="*",
        required=False,
    )

    args = parser.parse_args()
    user_path = args.user_path
    select_cg = args.select_cg
    choose_copy = args.choose_copy
    copy_dir = args.copy_dir

    # Parameters
    user_host = SSH_CONFIG["USER"] + "@" + SSH_CONFIG["HOST"]
    connect_kwargs = {"password": SSH_CONFIG["PASSWORD"]}

    # Execute command groups
    with fabric.connection.Connection(user_host, connect_kwargs=connect_kwargs) as conn:

        # Test for connection before executing commands
        if test_uname(conn):
            # Test for a valid path
            if user_path is not None:
                if os.path.exists(user_path):
                    dir_path = os.path.join(
                        user_path, dump_dirname
                    )  # Complete path on local machine
                    os.makedirs(dir_path, exist_ok=True)  # Create path
                else:
                    print(f"\nPATH NAME '{user_path}' DOES NOT EXIST\n")
                    sys.exit()
            else:
                print(f"\nPATH NAME '{user_path}' DOES NOT EXIST\n")
                sys.exit()

        # Test if the selected command group(s) is valid
        if select_cg:
            for cg in select_cg:
                if cg in CMD_GROUPS.keys():
                    execute_cmdgroup(conn, cg, CMD_GROUPS[f"{cg}"], dir_path)
                elif cg not in CMD_GROUPS.keys():
                    print(f"\nCOMMAND GROUP NAME '{cg}' DOES NOT EXIST\n")
                    sys.exit()
        # Nothing was entered
        elif not select_cg:
            for cmd_grp, cmds in CMD_GROUPS.items():
                execute_cmdgroup(conn, cmd_grp, cmds, dir_path)


        # Copy Files/Directories
        if copy_dir:
            for log_path in copy_dir:
                copy_log(log_path, dir_path)
        else:
            for log_path in REMOTE_DIR_PATHS:
                copy_log(log_path, dir_path)
        
