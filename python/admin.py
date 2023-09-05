import os, subprocess, json, time, paramiko
from pathlib import Path
from config import Server, Configuration
from paramiko import SSHClient

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
        command = f"-f {LOCAL_SSH_KEY_FOLDER}/id_rsa -t rsa"
        p = subprocess.Popen(["ssh-keygen"] + command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result, errors = p.communicate()
        # result = subprocess.run(["ssh-keygen"] + command.split(' '), stdout=subprocess.PIPE)
        print(result)
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
        print()
        printConfigServers()
        command = input("Enter a number to edit a server or `+` to add a new one: ")
        if command == "+":
            commandManagerNewServer()
            time.sleep(1)
        elif command.isdigit():
            serverInd = int(command) - 1
            if len(CONFIGURATION.servers) <= serverInd:
                print("Invalid index was entered. Please try again.")
            else:
                commandManageOldServer(CONFIGURATION.servers[serverInd])

def commandManageOldServer(server):
    while True:
        print(f'''
Please choose from the following commands for the server {server.ip}:
0. Exit to main menu
1. Run a test connection
2. Toggle enabled status from {server.enabled} to {not server.enabled}''')
        command = input("Enter the command number: ")
        if command == "0":
            break
        elif command == "1":
            try:
                runTestConnection(server)
                print(f"Connection to {server.ip} was successful.")
            except:
                print(f"Connection to {server.ip} failed.")
            time.sleep(1)
        elif command == "2":
            server.enabled = not server.enabled
            updateConfigFile()
        else:
            print("Invalid command. Please try again.")
            time.sleep(1)

def runTestConnection(server):
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server.ip, port=server.sshPort, 
                   username=server.username)
    client.exec_command(f'ls -a')

def commandManagerNewServer():
    try:
        ip = input("Input the new server's IP: ")
        sshPortText = input("Input the new server's SSH port if it's not the default value (22): ")
        username = input("Input the new server's username: ")
        password = input("Input the password to connect for the first time and add our SSH key: ")
        if sshPortText == "":
            sshPortText = "22"
        sshPort = int(sshPortText)
        server = Server(ip, username, True, True, sshPort)
    except Exception:
        print("Invalid input, please try again.")
    try:
        addMyKeyToServer(server, password)
    except:
        print("Error while adding our SSH key to the new server, please check the credentials.")
    CONFIGURATION.servers.append(server)
    updateConfigFile()

def addMyKeyToServer(server, password):
    mySshKey = readLocalSshKey()
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server.ip, port=server.sshPort, 
                   username=server.username, password=password)
    stdin, stdout, stderr = client.exec_command(f'echo -n \"{mySshKey}\" >> .ssh/authorized_keys')

def readLocalSshKey():
    with open(LOCAL_SSH_KEY_FOLDER / "id_rsa.pub", "r") as file:
        return file.read()

def printConfigServers():
    if len(CONFIGURATION.servers) == 0:
        print("Config file has no servers currently.")
    else:
        for i, server in enumerate(CONFIGURATION.servers):
            print(f"{i+1}: {server}")

if __name__ == "__main__":
    print("Running SshPersistentProxy Admin.")
    findLocalSshKeyFolder()
    keyIsNew = checkSshKey()
    checkConfigFile(keyIsNew)
    runCommandManager()
