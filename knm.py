import os
import shutil
import time
from getpass import getuser

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.styles.colors import RED, GREEN
"""
Category and category group classes
Keynote and keynote group classes
File I/O

Spreadsheet file is the master file and is used for loading.
.txt file can be saved, as can the spreadsheet.
"""


class Category(object):
    """
    Information for a specific category.
    A Category holds three dictionaries of keynotes.
    """

    def __init__(self, num, name):
        """
        Create category object
        """
        # print("Creating category {}".format(name))
        self.name = name
        self.num = int(num)
        # Placeholders for keynotes to be added later
        self.demoKeynotes = []
        self.existingKeynotes = []
        self.newKeynotes = []

    def addKeynote(self, keynote):
        """
        Add a keynote into the correct category
        """
        if keynote.den == 'D':
            nextNum = len(self.demoKeynotes)
            self.demoKeynotes.append(keynote)
        elif keynote.den == 'E':
            nextNum = len(self.existingKeynotes)
            self.existingKeynotes.append(keynote)
        else:
            nextNum = len(self.newKeynotes)
            self.newKeynotes.append(keynote)
        keynote.num = nextNum
        keynote.catnum = self.num
        keynote.category = self

    @property
    def keynotes(self):
        return self.demoKeynotes + self.existingKeynotes + self.newKeynotes

    @property
    def fullstring(self):
        return "{}\t{}".format(self.num, self.name)

    def __repr__(self):
        return "Category({}, {})".format(self.name, self.num)

    def __str__(self):
        return "Category {}: {}".format(self.num, self.name)


class Keynote(object):
    """
    Information for a single keynote.
    """

    def __init__(self, number=None, kType=None, disabled=False,
                 numString=None, kText='<Empty>', catString=None):
        """
        Build a Keynote.
        """
        if kType:
            # Build from scratch using num and kType
            self.den = kType  # D, E or N
            if number:
                self.num = number
            self.text = kText
            self.disabled = disabled
            # print(self)
            return
        # We are building from a line in a file
        if len(numString) == 5:
            if not numString[0] in 'DEN':
                print("Bad first character: <{}>".format(numString))
            self.den = numString[0]   # First character is D, E, or N
            self.catnum = int(numString[1:3])  # Category Number
            self.num = int(numString[3:6])
        else:
            print("Bad number string: <{}>".format(numString))
        self.text = kText
        if catString == 'disabled':  # Keynote is Disabled
            self.disabled = True
        else:
            self.disabled = False
        # print(self)

    @property
    def identifier(self):
        return "{}{:02d}{:02d}".format(self.den, self.catnum, self.num)

    @property
    def fullstring(self):
        if self.disabled:
            return "{}\t{}\tdisabled".format(self.identifier, self.text)
        else:
            return "{}\t{}\t{}".format(self.identifier, self.text,
                                       self.category.num)

    def __str__(self):
        self.fullstring

    def __repr__(self):
        if self.disabled:
            cat = 'disabled'
        else:
            cat = self.catnum
        return ("Keynote(numString={}, "
                "kText='{}', catString={})".format(self.identifier,
                                                   self.text, cat))


