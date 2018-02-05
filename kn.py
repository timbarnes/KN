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

    def saveKeynotes(self):
        """
        Write out the keynotes file.
        """
        print("Saving file {}".format(self.keynote_file))

    def createWidgets(self):
        """
        Build the GUI.
        """
        self.grid()
        # Action buttons along the top
        cr = 0  # current row
        self.label1 = ttk.Label(self, text=self.keynote_file, justify='right')
        self.label1.grid(row=cr, column=0)

        self.saveButton = ttk.Button(
            self, text='Save', width=12,
            command=self.saveKeynotes)
        self.saveButton.grid(column=3, row=cr)
        # Build the notebook / tabs for each category of keynote
        cr += 1
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=cr, column=0)
        self.search = ttk.Frame()
        self.search.grid()
        self.tabs.add(self.search, text='Search')

    def readCategories(self, f):
        """
        Read the category list from a keynote file
        """
        while True:
            ll = f.readline().rstrip('\n')
            print("Read <{}>".format(ll))
            if len(ll) == 0 or ll[0] in '# ':
                break
            else:
                self.categories.append(ll)
                print(ll)
        return len(self.categories)

    def readKeynotes(self, f):
        """
        Read the keynotes from a keynote file
        """
        ll = f.readline()
        while ll != '':    # Empty string signified end of file
            ll = ll.rstrip(' \n')  # Remove leading/trailing newline or space
            if ll == '':   # It's a blank line and can be ignored
                pass
            else:
                kn = ll.split('\t')
                if len(kn) == 2:
                    kn.append('disabled')
                print('Found keynote: {}'.format(kn))
                self.keynotes.append(kn)
            ll = f.readline()
        return len(self.keynotes)

    def buildTabs(self):
        """
        Build the tabs and populate with keynotes; add to the main frame.
        """
        cats = self.categories
        if not cats:
            error("No categories found.")
            return 0
        for tab in cats:
            fr = ttk.Frame()
            fr.grid()
            self.tabs.add(fr, text=tab)

    def loadKeynotes(self):
        """
        Load in a file full of keynotes and build the GUI.
        """
        with open(self.keynote_file, "r") as f:
            self.label1.config(text=self.keynote_file)
            print("{} categories found.".format(self.readCategories(f)))
            print("{} keynotes found.".format(self.readKeynotes(f)))
            self.buildTabs()


def main():
    """
    Top level function processes arguments and runs the app.
    """
    # Create and run the application object
    try:
        keynote_file = sys.argv[1]
    except IndexError:
        error("Usage: python kn.py <keynote file>")
    app = Application()
    app.master.title('Revit Keynote Editor')
    app.keynote_file = keynote_file
    if app.loadKeynotes():
        print('Keynote file loaded successfully.')
    app.mainloop()


if __name__ == '__main__':
    main()
