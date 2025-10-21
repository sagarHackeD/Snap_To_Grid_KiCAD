"A KiCAD action plugin to snap components to the grid"

from functools import lru_cache
import os
import pcbnew
import wx

@lru_cache()        #(maxsize=5)
def get_grid(grid_selection):
    "funtion to get currently selected grid"
    grid_selection = grid_selection.strip("Grid: ")  # for KiCad 6
    grid_data = grid_selection.split(' ')
    grid_data_invariant = float(grid_data[0].replace(",","."))
    if grid_data[1] == 'mm':
        return pcbnew.FromMM(grid_data_invariant)
    if grid_data[1] == 'mils':
        return pcbnew.FromMils(grid_data_invariant)
    if grid_data[1] == 'in':
        return pcbnew.FromMM(grid_data_invariant/25.4)
    return None


# grid_se = [25.4000,12.7000,6.3500, 5.0800,2.5400,1.2700,0.6350,0.5080,0.2540,0.1270,
#         0.0635,0.0508,0.0254,0.0127,0.0051,0.0025,5.0000,2.5000,1.0000,0.5000,0.2500,
#         0.2000,0.1000,0.0500,0.0250,0.0100]

class SnapToGrid(pcbnew.ActionPlugin):
    "main class of action plugin"
    def defaults(self):
        self.name = "Snap To Grid"
        self.category = "Layout Helper"
        self.description = "Snaps footprints to currently selected grid"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def Run(self):
        # print("Sagar Naik - Snap to grid")
        #gs = wx.FindWindowById(pcbnew.ID_ON_GRID_SELECT)
        # print(pcbnew.ID_ON_GRID_SELECT)
        #grid = pcbnew.FromMM(grid_se[gs.CurrentSelection])
        grid = get_grid(wx.FindWindowById(pcbnew.ID_ON_GRID_SELECT).GetStringSelection())
        #grid = wx.FindWindowById(pcbnew.ID_ON_GRID_SELECT).CurrentSelection
        # print(grid)
        board = pcbnew.GetBoard()
        for footprint in board.GetFootprints():
            if footprint.IsSelected() and not footprint.IsLocked():
                pos = footprint.GetPosition()
                x = int((pos[0]+(grid/2))/grid)*grid
                y = int((pos[1]+(grid/2))/grid)*grid
                #x = round(pos[0],grid) #there is something wrong with python round funtion
                                        # so i roled back to previous metohd on 28/09/2020
                #y = round(pos[1],grid)
                # pos = pcbnew.PutOnGridMM(pos[0], grid_se[gs.CurrentSelection]),
                #                  pcbnew.PutOnGridMM(pos[1], grid_se[gs.CurrentSelection])
                try:
                    footprint.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
                except:
                    footprint.SetPosition(pcbnew.wxPoint(int(x), int(y)))  # for KiCad 6
                # print(footprint.GetReference(),pos,x,y)
        #pcbnew.Refresh()

#snap_to_grid().register() # Instantiate and register to Pcbnew
