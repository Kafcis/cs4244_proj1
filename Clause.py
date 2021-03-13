class Clause:

    def __init__(self, literals):
        self.literals = literals

    def __str__(self):
        print(self.literals)

    def getLiterals(self):
        return self.literals
