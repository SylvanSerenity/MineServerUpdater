#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
JAR_FILE="$SCRIPT_DIR/server.jar"
CONFIG_FILE="$SCRIPT_DIR/server.cfg"

# Ensure config file exists
if [ ! -f "$CONFIG_FILE" ]; then
  cat > "$CONFIG_FILE" <<EOF
stop=false
args=-Xms1G -Xmx6G
EOF
  echo "Created default $CONFIG_FILE"
fi

if grep -iq '^stop=true' "$CONFIG_FILE"; then
  echo 'Server is configured to stop. Exiting...'
  break
fi

JVM_ARGS=$(grep -i '^args=' "$CONFIG_FILE" | cut -d'=' -f2 | cut -d'#' -f1)

echo "$(date): Starting Minecraft server in $SCRIPT_DIR with \"$JVM_ARGS\"..."
java $JVM_ARGS -jar "$JAR_FILE" nogui
