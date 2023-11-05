# SSH Persistent Proxy

SSH Persistent Proxy is a collection of Python executables and Docker images designed to simplify the establishment and maintenance of persistent SSH connections to designated servers. This project is particularly useful for individuals who have limited internet access or need to maintain continuous connections to remote servers.

## Features

- **One-time Password**: Securely connect to remote servers using SSH keys. The user only needs to provide a password during the initial configuration.
- **Unlimited Servers**: You can add multiple servers to the configuration list. If some servers become unreachable, the connection seamlessly switches to an available one.
- **Custom Port**: Specify the port for port forwarding, providing flexibility and customization according to your needs.
- **Docker Friendly**: Choose to run the Python code directly or use pre-configured Docker images for a smoother experience.
- **Update Configuration On-demand**: Run the configurator as you need and update the configuration whenever needed. This flexible feature allows you to adapt your setup as your requirements change.

## Running without Docker

Follow these steps to use the project without Docker:

1. **Clone the Repository**: Begin by cloning the GitHub repository to your local machine. Change your current directory to the `python` folder.
   ```bash
   git clone https://github.com/amirstm/SshPersistentProxy.git
   cd SshPersistentProxy/python
   ```
2. **Install Required Libraries**: Use pip to install the necessary Python libraries specified in the requirements.txt file.
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Configurator**: Execute the configurator script to set up your SSH connections and configurations. Follow the on-screen instructions to add at least one server to the configuration list.
   ```bash
   python admin.py
   ```
4. **Start the Main Executable**: Finally, run the main executable to establish and maintain a connection to one of the configured servers, forwarding the specified port for use as a proxy.
   ```bash
   python main.py
   ```

Your proxy is now ready and accessible as a socks5 proxy on the specified port.

## Running with Docker

Follow these steps to use the project with Docker:

1. **Run the Configurator**: 
   - Replace `<VOLUME_NAME>` in the following command with your custom volume name.
   - Execute the configurator image to set up your SSH connections and configurations. Follow the on-screen instructions to add at least one server to the configuration list.
 
    ```bash
    docker container run --rm -it -v <VOLUME_NAME>:/python/config  amirstm/sshproxy_admin
    ```
2. **Run the Main Image**: 
   - Replace `<VOLUME_NAME>` and `<PORT>` in the following command with the specified volume name and the desired port for the main image.
   - Start the main Docker image, which establishes and maintains a connection to one of the configured servers, forwarding the specified port as a proxy.
   
    ```bash
    docker container run -v <VOLUME_NAME>:/python/config -p <PORT>:<PORT> amirstm/sshproxy_main
    ```

Your proxy is now ready and accessible as a socks5 proxy on the specified port.