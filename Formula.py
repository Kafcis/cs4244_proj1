class Formula:

    def __init__(self, filename):
        self.filename = filename
        f = open(filename, "r")
        self.cnfArray = []
        counts = {}
        for line in f:
            if line[0] == "p":
                pLine = line.split(" ")
                self.numLiteral = int(pLine[2])
                self.numClause = int(pLine[-2])
            elif (line[0] == "c") | (line[0] == "0") |(line[0] == "%") | (line[0] == "\n"):
                pass
            else:
                fix =line.split(" ")[:-1]
                if "" in fix:
                    fix.remove("")
                literals = list(map(int,fix))
                for literal in literals:
                    if literal in counts:
                        counts[literal] = 1 + counts.get(literal)
                    else:
                        counts[literal] = 1
                newClause = literals
                self.cnfArray.append(newClause)
        self.counts = counts

    def __str__(self):
        string = ""
        for clause in self.cnfArray:
            string += str(clause)
        return string

    def getCounts(self):
        return self.counts

    def addClause(self, literals):
        for literal in literals:
            if literal in self.counts:
                self.counts[literal] = 1 + self.counts.get(literal)
            else:
                self.counts[literal] = 1
        newClause = literals
        self.cnfArray.append(newClause)



