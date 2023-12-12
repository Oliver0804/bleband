#!/bin/bash

# Service name
SERVICE_NAME="SetupMDNSService"

# Create a new systemd service file
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.service <<EOF
[Unit]
Description=Setup mDNS Service at Startup

[Service]
Type=oneshot
ExecStart=/home/rock/bletools/src/script/mDNS/setup_mDNS.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF"

# Reload systemd to apply the new service
sudo systemctl daemon-reload

# Enable the service
sudo systemctl enable $SERVICE_NAME.service

# (Optional) Start the service immediately
# sudo systemctl start $SERVICE_NAME.service

echo "$SERVICE_NAME has been created and enabled."


echo "you can use sudo journalctl -xe"

