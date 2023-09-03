import os, subprocess, json
from pathlib import Path
from config import Server, Configuration

global LOCAL_SSH_KEY_FOLDER
global CONFIGURATION
CONFIG_FILE_NAME = "private_config.json"

def findLocalSshKeyFolder():
    global LOCAL_SSH_KEY_FOLDER
    LOCAL_SSH_KEY_FOLDER = Path().home() / ".ssh" 

def checkSshKey():
    if os.path.isfile(LOCAL_SSH_KEY_FOLDER / "id_rsa.pub"):
        print("RSA key already exists.")
        return False
    else:
        print("RSA key was not found. We will build a new one.")
        if os.name == 'nt':
            command = f"-f {LOCAL_SSH_KEY_FOLDER}/id_rsa -t rsa -N ''"
        else:
            command = f"-f {LOCAL_SSH_KEY_FOLDER}/id_rsa -t rsa -N ''"
        result = subprocess.run(["ssh-keygen"] + command.split(' '), stdout=subprocess.PIPE)
        print(result.stdout.decode('utf-8'))
        return True

def checkConfigFile(keyIsNew):
    global CONFIGURATION
    if os.path.isfile(CONFIG_FILE_NAME):
        readConfigFile()
        if keyIsNew or True:
            for server in CONFIGURATION.servers:
                server.hasMyKey = False
            updateConfigFile()
        print("Configuration file is processed and ready.")
    else:
        proxyPort = input("Enter port to use for proxy tunneling: ")
        CONFIGURATION = Configuration(proxyPort=proxyPort)
        updateConfigFile()
        print("Configuration file is initiated and ready.")

def updateConfigFile():
    with open(CONFIG_FILE_NAME, "w") as file:
        file.write(CONFIGURATION.toJSON())

def readConfigFile():
    global CONFIGURATION
    with open(CONFIG_FILE_NAME, "r") as file:
        CONFIGURATION = Configuration(**json.loads(file.read()))

def runCommandManager():
    while True:
        printConfigServers()
        command = input("Enter a number to edit a server or input `+` to add a new one:")
        if command == "+":
                commandManagerNewServer()

def commandManagerNewServer():
    try:
        ip = input("Input new server's IP: ")
        sshPortText = input("Input new server's SSH port if it's not the default value (22): ")
        if sshPortText == "":
            sshPortText = "22"
        sshPort = int(sshPort)
        server = Server(ip, True, True, sshPort)
    except:
        print("Invalid input, please try again.")

def printConfigServers():
    if len(CONFIGURATION.servers) == 0:
        print("Config file has no servers currently.")
    else:
        for i, server in enumerate(CONFIGURATION.servers):
            print(f"{i}: {server}")

if __name__ == "__main__":
    print("Running SshPersistentProxy Admin.")
    findLocalSshKeyFolder()
    keyIsNew = checkSshKey()
    checkConfigFile(keyIsNew)
    runCommandManager()
