import sys
import logging
import wx
import wx.lib.agw.aui as aui
import wx.lib.scrolledpanel as scrolled
import knm

logger = knm.logger


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
        self.categoryNotebook = None
        self.keynoteFile = None
        self.inactiveHidden = False
        self.fileEdited = False
        self.currentCategory = None
        self.buildGUI()

    def buildGUI(self):
        """
        Build the GUI. It's divided into command and keynote sections.
        """
        # Create the main panel that goes in the frame
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.SetAutoLayout(True)
        # Status bar for messages
        self.sb = self.CreateStatusBar(2)
        self.sb.SetStatusText("Simple keynote editor", 0)
        # Create the sizers: overall and command section.
        self.mainBox = wx.BoxSizer(wx.VERTICAL)
        self.commands = wx.BoxSizer(wx.HORIZONTAL)
        self.mainBox.Add(self.commands, 0, wx.EXPAND, 0)
        # self.loadText = wx.Button(self.panel, label="Load .txt:")
        # self.loadText.Bind(wx.EVT_BUTTON, self.onOpenTxt)
        # self.commands.Add(self.loadText, 0, wx.ALL, 8)
        self.loadXlsx = wx.Button(self.panel, label="Load .xlsx:")
        self.loadXlsx.Bind(wx.EVT_BUTTON, self.onOpenXlsx)
        self.commands.Add(self.loadXlsx, 0, wx.ALL, 8)
        # Create the search / filter box
        sPrompt = wx.StaticText(self.panel, label="Search:")
        self.commands.Add(sPrompt, 0, wx.ALL, 8)
        self.sString = wx.TextCtrl(self.panel)
        self.sString.SetMinSize(wx.Size(50, 20))
        self.commands.Add(self.sString, 2, wx.EXPAND | wx.ALL, 8)
        self.sString.Bind(wx.EVT_KEY_DOWN, self.onFilterKey)
        self.filter = wx.Button(self.panel, label="Search")
        self.filter.Bind(wx.EVT_BUTTON, self.onFilter)
        self.commands.Add(self.filter, 0, wx.ALL, 8)
        # Create save buttons
        self.saveText = wx.Button(self.panel, label="Save .txt")
        self.commands.Add(self.saveText, 0, wx.ALL, 8)
        self.saveText.Bind(wx.EVT_BUTTON, self.onSaveTxt)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.saveXlsx = wx.Button(self.panel, label='Save .xlsx')
        self.saveXlsx.Bind(wx.EVT_BUTTON, self.onSaveXlsx)
        self.commands.Add(self.saveXlsx, 0, wx.ALL, 8)
        # Create close button
        # self.closeXlsx = wx.Button(self.panel, label='Close .xlsx')
        # self.closeXlsx.Bind(wx.EVT_BUTTON, self.onCloseXlsx)
        # self.commands.Add(self.closeXlsx, 0, wx.ALL, 8)
        # Create the Add keynote sizer - a second row of commands
        self.addSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainBox.Add(self.addSizer, 0, wx.EXPAND, 0)
        # Create the show/hide inactive and add keynote buttons
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
        # Attach the sizer and fit the elements.
        self.panel.SetSizer(self.mainBox)
        self.panel.Fit()

    def msg(self, message, field=0):
        """
        Display in Status area.
        """
        logger.info(message)
        self.sb.SetStatusText(message, field)

    def error(self, message, field=0):
        """
        Emit an error.
        """
        logger.error(message)
        self.sb.SetStatusText(message, field)
        wx.MessageBox(message, 'Error', wx.ICON_ERROR | wx.OK)

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

    def refreshKeynoteWidgets(self):
        """
        Hide and unhide widgets based on filter, disabled, and hide flag.
        """
        n = 0
        for c in self.keynoteFile.categories:
            found = False
            for k in c.keynotes:
                if k.filter or (self.inactiveHidden and k.disabled):
                    self.hideKeynote(k)
                else:
                    self.unHideKeynote(k)
                    found = True
            # Disable tabs where no widgets are visible
            if found:
                self.categoryNotebook.EnableTab(n, True)
            else:
                self.categoryNotebook.EnableTab(n, False)
            n += 1
            c.pageWidget.Layout()

    def onFilterKey(self, event):
        """
        Hide keynotes that don't match a search string.
        """
        if event.GetKeyCode() in [wx.WXK_RETURN, wx.WXK_TAB, wx.WXK_CONTROL_F]:
            self.onFilter()
        else:
            event.Skip()

    def onFilter(self, event=None):
        ss = self.sString.GetValue()
        if ss == '':  # Remove the filter
            for c in self.keynoteFile.categories:
                for k in (c.keynotes):
                    k.filter = False
        else:
            for c in self.keynoteFile.categories:
                for k in (c.keynotes):
                    ktext = k.textWidget.GetValue()
                    if ktext.upper().count(ss.upper()) > 0:
                        k.filter = False
                    else:
                        k.filter = True
        self.refreshKeynoteWidgets()
        if event:
            event.Skip()

    def onHideInactive(self, event):
        """
        Hide or show inactive keynotes
        """
        if self.inactiveHidden:
            event.GetEventObject().SetLabelText('Hide Inactive')
            self.inactiveHidden = False
        else:
            event.GetEventObject().SetLabelText('Show Inactive')
            self.inactiveHidden = True
        self.refreshKeynoteWidgets()

    def onOpenTxt(self, event):
        """
        Open a text file
        """
        self.openFile('Text')

    def onOpenXlsx(self, event):
        """
        Open an Excel file
        """
        self.openFile('Excel')
        # self.loadXlsx.Enable(False)  # Grey out the button

    def openFile(self, fileType):
        """
        Open a keynote file, calling the appropriate loader based on fileType.
        """
        if fileType == 'Excel':
            wc = "xlsx files (*.xlsx)|*.xlsx"  # Wildcard
        elif fileType == 'Text':
            wc = "txt files (*.txt|*.txt"
        else:
            self.error("Save: filetype error")
            return
        # We're ready to load the file
        with wx.FileDialog(self, "Open keynote text file",
                           wildcard=wc,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) \
                as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                self.msg('Load canceled by user')
                return
            logger.debug(f'self.keynoteFile = {self.keynoteFile}')
            new_file = fileDialog.GetPath()
            if new_file.upper().count('NOTES.XLSX') == 0:
                try:
                    user = new_file.upper().split("_")[1].split(".XLSX")[0]
                except IndexError:
                    self.error(f'{new_file} is not a keynote file')
                else:
                    self.error(f'{new_file} is locked by user {user}')
                return
            if self.keynoteFile is not None:
                logger.debug('Flushing the old file')
                self.onClose()
            else:
                logger.debug('Creating a new keynoteFile')
            # Make a keynoteFile object and populate
            self.keynoteFile = knm.keynoteFile()
            logger.debug(f'New keynoteFile created: # categories = '
                         f'{len(self.keynoteFile.categories)}')
            if self.keynoteFile.load(new_file, fileType):
                logger.info('New keynoteFile loaded: # categories = '
                            f'{len(self.keynoteFile.categories)}')
            else:
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

    def onClose(self, event=None):
        """
        If a file is open and there are changes, save it, then exit.
        """
        self.onCloseXlsx()
        if event:
            event.Skip()  # Exit

    def onCloseXlsx(self, event=None):
        """
        If file is unsaved, prompt for save.
        """
        if not self.keynoteFile:
            print("no file to close")
            return
        if self.fileEdited:
            if wx.MessageBox("The file has not been saved.",
                             "Do you really want to close the file?",
                             wx.YES_NO) != wx.YES:
                event.Veto()
                return
        self.cleanUp()
        self.keynoteFile.unlockFile(self.keynoteFile.fileName)
        self.keynoteFile = None
        self.msg("Load a new file or exit.")

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

    def onTab(self, event):
        """
        If key pressed was tab, move to next field and update text.
        """
        if event.GetKeyCode() == wx.WXK_TAB:
            self.onTextChange(event)
            event.EventObject.Navigate()
        event.Skip()

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
            self.msg(f"Updating text: {w.keynote.fullstring}")
            self.fileEdited = True
            self.currentCategory.pageWidget.Layout()
        else:
            self.msg("")
        event.Skip()

    def onMouseMove(self, event):
        """
        Mouse scrolling support.
        """
        logging.debug("Scroll event received")
        self.categoryNotebook.GetCurrentPage().SetFocus()

    def addKeynote(self, kType):
        """
        Add a keynote to the current category (page) of the specified type
        """
        category = self.currentCategory
        if kType == 'D':
            kSizer = category.demoSizer
            kColor = (180, 0, 0)
        elif kType == 'E':
            kSizer = category.existingSizer
            kColor = (0, 0, 0)
        else:
            kSizer = category.newSizer
            kColor = (0, 160, 0)
        # Make the keynote and append it to the appropriate list
        k = knm.Keynote(kType=kType, category=category)
        category.addKeynote(k)
        # Build the keynote widgets and add to the sizer
        sizer = self.buildKeynote(self.currentCategory.pageWidget, k, kColor)
        kSizer.Add(sizer, 0, wx.EXPAND, 0)
        category.pageWidget.Layout()
        self.categoryNotebook.DoSizing()
        self.fileEdited = True

    def buildKeynote(self, page, k, color):
        """Create a row for a keynote"""
        kSizer = wx.BoxSizer(wx.HORIZONTAL)
        id = k.identifier
        kn = wx.StaticText(page, label=id)
        kn.SetMinSize(wx.Size(50, 16))
        kn.SetForegroundColour(color)
        kt = wx.TextCtrl(page,
                         style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER,
                         value=k.text)
        yDepth = 20 * max(len(k.text) / 75, 2)
        kt.SetMinSize(wx.Size(200, yDepth))
        kt.Bind(wx.EVT_KEY_DOWN, self.onTab)
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

    def cleanUp(self):
        """
        Destroy the current widget set
        """
        if self.categoryNotebook:
            self.categoryNotebook.Destroy()
            self.categoryNotebook = None
            logger.debug('Notebook destroyed')
        self.panel.Layout()

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

        # Create the notebook for Categories
        self.categoryNotebook = aui.AuiNotebook(self.panel)
        self.mainBox.Add(self.categoryNotebook, 1, wx.EXPAND | wx.ALL, 8)
        self.categoryNotebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED,
                                   self.onPageChanged)
        notebook = self.categoryNotebook
        for c in self.keynoteFile.categories:  # Original data from the file
            logger.debug(f"Building category page for {c.name}")  # A category
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
            page.Bind(wx.EVT_MOTION, self.onMouseMove)
        # Save the current category (the first one created)
        print(f'Setting current category to {self.keynoteFile.categories[0]}')
        self.currentCategory = self.keynoteFile.categories[0]
        self.mainBox.Layout()


def main():
    """
    Top level function processes arguments and runs the app.
    """
    global logger
    logger.setLevel(logging.DEBUG)
    if len(sys.argv) == 2:
        flag = sys.argv[1]
        if flag == '-i':
            logger.debug('Setting logging level to INFO')
            logger.setLevel(logging.INFO)
        elif flag == '-w':
            logger.debug('Setting logging level to WARN')
            logger.setLevel(logging.WARN)
        else:
            logger.debug(f'Flag was <{flag}>')
    app = wx.App()
    Application().Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
