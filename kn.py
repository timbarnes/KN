import os
import sys
import platform
import subprocess
import functools
import tkinter
from tkinter import ttk


def popup(message):
    """
    Simple popup message box.
    """
    w = tkinter.Toplevel()
    m = tkinter.Message(w, text=message, width=400)
    m.grid(row=0, column=0, pady=20)
    e = ttk.Button(w, text="OK", command=w.destroy)
    e.grid(row=1, column=0, pady=20)


def error(message):
    """
    Print an error to a pop-up.
    """
    popup("Error: {}".format(message))


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
        self.disabledVar = tkinter.BooleanVar()
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

    def addKeynote(self, keynote):
        self.keynotes.append(keynote)

    def __str__(self):
        return "Category({} / {})".format(self.name, self.num)


class Application(ttk.Frame):
    """
    Build the application window and initialize a project
    """

    def __init__(self, master=None):
        # Create the main frame
        ttk.Frame.__init__(self, master)
        # Create the communicating variables
        self.categories = []
        self.keynote_file = "Loading..."
        self.keynotes = []
        self.createWidgets()
        self.found_widgets = []

    def createWidgets(self):
        """
        Build the GUI.
        """
        self.grid()
        # Action buttons along the top
        cr = 0  # current row
        self.topFrame = ttk.Frame(self)
        self.topFrame.grid(row=cr, column=0)
        self.label1 = ttk.Label(self.topFrame, text=self.keynote_file, justify='right')
        self.label1.grid(row=cr, column=0, padx=10)

        self.saveButton = ttk.Button(
            self.topFrame, text='Save', width=12,
            command=self.saveKeynotes)
        self.saveButton.grid(column=3, row=cr)
        # Build the notebook / tabs for each category of keynote
        cr += 1
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=cr, column=0, columnspan=2)
        self.search = ttk.Frame()
        self.search.grid()
        self.tabs.add(self.search, text='Search')

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
            c.tab = fr  # Save the tab in the category
            self.tabs.add(fr, text=c.name)  # Put it in the frame

    def buildKeynotes(self):
        """
        Create the widgets for keynotes
        """
        for c in self.categories:
            r = 0
            for k in c.keynotes:
                kn = ttk.Label(c.tab, text=k.identifier())
                kn.grid(row=r, column=0, padx=10)
                lines = len(k.text) / 60 + 2
                kt = tkinter.Text(c.tab, wrap=tkinter.WORD,
                                  height=lines, width=60)
                kt.insert(tkinter.END, k.text)  # use .get to access the text
                kt.grid(row=r, column=1, pady=2)
                k.textWidget = kt  # needed so we can access the text later
                kd = ttk.Checkbutton(c.tab, variable=k.disabledVar,
                                     command=k.toggleDisable)
                kd.grid(row=r, column=2, padx=10)
                r += 1

    def loadKeynotes(self):
        """
        Load in a file full of keynotes and build the GUI.
        """
        with open(self.keynote_file, "r") as f:
            self.label1.config(text=self.keynote_file)
            cats = self.readCategories(f)
            print("{} categories found.".format(len(cats)))
            for c in cats:
                kns = self.readKeynotes(f, c)
                print("Category {}: {} keynotes found.".format(c.name, kns))
        self.buildCategories()
        self.buildKeynotes()

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
                    k.text = k.textWidget.get('1.0', tkinter.END)[:-1]
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
        error("Usage: python kn.py <keynote file>")
        sys.exit()
    app = Application()
    app.master.title('Revit Keynote Editor')
    app.keynote_file = keynote_file
    if app.loadKeynotes():
        print('Keynote file loaded successfully.')
    app.mainloop()


if __name__ == '__main__':
    main()
