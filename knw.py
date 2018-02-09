import os
import sys
import functools
import wx

# wxPython version


class Keynote(object):
    """
    Information for a single keynote
    """

    def __init__(self, line, category):
        """
        Build a Keynote from a line in the file, attach to a category.
        """
        if not line[0] in 'DEN':
            error("Bad first character: <{}>".format(line))
        self.den = line[0]   # First character is D, E, or N
        self.catnum = int(line[1:3])  # Category Number
        # print(self.catnum)
        self.num = int(line[3:6])
        self.category = category  # Zero-based categories
        ll = line.split('\t')  # Split at tabs
        print(ll)
        self.text = ll[1]
        self.kt = None  # Will be filled in when the widget is made
        self.disabledVar = tk.BooleanVar()
        if len(ll) == 2 or ll[2] == 'disabled':  # Keynote is Disabled
            self.disabledVar.set(True)
        else:
            self.disabledVar.set(False)
            if self.catnum != category.num:
                error("Category mismatch: {} / {}".format(self.catnum,
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


class Category(object):
    """
    Information for a specific category.
    """

    def __init__(self, name, num):
        """
        Create category, widget and stringVar
        """
        self.name = name
        self.num = num
        self.keynotes = []
        self.catWidget = None  # The tab, so we can tweak it's label

    def addKeynote(self, keynote):
        self.keynotes.append(keynote)

    def __str__(self):
        return "Category({} / {})".format(self.name, self.num)


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
        try:
            self.loadKeynotes()
        except Exception as e:
            self.error("Unable to load keynote file {}".format(self.keynote_file))
            print(e)

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
        self.commands = wx.FlexGridSizer(3, 2, 9, 25)
        self.tabs = wx.BoxSizer(wx.VERTICAL)
        # Add the inner sizers to the mainBox
        self.mainBox.Add(self.commands, 0, wx.EXPAND, 0)
        self.mainBox.Add(self.tabs, 1, wx.EXPAND, 0)
        #
        # cr = 0  # current row
        # self.topFrame = ttk.Frame(self, borderwidth=4)
        # self.topFrame.grid(row=cr, column=0)
        # self.label1 = ttk.Label(self.topFrame, text=self.keynote_file,
        #                         justify='right')
        # self.label1.grid(row=cr, column=0, padx=10)
        # self.saveButton = ttk.Button(
        #     self.topFrame, text='Save', width=12,
        #     command=self.saveKeynotes)
        # self.saveButton.grid(column=2, row=cr)
        # cr += 1
        # self.searchString = tk.StringVar()
        # self.searchEntry = ttk.Entry(
        #     self.topFrame, textvariable=self.searchString)
        # self.searchEntry.grid(row=cr, column=0)
        # self.searchButton = ttk.Button(
        #     self.topFrame, text='Search', width=12,
        #     command=self.searchKeynotes)
        # self.searchButton.grid(column=1, row=cr)
        # self.clearButton = ttk.Button(
        #     self.topFrame, text='Clear', width=12,
        #     command=self.clearKeynotes)
        # self.clearButton.grid(column=2, row=cr)
        # cr += 1
        # self.addDButton = ttk.Button(
        #     self.topFrame, text='Add Demo', width=12,
        #     command=functools.partial(self.addKeynote, 'Demo'))
        # self.addDButton.grid(column=0, row=cr)
        # self.addEButton = ttk.Button(
        #     self.topFrame, text='Add Existing', width=12,
        #     command=functools.partial(self.addKeynote, 'Existing'))
        # self.addEButton.grid(column=1, row=cr)
        # self.addNButton = ttk.Button(
        #     self.topFrame, text='Add New', width=12,
        #     command=functools.partial(self.addKeynote, 'New'))
        # self.addNButton.grid(column=2, row=cr)
        #
        # # Build the notebook / tabs for each category of keynote
        # cr += 1
        # # Make a scrollbar - still need to make window resizable
        # self.vsb = tk.Scrollbar(self, orient=tk.VERTICAL)
        # self.vsb.grid(row=cr, column=1, sticky=tk.N + tk.S)
        # # Make a canvas and link to scrollbar
        # self.canvas = tk.Canvas(self, width=600, height=600,
        #                         yscrollcommand=self.vsb.set)
        # self.canvas.grid(row=cr, column=0)
        # # link the scrollbar back to the canvas
        # self.vsb.config(command=self.canvas.yview)
        # # Make the notebook
        # self.tabs = ttk.Notebook(self.canvas)
        # self.tabs.grid(row=cr, column=0, columnspan=2)
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
                c = Category(ll, n)
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

    def buildCategories(self):
        """
        Build the tabs and populate with keynotes; add to the main frame.
        """
        cats = self.categories
        if not cats:
            error("No categories found.")
            return 0
        for c in cats:
            fr = ttk.Frame()
            fr.grid()
            c.catWidget = fr  # Save the tab in the category
            self.tabs.add(fr, text=c.name)  # Put it in the frame

    def buildKeynotes(self):
        """
        Create the widgets for keynotes
        """
        for c in self.categories:
            r = 0
            for k in c.keynotes:
                id = k.identifier()
                i = ['D', 'E', 'N'].index(id[0])
                color = ['red', 'black', 'green'][i]
                kn = ttk.Label(c.catWidget, foreground=color, text=id)
                kn.grid(row=r, column=0, padx=10)
                lines = len(k.text) / 60 + 2
                kt = tk.Text(c.catWidget, wrap=tk.WORD,
                             height=lines, width=60)
                kt.insert(tk.END, k.text)  # use .get to access the text
                kt.grid(row=r, column=1, pady=2)
                k.textWidget = kt  # needed so we can access the text later
                kd = ttk.Checkbutton(c.catWidget, variable=k.disabledVar,
                                     command=k.toggleDisable)
                kd.grid(row=r, column=2, padx=10)
                r += 1

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
        self.buildCategories()
        self.buildKeynotes()

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
