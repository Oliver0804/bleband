from bluepy.btle import Scanner, Peripheral, DefaultDelegate, ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC
from bluepy.btle import BTLEDisconnectError

import threading
import select
import sys
import time
from bluepy import btle
import pymysql
import json

def get_config():
    with open('./src/config.json', 'r') as file:
        config = json.load(file)
    return config

def save_to_sql(mac_address, heartbeat):
    config = get_config()

    conn = pymysql.connect(
        host=config["mysql"]["IP"],
        port=int(config["mysql"]["PORT"]),
        user=config["mysql"]["username"],
        passwd=config["mysql"]["password"],
        db=config["mysql"]["DB"]
    )

    try:
        with conn.cursor() as cursor:
            sql = f"INSERT INTO {config['mysql']['TABLES']} (mac_address, heartbeat) VALUES (%s, %s)"
            cursor.execute(sql, (mac_address, heartbeat))
        conn.commit()
    finally:
        conn.close()

class BatteryDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(f"Battery Level: {ord(data)}%")

def scan_for_devices():
    while True:  # Infinite loop to allow re-scanning
        scanner = Scanner()
        scanner.scan(10.0)  # Scan for 10 seconds
        devices = list(scanner.getDevices())  # Convert devices to a list

        print("0. Rescan for devices.")
        for i, dev in enumerate(devices, start=1):  # start=1 makes the index start from 1
            print(f"{i}. Device {dev.addr} ({dev.addrType}, {dev.getValueText(9) or 'Unknown Name'}), RSSI={dev.rssi} dB")  # dev.getValueText(9) gets the device name
        
        print(f"{len(devices) + 1}. Exit.")

        while True:  # Inner loop to validate the user's input
            try:
                index = int(input("Select the device to connect to (by index) or other options above: "))
                if 0 <= index <= len(devices) + 1:
                    break  # Valid input, break out of the inner loop
                else:
                    print("Invalid choice. Please select a valid option.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        if index == 0:  # Rescan
            continue
        elif index == len(devices) + 1:  # Exit
            exit(0)
        else:
            return devices[index - 1].addr, devices[index - 1].addrType  # -1 because our device indexing starts from 1


def list_characteristics_for_service(peripheral, service_uuid):
    service = peripheral.getServiceByUUID(service_uuid)
    chars = service.getCharacteristics()
    
    print(f"Characteristics for Service UUID: {service_uuid}")
    for char in chars:
        print(f"  UUID: {char.uuid} - Properties: {char.propertiesToString()}")
        if "READ" in char.propertiesToString():
            try:
                value = char.read()
                print(f"    Value: {value}")
            except:
                print(f"    Value: Unable to read")

class NotifyDelegate(DefaultDelegate):
    def __init__(self, mac_address):
        DefaultDelegate.__init__(self)
        self.mac_address = mac_address

    def handleNotification(self, cHandle, data):
        print(f"Notification received from {cHandle}: {data}")
        
        if len(data) >= 4:
            try:
                heartbeat_byte = data[3]
                heartbeat_value = int(heartbeat_byte)
                print(f"Heartbeat Value: {heartbeat_value}")

                # 保存到SQL
                save_to_sql(self.mac_address, heartbeat_value)

            except IndexError:
                print("Received data is incomplete or too long. Skipping this notification.")
        else:
            print(f"Received data length {len(data)} is less than expected. Skipping this notification.")
'''
class NotifyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(f"Notification received from {cHandle}: {data}")
        
        if len(data) >= 4:
            try:
                # 提取第四個byte
                heartbeat_byte = data[3]
                
                # 將其從hex轉換為int
                heartbeat_value = int(heartbeat_byte)
                
                # 打印心跳的數值
                print(f"Heartbeat Value: {heartbeat_value}")
            except IndexError:
                print("Received data is incomplete or too long. Skipping this notification.")
        else:
            print(f"Received data length {len(data)} is less than expected. Skipping this notification.")

'''
def write_data_every_interval(p, interval=60):
    while not exit_flag.is_set():  # While the program should not exit
        char_to_write = p.getCharacteristics(uuid="000033f1-0000-1000-8000-00805f9b34fb")[0]
        char_to_write.write(bytes([0xe5, 0x11]), withResponse=True)
        time.sleep(interval)

def check_for_exit_key():
    while not exit_flag.is_set():  # While the program should not exit
        user_input = input()
        if user_input.lower() == 'q':
            exit_flag.set()  # Set the exit_flag to indicate the program should exit

def main():
    while True:
        device_mac, addr_type = scan_for_devices()

        p = Peripheral(device_mac, addr_type)
        try:
            p.withDelegate(NotifyDelegate(device_mac))

            last_write_time = 0

            # Enable notifications for the characteristic
            notify_char = p.getCharacteristics(uuid="000033f2-0000-1000-8000-00805f9b34fb")[0]
            notify_handle = notify_char.getHandle() + 1
            p.writeCharacteristic(notify_handle, (1).to_bytes(2, byteorder='little'))

            print("Press q to exit.")
            while True:
                current_time = time.time()
                if current_time - last_write_time >= 60:
                    char_to_write = p.getCharacteristics(uuid="000033f1-0000-1000-8000-00805f9b34fb")[0]
                    char_to_write.write(bytes([0xe5, 0x11]), withResponse=True)
                    last_write_time = current_time

                if p.waitForNotifications(1.0):
                    continue

                # Check for user input
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                if rlist:
                    user_input = sys.stdin.readline()
                    if user_input.lower().strip() == 'q':
                        p.disconnect()
                        return

        except BTLEDisconnectError:
            print("Device disconnected. Trying to reconnect...")
            p.disconnect()
            time.sleep(5)  # Wait for 5 seconds before trying to reconnect

        finally:
            p.disconnect()

if __name__ == "__main__":
    main()

