import pynetbox # type: ignore
import urllib3
import pandas as pd # type: ignore

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pynetbox.api

nb_url = ""
nb_token = ""
csv = "./data-addr.csv"
chunk_size = 10

nb = pynetbox.api(nb_url, nb_token, threading=True)
nb.http_session.verify = False

csv_chunks = pd.read_csv(csv, chunksize=chunk_size)

counter = 0
success = 0


def process_chunk(chunk):
    global counter
    global success

    for _, row in chunk.iterrows():
        try:
            counter += 1

            queried_device = nb.dcim.devices.get(name=row["device"])
            if not queried_device:
                print(f"The device {row['device']} does not exist. Skipping.")
                continue

            queried_int = nb.dcim.interfaces.get(
                name=row["interface"], device=row["device"]
            )
            if not queried_int:
                print(
                    f"The device {row['device']}-{row['interface']} does not exist. Skipping."
                )
                continue

            if queried_device.primary_ip:
                if str(row["address"]) == str(queried_device.primary_ip):
                    print(
                        f"The IP address {row['address']} is already assigned as primary to the device {row['device']}. Skipping."
                    )
                    continue

            ip = nb.ipam.ip_addresses.create(
                address=row["address"],
                status=row["status"],
                assigned_object_type="dcim.interface",
                assigned_object_id=queried_int.id,
                is_primary=row["is_primary"],
            )
            queried_device.primary_ip4 = ip
            queried_device.primary_ip = ip
            queried_device.save()

            print(f"{counter}. Added address: {row['device']}-{row['address']}")

            success += 1
        except Exception as e:
            print(
                f"{counter}. Error adding address {row['device']}-{row['address']}: {e}"
            )


def main():
    global counter
    global success

    for chunk in pd.read_csv(csv, chunksize=chunk_size):
        process_chunk(chunk)
    print(f"Added {success}/{counter} node")


if __name__ == "__main__":
    main()
