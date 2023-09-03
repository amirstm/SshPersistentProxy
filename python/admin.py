import os, subprocess
from pathlib import Path

global LOCAL_SSH_KEY_FOLDER

def findLocalSshKeyFolder():
    global LOCAL_SSH_KEY_FOLDER
    LOCAL_SSH_KEY_FOLDER = Path().home() / ".ssh" 

def CheckSshKey():
    if os.path.isfile(LOCAL_SSH_KEY_FOLDER / "id_rsa.pub"):
        print("RSA key already exists.")
    else:
        print("RSA key was not found. We will build a new one.")
        if os.name == 'nt':
            command = f"-f {LOCAL_SSH_KEY_FOLDER}/id_rsa -t rsa -N ''"
        else:
            command = f"-f {LOCAL_SSH_KEY_FOLDER}/id_rsa -t rsa -N ''"
        result = subprocess.run(["ssh-keygen"] + command.split(' '), stdout=subprocess.PIPE)
        print(result.stdout.decode('utf-8'))

if __name__ == "__main__":
    print("Running SshPersistentProxy Admin.")
    findLocalSshKeyFolder()
    CheckSshKey()
