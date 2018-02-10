import os
import sys
import functools
import wx

# wxPython version


class Keynote(object):
    """
    Information for a single keynote. Represented by a BoxSizer.
    """

    def __init__(self, line, category):
        """
        Build a Keynote from a line in the file, attach to a category.
        """
        if not line[0] in 'DEN':
            print("Bad first character: <{}>".format(line))
        self.den = line[0]   # First character is D, E, or N
        self.catnum = int(line[1:3])  # Category Number
        # print(self.catnum)
        self.num = int(line[3:6])
        self.category = category  # Zero-based categories
        ll = line.split('\t')  # Split at tabs
        # print(ll)
        self.text = ll[1]
        self.kt = None  # Will be filled in when the widget is made
        if len(ll) == 2 or ll[2] == 'disabled':  # Keynote is Disabled
            self.disabled = True
        else:
            self.disabled = False
            if self.catnum != category.num:
                print("Category mismatch: {} / {}".format(self.catnum,
                                                          category.num))

    def identifier(self):
        return "{}{:02d}{:02d}".format(self.den, self.catnum, self.num)

    def fullstring(self):
        if self.disabledVar.get():
            return "{}\t{}".format(self.identifier(), self.text)
        else:
            return "{}\t{}\t{}".format(self.identifier(),
                                       self.text, self.category.name)

    def toggleDisable(self):
        if self.disabledVar.get():
            # Should gray out the text field
            pass

    def __str__(self):
        return "Keynote({}, {})".format(self.identifier(),
                                        self.category.__str__())


class Category(wx.Panel):
    """
    Information for a specific category. A Category is a wx.Panel.
    """

    def __init__(self, parent, name, num=99):
        """
        Create category, widget and stringVar
        """
        print("Creating category {}".format(name))
        self.name = name
        self.num = num
        self.keynotes = []

    def addKeynote(self, keynote):
        self.keynotes.append(keynote)

    def __str__(self):
        return "Category({}, {})".format(self.name, self.num)


