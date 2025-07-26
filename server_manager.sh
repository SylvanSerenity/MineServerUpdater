#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PARENT_DIR=$(dirname "$SCRIPT_DIR")

SCREEN_NAME=$(basename "$PARENT_DIR")
JAR_FILE="$PARENT_DIR/server.jar"
CONFIG_FILE="$PARENT_DIR/server.cfg"

# Ensure config file exists
if [ ! -f "$CONFIG_FILE" ]; then
  cat > "$CONFIG_FILE" <<EOF
stop=false
xms=1G
xmx=2G
EOF
  echo "Created default $CONFIG_FILE"
fi

# Don't start if session already exists
if screen -list | grep -qw "\.${SCREEN_NAME}"; then
  echo "Screen session '$SCREEN_NAME' is already running."
  exit 0
fi

while true; do
  if grep -iq '^stop=true' "$CONFIG_FILE"; then
    echo 'Server is configured to stop. Exiting...'
    break
  fi

  SERVER_CMD=$(grep -i '^args=' "$CONFIG_FILE" | cut -d'=' -f2 | cut -d'#' -f1)

  echo "$(date): Starting Minecraft server with \"$SERVER_ARGS\"..."
  java -jar "$JAR_FILE" $SERVER_ARGS nogui

  echo "$(date): Server stopped. Restarting in 5 seconds..."
  sleep 5
done
