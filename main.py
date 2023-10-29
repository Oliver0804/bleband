import threading
import select
import sys
import time
import json
from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError
from src.bluetooth import scan_for_devices, NotifyDelegate
from src.process_data import process_data
from src.database import init_db_connection

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
        write_and_enable_notifications(p)

        no_data_time = 0
        while True:
            if p.waitForNotifications(1.0):
                no_data_time = 0
            else:
                no_data_time += 1

            if no_data_time >= 5:
                write_and_enable_notifications(p)
                no_data_time = 0

            time.sleep(0.5)  # To avoid high CPU usage

    except BTLEDisconnectError:
        print(f"Device {device_mac} disconnected. Trying to reconnect...")
        p.disconnect()
        time.sleep(5)
    finally:
        p.disconnect()

def main():
    init_db_connection()  # Initialize database connection
    threading.Thread(target=process_data).start()  # Start the data processing thread
    
    with open('./src/config.json', 'r') as file:
        config = json.load(file)
        auto_connect = config.get('bluetooth_settings', {}).get('auto_connect', 'n')
    print (auto_connect)
    while auto_connect=='n':
        device_mac, addr_type = scan_for_devices()
        p = Peripheral(device_mac, addr_type)
        try:
            p.withDelegate(NotifyDelegate(device_mac))
            last_write_time = 0
            write_and_enable_notifications(p)  # Call the new function here

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
    while auto_connect == 'y':
        max_connection_limit = config.get('bluetooth_settings', {}).get('max_connection_limit', 5)
        devices = config.get('bluetooth_devices', [])
        d,a=scan_for_devices() 
        threads = []
        for device in devices:
            if len(threads) < max_connection_limit:
                device_mac = device['MAC']
                t = threading.Thread(target=connect_device, args=(device_mac, "public"))  # assuming addr_type is "random"
                t.start()
                threads.append(t)
                
                # Allow some time for connection establishment before starting the next thread
                time.sleep(1)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()

        time.sleep(5)  # Wait for some time before checking auto_connect again
 
if __name__ == "__main__":
    main()

