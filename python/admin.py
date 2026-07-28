import os, subprocess, time, paramiko
from config import Server, Configuration, GlobalConfig
from paramiko import SSHClient
from getpass import getpass

global local_ssh_key_folder
global configuration
CONFIG_FILE_FOLDER = GlobalConfig.CONFIG_FILE_FOLDER
CONFIG_FILE_NAME = GlobalConfig.CONFIG_FILE_NAME

def set_ssh_key_folder():
    global local_ssh_key_folder
    local_ssh_key_folder = GlobalConfig.get_ssh_key_folder()
    
def make_necessary_directories():
    if not os.path.isdir(CONFIG_FILE_FOLDER):
        os.mkdir(CONFIG_FILE_FOLDER)
    if not os.path.isdir(local_ssh_key_folder):
        os.mkdir(local_ssh_key_folder)

def approve_ssh_key():
    if os.path.isfile(local_ssh_key_folder / "id_rsa.pub"):
        print("RSA key already exists.")
        return False
    else:
        print("RSA key was not found. We will build a new one.")
        command = f"-f {local_ssh_key_folder}/id_rsa -t rsa -N "
        p = subprocess.Popen(["ssh-keygen"] + command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result, errors = p.communicate()
        print(result)
        return True

def approve_config_file(key_is_new):
    global configuration
    if os.path.isfile(CONFIG_FILE_FOLDER + CONFIG_FILE_NAME):
        configuration = GlobalConfig.read_config_file()
        if key_is_new:
            for server in configuration.servers:
                server.has_my_key = False
            GlobalConfig.update_config_file(configuration)
        print("Configuration file is processed and ready.")
    else:
        while True:
            proxy_port_str = input("Enter port to use for proxy tunneling: ")
            if proxy_port_str.isdigit():
                proxy_port = int(proxy_port_str)
                break
            else:
                print("Proxy port should be an integer. Please, try again.")
        configuration = Configuration(proxy_port=proxy_port)
        GlobalConfig.update_config_file(configuration)
        print("Configuration file is initiated and ready.")

def run_command_manager():
    while True:
        print()
        print_config_servers()
        command = input("Enter a number to edit a server or `+` to add a new one: ")
        if command == "+":
            command_manager_new_server()
            time.sleep(1)
        elif command.isdigit():
            server_index = int(command) - 1
            if len(configuration.servers) <= server_index or server_index < 0:
                print("Invalid index was entered. Please try again.")
            else:
                command_manage_old_server(configuration.servers[server_index])

def command_manage_old_server(server):
    while True:
        print(f'''
Please choose from the following commands for the server {server.username}@{server.ip}:
0. Exit to main menu
1. Run a test connection
2. Toggle enabled status from {server.enabled} to {not server.enabled}
3. Delete server from list''')
        if not server.has_my_key:
            print("4. Add my key to the server")
        command = input("Enter the command number: ")
        if command == "0":
            break
        elif command == "1":
            try:
                run_test_connection(server)
                print(f"Connection to {server.ip} was successful.")
            except Exception:
                print(f"Connection to {server.ip} failed.")
            time.sleep(1)
        elif command == "2":
            server.enabled = not server.enabled
            GlobalConfig.update_config_file(configuration)
        elif command == "3":
            configuration.servers.remove(server)
            GlobalConfig.update_config_file(configuration)
            break
        elif command == "4" and (not server.has_my_key):
            password = getpass("Input remote server's password to transfer the SSH key: ")
            add_my_key_to_server(server, password)
            server.has_my_key = True
            GlobalConfig.update_config_file(configuration)
            print("Your key was successfully added to the server.")
        else:
            print("Invalid command. Please try again.")
            time.sleep(1)

def run_test_connection(server):
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server.ip, port=server.ssh_port, username=server.username,
                   key_filename=str(local_ssh_key_folder / "id_rsa"))
    client.exec_command(f'ls -a')

def command_manager_new_server():
    try:
        ip = input("Input the new server's IP: ")
        ssh_port_text = input("Input the new server's SSH port if it's not the default value (22): ")
        username = input("Input the new server's username: ")
        password = getpass("Input remote server's password to transfer the SSH key: ")
        if ssh_port_text == "":
            ssh_port_text = "22"
        ssh_port = int(ssh_port_text)
        server = Server(ip, username, True, True, ssh_port)
    except Exception:
        print("Invalid input, please try again.")
        return
    try:
        add_my_key_to_server(server, password)
        print("Your key was successfully added to the server.")
    except:
        print("Error while adding our SSH key to the new server, please check the credentials.")
        return
    configuration.servers.append(server)
    GlobalConfig.update_config_file(configuration)

def add_my_key_to_server(server, password):
    my_ssh_key = read_local_ssh_key()
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server.ip, port=server.ssh_port, username=server.username, password=password)
    client.exec_command(f'mkdir .ssh')
    client.exec_command(f'echo -n \"{my_ssh_key}\" >> .ssh/authorized_keys')

def read_local_ssh_key():
    with open(local_ssh_key_folder / "id_rsa.pub", "r") as file:
        return file.read()

def print_config_servers():
    if len(configuration.servers) == 0:
        print("Config file currently has no servers.")
    else:
        for i, server in enumerate(configuration.servers):
            print(f"{i+1}: {server} {'' if server.has_my_key else '(NO KEY)'}")

if __name__ == "__main__":
    print("Running SshPersistentProxy Admin.")
    set_ssh_key_folder()
    make_necessary_directories()
    key_is_new = approve_ssh_key()
    approve_config_file(key_is_new)
    run_command_manager()
