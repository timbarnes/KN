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

    def __init__(self, name, num=99):
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

    def __init__(self, line, category):
        """
        Build a Keynote from a line in the file, attach to a category.
        """
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
        demoKeynotes = []
        existingKeynotes = []
        newKeynotes = []
        ll = f.readline()
        while ll != '':    # Empty string signified end of file
            ll = ll.rstrip(' \n')  # Remove leading/trailing newline or space
            if ll == '':   # It's a blank line and the group is finished
                break
            else:
                kn = Keynote(ll, category)
                # print('Found keynote: {}'.format(kn))
                if kn.den == 'D':
                    demoKeynotes.append(kn)
                elif kn.den == 'E':
                    existingKeynotes.append(kn)
                else:
                    newKeynotes.append(kn)
            ll = f.readline()
        return (demoKeynotes, existingKeynotes, newKeynotes)

    def save(self):
        """
        Write out the keynote data in the record.
        Assumes any updates to the record have already been made.
        """
        # Create a backup copy of the file
        os.rename(self.fileName, self.fileName + '~')
        with open(self.fileName, 'w+') as f:
            for c in self.categories:
                f.write(c.name)
                f.write('\n')
                print(c.name)
            f.write('\n')  # A blank line
            for c in self.categories:
                for k in c.demoKeynotes:
                    f.write(k.fullstring())
                    f.write('\n')
                for k in c.existingKeynotes:
                    f.write(k.fullstring())
                    f.write('\n')
                for k in c.newKeynotes:
                    f.write(k.fullstring())
                    f.write('\n')
                    print(k.fullstring())
                f.write('\n')  # A blank line
