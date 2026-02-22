"This file is executed when the package is imported (on PCB editor startup)"

from .snap_to_grid import SnapToGrid # Note the relative import!

SnapToGrid().register() # Instantiate and register to PCB editor
