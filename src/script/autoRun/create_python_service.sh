#!/bin/bash

# 服務名稱
SERVICE_NAME="PythonAppService"

# 創建一個新的 systemd 服務文件
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.service <<EOF
[Unit]
Description=Python Application Service

[Service]
WorkingDirectory=/home/rock/bletools
ExecStart=/usr/bin/python3 /home/rock/bletools/main.py
Restart=always
User=root
Group=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF"

# 重新加載 systemd 以應用新的服務
sudo systemctl daemon-reload

# 啟用服務
sudo systemctl enable $SERVICE_NAME.service

# （可選）立即啟動服務
# sudo systemctl start $SERVICE_NAME.service

echo "$SERVICE_NAME has been created and enabled."

