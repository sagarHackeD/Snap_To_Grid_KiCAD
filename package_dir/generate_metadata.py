import hashlib
import json
import os
import zipfile

READ_SIZE = 65536


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


def generate_metadata(
    input_metadata_file, output_metadata_file, zip_filename, zip_file_url
):
    with open(input_metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        version = metadata["versions"][0]
        package_metadata = get_package_metadata(zip_filename)
        package_metadata["download_url"] = zip_file_url
        version.update(package_metadata)

    with open(output_metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        f.write("\n")
    print(f"Generated {output_metadata_file} with updated metadata.")


if __name__ == "__main__":
    zip_file_url = "https://github.com/sagarHackeD/Snap_To_Grid_KiCAD/releases/download/v1.0.0/kicad-package.zip"

    curll_command = (
        f'curl -L -o "package_dir/Downloaded-kicad-package.zip" "{zip_file_url}"'
    )
    print(f"Downloading package with command:\n{curll_command}")

    os.system(curll_command)

    generate_metadata(
        "build/metadata.json",
        "package_dir/metadata.json",
        "package_dir/Downloaded-kicad-package.zip",
        zip_file_url,
    )
