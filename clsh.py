import os

from pssh.clients import ParallelSSHClient
import argparse


# Available SSH server (hosted in AWS EC2)
# 13.124.15.148
# 3.38.95.225
# 43.201.19.126

def connect_SSH(hosts, command, interactive, out, err):
    if interactive:
        client = ParallelSSHClient(hosts, user="ec2-user", pkey="ssh-key.pem")
        print("Enter ‘quit’ to leave this interactive mode")

        while True:
            shells = client.open_shell()
            command = input("clsh> ")
            if command == "quit":
                break
            client.run_shell_commands(shells, command)
            client.join_shells(shells)
            print("------------------------")
            for shell in shells:
                is_empty = True
                for line in shell.stdout:
                    is_empty = False
                    print(f"{shell.output.host}: {line}")
                for line in shell.stderr:
                    is_empty = False
                    print(f"{shell.output.host}: {line}")
                if is_empty:
                    print(f"{shell.output.host}:")
            print("------------------------")
    else:
        client = ParallelSSHClient(hosts, user="ec2-user", pkey="ssh-key.pem")
        output = client.run_command(command)
        for host_out in output:
            is_empty = True
            if out:
                with open(out, "a+") as file:
                    for line in host_out.stdout:
                        is_empty = False
                        file.write(f"{host_out.host}: ")
                        file.write(f"{line}\n")
            else:
                for line in host_out.stdout:
                    is_empty = False
                    print(f"{host_out.host}: {line}")
            if err:
                with open(err, "a+") as file:
                    for line in host_out.stderr:
                        is_empty = False
                        file.write(f"{host_out.host}: ")
                        file.write(f"{line}\n")
            else:
                for line in host_out.stderr:
                    is_empty = False
                    print(f"{host_out.host}: {line}")
            if is_empty:
                if out:
                    with open(out, "a+") as file:
                        file.write(f"{host_out.host}:\n")
                else:
                    print(f"{host_out.host}:")


def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--hostfile")
    parser.add_argument("-h")
    parser.add_argument("-i", action='store_true')
    parser.add_argument("--out")
    parser.add_argument("--err")

    parsed = parser.parse_known_args()
    return vars(parsed[0]), " ".join(parsed[1])


def execute(args, command):
    # default hosts listing
    if args["h"]:
        hosts = args["h"].split(",")
        print(command)
        connect_SSH(hosts, command, args["i"], args["out"], args["err"])
    elif args["hostfile"]:
        path = args["hostfile"]
        with open(path) as file:
            hosts = [line.rstrip() for line in file]
            connect_SSH(hosts, command, args["i"], args["out"], args["err"])
    elif os.environ.get("CLSH_HOSTS"):
        print("Note: use CLSH_HOSTS environment")
        hosts = os.environ.get("CLSH_HOSTS").split(":")
        connect_SSH(hosts, command, args["i"], args["out"], args["err"])
    elif os.environ.get("CLSH_HOSTFILE"):
        path = os.environ.get("CLSH_HOSTFILE")
        print(f"Note: use hostfile ‘{path}’ (CLSH_HOSTFILE env)")
        with open(path) as file:
            hosts = [line.rstrip() for line in file]
            connect_SSH(hosts, command, args["i"], args["out"], args["err"])
    elif os.path.exists(".hostfile"):
        print("Note: use hostfile ‘.hostfile’ (default)")
        with open(".hostfile") as file:
            hosts = [line.rstrip() for line in file]
            connect_SSH(hosts, command, args["i"], args["out"], args["err"])
    else:
        print("--hostfile 옵션이 제공되지 않았습니다")


if __name__ == '__main__':
    args, command = get_args()
    execute(args, command)
