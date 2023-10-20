from bluepy.btle import Scanner, Peripheral, DefaultDelegate, ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC

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
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(f"Notification received from {cHandle}: {data}")
        
        try:
            # 提取第四個byte
            heartbeat_byte = data[3]
            
            # 將其從hex轉換為int
            heartbeat_value = int(heartbeat_byte)
            
            # 打印心跳的數值
            print(f"Heartbeat Value: {heartbeat_value}")
        except IndexError:
            print("Received data is incomplete or too long. Skipping this notification.")


def main():
    device_mac, addr_type = scan_for_devices()
    p = Peripheral(device_mac, addr_type)

    try:
        p.withDelegate(NotifyDelegate())
        
        # Find the characteristic to write to
        char_to_write = p.getCharacteristics(uuid="000033f1-0000-1000-8000-00805f9b34fb")[0]

        # Write the value 0xe511 to the characteristic
        char_to_write.write(bytes([0xe5, 0x11]))

        # Enable notifications for the other characteristic
        notify_char = p.getCharacteristics(uuid="000033f2-0000-1000-8000-00805f9b34fb")[0]
        notify_handle = notify_char.getHandle() + 1  # Usually the handle used for notifying is the characteristic handle + 1
        p.writeCharacteristic(notify_handle, (1).to_bytes(2, byteorder='little'))

        while True:
            if p.waitForNotifications(1.0):  # Wait for notification for 1 second
                continue  # Notification received, process it in the delegate
            print("Waiting for notification...")

    finally:
        p.disconnect()

if __name__ == "__main__":
    main()
