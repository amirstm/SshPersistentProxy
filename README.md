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

1. **Clone**: Clone the GitHub repository and change directory to the *python* folder.
2. **Install Requirements**: Install the required python libraries.
   ```bash
   pip install -r requirements.txt
   ```
