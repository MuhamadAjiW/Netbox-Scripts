import pynetbox
import urllib3
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NetboxManager:
    """
    Manages the creation and update of data in NetBox,
    1. the fiture that have been used and tested are devices, interfaces, and IP addresses in Netbox.
    """

    def __init__(self, nb_url, nb_token, chunk_size=10):
        self._nb = pynetbox.api(nb_url, nb_token, threading=True)
        self._nb.http_session.verify = False
        self.chunk_size = chunk_size
        self._counter = 0
        self._success = 0

    def process_devices(self, csv_file):
        """
        Processes devices from a CSV file and creates them in Netbox.
        """
        csv_chunks = pd.read_csv(csv_file, chunksize=self.chunk_size)
        for chunk in csv_chunks:
            chunk["name"] = chunk["name"].replace({None: "-"})
            chunk["serial"] = chunk["serial"].replace({None: "-"})
            self._process_chunk_device(chunk)
        print(f"Added {self._success}/{self._counter} devices")

    def process_interfaces(self, csv_file):
        """
        Processes interfaces from a CSV file and creates them in Netbox.
        """
        csv_chunks = pd.read_csv(csv_file, chunksize=self.chunk_size)
        for chunk in csv_chunks:
            self._process_chunk_interface(chunk)
        print(f"Added {self._success}/{self._counter} interfaces")

    def process_ip_addresses(self, csv_file):
        """
        Processes IP addresses from a CSV file and creates them in Netbox.
        """
        csv_chunks = pd.read_csv(csv_file, chunksize=self.chunk_size)
        for chunk in csv_chunks:
            self._process_ip_chunk_address(chunk)
        print(f"Added {self._success}/{self._counter} IP addresses")

    def _process_chunk_device(self, chunk):
        for _, row in chunk.iterrows():
            try:
                self._counter += 1
                self._create_device(row)
            except Exception as e:
                print(f"{self._counter}. Error adding device {row['name']}: {e}")

    def _process_chunk_interface(self, chunk):
        for _, row in chunk.iterrows():
            try:
                self._counter += 1
                self._create_interface(row)
            except Exception as e:
                print(
                    f"{self._counter}. Error adding interface {row['device']}-{row['name']}: {e}"
                )

    def _process_ip_chunk_address(self, chunk):
        for _, row in chunk.iterrows():
            try:
                self._counter += 1
                self._create_ip_address(row)
            except Exception as e:
                print(
                    f"{self._counter}. Error adding address {row['device']}-{row['address']}: {e}"
                )

    def _create_device(self, row):
        queried_device = self._nb.dcim.devices.get(name=row["name"])
        if queried_device and row["name"] and row["name"] != "-":
            print(f"The device {row['name']} already exists. Skipping.")
            return

        queried_type = self._nb.dcim.device_types.get(model="device_type")
        queried_role = self._nb.dcim.device_roles.get(name="role")
        queried_manufacturer = self._nb.dcim.manufacturers.get(name="manufacturer")
        queried_site = self._nb.dcim.sites.get(name="site")
        queried_location = self._nb.dcim.locations.get(name="location")
        queried_tags = self._nb.extras.tags.get(slug="tags")

        if row["name"] != "-":
            self._nb.dcim.devices.create(
                name=row["name"],
                device_type=queried_type.id,
                role=queried_role.id,
                manufacturer=queried_manufacturer.id,
                site=queried_site.id,
                status=row["status"],
                serial=row["serial"],
                location=queried_location.id,
                tags=[queried_tags.id],
            )
        else:
            self._nb.dcim.devices.create(
                device_type=queried_type.id,
                role=queried_role.id,
                manufacturer=queried_manufacturer.id,
                site=queried_site.id,
                status=row["status"],
                serial=row["serial"],
                location=queried_location.id,
                tags=[queried_tags.id],
            )

        print(f"{self._counter}. Added device: {row['name']}")
        self._success += 1

    def _create_interface(self, row):
        queried_device = self._nb.dcim.devices.get(name=row["device"])
        if not queried_device:
            print(f"The device {row['device']} does not exist. Skipping.")
            return

        queried_int = self._nb.dcim.interfaces.get(
            name=row["name"], device=row["device"]
        )
        if queried_int:
            print(f"The device {row['device']}-{row['name']} already exists. Skipping.")
            return

        self._nb.dcim.interfaces.create(
            device=queried_device.id,
            name=row["name"],
            type=row["type"],
        )

        print(f"{self._counter}. Added interface: {row['device']}-{row['name']}")
        self._success += 1

    def _create_ip_address(self, row):
        queried_device = self._nb.dcim.devices.get(name=row["device"])
        if not queried_device:
            print(f"The device {row['device']} does not exist. Skipping.")
            return

        queried_int = self._nb.dcim.interfaces.get(
            name=row["interface"], device=row["device"]
        )
        if not queried_int:
            print(
                f"The device {row['device']}-{row['interface']} does not exist. Skipping."
            )
            return

        if queried_device.primary_ip:
            if str(row["address"]) == str(queried_device.primary_ip):
                print(
                    f"The IP address {row['address']} is already assigned as primary to the device {row['device']}. Skipping."
                )
                return

        ip = self._nb.ipam.ip_addresses.create(
            address=row["address"],
            status=row["status"],
            assigned_object_type="dcim.interface",
            assigned_object_id=queried_int.id,
            is_primary=row["is_primary"],
        )
        queried_device.primary_ip4 = ip
        queried_device.primary_ip = ip
        queried_device.save()

        print(f"{self._counter}. Added address: {row['device']}-{row['address']}")
        self._success += 1


def main():
    nb_manager = NetboxManager(
        nb_url="https://10.10.14.52",
        nb_token="5dfea48baa5491b52a9c601fd0a6e115a5523f54",
    )
    nb_manager.process_devices("./data.csv")


if __name__ == "__main__":
    main()
