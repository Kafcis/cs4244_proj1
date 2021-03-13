import DPLL as d
import random

def UnitPropogation(literals, clauses):
    return not d.oneFalseUnder(literals, clauses)


def hasUndefinedVar(literals, clauses):
    undefinedvars = d.getUndefinedVars(literals, clauses)
    return undefinedvars


def PickBranchingVar(literals, clauses):
    undefinedvars = d.getUndefinedVars(literals, clauses)
    a= random.randint(0, len(undefinedvars)-1)
    return undefinedvars[a]


def ConflictAnalysis(literals, clauses):
    level = len(literals)
    if level == 0:
        return -1
    optionliteral = literals.copy()
    newClause =[]
    flag=True
    for literal in literals:
        excess_literal = optionliteral.pop(0)
        if UnitPropogation(optionliteral, clauses)==1:
            flag=False
            newClause.append(-excess_literal)
            optionliteral.append(excess_literal)
        elif(flag):
            level -= 1


    clauses.append(newClause)
    return level


def BackTrack(literals, clauses, currLevel):
    removenumber = len(literals) - currLevel
    for i in range(0, removenumber):
        literals.pop()
    return


def CDCL(literals, clauses):
    if (UnitPropogation(literals, clauses) == 0):
        return False
    decisionLevel = 0
    print("start")
    while (hasUndefinedVar(literals, clauses)):
        branchVar = PickBranchingVar(literals, clauses)
        decisionLevel += 1
        print(decisionLevel)
        literals.append(branchVar)
        if (UnitPropogation(literals, clauses) == 0):
            currLevel = ConflictAnalysis(literals, clauses)
            if currLevel < 0:
                return False
            else:
                BackTrack(literals, clauses, currLevel)
                decisionLevel = currLevel

    return True
