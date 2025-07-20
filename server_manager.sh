#!/bin/bash

# Get the name of the current directory for the screen session
SCREEN_NAME=$(basename "$PWD")
JAR_FILE="server.jar"
CONFIG_FILE="server.cfg"

# Ensure config file exists
if [ ! -f "$CONFIG_FILE" ]; then
  cat > "$CONFIG_FILE" <<EOF
stop=false
xms=1G
xmx=2G
EOF
  echo "Created default $CONFIG_FILE"
fi

# Extract config values
STOP=$(grep -i '^stop=' "$CONFIG_FILE" | cut -d'=' -f2 | cut -d'#' -f1 | tr -d '[:space:]')
XMS=$(grep -i '^xms=' "$CONFIG_FILE" | cut -d'=' -f2 | cut -d'#' -f1 | tr -d '[:space:]')
XMX=$(grep -i '^xmx=' "$CONFIG_FILE" | cut -d'=' -f2 | cut -d'#' -f1 | tr -d '[:space:]')

# Validate required values
if [ -z "$XMS" ] || [ -z "$XMX" ]; then
  echo "Error: xms or xmx not set in $CONFIG_FILE"
  exit 1
fi

# If screen session is already running, do not start another
if screen -list | grep -q "\.${SCREEN_NAME}"; then
  echo "Screen session '$SCREEN_NAME' is already running."
  exit 0
fi

# Don't start if session already exists
if screen -list | grep -q "\.${SCREEN_NAME}"; then
  echo "Screen session '$SCREEN_NAME' is already running."
  exit 0
fi

# Launch the server in a screen loop
screen -S "$SCREEN_NAME" bash -c "
while true; do
  if grep -iq '^stop=true' \"$CONFIG_FILE\"; then
    echo 'Server is configured to stop. Exiting...'
    break
  fi
  echo 'Starting Minecraft server with Xms=$XMS, Xmx=$XMX...'
  java -Xms$XMS -Xmx$XMX -jar \"$JAR_FILE\" nogui
  echo \"\$(date): Server stopped. Restarting in 5 seconds...\"
  sleep 5
done
"
