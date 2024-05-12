#!/bin/bash
# Exit immediately if a command returns a non-zero exit code
set -e
# Check if the script is being run as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi
# Start the makeconfig, unless service is running
if ! systemctl is-active --quiet templogger.service; then
  # Start the other makeconfig.sh in the foreground
  python3 makeconfig.py
  # Store the PID of the makeconfig.sh
  OTHER_SCRIPT_PID=$! 
fi
# Check if the required packages are already installed
REQUIRED_PACKAGES=`grep -E "^[^#]" requirements.txt`
INSTALLED_PACKAGES=`pip freeze`
# Install any missing packages
for package in $REQUIRED_PACKAGES; do
  if ! echo "$INSTALLED_PACKAGES" | grep -q "$package"; then
    pip install "$package"
  fi
done
# Copy the service file and enable it
cp templogger.service /lib/systemd/system/
chmod 644 /lib/systemd/system/templogger.service
# Replace the working directory placeholder in the service file with the current working directory
sed -i "s#{CWD}#$(pwd)#" /lib/systemd/system/templogger.service
systemctl daemon-reload
systemctl enable templogger.service
# Start the service, unless it's already running
if ! systemctl is-active --quiet templogger.service; then
  # Wait for the other script to finish
  wait $OTHER_SCRIPT_PID
  systemctl start templogger.service
fi
# Reload the bashrc file to apply the changes
source ~/.bashrc
