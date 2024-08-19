import os

DEVICES_DEVICES = "nbox_devices.py"

DEVICES_INTERFACES = "nbox_interfaces.py"

DEVICES_IP_ADDR = "nbox_ip_addresses.py"

os.system(f"python {DEVICES_DEVICES}")
os.system(f"python {DEVICES_INTERFACES}")
os.system(f"python {DEVICES_IP_ADDR}")