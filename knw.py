import os
import wx
import knm

# wxPython version refactored


class categoryPage(wx.Panel):
    """
    A tab for a category
    """

    def __init__(self, parent):
        """
        Create a page record and add to the notebook
        """
        # Store the keynote elements
        self.demoRows = []
        self.existingRows = []
        self.newRows = []
        # Create the page
        wx.Panel.__init__(self, parent)


# class keynoteRow(wx.BoxSizer):
#     """
#     A number, text and checkbox for a keynote.
#     """
#
#     def __init__(self, *args, **kwargs):
#         self.keynote = {}
#         self.keynote = kwargs.pop('keynote')
#         print(self.keynote)
#         wx.BoxSizer.__init__(self, *args, **kwargs)
#         self.SetOrientation(wx.HORIZONTAL)


class Application(wx.Frame):
    """
    Build the application window and initialize a project
    """

    def __init__(self, *args, **kwargs):
        # Create the main frame
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          'Edit Keynotes', size=(500, 500))
        # Create the communicating variables
        self.categories = []
        self.keynoteFile = ''
        self.keynotes = []
        self.buildGUI()

    def buildGUI(self):
        """
        Build the GUI.
        """
        # Add a button so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
        # Status bar for messages
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText("Simple keynote editor")
        # Create the sizers
        self.mainBox = wx.BoxSizer(wx.VERTICAL)
        self.commands = wx.BoxSizer(wx.HORIZONTAL)
        # Add the inner sizers to the mainBox
        self.mainBox.Add(self.commands, 0, wx.EXPAND, 0)
        # Create the search box and save button(s)
        self.loadText = wx.Button(self.panel, label="Load keynotes:")
        self.loadText.Bind(wx.EVT_BUTTON, self.onOpen)
        sPrompt = wx.StaticText(self.panel, label="Filter:")
        self.sString = wx.TextCtrl(self.panel)
        self.sString.SetMinSize(wx.Size(50, 20))
        self.sString.Bind(wx.EVT_KEY_DOWN, self.onFilter)
        self.saveText = wx.Button(self.panel, label="Save .txt")
        self.saveText.Bind(wx.EVT_BUTTON, self.onSave)
        self.saveXlsx = wx.Button(self.panel, label='Save .xlsx')
        self.commands.Add(self.loadText, 0, wx.ALL, 8)
        self.commands.Add(sPrompt, 0, wx.ALL, 8)
        self.commands.Add(self.sString, 2, wx.EXPAND | wx.ALL, 8)
        self.commands.Add(self.saveText, 0, wx.ALL, 8)
        self.commands.Add(self.saveXlsx, 0, wx.ALL, 8)
        # Create the notebook for Categories
        self.categoryNotebook = wx.Notebook(self.panel)
        self.mainBox.Add(self.categoryNotebook, 1, wx.EXPAND | wx.ALL, 8)
        #
        self.panel.SetSizer(self.mainBox)
        self.panel.Fit()

    def msg(self, message):
        """
        Display in Status area.
        """
        self.sb.SetStatusText(message)

    def error(self, message):
        """
        Print an error.
        """
        self.msg("Error: {}".format(message))

    def onFilter(self, event):
        """
        Hide keynotes that don't match a search string.
        """
        def hide(k):
            k.numberWidget.Hide()
            k.textWidget.Hide()
            k.disabledWidget.Hide()

        def unHide(k):
            k.numberWidget.Show()
            k.textWidget.Show()
            k.disabledWidget.Show()

        if event.GetKeyCode() == wx.WXK_RETURN:
            found = False
            ss = event.GetEventObject().GetValue()
            if ss == '':  # Show everything
                for c in self.data:
                    for k in c.demoKeynotes + c.existingKeynotes + c.newKeynotes:
                        unHide(k)
                return
            for c in self.data:
                for k in c.demoKeynotes + c.existingKeynotes + c.newKeynotes:
                    ktext = k.textWidget.GetValue()
                    if ktext.upper().count(ss.upper()) > 0:
                        found = True
                        unHide(k)
                    else:
                        hide(k)
                if not found:
                    # Hide the tab
                    c.pageWidget.Hide()
                    pass
        else:
            event.Skip()
            # if found:
            #     self.tabs.add(c.catWidget)
            #     found = False
            # else:
            #     self.tabs.hide(c.catWidget)

    def onOpen(self, event):
        """
        Open a keynote file.
        """
        with wx.FileDialog(self, "Open keynote text file",
                           wildcard="txt files (*.txt|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) \
                as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.keynoteFileName = fileDialog.GetPath()
            self.keynoteFile = knm.keynoteFile()
            try:
                self.data = self.keynoteFile.load(self.keynoteFileName)
            except IOError:
                self.error("Unable to load file {}".format(self.keynoteFile))
            # self.data is the input from the file, so build the GUI
            self.msg("Loaded file data")
            self.buildEditor()

    def onSave(self, event):
        """
        Write out the keynotes file.
        """
        # Create an updated knm.keynoteFile from the widgets
        for c in self.data:
            # Rebuild all the keynote Information
            # k.text = k.textWidget.GetValue()
            # k.disabled = k.disabledWidget.GetValue()
            pass

        self.msg("Saving file {}".format(self.keynoteFile))
        # Move the old file before overwriting
        knm.save(self.data, self.keynoteFile)

    def hideKeynote(self):
        """
        Hide the GUI elements of a widget.
        """
        self.numberWidget.Hide()
        self.textWidget.Hide()
        self.disabledWidget.Hide()

    def unHide(self):
        """
        Hide the GUI elements of a widget.
        """
        self.numberWidget.Show()
        self.textWidget.Show()
        self.disabledWidget.Show()

    def buildEditor(self):
        """
        Create the widgets for keynotes under category tabs in the notebook
        """

        def buildKeynote(page, k, color):
            """Create a row for a keynote"""
            print("Building keynote {}".format(k))
            kSizer = wx.BoxSizer(wx.HORIZONTAL)
            id = k.identifier()
            kn = wx.StaticText(page, label=id)
            kn.SetForegroundColour(color)
            kn.SetMinSize(wx.Size(50, 20))
            kt = wx.TextCtrl(page,
                             style=wx.TE_MULTILINE, value=k.text)
            kd = wx.CheckBox(page, label='Exclude')
            kd.SetValue(k.disabled)
            kSizer.Add(kn, 0, wx.ALL, 3)
            kSizer.Add(kt, 1, wx.EXPAND | wx.ALL, 3)
            kSizer.Add(kd, 0, wx.ALL, 3)
            # Store the widgets back into the data
            k.numberWidget = kn
            k.textWidget = kt
            k.disabledWidget = kd
            return kSizer

        notebook = self.categoryNotebook
        # If there was a file previously loaded, delete its pages and widgets
        while notebook.GetPageCount():
            notebook.DeletePage(0)

        for c in self.data:  # The original data from the file
            print("Building category {}".format(c))  # A category
            # Create a new page (frame), add it to the notebook
            page = categoryPage(notebook)  # Make the page
            notebook.AddPage(page, c.name)
            c.pageWidget = page  # Save the page so we can turn it on and off
            # Make a sizer for the notebook page
            pageSizer = wx.BoxSizer(wx.VERTICAL)
            # Build the keynote entries and add to the notebook page sizer
            for k in c.demoKeynotes:
                kSizer = buildKeynote(page, k, (180, 0, 0))
                pageSizer.Add(kSizer, 1, wx.EXPAND, 2)
            for k in c.existingKeynotes:
                kSizer = buildKeynote(page, k, (0, 0, 0))
                pageSizer.Add(kSizer, 1, wx.EXPAND, 2)
            for k in c.newKeynotes:
                kSizer = buildKeynote(page, k, (0, 150, 0))
                pageSizer.Add(kSizer, 1, wx.EXPAND, 2)
            page.SetSizer(pageSizer)
            page.Layout()

    def addKeynote(self, ktype):
        """
        Add a new keynote in the current tab. Type is demo, existing or new.
        Insert widget into the frame and re-add the elements below.
        """
        ctab = self.tabs.select()
        cname = self.tabs.tab(ctab)['text']
        for c in self.categories:
            if c.name == cname:
                # Make a new blank widget with the right Number
                print("Adding a keynote to {}".format(cname))
                if ktype == 'Demo':
                    # Create a demo keynote
                    pass
                elif ktype == 'Existing':
                    # Create an existing keynote
                    pass
                else:
                    # Create a new keynote
                    pass

    def clearKeynotes(self):
        """
        Remove color highlighting from the keynotes.
        """
        for c in self.categories:
            self.tabs.add(c.catWidget)
            for k in c.keynotes:
                k.textWidget.config(bg='white')


def main():
    """
    Top level function processes arguments and runs the app.
    """
    app = wx.App()
    Application().Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
