from bluepy.btle import Scanner, Peripheral, DefaultDelegate, ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC
from time import sleep
class BatteryDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(f"Battery Level: {ord(data)}%")



def list_characteristics_for_service(peripheral, service_uuid):
    service = peripheral.getServiceByUUID(service_uuid)
    chars = service.getCharacteristics()
    
    print(f"\nCharacteristics for Service UUID: {service_uuid}")
    for char in chars:
        print(f"  UUID: {char.uuid} - Properties: {char.propertiesToString()}")
        if "READ" in char.propertiesToString():
            try:
                value = char.read()
                print(f"    Value: {value}")
            except:
                print(f"    Value: Unable to read")

from bluepy.btle import Scanner, Peripheral

def scan_for_devices():
    scanner = Scanner()
    devices_list = scanner.scan(10.0)
    
    devices = list(devices_list)  # Ensure devices is a list

    print("Detected devices:")
    for i, dev in enumerate(devices):
        device_name = dev.getValueText(9) or "None"
        print(f"{i+1}. Device {dev.addr} ({dev.addrType}) - {device_name} RSSI={dev.rssi} dB")

    index = int(input("Select the device to connect to (by index): "))
    return devices[index-1].addr, devices[index-1].addrType

def main():
    device_mac, addr_type = scan_for_devices()
    device = Peripheral(device_mac, addr_type)
    
    while True :
        # Find the desired service
        service_uuid = "000055ff-0000-1000-8000-00805f9b34fb"
        char_uuid = "000033f1-0000-1000-8000-00805f9b34fb"
        service = device.getServiceByUUID(service_uuid)
    
        # Get the desired characteristic
        char = service.getCharacteristics(char_uuid)[0]
        print(char) 
        # Write the desired data to the characteristic
        char.write(bytes([0xe5, 0x11]))
        print(bytes([0xe5,0x11]))
        print("send e511")
        sleep(1);
    
    device.disconnect()

if __name__ == "__main__":
    main()

