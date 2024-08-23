import pynetbox
import urllib3
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pynetbox.api

nb_url = ""
nb_token = ""
csv = "./data-int.csv"
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

            queried_int = nb.dcim.interfaces.get(name=row["name"], device=row["device"])
            if queried_int:
                print(
                    f"The device {row['device']}-{row['name']} already exists. Skipping."
                )
                continue

            nb.dcim.interfaces.create(
                device=queried_device.id,
                name=row["name"],
                type=row["type"],
            )

            print(f"{counter}. Added interface: {row['device']}-{row['name']}")

            success += 1
        except Exception as e:
            print(
                f"{counter}. Error adding interface {row['device']}-{row['name']}: {e}"
            )


def main():
    global counter
    global success

    for chunk in pd.read_csv(csv, chunksize=chunk_size):
        process_chunk(chunk)
    print(f"Added {success}/{counter} node")


if __name__ == "__main__":
    main()
