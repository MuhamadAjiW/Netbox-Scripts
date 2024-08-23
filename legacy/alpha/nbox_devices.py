import pynetbox
import urllib3
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pynetbox.api

nb_url = ""
nb_token = ""
csv = "./data.csv"
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

            queried_device = nb.dcim.devices.get(name=row["name"])
            if queried_device and row["name"] and row["name"] != "-":
                print(f"The device {row['name']} already exists. Skipping.")
                continue

            queried_type = nb.dcim.device_types.get(model=row["device_type"])
            if isinstance(queried_type, type(None)):
                print(f"The type {row['device_type']} does not exist. Skipping.")
                continue

            queried_role = nb.dcim.device_roles.get(name=row["role"])
            if isinstance(queried_role, type(None)):
                print(f"The role {row['role']} does not exist. Skipping.")
                continue

            queried_manufacturer = nb.dcim.manufacturers.get(name=row["manufacturer"])
            if isinstance(queried_manufacturer, type(None)):
                print(
                    f"The manufacturer {row['manufacturer']} does not exist. Skipping."
                )
                continue

            queried_site = nb.dcim.sites.get(name=row["site"])
            if isinstance(queried_site, type(None)):
                print(f"The site {row['site']} does not exist. Skipping.")
                continue

            queried_location = nb.dcim.locations.get(name=row["location"])
            if isinstance(queried_location, type(None)):
                print(f"The location {row['location']} does not exist. Skipping.")
                continue

            queried_tags = nb.extras.tags.get(slug=row["tags"])
            if isinstance(queried_tags, type(None)):
                print(f"The tag {row['tags']} does not exist. Skipping.")
                continue

            if row["name"] != "-":
                nb.dcim.devices.create(
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
                nb.dcim.devices.create(
                    device_type=queried_type.id,
                    role=queried_role.id,
                    manufacturer=queried_manufacturer.id,
                    site=queried_site.id,
                    status=row["status"],
                    serial=row["serial"],
                    location=queried_location.id,
                    tags=[queried_tags.id],
                )

            print(f"{counter}. Added device: {row['name']}")

            success += 1
        except Exception as e:
            print(f"{counter}. Error adding device {row['name']}: {e}")


def main():
    global counter
    global success

    for chunk in pd.read_csv(csv, chunksize=chunk_size):
        chunk["name"] = chunk["name"].replace({None: "-"})
        chunk["serial"] = chunk["serial"].replace({None: "-"})
        process_chunk(chunk)
    print(f"Added {success}/{counter} node")

if __name__ == "__main__":
    main()