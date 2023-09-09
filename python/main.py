import os, subprocess, json, time, paramiko, sys, socket, traceback
from pathlib import Path
from config import Server, Configuration, GlobalConig
from paramiko import SSHClient
from psutil import process_iter

global LOCAL_SSH_KEY_FOLDER
global CONFIGURATION
global SERVERS
CONFIG_FILE_FOLDER = GlobalConig.CONFIG_FILE_FOLDER
CONFIG_FILE_NAME = GlobalConig.CONFIG_FILE_NAME

def setSshKeyFolder():
    global LOCAL_SSH_KEY_FOLDER
    LOCAL_SSH_KEY_FOLDER = GlobalConig.getSshKeyFolder() 

def checkSshKey():
    if os.path.isfile(LOCAL_SSH_KEY_FOLDER / "id_rsa.pub"):
        print("SSH key is successfully found.")
        return True
    else:
        print("SSH key is not found.")
        return False

def readConfigFile():
    global CONFIGURATION
    if os.path.isfile(CONFIG_FILE_FOLDER + CONFIG_FILE_NAME):
        CONFIGURATION = GlobalConig.readConfigFile()
        SERVERS = [server for server in CONFIGURATION.servers if server.enabled and server.hasMyKey]
        print("Configuration file is processed and ready.")
        if len(SERVERS) > 0:
            print(f"Available server count: {len(SERVERS)}")
            return True
        else:
            print("No available server was found.")
            return False
    else:
        print("Configuration file is not found.")
        return False

def proxySwitcher():
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    # sock.connect(('127.0.0.1', CONFIGURATION.proxyPort))
    while True:
        checkConnection()
        time.sleep(10)
    pass

def checkConnection():
    while True:
        try:
            print("Connecting new socket to proxy.")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', CONFIGURATION.proxyPort))
            print("New socket successfully connected to proxy.")
            tcpConnectionChecker(sock)
            sock.close()
            print("Discarding old socket.")
        except Exception:
            print("Connection to proxy failed.")
            break
        closeOldConnection()
        time.sleep(1)

def closeOldConnection():
    for proc in process_iter():
        try:
            if any([conns for conns in proc.connections(kind='inet') if conns.laddr.port == CONFIGURATION.proxyPort]):
                print(proc)
                procFound = proc.terminate()
        except:
            pass

def is_socket_closed(sock: socket.socket) -> bool:
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) == 0:
            return True
    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except Exception as e:
        print("unexpected exception when checking if a socket is closed")
        return False
    return False

def tcpConnectionChecker(sock):
    while True:
        if is_socket_closed(sock):
            print("Socket has been closed.")
            break
        time.sleep(1)

def main():
    print("Running SshPersistentProxy Main.")
    setSshKeyFolder()
    if not checkSshKey():
        return
    if not readConfigFile():
        return
    proxySwitcher()

if __name__ == "__main__":
    main()