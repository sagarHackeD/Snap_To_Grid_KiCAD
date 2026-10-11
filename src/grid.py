"""funtions to get grid information from the current selection in KiCad"""

import re

import pcbnew
import wx


def clean_entry(grid_string: str) -> str:
    grid_string = grid_string.strip()

    grid_string = grid_string.replace(",", ".")  # Handle comma as decimal separator

    # remove any leading label like "Anything: " and "Grid: " for kicad 6 and user defined grid
    if ":" in grid_string:
        grid_string = grid_string.split(":", 1)[1].strip()

    return grid_string


def grid_to_iu(value, unit):
    if not value:
        return None

    if unit == "mm":
        return pcbnew.FromMM(float(value))
    elif unit == "mils":
        return pcbnew.FromMils(float(value))
    elif unit == "in":
        return pcbnew.FromMM(float(value) * 25.4)
    return None


def parse_grid(grid_selection):
    grid_selection = clean_entry(grid_selection)
    if not grid_selection:
        return None

    # rectangular grid
    rect_grid = re.search(
        r"([\d.]+)\s*(mm|in|mils?)\s*x\s*([\d.]+)\s*(mm|in|mils?)", grid_selection
    )
    if rect_grid:
        x_grid, x_unit, y_grid, y_unit = rect_grid.groups()

        x_grid = grid_to_iu(x_grid, x_unit)
        y_grid = grid_to_iu(y_grid, y_unit)

        return {
            "type": "rectangular",
            "x_iu": x_grid,
            "y_iu": y_grid,
            "raw": grid_selection,
        }

    # square grid
    square_grid = re.search(r"([\d.]+)\s*(mm|in|mils?)", grid_selection)
    if square_grid:
        xy_grid, xy_unit = square_grid.groups()
        xy_grid = grid_to_iu(xy_grid, xy_unit)

        return {
            "type": "square",
            "x_iu": xy_grid,
            "y_iu": xy_grid,
            "raw": grid_selection,
        }

    return None


def get_grid(raw_grid_selection) -> tuple:
    "funtion to get currently selected grid"

    grid_dict = parse_grid(raw_grid_selection)

    if grid_dict and "x_iu" in grid_dict:
        return grid_dict["x_iu"], grid_dict["y_iu"]
    return None, None


if __name__ == "__main__":
    import wx

    x_iu, y_iu = get_grid(wx.FindWindowById(pcbnew.ID_ON_GRID_SELECT).GetStringSelection())
    print(f"Grid X: {x_iu} iu, Grid Y: {y_iu} iu")
