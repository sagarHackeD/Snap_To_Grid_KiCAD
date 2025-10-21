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
    os.mkdir("build/plugins")


def copy_icons_to_build_dir():
    resize_image("icon.png", (64, 64), "build/resources/icon.png")
    resize_image("icon.png", (24, 24), "build/plugins/icon.png")


def copy_files_to_build_dir():
    shutil.copy("__init__.py", "build/plugins")
    shutil.copy("snap_to_grid.py", "build/plugins")
    shutil.copy("metadata.json", "build")


def build_plugin_zip(zip_filename):
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
    copy_files_to_build_dir()
    copy_icons_to_build_dir()
    build_plugin_zip("kicad-package.zip")
    generate_metadata("kicad-package-metadata.json", "kicad-package.zip")
    remove_build_dir()
