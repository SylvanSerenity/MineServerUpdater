# MineServerUpdater

MineServerUpdater is a Minecraft server manager and updater that allows you to specify global and server-specific configuration. You can specify server properties, whitelists, banned/op lists, and the target version (including keeping the latest server version).

## Install

1. Clone the repository:

    ```sh
    git clone https://github.com/SylvanSerenity/MineServerUpdater
    cd MineServerUpdater
    ```

2. Install dependencies (screen, python3, python3-venv, python3-pip):

    ```sh
    sudo apt install -y screen python3 python3-venv python3-pip
    ```

3. Activate the Python virtual environment:

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

4. Install Python requirements

    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Configure the `servers.json` file for your servers. See below for configuration specification.

2. Run the `update.py` script to install/update all servers to match your configuration specified in `servers.json`.

    ```sh
    python3 update.py
    ```

## Configuration

The `servers.json` configuration file for your servers is what defines how your servers behave whenever the `update.py` script is run. See below for how specification of each object.

### Top Level

* `install_dir`: Defines the directory, relative to the working directory, where the servers are installed and updated. Defaults to `./minecraft-servers`.

    Example:

    ```json
    {
      "install_dir": "/home/minecraft"
    }
    ```

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

  *Note: `default` does not take an `id` object.*

* `version`: The Minecraft version to use for this server. This can either be a specific version or snapshot (e.g. `1.6.4`), or one of the following:

  * `latest:release`: The latest full release version of Minecraft.

  * `latest:snapshot`: The latest snapshot version of Minecraft.

  * `custom`: Does not manage server jar file installation/updates at all. Use this for modded servers. You will need to manually download the server jar file.

  Example:

  ```json
  "version": "1.6.4"
  ```

* `eula`: Whether the EULA is accepted. Recommended to be set to `true` as a `default` configuration.

  Example:

  ```json
  "eula": true
  ```

  *Note: This is set to false by default to adhere to Minecraft's terms of service. You will have to manually edit this to true in your `servers.json` file.*

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

  *Note: See [`server.properties` keys](https://minecraft.fandom.com/wiki/Server.properties#Keys) for a list of accepted key/value pairs.*

* `whitelist`: The whitelist to apply to the server. It takes an array of usernames.

  Example:

  ```json
  "whitelist": ["YourUsername", "Notch"]
  ```

  *Note: You will also need to set the `white-list` server property to `true` for the whitelist to take effect.*

* `ops`: The operator list. This takes an array of usernames.

  Example:

  ```json
  "ops": ["YourUsername", "Notch"]
  ```

* `banned_players`: The banned players list. This takes an array of usernames.

  Example:

  ```json
  "banned_players": ["EvildoerUsername", "Notch"]
  ```

* `banned_ips`: The banned IPs list. This takes an array of IP addresses.

  Example:

  ```json
  "banned_ips": ["1.1.1.1", "8.8.8.8"]
  ```

### Example

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
    "banned_ips": ["1.1.1.1"]
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
