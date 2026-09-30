""" functions to get grid information from the current selection in KiCad """

import re

import pcbnew
import wx

_NUM = r"(\d+(?:[.,]\d+)?)"
_UNIT = r"(mm|mils?|thou|inch(?:es)?|in)"

_RECT_RE = re.compile(rf"{_NUM}\s*{_UNIT}\s*x\s*{_NUM}\s*{_UNIT}", re.IGNORECASE)
_SQUARE_RE = re.compile(rf"{_NUM}\s*{_UNIT}", re.IGNORECASE)


def clean_entry(grid_string: str) -> str:
    grid_string = (grid_string or "").strip()
    # remove any leading label like "Grid: " (KiCad 6)
    if ":" in grid_string:
        grid_string = grid_string.split(":", 1)[1].strip()
    return grid_string


def to_internal_units(value: str, unit: str):
    """Convert a number + unit string to KiCad internal units."""
    value = float(value.replace(",", "."))
    unit = unit.lower()

    if unit == "mm":
        return pcbnew.FromMM(value)
    if unit in ("mil", "mils", "thou"):
        return pcbnew.FromMils(value)
    if unit in ("in", "inch", "inches"):
        return pcbnew.FromMils(value * 1000.0)
    return None


def parse_grid(grid_selection: str):
    grid_selection = clean_entry(grid_selection)
    if not grid_selection:
        return None

    # rectangular grid, e.g. "1.27 mm x 2.54 mm"
    m = _RECT_RE.search(grid_selection)
    if m:
        xv, xu, yv, yu = m.groups()
        x, y = to_internal_units(xv, xu), to_internal_units(yv, yu)
        if x and y:
            return {"type": "rectangular", "x": x, "y": y, "raw": grid_selection}

    # square grid, e.g. "50 mil" or "1.27 mm (50 mils)" -> first match wins
    m = _SQUARE_RE.search(grid_selection)
    if m:
        v = to_internal_units(*m.groups())
        if v:
            return {"type": "square", "x": v, "y": v, "raw": grid_selection}

    return None


def read_grid_label() -> str:
    """Read the currently selected grid from the toolbar dropdown (live, every call)."""
    win = wx.FindWindowById(pcbnew.ID_ON_GRID_SELECT)
    if win is None:
        return ""
    return win.GetStringSelection()


def get_grid():
    """Return (x, y) of the currently selected grid in internal units, or (None, None)."""
    grid = parse_grid(read_grid_label())
    if grid:
        return grid["x"], grid["y"]
    return None, None
