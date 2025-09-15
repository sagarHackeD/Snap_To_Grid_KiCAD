import shutil
import os
from PIL import Image
import hashlib
import zipfile
import sys
import json


def resize_image(input_path, size, output_path):
    # Open the image
    img = Image.open(input_path)

    # Resize the image
    img_resized = img.resize(size, Image.LANCZOS)

    # Save the resized image
    img_resized.save(output_path)
    print(f"Image saved to {output_path}")


shutil.rmtree("build", ignore_errors=True)

os.mkdir("build")
os.mkdir("build/resources")
os.mkdir("build/plugin")

# ffmpeg.exe -i icon.jpg -vf scale=320:240 build/resources/icon.png
# ffmpeg -i icon.jpg -vf scale=320:240 build/plugin/icon.png

# Example usage:
resize_image("icon.png", (64, 64), "build/resources/icon.png")
resize_image("icon.png", (24, 24), "build/plugin/icon.png")


shutil.copy("__init__.py", "build/plugin/__init__.py")
shutil.copy("snap_to_grid.py", "build/plugin/snap_to_grid.py")
shutil.copy("metadata.json", "build/metadata.json")


shutil.make_archive("snap_to_grid", "zip", "build")


# zip = zipfile.ZipFile("build", "w", compression=zipfile.ZIP_DEFLATED)


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


zip_file = "snap_to_grid.zip"
if not os.path.isfile(zip_file):
    print(f"Error: {zip_file} not found!")
    sys.exit(1)
print("download_sha256:", sha256sum(zip_file))
print("download_size:", file_size_bytes(zip_file))
print("install_size:", install_size_bytes(zip_file))


with open("metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)
    version = metadata["versions"][0]
    version["download_sha256"] = sha256sum(zip_file)
    version["download_size"] = file_size_bytes(zip_file)
    version["install_size"] = install_size_bytes(zip_file)

with open("metadata_submit.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)
    f.write("\n")
print("Updated metadata.json with new checksum and sizes.")


import hashlib

READ_SIZE = 65536


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

print(get_package_metadata("snap_to_grid.zip"))