class Application(wx.Frame):
    """
    Build the application window and initialize a project
    """

    def __init__(self, *args, **kwargs):
        # Create the main frame
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          'Edit Keynotes', size=(400, 500))
        # Create the communicating variables
        self.categories = []
        self.keynote_file = sys.argv[1]
        self.keynotes = []
        self.buildGUI()
        # try:
        self.loadKeynotes()
        # except Exception as e:
        # self.error("Unable to load keynote file {}".format(self.keynote_file))
        # print(e)

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
        # self.tabs = wx.BoxSizer(wx.VERTICAL)
        # Add the inner sizers to the mainBox
        self.mainBox.Add(self.commands, 0, wx.EXPAND, 0)
        # self.mainBox.Add(self.tabs, 1, wx.EXPAND, 0)
        # Create the search box and save button(s)
        sPrompt = wx.StaticText(self.panel, label="Search:")
        self.sString = wx.TextCtrl(self.panel)
        self.saveText = wx.Button(self.panel, label="Save .txt")
        self.saveXlsx = wx.Button(self.panel, label='Save .xlsx')
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
        Simple popup message box.
        """
        self.sb.SetStatusText(message)

    def error(self, message):
        """
        Print an error to a pop-up.
        """
        self.msg("Error: {}".format(message))

    def readCategories(self, f):
        """
        Read the category list from a keynote file
        """
        n = 0
        while True:
            ll = f.readline().rstrip('\n')
            if len(ll) == 0 or ll[0] in '# ':
                break
            else:
                # print('Creating category: {}/{}'.format(ll, n))
                c = Category(self.categoryNotebook, ll, n)
                print(c)
                self.categories.append(c)  # Make a new one
                n += 1
        return self.categories

    def readKeynotes(self, f, category):
        """
        Read the keynotes from an open keynote file for one category.
        Disabled keynotes don't have a 3rd entry;
        Store them by category.
        """
        ll = f.readline()
        while ll != '':    # Empty string signified end of file
            ll = ll.rstrip(' \n')  # Remove leading/trailing newline or space
            if ll == '':   # It's a blank line and the group is finished
                break
            else:
                kn = Keynote(ll, category)
                # print('Found keynote: {}'.format(kn))
                category.keynotes.append(kn)
            ll = f.readline()
        return len(category.keynotes)

    def buildEditor(self):
        """
        Create the widgets for keynotes under category tabs in the notebook
        """
        nb = self.categoryNotebook
        for c in self.categories:
            print(c)
            # Create a new page (frame)
            cPageFrame = wx.Panel(nb, c.num)
            # Add it to the notebook
            nb.AddPage(cPageFrame, c.name)
            # Make a sizer for the notebook page
            cSizer = wx.BoxSizer(wx.VERTICAL)
            # Build the keynote entries and add to the notebook page sizer
            for k in c.keynotes:
                print(k)
                kSizer = wx.BoxSizer(wx.HORIZONTAL)
                id = k.identifier()
                i = ['D', 'E', 'N'].index(id[0])
                color = [(255, 0, 0), (0, 0, 0), (0, 255, 0)][i]
                kn = wx.StaticText(cPageFrame, label=id)
                kn.SetForegroundColour(color)
                kt = wx.TextCtrl(cPageFrame, value=k.text)
                kd = wx.CheckBox(cPageFrame, label='Disabled')
                kSizer.Add(kn, 0, wx.ALL, 3)
                kSizer.Add(kt, 1, wx.EXPAND | wx.ALL, 3)
                kSizer.Add(kd, 0, wx.ALL, 3)
                cSizer.Add(kSizer, 1, wx.EXPAND | wx.ALL, 2)
            cPageFrame.SetSizer(cSizer)
            # Add the BoxSizer to the page
            # print(page.sizer)

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

    def loadKeynotes(self):
        """
        Load in a file full of keynotes and build the GUI.
        """
        with open(self.keynote_file, "r") as f:
            self.msg(self.keynote_file)
            cats = self.readCategories(f)
            print("{} categories found.".format(len(cats)))
            for c in cats:
                kns = self.readKeynotes(f, c)
                print("Category {}: {} keynotes found.".format(c.name, kns))
        self.buildEditor()

    def searchKeynotes(self):
        """
        Populate the search tab with keynotes matching a search string.
        Executed as a callback from search button.
        """
        found = False
        ss = self.searchString.get()
        if len(ss) < 2:
            self.error("Search string too short")
            return
        for c in self.categories:
            for k in c.keynotes:
                ktext = k.textWidget.get('0.0', tk.END)
                if ktext.upper().count(self.searchString.get().upper()) > 0:
                    k.textWidget.config(bg='orange')
                    found = True
                else:
                    k.textWidget.config(bg='white')
            if found:
                self.tabs.add(c.catWidget)
                found = False
            else:
                self.tabs.hide(c.catWidget)

    def clearKeynotes(self):
        """
        Remove color highlighting from the keynotes.
        """
        for c in self.categories:
            self.tabs.add(c.catWidget)
            for k in c.keynotes:
                k.textWidget.config(bg='white')

    def saveKeynotes(self):
        """
        Write out the keynotes file.
        """
        print("Saving file {}".format(self.keynote_file))
        # Move the old file before overwriting
        os.rename(self.keynote_file, self.keynote_file + '~')
        with open(self.keynote_file, 'w+') as f:
            for c in self.categories:
                f.write(c.name)
                f.write('\n')
                print(c.name)
            f.write('\n')  # A blank line
            for c in self.categories:
                for k in c.keynotes:
                    k.text = k.textWidget.get('1.0', tk.END)[:-1]
                    f.write(k.fullstring())
                    f.write('\n')
                    print(k.fullstring())
                f.write('\n')  # A blank line


def main():
    """
    Top level function processes arguments and runs the app.
    """
    # Create and run the application object
    try:
        keynote_file = sys.argv[1]
    except IndexError:
        self.error("Usage: python kn.py <keynote file>")
        sys.exit()
    app = wx.App()
    frame = Application().Show()
    app.keynote_file = keynote_file
    # if app.loadKeynotes():
    #     print('Keynote file loaded successfully.')
    app.MainLoop()


if __name__ == '__main__':
    main()
