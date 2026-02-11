"A KiCAD action plugin to snap components to the grid"

import os

import pcbnew

from .grid import get_grid


class SnapToGrid(pcbnew.ActionPlugin):
    "main class of action plugin"

    def defaults(self):
        self.name = "Snap To Grid"
        self.category = "Layout Helper"
        self.description = "Snaps footprints to currently selected grid"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")

    def round_off(self, value, grid):
        "function to round off value to nearest grid"
        if value < 0:
            return int((value - (grid / 2)) / grid) * grid
        return int((value + (grid / 2)) / grid) * grid

    def Run(self):
        # print("Sagar Naik - Snap to grid")

        board = pcbnew.GetBoard()

        x_grid, y_grid = get_grid()

        for footprint in board.GetFootprints():
            if footprint.IsSelected() and not footprint.IsLocked():
                pos = footprint.GetPosition()

                x = self.round_off(pos[0], x_grid)
                y = self.round_off(pos[1], y_grid)

                # x = round(pos[0],grid) #there is something wrong with python round funtion
                # so i roled back to previous metohd on 28/09/2020
                # y = round(pos[1],grid)
                try:
                    footprint.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
                except TypeError:
                    footprint.SetPosition(pcbnew.wxPoint(int(x), int(y)))  # for KiCad 6
