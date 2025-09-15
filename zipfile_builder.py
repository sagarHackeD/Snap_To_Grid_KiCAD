import zipfile
import os
from datetime import datetime

FIXED_DATE = (1980, 1, 1, 0, 0, 0)  # ISO 21320-1 friendly earliest ZIP timestamp

def create_reproducible_iso21320_zip(zip_name, files, compression=zipfile.ZIP_DEFLATED):
    """
    Create an ISO/IEC 21320-1 compliant & reproducible ZIP archive.
    
    Args:
        zip_name (str): Output ZIP filename.
        files (list of str): List of file paths to include.
        compression: zipfile.ZIP_DEFLATED (default) or zipfile.ZIP_STORED
    """
    # Ensure deterministic order
    files = sorted(files)

    with zipfile.ZipFile(zip_name, "w", compression=compression, allowZip64=True) as zf:
        for f in files:
            arcname = os.path.basename(f)  # clean archive name
            data = open(f, "rb").read()

            # Create ZipInfo manually for reproducibility
            info = zipfile.ZipInfo(filename=arcname, date_time=FIXED_DATE)
            info.compress_type = compression
            info.external_attr = 0  # avoid OS-specific file permissions

            # Write file with fixed metadata
            zf.writestr(info, data)




# Example usage
files_to_zip = [
    "build/plugin/__init__.py",
    "build/plugin/icon.png",
    "build/plugin/snap_to_grid.py",
    "build/metadata.json",
]
create_reproducible_iso21320_zip("output21320.zip", files_to_zip)

