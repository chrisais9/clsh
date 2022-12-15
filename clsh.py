import os
import argparse
import subprocess
import signal
from sys import exit

# Available SSH server (hosted in AWS EC2)
# 13.124.15.148
# 3.38.165.191
# 43.201.19.126

p_pool = []

def connect_SSH(hosts, command, interactive, out, err, user):
    if interactive:
        print("Enter ‘quit’ to leave this interactive mode")
        print(f"Working with nodes: {', '.join(hosts)}")
        while True:
            inp = input("clsh> ")
            if inp == "quit":
                break

            print("------------------------")
            if inp.startswith("!"):
                p = subprocess.Popen(inp[1:],
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     shell=True,
                                     universal_newlines=True)
                out, err = p.communicate(inp)
                p_pool.append(p)
                if len(out):
                    print("LOCAL:", out, end="")
                elif len(err):
                    print("LOCAL:", err, end="")
                else:
                    print("LOCAL:")
                p.wait()
                p.terminate()
                p_pool.remove(p)
            else:
                for host in hosts:
                    p = subprocess.Popen(f'ssh -i ssh-key.pem {user+"@" if user else "ubuntu@"}{host} -T -o "StrictHostKeyChecking=no"',
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         shell=True,
                                         universal_newlines=True,
                                         preexec_fn=os.setsid)
                    try:
                        p_pool.append(p)
                        out, err = p.communicate(inp, timeout=5)
                        if len(out):
                            print(f"{host}:", out, end="")
                        elif len(err):
                            print(f"{host}:", err, end="")
                        else:
                            print(f"{host}:")
                        p.wait()
                        p.terminate()
                        p_pool.remove(p)
                    except subprocess.TimeoutExpired:
                        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                        print(f"ERROR: {host} connection lost")
                        exit(0)

            print("------------------------")
    else:
        for host in hosts:
                p = subprocess.Popen(f'ssh -i ssh-key.pem {user+"@" if user else "ubuntu@"}{host} -T -o "StrictHostKeyChecking=no"',
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     shell=True,
                                     universal_newlines=True,
                                     preexec_fn=os.setsid)
                try:
                    stdout, stderr = p.communicate(command, timeout=5)
                    if len(stdout):
                        if out:
                            with open(out, "a+") as file:
                                file.write(f"{host}: {stdout}")
                        else:
                            print(f"{host}:", stdout, end="")
                    elif len(stderr):
                        if err:
                            with open(err, "a+") as file:
                                file.write(f"{host}: {stderr}")
                        else:
                            print(f"{host}:", stderr, end="")
                    else:
                        if out:
                            with open(out, "a+") as file:
                                file.write(f"{host}:\n")
                        else:
                            print(f"{host}:")
                    p.wait()
                    p.terminate()
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                    print(f"ERROR: {host} connection lost")
                    exit(0)


def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--hostfile")
    parser.add_argument("--user")
    parser.add_argument("-h")
    parser.add_argument("-i", action='store_true')
    parser.add_argument("--out")
    parser.add_argument("--err")

    parsed = parser.parse_known_args()
    return vars(parsed[0]), " ".join(parsed[1])


def execute(args, command):
    if args["h"]:
        hosts = args["h"].split(",")
        connect_SSH(hosts, command, args["i"], args["out"], args["err"], args["user"])
    elif args["hostfile"]:
        path = args["hostfile"]
        with open(path) as file:
            hosts = [line.rstrip() for line in file]
            connect_SSH(hosts, command, args["i"], args["out"], args["err"], args["user"])
    elif os.environ.get("CLSH_HOSTS"):
        print("Note: use CLSH_HOSTS environment")
        hosts = os.environ.get("CLSH_HOSTS").split(":")
        connect_SSH(hosts, command, args["i"], args["out"], args["err"], args["user"])
    elif os.environ.get("CLSH_HOSTFILE"):
        path = os.environ.get("CLSH_HOSTFILE")
        print(f"Note: use hostfile ‘{path}’ (CLSH_HOSTFILE env)")
        with open(path) as file:
            hosts = [line.rstrip() for line in file]
            connect_SSH(hosts, command, args["i"], args["out"], args["err"], args["user"])
    elif os.path.exists(".hostfile"):
        print("Note: use hostfile ‘.hostfile’ (default)")
        with open(".hostfile") as file:
            hosts = [line.rstrip() for line in file]
            connect_SSH(hosts, command, args["i"], args["out"], args["err"], args["user"])
    else:
        print("--hostfile 옵션이 제공되지 않았습니다")


def handler(signum, frame):
    if signum == signal.SIGTERM:
        for p in p_pool:
            p.send_signal(signal.SIGTERM)
            p.wait()  # wait until shutdown
        exit(0)
    if signum == signal.SIGQUIT:
        for p in p_pool:
            p.send_signal(signal.SIGQUIT)
            os.kill(p.pid, signal.SIGQUIT)
        exit(0)
    if signum == signal.SIGINT:
        for p in p_pool:
            p.send_signal(signal.SIGINT)
            os.kill(p.pid, signal.SIGINT)
        exit(0)


if __name__ == '__main__':
    args, command = get_args()
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGQUIT, handler)
    signal.signal(signal.SIGINT, handler)
    execute(args, command)
