import json
from pathlib import Path

class Server:
    def __init__(
        self,
        ip,
        username,
        enabled,
        has_my_key=None,
        ssh_port=22,
        **legacy_fields,
    ):
        self.ip = ip
        self.ssh_port = legacy_fields.get("sshPort", ssh_port)
        self.username = username
        self.has_my_key = legacy_fields.get("hasMyKey", has_my_key)
        self.enabled = enabled

    def to_dict(self):
        return {
            "ip": self.ip,
            "ssh_port": self.ssh_port,
            "has_my_key": self.has_my_key,
            "enabled": self.enabled,
            "username": self.username
        }

    def __str__(self):
        return self.ip

class Configuration:
    def __init__(self, proxy_port=None, servers=None, **legacy_fields):
        proxy_port = legacy_fields.get("proxyPort", proxy_port)
        servers = servers or []
        self.proxy_port = proxy_port
        self.servers = [Server(**s) for s in servers]

    def to_json(self):
        return json.dumps({
            "proxy_port": self.proxy_port,
            "servers": [s.to_dict() for s in self.servers]
            },
            indent=2)
    
class GlobalConfig:
    CONFIG_FILE_FOLDER = "config/"
    CONFIG_FILE_NAME = "private_config.json"

    def get_ssh_key_folder():
        return Path(GlobalConfig.CONFIG_FILE_FOLDER) / ".ssh"
        # local_ssh_key_folder = Path().home() / ".ssh"   # Obsolete

    def read_config_file():
        with open(GlobalConfig.CONFIG_FILE_FOLDER + GlobalConfig.CONFIG_FILE_NAME, "r") as file:
            return Configuration(**json.loads(file.read()))
        
    def update_config_file(configuration):
        with open(GlobalConfig.CONFIG_FILE_FOLDER + GlobalConfig.CONFIG_FILE_NAME, "w") as file:
            file.write(configuration.to_json())


