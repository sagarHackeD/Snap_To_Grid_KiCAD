""" funtions to get grid information from the current selection in KiCad """

import re
from functools import lru_cache

import pcbnew
import wx


def clean_entry(grid_string: str) -> str:
    grid_string = grid_string.strip()
    # remove any leading label like "Anything: " and "Grid: " for kicad 6
    if ":" in grid_string:
        grid_string = grid_string.split(":", 1)[1].strip()

    return grid_string


def grid_to_mm(value, unit):
    if not value:
        return None

    value = float(value.replace(",", "."))  # Handle comma as decimal separator

    if unit == "mm":
        return pcbnew.FromMM(value)
    elif unit == "mils":
        return pcbnew.FromMils(value)
    elif unit == "in":
        return pcbnew.FromMM(value / 25.4)

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

        x_grid = grid_to_mm(x_grid, x_unit)
        y_grid = grid_to_mm(y_grid, y_unit)

        return {
            "type": "rectangular",
            "x_mm": x_grid,
            "y_mm": y_grid,
            "raw": grid_selection,
        }

    # single grid
    squre_grid = re.search(r"([\d.]+)\s*(mm|in|mils?)", grid_selection)
    if squre_grid:
        xy_grid, xy_unit = squre_grid.groups()
        xy_grid = grid_to_mm(xy_grid, xy_unit)

        return {
            "type": "square",
            "x_mm": xy_grid,
            "y_mm": xy_grid,
            "raw": grid_selection,
        }

    return None


@lru_cache()  # (maxsize=5)
def get_grid(raw_grid_selection = wx.FindWindowById(pcbnew.ID_ON_GRID_SELECT).GetStringSelection()) -> tuple:
    "funtion to get currently selected grid"

    clean_grid_selection = clean_entry(raw_grid_selection)

    grid_dict = parse_grid(clean_grid_selection)

    # wx.MessageBox(f"Parsed grid dict : {grid_dict}")

    if grid_dict and "x_mm" in grid_dict:
        return grid_dict["x_mm"], grid_dict["y_mm"]
    return None, None



if __name__ == "__main__":
    x_mm, y_mm = get_grid()
    print(f"Grid X: {x_mm} mm, Grid Y: {y_mm} mm")