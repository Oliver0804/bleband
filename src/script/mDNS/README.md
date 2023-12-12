# Automatic mDNS Service Setup
This README outlines the steps to automatically run the SetupMDNSService on system startup.

## Quick Start
### Run the Service Setup Script:
To create and enable the SetupMDNSService, run the provided setup script:

```
sudo /path/to/create_mdns_service.sh
```
Replace /path/to/create_mdns_service.sh with the actual path of the service creation script.

### Reboot the System:
After running the setup script, reboot your system to apply the changes:

```
sudo reboot
```

## Service Execution:
Upon system reboot, SetupMDNSService will automatically run based on the configurations set by the script.

Additional Information
The service is designed to execute the setup_mDNS.sh script at system startup.
The service type is set to oneshot, meaning it runs once at startup and then stops.
Make sure the setup_mDNS.sh script has the necessary execute permissions.
For more detailed information, refer to the script documentation or system logs.
