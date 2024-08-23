import sys
import argparse

from lib.NetBoxManager import NetboxManager
from config import Config

def main():
    parser = argparse.ArgumentParser(description="Process Netbox data")
    choice: list = [
        'devices',
        'interfaces',
        'ip-address',
    ]
    
    
    parser.add_argument('action', choices=choice, help='Action to perform: device, interfaces, or ip')
    parser.add_argument('-f', '--file', help='Path to the CSV file', required=True)
    args = parser.parse_args()

    nb_manager = NetboxManager(
        nb_url=Config.NetBox.URL,
        nb_token=Config.NetBox.TOKEN
    )

    if args.action == 'devices':
        nb_manager.process_devices(args.file)
    elif args.action == 'interfaces':
        nb_manager.process_interfaces(args.file)
    elif args.action == 'ip':
        nb_manager.process_ip_addresses(args.file)

if __name__ == "__main__":
    main()