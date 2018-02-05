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

    def createWidgets(self):
        """
        Create the elements of the UI and connect to variables.
        """
        self.grid()
        self.search_string = tkinter.StringVar()
        # Frame with prompt, string, and go button
        self.query_frame = ttk.Frame(self, borderwidth=5)
        self.query_frame.grid(row=0, column=0)

        self.prompt = ttk.Label(self.query_frame,
                                text="Search for:", justify='right')
        self.prompt.grid(row=0, column=0)

        self.search_string = ttk.Entry(self.query_frame, width=25,
                                       textvariable=self.search_string)
        self.search_string.focus()
        self.search_string.bind('<Return>', self.onEnter)
        self.search_string.grid(row=1, column=0)

        self.go = ttk.Button(self.query_frame, text='GO',
                             command=self.go_search)
        self.go.grid(row=2, column=0)

        self.photo_frame = ttk.LabelFrame(self, text='Photo Folders',
                                          borderwidth=5, width=200)
        self.photo_frame.grid(row=1, column=0)

        self.project_frame = ttk.LabelFrame(self, text='Project Folders',
                                            borderwidth=5, width=200)
        self.project_frame.grid(row=2, column=0)

    def onEnter(self, event):
        """
        Hitting enter should be the same as clicking GO.
        """
        self.go_search()

    def launchWindow(self, base, match):
        """
        Create a window to view the folder matched.
        """
        full_path = os.path.join(base, match)
        print(full_path)
        system = platform.system()
        if system == 'Windows':
            subprocess.Popen(['explorer', full_path])
        elif system == 'Darwin':
            subprocess.Popen(['open', full_path])
        else:
            error('Unsupported platform: {}'.format(system))

    @staticmethod
    def findMatches(f_list, search_str):
        """
        Return the list of folders that match the search_str.
        """
        return [x for x in f_list
                if x.upper().count(search_str.upper()) > 0]

    def showResults(self, frame, base, matches):
        """
        Generate buttons in _frame_ for _matches_.
        """
        print(len(matches))
        widget_list = []
        i = 0
        for match in matches:
            widget_list.append(ttk.Button(
                frame, text=match, width=50,
                command=functools.partial(self.launchWindow, base, match)))
            # command=lambda: self.launchWindow(match)))
            widget_list[-1].grid(row=i, column=0)
            i += 1
        self.found_widgets += widget_list  # Save the created widgets

    def destroyWidgets(self):
        """
        Delete any widgets in self.widget_list, because this is a new run.
        """
        for w in self.found_widgets:
            w.destroy()
        self.photo_frame.grid()
        self.project_frame.grid()

    def go_search(self):
        """
        Execute the search, and post results as widgets.
        """
        ss = self.search_string.get()
        if len(ss) < 2:
            error("Search string too short")
        else:
            pr_list = self.findMatches(PROJECT_LIST, ss)
            ph_list = self.findMatches(PHOTO_LIST, ss)
            self.destroyWidgets()  # Delete any previous results
            self.showResults(self.project_frame, PROJECT_BASE, pr_list)
            self.showResults(self.photo_frame, PHOTO_BASE, ph_list)


def main():
    """
    Top level function processes arguments and runs the app.
    """
    global PROJECT_BASE
    global PHOTO_BASE
    global PROJECT_LIST
    global PHOTO_LIST
    try:
        PROJECT_BASE = sys.argv[1]
        PHOTO_BASE = sys.argv[2]
        PROJECT_LIST = os.listdir(PROJECT_BASE)
        PHOTO_LIST = os.listdir(PHOTO_BASE)
        # Create and run the application object
        app = Application()
        app.master.title('Project Finder')
        app.mainloop()
    except IndexError:
        error("Usage: python pf.py <folder1> <folder2>")


if __name__ == '__main__':
    main()
