import os
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
        print("Creating category {}".format(name))
        self.name = name
        self.num = num
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

    def destroyKeynotes(self):
        """
        Forget all the keynotes associated with the category.
        """
        self.demoKeynotes = []
        self.existingKeynotes = []
        self.newKeynotes = []

    def keynotesAll(self):
        return self.demoKeynotes + self.existingKeynotes + self.newKeynotes

    def __str__(self):
        return "Category({}, {})".format(self.name, self.num)


class Keynote(object):
    """
    Information for a single keynote.
    """

    def __init__(self, category, line=None, num=None, kType=None, note=None):
        """
        Build a Keynote from a line in the file, attach to a category.
        Alternatively build from a number and category.
        """
        if not line:
            # Build from scratch using num and kType
            self.den = kType  # D, E or N
            self.catnum = category.num
            self.num = num
            if note:
                self.text = note
            else:
                self.text = '<Empty>'
            self.disabled = False
            self.category = category
            return
        # We are building from a line in a file
        if not line[0] in 'DEN':
            print("Bad first character: <{}>".format(line))
        self.den = line[0]   # First character is D, E, or N
        self.catnum = int(line[1:3])  # Category Number
        self.num = int(line[3:6])
        self.category = category  # Zero-based categories
        ll = line.split('\t')  # Split at tabs
        # print(ll)
        self.text = ll[1]
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
        if self.disabled:
            return "{}\t{}".format(self.identifier(), self.text)
        else:
            return "{}\t{}\t{}".format(self.identifier(),
                                       self.text, self.category.num)

    def __str__(self):
        return "Keynote({}, {})".format(self.identifier(),
                                        self.category.__str__())


class keynoteFile(object):
    """
    A record containing all the data for a keynote file.
    """
    fileName = None
    categories = []  # A list of categories, with keynotes attached

    def load(self, keynoteFile):
        """
        Load in a file full of keynotes and return categories and keynotes.
        """
        # Clear out any existing categories or keynotes
        self.categories = []
        # Load in the new stuff
        with open(keynoteFile, "r") as f:
            # Save the filename now that we know it opened OK
            self.fileName = keynoteFile
            self.categories = self.readCategories(f)
            print("{} categories found.".format(len(self.categories)))
            for c in self.categories:
                (c.demoKeynotes, c.existingKeynotes, c.newKeynotes) =\
                    self.readKeynotes(f, c)  # Read the keynotes for a category
                print(c)
        return self.categories

    def readCategories(self, f):
        """
        Read the category list from a keynote file
        Line format is <number> \t <name>
        """
        while True:
            line = f.readline().rstrip('\n')
            if len(line) == 0 or line[0] in '# \t':
                break
            else:
                ll = line.split('\t')
                print(ll)
                c = Category(int(ll[0]), ll[1])  # number then name
                print(c)
                self.categories.append(c)  # Make a new one
        return self.categories

    def readKeynotes(self, f, category):
        """
        Read the keynotes from an open keynote file for one category.
        Disabled keynotes don't have a 3rd entry;
        Store them by category.
        """
        demoKeynotes = []
        existingKeynotes = []
        newKeynotes = []
        ll = f.readline()
        while ll != '':    # Empty string signified end of file
            ll = ll.rstrip(' \n')  # Remove leading/trailing newline or space
            if ll == '':   # It's a blank line and the group is finished
                break
            else:
                kn = Keynote(category, ll)
                # print('Found keynote: {}'.format(kn))
                if kn.den == 'D':
                    demoKeynotes.append(kn)
                elif kn.den == 'E':
                    existingKeynotes.append(kn)
                else:
                    newKeynotes.append(kn)
            ll = f.readline()
        self.pprint()
        return (demoKeynotes, existingKeynotes, newKeynotes)

    def save(self):
        """
        Write out the keynote data in the record.
        Assumes any updates to the record have already been made.
        """
        self.pprint()
        # Create a backup copy of the file
        os.rename(self.fileName, self.fileName + '~')
        with open(self.fileName, 'w+') as f:
            cCount = 0
            kCount = 0
            for c in self.categories:
                f.write("{}\t{}".format(c.num, c.name))
                f.write('\n')
                cCount += 1
            f.write('\n')  # A blank line
            for c in self.categories:
                for k in c.demoKeynotes:
                    f.write(k.fullstring())
                    f.write('\n')
                    kCount += 1
                for k in c.existingKeynotes:
                    f.write(k.fullstring())
                    f.write('\n')
                    kCount += 1
                for k in c.newKeynotes:
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
            print(c)
            for k in c.demoKeynotes:
                print("- {}".format(k.fullstring()))
            for k in c.existingKeynotes:
                print("- {}".format(k.fullstring()))
            for k in c.newKeynotes:
                print("- {}".format(k.fullstring()))