class keynoteFile(object):
    """
    A record containing all the data for a keynote file.
    """
    fileName = None   # Store the original filename
    user = getuser()  # We use the username for the lock
    modified = False  # Marker tells us if the file content has been changed
    categories = []  # A list of categories, with keynotes attached

    def lockedName(self, name):
        parts = name.rsplit('.', 1)
        return parts[0] + '_' + self.user + '.' + parts[1]

    def lockFile(self, name):
        """
        Make a backup then lock the file (via copy)
        """
        result = os.path.isfile(name)
        if result:
            shutil.copy(name, name + '.' + str(int(time.time())))
            os.rename(name, self.lockedName(name))
            self.fileName = name
        return result  # Will be False if there's no file

    def unlockFile(self, name):
        result = os.path.isfile(self.lockedName(name))
        if result:
            os.rename(self.lockedName(name), name)
        self.fileName = None  # Blank out the closed file
        self.categories = None  # Blank out the loaded content
        return result  # Can't unlock non-existent file

    def checkLock(self, fileName=None):
        """
        Before opening or saving a file, create and/or release a lock.
        Save check is implemented through the GUI.
        """
        if self.fileName is not None:  # We have a file already open
            # Unlock self.fileName
            return self.unlockFile(fileName)
        if fileName is not None:
            # Lock the new file
            return self.lockFile(fileName)

    def load(self, fileName, fileType):
        """
        Load the new file. Locks only apply to the spreadsheet.
        """
        # if fileType == 'Text':
        #     self.loadTxt(self.lockedName(fileName))
        if fileType == 'Excel':
            if self.checkLock(fileName):
                self.loadXlsx(self.lockedName(fileName))
            else:
                print('File not found', fileName)
        else:
            print('Bad fileType', fileType)

    # def loadTxt(self, keynoteFile):
    #     """
    #     Load in a file full of keynotes and return categories and keynotes.
    #     """
    #     # Clear out any existing categories or keynotes
    #     self.categories = []
    #     keynoteList = []
    #     # Load in the new stuff
    #     with open(keynoteFile, "r") as f:
    #         # Save the filename now that we know it opened OK
    #         self.fileName = keynoteFile
    #         line = f.readline()
    #         while line != '':  # Empty string means end of file
    #             line = line.rstrip('\t \n')
    #             ll = line.split('\t')
    #             # print(ll)
    #             if len(ll) == 2:
    #                 self.categories.append(Category(ll[0], ll[1]))
    #             elif len(ll) == 3:
    #                 keynoteList.append(Keynote(numString=ll[0], kText=ll[1],
    #                                            catString=ll[2]))
    #             else:
    #                 print("Ignoring line <{}>".format(line))
    #             line = f.readline()
    #
    #         print("{} categories found.".format(len(self.categories)))
    #         print("{} keynotes found".format(len(keynoteList)))
    #         for c in self.categories:
    #             # Attach keynotes to categories correctly
    #             for k in keynoteList:
    #                 if k.catnum == c.num:
    #                     k.category = c
    #                     c.addKeynote(k)
    #     # self.pprint()
    #     return self.categories

    def saveTxt(self):
        """
        Write out the keynote data in the record to a tab - delimited file.
        """
        # Make sure the filename ends in .xlsx, changing it if necessary
        txtFileName = self.fileName.rsplit('.', 1)[0] + '.txt'
        print('Saving file: {}', txtFileName)
        with open(txtFileName, 'w+') as f:
            cCount = 0
            kCount = 0
            for c in self.categories:
                f.write("{}\t{}".format(c.num, c.name))
                f.write('\n')
                cCount += 1
            f.write('\n')  # A blank line
            for c in self.categories:
                for k in c.keynotes:
                    f.write(k.fullstring)
                    f.write('\n')
                    kCount += 1
                f.write('\n')  # A blank line
            return (cCount, kCount)

    def loadXlsx(self, keynoteFile):
        """
        Load in an Excel keynote fileand return categories and keynotes.
        """
        try:
            print("Opening file:", keynoteFile)
            self.workbook = load_workbook(filename=keynoteFile)
        except Exception as e:
            print('Excel open failed: {}', e)
            return False
        # Assume first tab holds the Data
        rows = tuple(self.workbook.active.rows)
        keynoteList = []
        for row in rows:
            if not ((row[0].value or row[0].value == 0) and row[1].value):
                continue  # Ignore any row with a blank in columns A or B
            if type(row[0].value) == int:
                # It's a category
                print('Found category', row[1].value)
                self.categories.append(Category(row[0].value, row[1].value))
            elif row[0].value and len(row[0].value) == 5:
                # There's a keynote identifier
                keynoteList.append(Keynote(numString=row[0].value,
                                           kText=row[1].value,
                                           catString=str(row[2].value)))
            else:
                print("Can't process /{}/{}/{}/".format(row[0].value,
                                                        row[1].value,
                                                        row[2].value))
        print("{} categories found.".format(len(self.categories)))
        print("{} keynotes found".format(len(keynoteList)))
        for c in self.categories:
            # Attach keynotes to categories correctly
            for k in keynoteList:
                if k.catnum == c.num:
                    k.category = c
                    c.addKeynote(k)
        # self.pprint()
        return self.categories

    def saveXlsx(self):
        """
        Write out the keynote data in the record to a spreadsheet.
        Assumes any updates to the record have already been made.
        """
        def writeCell(worksheet, row, col, val,
                      font=None, fill=None, align=None):
            """
            row is a number, col is a letter
            """
            addr = '{}{}'.format(col, row)
            worksheet[addr] = val
            if font:
                worksheet[addr].font = font
            if fill:
                worksheet[addr].fill = fill
            if align:
                worksheet[addr].alignment = align

        # Make sure the filename ends in .xlsx, changing it if necessary
        fileName = self.lockedName(self.fileName)
        # Create a new workbook and worksheet
        wb = Workbook()
        ws = wb.active
        # Set up widths, colors and fonts
        ws.column_dimensions['B'].width = 100
        wrap = Alignment(wrapText=True)
        boldFont = Font(b=True)
        redFont = Font(color=RED)
        greenFont = Font(color=GREEN)
        grayFont = Font(color='888888', size=9)
        grayFill = PatternFill("solid", fgColor='BBBBBB')
        # Counters to keep track of things
        rowCount = 1
        cCount = 0
        kCount = 0
        # Loop through writing categories
        for c in self.categories:
            # Write a category record
            writeCell(ws, rowCount, 'A', c.num)
            writeCell(ws, rowCount, 'B', c.name)
            cCount += 1
            rowCount += 1
        writeCell(ws, rowCount, 'A',
                  ("Mechanically generated keynote file. "
                   "REMEMBER TO SAVE after editing, then SAVE FILE AS "
                   "Text (Tab delimited)(*.txt), then load/reload your "
                   "keynotes on your project Revit file so Revit can see "
                   "the changes. All keynote / text editing shall be "
                   "on the Excel file only."), font=redFont, align=wrap)
        ws.merge_cells(start_row=rowCount, end_row=rowCount,
                       start_column=1, end_column=2)

        rowCount += 2
        # Now write keynotes
        for c in self.categories:
            writeCell(ws, rowCount, 'A', c.name.upper(), font=boldFont)
            # startRow = rowCount  # First row in outline
            rowCount += 1
            for kt in (c.demoKeynotes, c.existingKeynotes, c.newKeynotes):
                for k in kt:
                    id = k.identifier
                    if id[0] == 'D':
                        f = redFont
                    elif id[0] == 'E':
                        f = None
                    else:
                        f = greenFont
                    writeCell(ws, rowCount, 'A', id, font=f)
                    writeCell(ws, rowCount, 'B', k.text, align=wrap)
                    if k.disabled:
                        writeCell(ws, rowCount, 'C', 'disabled')
                    else:
                        writeCell(ws, rowCount, 'C', k.catnum)
                    kCount += 1
                    rowCount += 1
                # endRow = rowCount
                rowCount += 1  # Leave a blank line
                writeCell(ws, rowCount, 'A', "DO NOT USE THIS ROW, "
                          "INSERT NEW ROW AS NEEDED",
                          font=grayFont, fill=grayFill)
                ws.merge_cells(start_row=rowCount, end_row=rowCount,
                               start_column=1, end_column=3)
                # Create outline for current category
                rowCount += 1
        print('Saving file: ', fileName)
        wb.save(fileName)
        return (cCount, kCount)

    def pprint(self):
        """
        Print a human readable version of the keynoteFile record.
        """
        for c in self.categories:
            print(c.fullstring)
            for k in c.keynotes:
                print("- {}".format(k.fullstring))
