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
        self.createWidgets()
        self.found_widgets = []

    def saveKeynotes(self):
        """
        Write out the keynotes file.
        """
        print("Saving file {}".format(KEYNOTE_FILE))

    def createWidgets(self):
        """
        Build the GUI.
        """
        self.grid()
        # Action buttons along the top
        cr = 0  # current row
        self.label1 = ttk.Label(self, text=KEYNOTE_FILE, justify='right')
        self.label1.grid(row=cr, column=0)

        self.saveButton = ttk.Button(
            self, text='Save', width=12,
            command=self.saveKeynotes)
        self.saveButton.grid(column=3, row=cr)


def main():
    """
    Top level function processes arguments and runs the app.
    """
    global KEYNOTE_FILE
    try:
        KEYNOTE_FILE = sys.argv[1]
        # Create and run the application object
        app = Application()
        app.master.title('Revit Keynote Editor')
        app.mainloop()
    except IndexError:
        error("Usage: python pf.py <folder1> <folder2>")


if __name__ == '__main__':
    main()
