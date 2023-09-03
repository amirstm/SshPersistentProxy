import json

class Server:
    def __init__(self, ip, hasMyKey, enabled, sshPort=22):
        self.ip = ip
        self.sshPort = sshPort
        self.hasMyKey = hasMyKey
        self.enabled = enabled

    def toDict(self):
        return {
            "ip": self.ip,
            "sshPort": self.sshPort,
            "hasMyKey": self.hasMyKey,
            "enabled": self.enabled
        }

class Configuration:
    def __init__(self, proxyPort, servers=[]):
        self.proxyPort = proxyPort
        self.servers = [Server(**s) for s in servers]

    def toJSON(self):
        return json.dumps({
            "proxyPort": self.proxyPort,
            "servers": [s.toDict() for s in self.servers]
            },
            indent=2)
    