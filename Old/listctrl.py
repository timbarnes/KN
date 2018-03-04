import sys

import wx
import wx.lib.agw.ultimatelistctrl as ULC


class MyFrame(wx.Frame):

    def __init__(self):

        wx.Frame.__init__(self, None, -1, "UltimateListCtrl Demo")

        list = ULC.UltimateListCtrl(self, wx.ID_ANY,
                                    agwStyle=wx.LC_REPORT |
                                    ULC.ULC_HAS_VARIABLE_ROW_HEIGHT |
                                    wx.LC_VRULES | wx.LC_HRULES |
                                    wx.LC_SINGLE_SEL)

        list.InsertColumn(0, "Column 1")
        list.InsertColumn(1, "Column 2")

        index = list.InsertStringItem(sys.maxsize, "Item 1")
        list.SetStringItem(index, 1, "Sub-item 1\nwith a second line")

        index = list.InsertStringItem(sys.maxsize, "Item 2")
        list.SetStringItem(index, 1, "Sub-item 2 WHICH IS LONGER")

        choice = wx.Choice(list, -1, choices=["one", "two"])
        index = list.InsertStringItem(sys.maxsize, "A widget")

        list.SetItemWindow(index, 1, choice, expand=True)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(list, 1, wx.EXPAND)
        self.SetSizer(sizer)


# our normal wxApp-derived class, as usual

app = wx.App()

frame = MyFrame()
app.SetTopWindow(frame)
frame.Show()

app.MainLoop()
