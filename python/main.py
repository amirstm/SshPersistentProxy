import os, subprocess, time, sys, socket, traceback
from config import GlobalConfig
from psutil import process_iter

global local_ssh_key_folder
global configuration
global servers
global next_server_index
CONFIG_FILE_FOLDER = GlobalConfig.CONFIG_FILE_FOLDER
CONFIG_FILE_NAME = GlobalConfig.CONFIG_FILE_NAME
next_server_index = 0

def set_ssh_key_folder():
    global local_ssh_key_folder
    local_ssh_key_folder = GlobalConfig.get_ssh_key_folder()

def check_ssh_key():
    if os.path.isfile(local_ssh_key_folder / "id_rsa.pub"):
        print("SSH key is successfully found.")
        return True
    else:
        print("SSH key is not found.")
        return False

def read_config_file():
    global configuration
    global servers
    if os.path.isfile(CONFIG_FILE_FOLDER + CONFIG_FILE_NAME):
        configuration = GlobalConfig.read_config_file()
        servers = [server for server in configuration.servers if server.enabled and server.has_my_key]
        print("Configuration file is processed and ready.")
        if len(servers) > 0:
            print(f"Available server count: {len(servers)}")
            return True
        else:
            print("No available server was found.")
            return False
    else:
        print("Configuration file is not found.")
        return False

def proxy_switcher():
    while True:
        # check_connection()
        kill_old_proxy_process()
        server = get_next_server()
        initiate_new_proxy_process(server)
        time.sleep(5)
    pass

def get_next_server():
    global next_server_index
    global servers
    server = servers[next_server_index]
    next_server_index = (next_server_index + 1) % len(servers)
    return server

def initiate_new_proxy_process(server):
    try:
        print("Initiating new proxy...")
        command = [
            "ssh",
            f"{server.username}@{server.ip}",
            "-p",
            str(server.ssh_port),
            "-D",
            str(configuration.proxy_port),
            "-oStrictHostKeyChecking=no",
            "-oExitOnForwardFailure=yes",
            "-oServerAliveInterval=30",
            "-oServerAliveCountMax=2",
            "-tt",
            "-g",
            "-i",
            str(local_ssh_key_folder / "id_rsa"),
        ]
        p = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stdout, text=True)
        p.communicate()
    except:
        print("Initiating new proxy failed.")
        print(traceback.format_exc())

def check_connection():
    while True:
        try:
            print("Connecting new socket to proxy.")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', configuration.proxy_port))
            print("New socket successfully connected to proxy.")
            tcp_connection_checker(sock)
            sock.close()
            print("Discarding old socket.")
        except Exception:
            print("Connection to proxy failed.")
            break
        time.sleep(1)

def kill_old_proxy_process():
    for proc in process_iter():
        try:
            if any([conns for conns in proc.connections(kind='inet') if conns.laddr.port == configuration.proxy_port]):
                print(f"Obsolete process blocking proxy port was found: {proc}")
                proc.terminate()
                print(f"Obsolete process with ID {proc.pid} was killed.")
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

def tcp_connection_checker(sock):
    while True:
        if is_socket_closed(sock):
            print("Socket has been closed.")
            break
        time.sleep(1)

def check_proxy_port_freedom():
    for proc in process_iter():
        try:
            if any([conns for conns in proc.connections(kind='inet') if conns.laddr.port == configuration.proxy_port]):
                print(f"Proxy port is already occupied by process: {proc}")
                return False
        except:
            pass
    return True

def initial_checks_pass():
    return check_ssh_key() and read_config_file() and check_proxy_port_freedom()

def main():
    print("Running SshPersistentProxy Main.")
    set_ssh_key_folder()
    if not initial_checks_pass():
        return
    proxy_switcher()

if __name__ == "__main__":
    main()
