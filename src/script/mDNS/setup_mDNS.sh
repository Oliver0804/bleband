#!/bin/bash
sudo apt-get update
sudo apt-get install avahi-utils avahi-daemon -y
# Specify the network interface name, e.g., eth0, wlan0, etc.
NETWORK_INTERFACE="eth0"

echo "Fetching MAC address for interface: $NETWORK_INTERFACE"

# Retrieve the MAC address of the network card
MAC_ADDRESS=$(cat /sys/class/net/$NETWORK_INTERFACE/address)

echo "Current MAC address: $MAC_ADDRESS"

# Extract the last four characters from the MAC address (remove colons)
LAST_FOUR=$(echo $MAC_ADDRESS | sed 's/://g' | tail -c 5)

echo "Last four characters of MAC: $LAST_FOUR"

# Construct the new hostname
NEW_HOSTNAME="bleband-${LAST_FOUR:0:2}-${LAST_FOUR:2:2}.local"

# Output the new hostname for debugging
echo "New hostname will be set to: $NEW_HOSTNAME"

# (Optional) Set the new hostname
# Uncomment the following line to apply the new hostname
echo "Setting new hostname..."
sudo hostnamectl set-hostname $NEW_HOSTNAME

# (Optional) Restart the Avahi service
# Uncomment the following lines to restart Avahi
echo "Restarting Avahi service..."
sudo systemctl restart avahi-daemon


echo "you can use avahi-browse -at to check"
