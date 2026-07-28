import os, subprocess, json, time, paramiko, sys
from config import Server, Configuration, GlobalConig
from paramiko import SSHClient
from getpass import getpass

global LOCAL_SSH_KEY_FOLDER
global CONFIGURATION
CONFIG_FILE_FOLDER = GlobalConig.CONFIG_FILE_FOLDER
CONFIG_FILE_NAME = GlobalConig.CONFIG_FILE_NAME

def setSshKeyFolder():
    global LOCAL_SSH_KEY_FOLDER
    LOCAL_SSH_KEY_FOLDER = GlobalConig.getSshKeyFolder() 
    
def makeNecessaryDirectories():
    if not os.path.isdir(CONFIG_FILE_FOLDER):
        os.mkdir(CONFIG_FILE_FOLDER)
    if not os.path.isdir(LOCAL_SSH_KEY_FOLDER):
        os.mkdir(LOCAL_SSH_KEY_FOLDER)

def approveSshKey():
    if os.path.isfile(LOCAL_SSH_KEY_FOLDER / "id_rsa.pub"):
        print("RSA key already exists.")
        return False
    else:
        print("RSA key was not found. We will build a new one.")
        command = f"-f {LOCAL_SSH_KEY_FOLDER}/id_rsa -t rsa -N "
        p = subprocess.Popen(["ssh-keygen"] + command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result, errors = p.communicate()
        print(result)
        return True

def approveConfigFile(key_is_new):
    global CONFIGURATION
    if os.path.isfile(CONFIG_FILE_FOLDER + CONFIG_FILE_NAME):
        CONFIGURATION = GlobalConig.readConfigFile()
        if key_is_new:
            for server in CONFIGURATION.servers:
                server.hasMyKey = False
            GlobalConig.updateConfigFile(CONFIGURATION)
        print("Configuration file is processed and ready.")
    else:
        while True:
            proxy_port_str = input("Enter port to use for proxy tunneling: ")
            if proxy_port_str.isdigit():
                proxy_port = int(proxy_port_str)
                break
            else:
                print("Proxy port should be an integer. Please, try again.")
        CONFIGURATION = Configuration(proxy_port=proxy_port)
        GlobalConig.updateConfigFile(CONFIGURATION)
        print("Configuration file is initiated and ready.")

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
            if len(CONFIGURATION.servers) <= serverInd or serverInd < 0:
                print("Invalid index was entered. Please try again.")
            else:
                commandManageOldServer(CONFIGURATION.servers[serverInd])

def commandManageOldServer(server):
    while True:
        print(f'''
Please choose from the following commands for the server {server.username}@{server.ip}:
0. Exit to main menu
1. Run a test connection
2. Toggle enabled status from {server.enabled} to {not server.enabled}
3. Delete server from list''')
        if not server.hasMyKey:
            print("4. Add my key to the server")
        command = input("Enter the command number: ")
        if command == "0":
            break
        elif command == "1":
            try:
                runTestConnection(server)
                print(f"Connection to {server.ip} was successful.")
            except Exception:
                print(f"Connection to {server.ip} failed.")
            time.sleep(1)
        elif command == "2":
            server.enabled = not server.enabled
            GlobalConig.updateConfigFile(CONFIGURATION)
        elif command == "3":
            CONFIGURATION.servers.remove(server)
            GlobalConig.updateConfigFile(CONFIGURATION)
            break
        elif command == "4" and (not server.hasMyKey):
            password = getpass("Input remote server's password to transfer the SSH key: ")
            addMyKeyToServer(server, password)
            server.hasMyKey = True
            GlobalConig.updateConfigFile(CONFIGURATION)
            print("Your key was successfully added to the server.")
        else:
            print("Invalid command. Please try again.")
            time.sleep(1)

def runTestConnection(server):
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server.ip, port=server.sshPort, username=server.username,
                   key_filename=str(LOCAL_SSH_KEY_FOLDER / "id_rsa"))
    client.exec_command(f'ls -a')

def commandManagerNewServer():
    try:
        ip = input("Input the new server's IP: ")
        sshPortText = input("Input the new server's SSH port if it's not the default value (22): ")
        username = input("Input the new server's username: ")
        password = getpass("Input remote server's password to transfer the SSH key: ")
        if sshPortText == "":
            sshPortText = "22"
        sshPort = int(sshPortText)
        server = Server(ip, username, True, True, sshPort)
    except Exception:
        print("Invalid input, please try again.")
    try:
        addMyKeyToServer(server, password)
        print("Your key was successfully added to the server.")
    except:
        print("Error while adding our SSH key to the new server, please check the credentials.")
        return
    CONFIGURATION.servers.append(server)
    GlobalConig.updateConfigFile(CONFIGURATION)

def addMyKeyToServer(server, password):
    mySshKey = readLocalSshKey()
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server.ip, port=server.sshPort, username=server.username, password=password)
    client.exec_command(f'mkdir .ssh')
    client.exec_command(f'echo -n \"{mySshKey}\" >> .ssh/authorized_keys')

def readLocalSshKey():
    with open(LOCAL_SSH_KEY_FOLDER / "id_rsa.pub", "r") as file:
        return file.read()

def printConfigServers():
    if len(CONFIGURATION.servers) == 0:
        print("Config file currently has no servers.")
    else:
        for i, server in enumerate(CONFIGURATION.servers):
            print(f"{i+1}: {server} {'' if server.hasMyKey else '(NO KEY)'}")

if __name__ == "__main__":
    print("Running SshPersistentProxy Admin.")
    setSshKeyFolder()
    makeNecessaryDirectories()
    key_is_new = approveSshKey()
    approveConfigFile(key_is_new)
    runCommandManager()
