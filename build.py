import hashlib
import json
import os
import shutil
import zipfile

from PIL import Image

READ_SIZE = 65536


def resize_image(input_path, size, output_path):
    img = Image.open(input_path)
    img_resized = img.resize(size, Image.LANCZOS)
    img_resized.save(output_path)


def sha256sum(filename):
    h = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def file_size_bytes(filename):
    return os.path.getsize(filename)


def install_size_bytes(zip_filename):
    total = 0
    with zipfile.ZipFile(zip_filename, "r") as zipf:
        for info in zipf.infolist():
            # Only files, not directories
            if not info.is_dir():
                total += info.file_size
    return total


def getsha256(filename) -> str:
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        while data := f.read(READ_SIZE):
            sha256.update(data)
    return sha256.hexdigest()


def get_package_metadata(filename):
    z = zipfile.ZipFile(filename, "r")
    install_size = sum(entry.file_size for entry in z.infolist() if not entry.is_dir())
    return {
        "download_sha256": getsha256(filename),
        "download_size": os.path.getsize(filename),
        "install_size": install_size,
    }

def remove_build_dir():
    shutil.rmtree("build", ignore_errors=True)

def create_build_dir():
    os.mkdir("build")
    os.mkdir("build/resources")
    os.mkdir("build/plugin")
    resize_image("src/icon.png", (64, 64), "build/resources/icon.png")
    resize_image("src/icon.png", (24, 24), "build/plugin/icon.png")
    shutil.copy("src/__init__.py", "build/plugin/__init__.py")
    shutil.copy("src/snap_to_grid.py", "build/plugin/snap_to_grid.py")
    shutil.copy("src/metadata.json", "build/metadata.json")


def build_plugin_zip(zip_filename):
    # zip = zipfile.ZipFile("build", "w", compression=zipfile.ZIP_DEFLATED)

    shutil.make_archive(zip_filename.replace(".zip", ""), "zip", "build")

    print(f"Created {zip_filename}")


def generate_metadata(output_metadata_file, zip_filename):
    with open("build/metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
        version = metadata["versions"][0]
        package_metadata = get_package_metadata(zip_filename)
        version.update(package_metadata)

    with open(output_metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        f.write("\n")
    print(f"Generated {output_metadata_file} with updated metadata.")


if __name__ == "__main__":
    remove_build_dir()
    create_build_dir()
    # build_plugin_zip("snap_to_grid.zip")
    # generate_metadata("metadata_submit.json", "snap_to_grid.zip")
    print("Done.")


# zip_file = "snap_to_grid.zip"
# if not os.path.isfile(zip_file):
#     print(f"Error: {zip_file} not found!")
#     sys.exit(1)
# print("download_sha256:", sha256sum(zip_file))
# print("download_size:", file_size_bytes(zip_file))
# print("install_size:", install_size_bytes(zip_file))


# with open("metadata.json", "r", encoding="utf-8") as f:
#     metadata = json.load(f)
#     version = metadata["versions"][0]
#     version["download_sha256"] = sha256sum(zip_file)
#     version["download_size"] = file_size_bytes(zip_file)
#     version["install_size"] = install_size_bytes(zip_file)

# with open("metadata_submit.json", "w", encoding="utf-8") as f:
#     json.dump(metadata, f, indent=4)
#     f.write("\n")
# print("Updated metadata.json with new checksum and sizes.")
