import wx
import wx.lib.agw.aui as aui
import wx.lib.scrolledpanel as scrolled
import knm

# wxPython version refactored


class categoryPage(scrolled.ScrolledPanel):
    """
    A tab for a category is a scrolled panel
    """

    def __init__(self, parent, category):
        """
        Create a page record and add to the notebook
        """
        # Store the keynote elements
        self.demoRows = []
        self.existingRows = []
        self.newRows = []
        self.category = category
        # Create the page
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.SetupScrolling()

    def GetPageName(self):
        return self.category.name


class Application(wx.Frame):
    """
    Build the application window and initialize a project
    """

    def __init__(self, *args, **kwargs):
        # Create the main frame
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          'Edit Keynotes', size=(800, 500))
        # We'll access notebook information from here
        self.categoryNotebook = None
        self.keynoteFile = None
        self.inactiveHidden = False
        self.fileEdited = False
        self.buildGUI()

    def buildGUI(self):
        """
        Build the GUI.
        """
        # Add a button so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
        # Status bar for messages
        self.sb = self.CreateStatusBar(2, -2, -1)
        self.sb.SetStatusText("Simple keynote editor", 0)
        # Create the sizers
        self.mainBox = wx.BoxSizer(wx.VERTICAL)
        self.commands = wx.BoxSizer(wx.HORIZONTAL)
        self.mainBox.Add(self.commands, 0, wx.EXPAND, 0)
        # Create the search box and save button(s)
        self.loadText = wx.Button(self.panel, label="Load keynotes:")
        self.loadText.Bind(wx.EVT_BUTTON, self.onOpen)
        self.commands.Add(self.loadText, 0, wx.ALL, 8)
        sPrompt = wx.StaticText(self.panel, label="Filter:")
        self.commands.Add(sPrompt, 0, wx.ALL, 8)
        self.sString = wx.TextCtrl(self.panel)
        self.sString.SetMinSize(wx.Size(50, 20))
        self.commands.Add(self.sString, 2, wx.EXPAND | wx.ALL, 8)
        self.sString.Bind(wx.EVT_KEY_DOWN, self.onFilter)
        self.saveText = wx.Button(self.panel, label="Save .txt")
        self.commands.Add(self.saveText, 0, wx.ALL, 8)
        self.saveText.Bind(wx.EVT_BUTTON, self.onSaveTxt)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.saveXlsx = wx.Button(self.panel, label='Save .xlsx')
        self.saveXlsx.Bind(wx.EVT_BUTTON, self.onSaveXlsx)
        self.commands.Add(self.saveXlsx, 0, wx.ALL, 8)
        # Create the Add keynote sizer
        self.addSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainBox.Add(self.addSizer, 0, wx.EXPAND, 0)
        # Create the Add keynote buttons
        self.hideButton = wx.Button(self.panel, label="  Hide inactive  ")
        self.addSizer.Add(self.hideButton, 0, wx.ALL, 8)
        self.hideButton.Bind(wx.EVT_BUTTON, self.onHideInactive)
        aPrompt = wx.StaticText(self.panel, style=wx.ALIGN_RIGHT,
                                label="Insert new keynotes:")
        self.addSizer.Add(aPrompt, 2, wx.EXPAND | wx.ALL, 8)
        self.addDemo = wx.Button(self.panel, label="Add Demo")
        self.addSizer.Add(self.addDemo, 0, wx.ALL, 8)
        self.addDemo.Bind(wx.EVT_BUTTON, self.onAddDemo)
        self.addExisting = wx.Button(self.panel, label="Add Existing")
        self.addSizer.Add(self.addExisting, 0, wx.ALL, 8)
        self.addExisting.Bind(wx.EVT_BUTTON, self.onAddExisting)
        self.addNew = wx.Button(self.panel, label="Add New")
        self.addSizer.Add(self.addNew, 0, wx.ALL, 8)
        self.addNew.Bind(wx.EVT_BUTTON, self.onAddNew)

        # Create the notebook for Categories
        self.categoryNotebook = aui.AuiNotebook(self.panel)
        self.mainBox.Add(self.categoryNotebook, 1, wx.EXPAND | wx.ALL, 8)
        self.categoryNotebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED,
                                   self.onPageChanged)
        self.panel.SetSizer(self.mainBox)
        self.panel.Fit()

    def msg(self, message, field=0):
        """
        Display in Status area.
        """
        self.sb.SetStatusText(message, field)

    def error(self, message):
        """
        Print an error.
        """
        self.msg("Error: {}".format(message))

    @staticmethod
    def hideKeynote(k):
        k.numberWidget.Hide()
        k.textWidget.Hide()
        k.disabledWidget.Hide()

    @staticmethod
    def unHideKeynote(k):
        k.numberWidget.Show()
        k.textWidget.Show()
        k.disabledWidget.Show()

    def onFilter(self, event):
        """
        Hide keynotes that don't match a search string.
        """
        if event.GetKeyCode() == wx.WXK_RETURN:
            ss = event.GetEventObject().GetValue()
            if ss == '':  # Show everything
                n = 0
                for c in self.keynoteFile.categories:
                    self.categoryNotebook.EnableTab(n, True)
                    n += 1
                    for k in (c.allKeynotes()):
                        self.unHideKeynote(k)
                    c.pageWidget.Layout()
                return
            n = 0
            for c in self.keynoteFile.categories:
                found = False
                for k in c.allKeynotes():
                    ktext = k.textWidget.GetValue()
                    if ktext.upper().count(ss.upper()) > 0:
                        found = True
                        self.unHideKeynote(k)
                    else:
                        self.hideKeynote(k)
                if not found:
                    # Hide the tab
                    self.categoryNotebook.EnableTab(n, False)
                n += 1
                self.categoryNotebook.DoSizing()
                c.pageWidget.Layout()
        else:
            event.Skip()

    def onHideInactive(self, event):
        """
        Hide or show inactive keynotes
        """
        if self.inactiveHidden:
            for c in self.keynoteFile.categories:
                for k in c.allKeynotes():
                    if k.disabled:
                        self.unHideKeynote(k)
                c.pageWidget.Layout()
            event.GetEventObject().SetLabelText('Hide Inactive')
            self.inactiveHidden = False
        else:
            for c in self.keynoteFile.categories:
                for k in c.allKeynotes():
                    if k.disabled:
                        self.hideKeynote(k)
                c.pageWidget.Layout()
            event.GetEventObject().SetLabelText('Show Inactive')
            self.inactiveHidden = True

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
            # Make a keynoteFile object and populate
            self.keynoteFile = knm.keynoteFile()
            try:
                self.keynoteFile.load(fileDialog.GetPath())
            except IOError:
                self.error("Unable to load file {}".format(
                    self.keynoteFile.fileName))
            if len(self.keynoteFile.categories) > 0:
                # Data is stored in the keynoteFile record, so build the GUI
                self.msg("Loaded file data")
                self.msg(self.keynoteFile.fileName, 1)
                self.buildEditor()
            else:
                self.error("No records found")

    def onSaveTxt(self, event):
        """
        Write out the keynotes file.
        """

        self.msg("Saving text file {}".format(self.keynoteFile.fileName))
        # Move the old file before overwriting
        r = self.keynoteFile.saveTxt()
        self.msg("Saved {} categories; {} keynotes".format(*r))
        self.fileEdited = False

    def onSaveXlsx(self, event):
        """
        Write out the keynotes file as a spreadsheet.
        """

        self.msg("Saving Excel file {}".format(self.keynoteFile.fileName))
        # Move the old file before overwriting
        r = self.keynoteFile.saveXlsx()
        self.msg("Saved {} categories; {} keynotes".format(*r))
        self.fileEdited = False

    def onClose(self, event):
        """
        If file is unsaved, prompt for save.
        """
        if event.CanVeto() and self.fileEdited:
            if wx.MessageBox("The file has not been saved.",
                             "Continue exiting?",
                             wx.ICON_QUESTION | wx.YES_NO) != wx.YES:
                event.Veto()
                return
        event.Skip()

    def onAddDemo(self, event):
        """
        Add a demo keynote to the current tab
        """
        if self.keynoteFile:
            self.msg("Adding demo keynote")
            self.addKeynote('D')
        else:
            self.error("Load keynote file first")

    def onAddExisting(self, event):
        if self.keynoteFile:
            self.msg("Adding existing keynote")
            self.addKeynote('E')
        else:
            self.error("Load keynote file first")

    def onAddNew(self, event):
        if self.keynoteFile:
            self.msg("Adding new keynote")
            self.addKeynote('N')
        else:
            self.error("Load keynote file first")

    def onPageChanged(self, event):
        """
        Capture the new tab for later use.
        """
        val = event.GetEventObject()
        val = val.GetCurrentPage()
        self.currentCategory = val.category

    def onDisableCheck(self, event):
        """
        Update keynote record based on GetValue.
        """
        w = event.GetEventObject()
        w.keynote.disabled = w.GetValue()
        self.fileEdited = True

    def onTextChange(self, event):
        """
        Update keynote record based on GetValue.
        """
        w = event.GetEventObject()
        s = w.GetValue()
        s = ''.join(c for c in s if c not in '\t\n')
        s = s.upper()
        if s != w.keynote.text:  # It's changed, so update
            w.keynote.text = s  # Write it to the keynote
            w.SetValue(s)       # Save it back to the widget
            yDepth = 20 * max(len(s) / 75, 2)
            w.SetMinSize(wx.Size(200, yDepth))
            self.msg("Updating text: {}".format(w.keynote.fullstring()))
            self.fileEdited = True
            self.currentCategory.pageWidget.Layout()

    def addKeynote(self, kType):
        """
        Add a keynote to the current category (page) of the specified type
        """
        category = self.currentCategory
        if kType == 'D':
            kList = category.demoKeynotes
            kSizer = category.demoSizer
            kColor = (180, 0, 0)
        elif kType == 'E':
            kList = category.existingKeynotes
            kSizer = category.existingSizer
            kColor = (0, 0, 0)
        else:
            kList = category.newKeynotes
            kSizer = category.newSizer
            kColor = (0, 160, 0)
        # Get the next number for the correct keynote type
        nextNum = kList[-1].num + 1
        # Make the keynote and append it to the appropriate list
        k = knm.Keynote(number=nextNum, kType=kType, category=category)
        kList.append(k)
        # print(k)
        # Build the keynote widgets and add to the sizer
        sizer = self.buildKeynote(self.currentCategory.pageWidget, k, kColor)
        kSizer.Add(sizer, 0, wx.EXPAND, 0)
        category.pageWidget.Layout()
        self.categoryNotebook.DoSizing()
        self.fileEdited = True

    def buildKeynote(self, page, k, color):
        """Create a row for a keynote"""
        # print("Building keynote {}".format(k))
        kSizer = wx.BoxSizer(wx.HORIZONTAL)
        id = k.identifier()
        kn = wx.StaticText(page, label=id)
        kn.SetMinSize(wx.Size(50, 16))
        kn.SetForegroundColour(color)
        kt = wx.TextCtrl(page,
                         style=wx.TE_MULTILINE,
                         value=k.text)
        yDepth = 20 * max(len(k.text) / 75, 2)
        kt.SetMinSize(wx.Size(200, yDepth))
        kt.Bind(wx.EVT_KILL_FOCUS, self.onTextChange)
        kt.keynote = k
        kd = wx.CheckBox(page, label='Exclude')
        kd.keynote = k
        kd.SetValue(k.disabled)
        kd.Bind(wx.EVT_CHECKBOX, self.onDisableCheck)
        kSizer.Add(kn, 0, wx.ALL, 3)
        kSizer.Add(kt, 1, wx.ALL, 3)
        kSizer.Add(kd, 0, wx.ALL, 3)
        # Store the widgets back into the data
        k.numberWidget = kn
        k.textWidget = kt
        k.disabledWidget = kd
        return kSizer

    def buildEditor(self):
        """
        Create the widgets for keynotes under category tabs in the notebook
        """

        def buildKeynoteSet(page, keynotes, color):
            """
            Create a D, E, or N group
            """
            sizer = wx.BoxSizer(wx.VERTICAL)
            for k in keynotes:
                kSizer = self.buildKeynote(page, k, color)
                sizer.Add(kSizer, 0, wx.EXPAND, 2)
            return sizer

        notebook = self.categoryNotebook
        # If there was a file previously loaded, delete its pages and widgets
        while notebook.GetPageCount():
            notebook.DeletePage(0)

        for c in self.keynoteFile.categories:  # Original data from the file
            # print("Building category {}".format(c))  # A category
            # Create a new page (frame), add it to the notebook
            page = categoryPage(notebook, c)  # Make the page
            notebook.AddPage(page, c.name)
            c.pageWidget = page  # Save the page so we can turn it on and off
            # Make a sizer for the notebook page
            pageSizer = wx.BoxSizer(wx.VERTICAL)
            # Build the keynote entries using three separate sizers
            # Save the sizers into the category for later access
            c.demoSizer = buildKeynoteSet(page,
                                          c.demoKeynotes, (180, 0, 0))
            c.existingSizer = buildKeynoteSet(page,
                                              c.existingKeynotes, (0, 0, 0))
            c.newSizer = buildKeynoteSet(page,
                                         c.newKeynotes, (0, 150, 0))
            pageSizer.Add(c.demoSizer, 0, wx.EXPAND, 0)
            pageSizer.Add(c.existingSizer, 0, wx.EXPAND, 0)
            pageSizer.Add(c.newSizer, 0, wx.EXPAND, 0)

            page.SetSizer(pageSizer)
            page.Layout()
        # Save the current category (the first one created)
        self.currentCategory = self.keynoteFile.categories[0]


def main():
    """
    Top level function processes arguments and runs the app.
    """
    app = wx.App()
    Application().Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
