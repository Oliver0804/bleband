import threading
import select
import sys
import time
import json
from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError
from src.bluetooth import scan_for_devices, NotifyDelegate
from src.database import init_db_connection

MAX_THREADS = 5  # Default value for maximum connection threads

def write_and_enable_notifications(p):
    char_to_write = p.getCharacteristics(uuid="000033f1-0000-1000-8000-00805f9b34fb")[0]
    char_to_write.write(bytes([0xe5, 0x11]), withResponse=True)
    # Enable notifications for the characteristic
    notify_char = p.getCharacteristics(uuid="000033f2-0000-1000-8000-00805f9b34fb")[0]
    notify_handle = notify_char.getHandle() + 1
    p.writeCharacteristic(notify_handle, (1).to_bytes(2, byteorder='little'))

def connect_device(device_mac, addr_type):
    p = Peripheral(device_mac, addr_type)
    try:
        p.withDelegate(NotifyDelegate(device_mac))
        last_write_time = 0
        write_and_enable_notifications(p)

        print("Press q to exit.")
        no_data_time = 0  # Reset the no data timer
        while True:
            if p.waitForNotifications(1.0):
                no_data_time = 0  # Reset the no data timer
                continue
            else:
                no_data_time += 1  # Increment the no data timer

            if no_data_time >= 5:
                write_and_enable_notifications(p)  # Call the function again if no data for 5 seconds
                no_data_time = 0  # Reset the no data timer

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

def auto_connect_from_config():
    global MAX_THREADS
    with open('./src/config.json', 'r') as file:
        config = json.load(file)
    auto_connect = config.get('bluetooth_settings', {}).get('auto_connect', 'n')
    max_connections = config.get('bluetooth_settings', {}).get('max_connection_limit', MAX_THREADS)
    devices = config.get('bluetooth_devices', [])

    if auto_connect.lower() == 'y':
        # Using multi-threading for multiple connections
        threads = []
        for i, device in enumerate(devices):
            if i >= max_connections:
                break
            t = threading.Thread(target=connect_device, args=(device['MAC'], "public"))  # Assuming addrType is "public" for all devices. Modify if needed.
            t.start()
            threads.append(t)

        # Waiting for all threads to finish
        for t in threads:
            t.join()
    else:
        # Old method for scanning and connecting
        while True:
            device_mac, addr_type = scan_for_devices()
            connect_device(device_mac, addr_type)

def main():
    init_db_connection()  # Initialize database connection
    threading.Thread(target=process_data).start()  # Start the data processing thread
    auto_connect_from_config()

if __name__ == "__main__":
    main()

