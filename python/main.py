import os, subprocess, json, time, paramiko, sys, socket
from pathlib import Path
from config import Server, Configuration, GlobalConig
from paramiko import SSHClient

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
    pass

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