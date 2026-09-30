"A KiCAD action plugin to snap components to the grid"

import os

import pcbnew
import wx

from .grid import get_grid, read_grid_label

# Set True to pop up a dialog showing what the plugin parsed (grid, origin, first footprint)
DEBUG = False


def get_grid_origin(board):
    """Return the board's grid origin (x, y) in internal units, or (0, 0)."""
    ds = board.GetDesignSettings()
    try:
        o = ds.GetGridOrigin()
        return int(o.x), int(o.y)
    except Exception:
        pass
    try:
        o = ds.m_GridOrigin
        return int(o.x), int(o.y)
    except Exception:
        return 0, 0


class SnapToGrid(pcbnew.ActionPlugin):
    "main class of action plugin"

    def defaults(self):
        self.name = "Snap To Grid"
        self.category = "Layout Helper"
        self.description = "Snaps footprints to currently selected grid"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")

    @staticmethod
    def snap_axis(value, origin, grid):
        "snap value to the nearest grid line, where grid lines sit at origin + n*grid"
        offset = value - origin
        n = int(round(offset / float(grid)))
        return int(origin + n * grid)

    def Run(self):
        board = pcbnew.GetBoard()

        x_grid, y_grid = get_grid()
        if not x_grid or not y_grid:
            wx.MessageBox(
                f"Snap To Grid could not parse the current grid: {read_grid_label()!r}",
                "Snap To Grid",
            )
            return

        ox, oy = get_grid_origin(board)

        if DEBUG:
            wx.MessageBox(
                f"label: {read_grid_label()!r}\n"
                f"grid (nm): {x_grid} x {y_grid}\n"
                f"origin (nm): {ox}, {oy}",
                "Snap To Grid debug",
            )

        for footprint in board.GetFootprints():
            if footprint.IsSelected() and not footprint.IsLocked():
                pos = footprint.GetPosition()

                x = self.snap_axis(pos.x, ox, x_grid)
                y = self.snap_axis(pos.y, oy, y_grid)

                try:
                    footprint.SetPosition(pcbnew.VECTOR2I(x, y))
                except TypeError:
                    footprint.SetPosition(pcbnew.wxPoint(x, y))  # KiCad 6

        pcbnew.Refresh()
