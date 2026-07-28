import json
from pathlib import Path

class Server:
    def __init__(self, ip, username, hasMyKey, enabled, sshPort=22):
        self.ip = ip
        self.sshPort = sshPort
        self.username = username
        self.hasMyKey = hasMyKey
        self.enabled = enabled

    def toDict(self):
        return {
            "ip": self.ip,
            "sshPort": self.sshPort,
            "hasMyKey": self.hasMyKey,
            "enabled": self.enabled,
            "username": self.username
        }

    def __str__(self):
        return self.ip

class Configuration:
    def __init__(self, proxy_port, servers=[]):
        self.proxy_port = proxy_port
        self.servers = [Server(**s) for s in servers]

    def toJSON(self):
        return json.dumps({
            "proxy_port": self.proxy_port,
            "servers": [s.toDict() for s in self.servers]
            },
            indent=2)
    
class GlobalConig():
    CONFIG_FILE_FOLDER = "config/"
    CONFIG_FILE_NAME = "private_config.json"

    def getSshKeyFolder():
        return Path(GlobalConig.CONFIG_FILE_FOLDER) / ".ssh"
        # LOCAL_SSH_KEY_FOLDER = Path().home() / ".ssh"   # Obsolete

    def readConfigFile():
        with open(GlobalConig.CONFIG_FILE_FOLDER + GlobalConig.CONFIG_FILE_NAME, "r") as file:
            return Configuration(**json.loads(file.read()))
        
    def updateConfigFile(configuration):
        with open(GlobalConig.CONFIG_FILE_FOLDER + GlobalConig.CONFIG_FILE_NAME, "w") as file:
            file.write(configuration.toJSON())


