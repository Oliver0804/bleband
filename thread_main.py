from bluepy.btle import Scanner, Peripheral, DefaultDelegate, ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC
import atexit
import signal
import threading

current_peripheral = None
lock = threading.Lock()

def disconnect_ble(p):
    if p:
        try:
            p.disconnect()
        except:
            pass  # Ignore any exception during disconnection

class NotifyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(f"Notification received from {cHandle}: {data}")
        try:
            heartbeat_byte = data[3]
            heartbeat_value = int(heartbeat_byte)
            print(f"Heartbeat Value: {heartbeat_value}")
        except IndexError:
            print("Received data is incomplete or too long. Skipping this notification.")

def scan_for_devices():
    while True:
        scanner = Scanner()
        scanner.scan(10.0)
        devices = list(scanner.getDevices())
        print("0. Rescan for devices.")
        for i, dev in enumerate(devices, start=1):
            print(f"{i}. Device {dev.addr} ({dev.addrType}, {dev.getValueText(9) or 'Unknown Name'}), RSSI={dev.rssi} dB")

        print(f"{len(devices) + 1}. Exit.")
        while True:
            try:
                index = int(input("Select the device to connect to (by index) or other options above: "))
                if 0 <= index <= len(devices) + 1:
                    break
                else:
                    print("Invalid choice. Please select a valid option.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        if index == 0:
            continue
        elif index == len(devices) + 1:
            exit(0)
        else:
            return devices[index - 1].addr, devices[index - 1].addrType

def scan_loop():
    global current_peripheral
    while True:
        device_mac, addr_type = scan_for_devices()
        with lock:
            if not current_peripheral:
                current_peripheral = Peripheral(device_mac, addr_type)
                setup_peripheral(current_peripheral)

def setup_peripheral(p):
    try:
        p.withDelegate(NotifyDelegate())
        char_to_write = p.getCharacteristics(uuid="000033f1-0000-1000-8000-00805f9b34fb")[0]
        char_to_write.write(bytes([0xe5, 0x11]))
        notify_char = p.getCharacteristics(uuid="000033f2-0000-1000-8000-00805f9b34fb")[0]
        notify_handle = notify_char.getHandle() + 1
        p.writeCharacteristic(notify_handle, (1).to_bytes(2, byteorder='little'))
    except:
        print("Error setting up the peripheral.")
        disconnect_ble(p)
        with lock:
            global current_peripheral
            current_peripheral = None

def main():
    global current_peripheral

    # Moving the signal registration to the main thread
    atexit.register(disconnect_ble, current_peripheral)
    signal.signal(signal.SIGTERM, lambda signum, frame: disconnect_ble(current_peripheral))
    signal.signal(signal.SIGINT, lambda signum, frame: disconnect_ble(current_peripheral))

    scan_thread = threading.Thread(target=scan_loop)
    scan_thread.start()
    while True:
        with lock:
            if current_peripheral:
                if current_peripheral.waitForNotifications(1.0):
                    continue
                print("Waiting for notification...")

if __name__ == "__main__":
    main()
