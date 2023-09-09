import os, subprocess, json, time, paramiko, sys
from pathlib import Path
from config import Server, Configuration, GlobalConig
from paramiko import SSHClient

global LOCAL_SSH_KEY_FOLDER
global CONFIGURATION
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

def checkConfigFile():
    global CONFIGURATION
    if os.path.isfile(CONFIG_FILE_FOLDER + CONFIG_FILE_NAME):
        CONFIGURATION = GlobalConig.readConfigFile()
        print("Configuration file is processed and ready.")
        return True
    else:
        print("Configuration file is not found.")
        return False

def main():
    print("Running SshPersistentProxy Main.")
    setSshKeyFolder()
    if not checkSshKey():
        return
    if not checkConfigFile():
        return

if __name__ == "__main__":
    main()