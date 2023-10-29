from bluepy.btle import Scanner, Peripheral, DefaultDelegate
from src.config import get_config
from src.database import save_to_sql
from datetime import datetime

from queue import Queue
import json
from bluepy.btle import Scanner
data_queue = Queue()

class BatteryDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(f"Battery Level: {ord(data)}%")

def save_device_info(name, mac):
    config_path = './src/config.json'
    with open(config_path, 'r') as file:
        config = json.load(file)
    
    # 檢查裝置是否已在列表中，檢查名稱和 MAC 地址
    if not any(device['name'] == name and device['MAC'] == mac for device in config['bluetooth_devices']):
        config['bluetooth_devices'].append({"name": name, "MAC": mac})
    
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"Device info saved: {name} - {mac}")
    else:
        print(f"Device info already exists: {name} - {mac}")


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




def scan_for_devices():
    while True:  # Infinite loop to allow re-scanning
        scanner = Scanner()
        scanner.scan(10.0)  # Scan for 10 seconds
        devices = list(scanner.getDevices())  # Convert devices to a list

        print("0. Rescan for devices.")
        for i, dev in enumerate(devices, start=1):  # start=1 makes the index start from 1
            print(f"{i}. Device {dev.addr} ({dev.addrType}, {dev.getValueText(9) or 'Unknown Name'}), RSSI={dev.rssi}")  # dev.getValueText(9) gets the device name
        
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
            selected_device = devices[index - 1]
            device_name = selected_device.getValueText(9) or 'Unknown Name'
            device_mac = selected_device.addr
            save_device_info(device_name, device_mac)  # Save device info
            print(f"Device info saved: {device_name} - {device_mac}")
            return device_mac, selected_device.addrType  # -1 because our device indexing starts from 1

def write_data_every_interval(p, interval=60):
    while not exit_flag.is_set():  # While the program should not exit
        char_to_write = p.getCharacteristics(uuid="000033f1-0000-1000-8000-00805f9b34fb")[0]
        char_to_write.write(bytes([0xe5, 0x11]), withResponse=True)
        time.sleep(interval)


class NotifyDelegate(DefaultDelegate):
    def __init__(self, mac_address):
        DefaultDelegate.__init__(self)
        self.mac_address = mac_address

    def handleNotification(self, cHandle, data):
        print(f"Notification received from {cHandle}: {data}")
        if (len(data)>2) and (len(data)<5) :
            try:
                heartbeat_byte = data[3]
                heartbeat_value = int(heartbeat_byte)

                # Get current time and print it along with Heartbeat Value
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"{current_time} - Heartbeat Value: {heartbeat_value}")

                # 调用 save_to_mysql 函数
                save_to_sql(self.mac_address, heartbeat_value)  # 替换为您的函数名和参数（如果有必要）

            except IndexError:
                print("Received data is incomplete or too long. Skipping this notification.")
        else:
            print ("Data len error.")
