# 使用方式
1. 透過腳本自動添加 Service 與 mDNS 服務
2. 配置src/config.json
3. 手動運行(第一次運行)
   
```sudo python3 main.py```

第一次運行會進行搜尋，並可以使用終端機添加設備。
選擇好後會自動更新config.json裝置名稱

4. config.json說明
```
{
    "bluetooth_devices": [  #可透過第一次搜尋藍牙設備進行修改
        {
            "name": "MK66(ID-1E35)",
            "MAC": "78:02:b7:dc:1e:35"
        }
    ],
    "mysql": {
        "IP": "bleband-1c-c3.local",    #mysql IP地址
        "PORT": "3306",                 #mysql Port
        "DB": "ble_devices",            #DB名稱
        "TABLES": "HeartbeatData",      #表單名稱
        "username": "root",             #帳號密碼
        "password": "password"
    },
    "bluetooth_settings": {
        "auto_connect": "y",            #自否開啟自動連線，如果需要重新搜尋手錶MAC則設為n，並進行手動運行，完成配置後可改為y（只支持小寫）
        "max_connection_limit": 1
    }
}
```

5. 匯入sql檔，檔案存放於src中，立面以包含sql內部表單結構
