import os
import time
"""
Category and category group classes
Keynote and keynote group classes
File I/O
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
            self.demoKeynotes.append(keynote)
        elif keynote.den == 'E':
            self.existingKeynotes.append(keynote)
        else:
            self.newKeynotes.append(keynote)

    def allKeynotes(self):
        return self.demoKeynotes + self.existingKeynotes + self.newKeynotes

    def fullstring(self):
        return "{}\t{}".format(self.num, self.name)

    def __str__(self):
        return "Category({}, {})".format(self.name, self.num)


class Keynote(object):
    """
    Information for a single keynote.
    """

    def __init__(self, number=None, kType=None, category=None,
                 disabled=False,
                 numString=None, kText='<Empty>', catString=None):
        """
        Build a Keynote from a number (as string), kText and category no.
        """
        if number and kType and category:
            # Build from scratch using num and kType
            self.den = kType  # D, E or N
            self.catnum = category.num
            self.num = number
            self.text = kText
            self.disabled = disabled
            self.category = category
            # print(self)
            return
        # We are building from a line in a file
        if len(numString) == 5:
            if not numString[0] in 'DEN':
                print("Bad first character: <{}>".format(numString))
            self.den = numString[0]   # First character is D, E, or N
            self.catnum = int(numString[1:3])  # Category Number
            self.num = int(numString[3:6])
            if category:
                self.category = category
        else:
            print("Bad number string: <{}>".format(numString))
        self.text = kText
        if catString == 'disabled':  # Keynote is Disabled
            self.disabled = True
        else:
            self.disabled = False
        # print(self)

    def identifier(self):
        return "{}{:02d}{:02d}".format(self.den, self.catnum, self.num)

    def fullstring(self):
        if self.disabled:
            return "{}\t{}\tdisabled".format(self.identifier(), self.text)
        else:
            return "{}\t{}\t{}".format(self.identifier(), self.text,
                                       self.category.num)

    def __str__(self):
        if self.disabled:
            cat = 'disabled'
        else:
            cat = self.catnum
        return ("Keynote(numString={}, "
                "kText='{}', catString={})".format(self.identifier(),
                                                   self.text, cat))


class keynoteFile(object):
    """
    A record containing all the data for a keynote file.
    """
    fileName = None
    categories = []  # A list of categories, with keynotes attached

    def load(self, fileName, fileType):
        if fileType == 'Text':
            self.loadTxt(fileName)
        elif fileType == 'Excel':
            self.loadXlsx(fileName)
        else:
            print('Bad fileType', fileType)

    def loadTxt(self, keynoteFile):
        """
        Load in a file full of keynotes and return categories and keynotes.
        """
        # Clear out any existing categories or keynotes
        self.categories = []
        keynoteList = []
        # Load in the new stuff
        with open(keynoteFile, "r") as f:
            # Save the filename now that we know it opened OK
            self.fileName = keynoteFile
            line = f.readline()
            while line != '':  # Empty string means end of file
                line = line.rstrip('\t \n')
                ll = line.split('\t')
                # print(ll)
                if len(ll) == 2:
                    self.categories.append(Category(ll[0], ll[1]))
                elif len(ll) == 3:
                    keynoteList.append(Keynote(numString=ll[0], kText=ll[1],
                                               catString=ll[2]))
                else:
                    print("Ignoring line <{}>".format(line))
                line = f.readline()

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

    def saveTxt(self):
        """
        Write out the keynote data in the record to a tab-delimited file.
        Assumes any updates to the record have already been made.
        """
        # Make sure the filename ends in .xlsx, changing it if necessary
        self.fileName = self.fileName.rsplit('.', 1)[0] + '.txt'
        # Create a backup copy of the file
        if os.path.isfile(self.fileName):
            os.rename(self.fileName, self.fileName +
                      '.' + str(int(time.time())))
        with open(self.fileName, 'w+') as f:
            cCount = 0
            kCount = 0
            for c in self.categories:
                f.write("{}\t{}".format(c.num, c.name))
                f.write('\n')
                cCount += 1
            f.write('\n')  # A blank line
            for c in self.categories:
                for k in c.allKeynotes():
                    f.write(k.fullstring())
                    f.write('\n')
                    kCount += 1
                f.write('\n')  # A blank line
            return (cCount, kCount)

    def loadXlsx(self, keynoteFile):
        """
        Load in an Excel keynote fileand return categories and keynotes.
        """
        pass

    def saveXlsx(self):
        """
        Write out the keynote data in the record to a spreadsheet.
        Assumes any updates to the record have already been made.
        """
        # Make sure the filename ends in .xlsx, changing it if necessary
        self.fileName = self.fileName.rsplit('.', 1)[0] + '.xlsx'
        # Create a backup copy of the file
        if os.path.isfile(self.fileName):
            os.rename(self.fileName, self.fileName +
                      '.' + str(int(time.time())))
        with open(self.fileName, 'w+') as f:
            cCount = 0
            kCount = 0
            for c in self.categories:
                f.write("{}\t{}".format(c.num, c.name))
                f.write('\n')
                cCount += 1
            f.write('\n')  # A blank line
            for c in self.categories:
                for k in c.allKeynotes():
                    f.write(k.fullstring())
                    f.write('\n')
                    kCount += 1
                f.write('\n')  # A blank line
            return (cCount, kCount)

    def pprint(self):
        """
        Print a human readable version of the keynoteFile record.
        """
        for c in self.categories:
            print(c.fullstring())
            for k in c.allKeynotes():
                print("- {}".format(k.fullstring()))
