# MineServerUpdater

MineServerUpdater is a Minecraft server manager and updater that allows you to specify global and server-specific configuration. You can specify server properties, whitelists, banned/op lists, and the target version (including keeping the latest server version).

## Contents

* [Install](#install)
* [Usage](#usage)
* [Configuration](#configuration)
  * [Top Level](#top-level)
  * [Server Configuration](#server-configuration)
  * [Configuration Example](#configuration-example)
* [Server Manager](#server-manager)
  * [Server Manager Configuration](#server-manager-configuration)
  * [Server Manager Service](#server-manager-service)

## Install

1. **Clone the repository:**

    ```sh
    git clone https://github.com/SylvanSerenity/MineServerUpdater
    cd MineServerUpdater
    ```

    ---

2. **Install dependencies (screen, python3, python3-venv):**

    ```sh
    sudo apt update
    sudo apt install -y screen python3 python3-venv
    ```

    ---

3. **Activate the Python virtual environment:**

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

    ---

4. **Install Python requirements:**

    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. **Configure the `servers.json` file for your servers.** See [Configuration](#configuration) for configuration specification.

    ```sh
    nano servers.json
    ```

    ---

2. **Run the `update.sh` script to install/update all servers to match your configuration specified in `servers.json`.**

    ```sh
    chmod +x update.sh
    ./update.sh
    ```

    ---

3. Consider making a cron task to automatically update the server on a schedule:

    ```sh
    chmod +x update.sh
    crontab -e
    ```

    Add an update task with your preferred schedule. This one updates the servers every day at 03:00 in the morning.

    ```txt
    0 3 * * * /home/minecraft/MineServerUpdater/update.sh >> /home/minecraft/MineServerUpdater/log.log >> 2>&1
    ```

    ***Note:** Replace `/home/minecraft/` with the absolute path of the `MineServerUpdater` directory.*

    ---

4. **Navigate to your new server directory and use the `server_manager.sh` script to start your server.** See [Server Manager](#server-manager) for more information, including how to [start the server on system boot](#server-manager-service).

    ```sh
    ./server_manager.sh
    ```

## Configuration

The `servers.json` configuration file for your servers is what defines how your servers behave whenever the `update.py` script is run. See below for specification of each object.

### Top Level

* `install_dir`: Defines the directory, relative to the working directory, where the servers are installed and updated. Defaults to `./minecraft-servers`.

    Example:

    ```json
    {
      "install_dir": "/home/minecraft"
    }
    ```

    ---

* `default`: The default options to be applied to all servers unless overridden by configuration defined in the `servers` object.

    Example:

    ```json
    {
      "default": {
        "version": "latest:release",
        "eula": false,
        "properties": {
            "difficulty": "normal",
            "allow-flight": true,
            "enable-command-block": true,
            "white-list": true,
            "motd": "\u00a7dA Cool Minecraft Server"
        },
        "whitelist": ["SylvanSerenity", "awesomeis9"],
        "ops": ["SylvanSerenity"],
        "banned_players": ["Notch"],
        "banned_ips": ["1.1.1.1"]
      }
    }
    ```

    ---

* `servers`: An array of server configurations that are specific to each server and add to or replace configurations defined in `default`.

    Example:

    ```json
    {
      "servers": [
        {
          "id": "vanilla",
          "version": "latest:release",
          "properties": {
            "level-seed": "12345",
            "server-port": "25565",
            "motd": "\u00a7bVanilla Minecraft Server"
          }
        },
        {
          "id": "snapshot",
          "version": "latest:snapshot",
          "properties": {
            "level-seed": "67890",
            "server-port": "25566",
            "motd": "\u00a7eSnapshot Minecraft Server"
          }
        },
        {
          "id": "legacy",
          "version": "1.6.4",
          "properties": {
            "level-seed": "ethoslab",
            "server-port": "25567"
          }
        },
        {
          "id": "modded",
          "version": "custom",
          "properties": {
            "level-seed": "toomanymods",
            "server-port": "25568"
          }
        }
      ]
    }
    ```

### Server Configuration

Both the `default` and `servers` objects take the following server configuration objects. All objects (besides `id` for `servers`) are optional.

* `id`: The ID of the server, which will become the directory where the server is installed.

  Example:

  ```json
  "id": "my-server"
  ```

  ***Note:** `default` does not take an `id` object.*

  ---

* `version`: The Minecraft version to use for this server. This can either be a specific version or snapshot (e.g. `1.6.4`), or one of the following:

  * `latest:release`: The latest full release version of Minecraft.

  * `latest:snapshot`: The latest snapshot version of Minecraft.

  * `custom`: Does not manage server jar file installation/updates at all. Use this for modded servers. You will need to manually download the server jar file.

  Example:

  ```json
  "version": "1.6.4"
  ```

  ---

* `eula`: Whether the EULA is accepted. Recommended to be set to `true` as a `default` configuration.

  Example:

  ```json
  "eula": true
  ```

  ***Note:** This is set to false by default to adhere to Minecraft's terms of service. You will have to manually edit this to true in your `servers.json` file.*

  ---

* `properties`: Defines key-value pairs for the `server.properties` file.

  Example:

  ```json
  "properties": {
    "difficulty": "normal",
    "allow-flight": true,
    "enable-command-block": true,
    "white-list": true,
    "motd": "\u00a7dA Cool Minecraft Server"
  }
  ```

  ***Note:** See [`server.properties` keys](https://minecraft.fandom.com/wiki/Server.properties#Keys) for a list of accepted key/value pairs.*

  ---

* `whitelist`: The whitelist to apply to the server. It takes an array of usernames.

  Example:

  ```json
  "whitelist": ["YourUsername", "Notch"]
  ```

  ***Note:** You will also need to set the `white-list` server property to `true` for the whitelist to take effect.*

  ---

* `ops`: The operator list. This takes an array of usernames.

  Example:

  ```json
  "ops": ["YourUsername", "Notch"]
  ```

  ---

* `banned_players`: The banned players list. This takes an array of usernames.

  Example:

  ```json
  "banned_players": ["EvildoerUsername", "Notch"]
  ```

  ---

* `banned_ips`: The banned IPs list. This takes an array of IP addresses.

  Example:

  ```json
  "banned_ips": ["1.1.1.1", "8.8.8.8"]
  ```

  ---

* `server_config`: The configuration for `server.cfg` as used by `server_manager.sh`. See [Server Manager Configuration](#server-manager-configuration) for more information.

  Example:

  ```json
  "server_config": {
    "xms": "2G",
    "xmx": "8G",
    "stop": false
  }
  ```

### Configuration Example

Here is a complete working example of the `servers.json` configuration:

```json
{
  "install_dir": "minecraft-servers",
  "default": {
    "version": "latest:release",
    "eula": false,
    "properties": {
        "difficulty": "normal",
        "allow-flight": true,
        "enable-command-block": true,
        "white-list": true,
        "motd": "\u00a7dA Cool Minecraft Server"
    },
    "whitelist": ["SylvanSerenity", "awesomeis9"],
    "ops": ["SylvanSerenity"],
    "banned_players": ["Notch"],
    "banned_ips": ["1.1.1.1"],
    "server_config": {
      "xms": "2G",
      "xmx": "8G",
      "stop": false
    }
  },
  "servers": [
    {
      "id": "vanilla",
      "version": "latest:release",
      "properties": {
        "level-seed": "12345",
        "server-port": "25565",
        "motd": "\u00a7bVanilla Minecraft Server"
      }
    },
    {
      "id": "snapshot",
      "version": "latest:snapshot",
      "properties": {
        "level-seed": "67890",
        "server-port": "25566",
        "motd": "\u00a7eSnapshot Minecraft Server"
      }
    },
    {
      "id": "legacy",
      "version": "1.6.4",
      "properties": {
        "level-seed": "ethoslab",
        "server-port": "25567"
      }
    },
    {
      "id": "modded",
      "version": "custom",
      "properties": {
        "level-seed": "toomanymods",
        "server-port": "25568"
      }
    }
  ]
}
```

## Server Manager

The `server_manager.sh` script is found in every server's installation directory. It opens a screen session and continues to restart the server until the `server.cfg` is updated with `stop=true`.

***Note:** This script is intended to run as a service on system boot. See [Server Manager Service](#server-manager-service) for more information.*

### Server Manager Configuration

The `server.cfg` file contains configuration for the actual server startup process, including memory settings and whether the server should be stopped. The settings are as follows:

* `xms`: The initial heap memory size (RAM) for the JVM running the server.

  Example:

  ```cfg
  xms=1024M
  ```

    ---

* `xmx`: The maximum heap memory size (RAM) for the JVM running the server.

  Example:

  ```cfg
  xmx=8G
  ```

    ---

* `stop`: Whether the `server_manager.sh` script should stop. If it is set to `false`, the script will start the server on boot and continue restarting the server until this value is updated.

  Example:

  ```cfg
  stop=false
  ```

### Server Manager Service

You can have your Minecraft servers start on boot by creating a service that runs the `server_manager.sh` script. Follow the below steps for each of your servers:

1. **Create the systemd service for all your servers:**

    ```sh
    sudo nano /etc/systemd/system/minecraft@.service
    ```

    ---

2. **Create a `minecraft` user (if not already done), and give it ownership of the `install_dir` that you set in the `servers.json` file:**

    ```sh
    sudo useradd -r -m -U -d /home/minecraft -s /bin/bash minecraft
    sudo chown -R minecraft:minecraft /home/minecraft
    ```

    ***Note:** Replace `/home/minecraft` with the `install_dir` you defined earlier in `servers.json`.*

    ---

3. **Paste the following into the service file:**

    ```ini
    [Unit]
    Description=Minecraft Server in %i
    After=network.target

    [Service]
    Type=simple
    User=minecraft
    WorkingDirectory=/home/minecraft/%i
    ExecStart=/home/minecraft/%i/server_manager.sh
    Restart=on-failure
    RestartSec=10
    StandardInput=tty

    [Install]
    WantedBy=multi-user.target
    ```

    ***Note:** Replace `/home/minecraft/` with the absolute path defined by your `install_dir`.*

    ---

4. **Enable the service on system boot and start it:**

    ```sh
    sudo systemctl daemon-reload
    sudo systemctl enable minecraft@my-server
    sudo systemctl start minecraft@my-server
    ```

    ***Note:** Replace `my-server` with the `id` of your server defined in `servers.json`. Do this step for each server you want to start on boot.*
