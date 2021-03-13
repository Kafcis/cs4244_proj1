
def DPLL(literals, clauses):
    unitClause = getUnitClause(literals, clauses)
    unitLiteral = getUnitLiteral(literals, unitClause)
    pureLiterals = getPureLiterals(literals, clauses)
    copyLiterals = literals.copy()
    # print(len(literals))
    if (trueUnder(literals, clauses)):
        print(literals)
        return True
    elif (oneFalseUnder(literals, clauses)):
        return False
    elif unitLiteral != 0:
        copyLiterals.append(unitLiteral)
        return DPLL(copyLiterals, clauses)
    elif len(pureLiterals) > 0:
        pureLiteral = pureLiterals[0]
        pureLiterals.clear()
        copyLiterals.append(pureLiteral)
        return DPLL(copyLiterals, clauses)
    else:
        undefinedVars = getUndefinedVars(literals, clauses)
        undefinedVar = undefinedVars[0]  # replace with branching heuristic
        copyLiterals.append(undefinedVar)
        if (DPLL(copyLiterals, clauses)):
            return True
        else:
            copyLiterals.remove(undefinedVar)
            copyLiterals.append(-undefinedVar)
            return DPLL(copyLiterals, clauses)


def trueUnder(literals, clauses):
    trueClauses = getTrueClauses(literals, clauses)
    if clauses == trueClauses:
        return True
    else:
        return False


def oneFalseUnder(literals, clauses):
    if getFalseClauses(literals, clauses):
        return True
    return False


def getUnitClause(literals, clauses):
    if literals:
        for clause in clauses:
            if getUnitLiteral(literals, clause) != 0:
                return clause
    return []


def getUnitLiteral(literals, clause):
    if literals:
        count = 0
        unitLiteral = 0
        for literal in clause:
            if literal in literals:
                return 0
            elif (-literal) in literals:
                pass
            else:
                unitLiteral = literal
                count += 1
        if count == 1:
            return unitLiteral
    return 0


def getTrueClauses(literals, clauses):
    trueClauses = []
    if literals:
        for clause in clauses:
            for literal in literals:
                if literal in clause:
                    trueClauses.append(clause)
                    break
    return trueClauses


def getFalseClauses(literals, clauses):
    falseClauses = []
    if literals:
        for clause in clauses:
            isFalseClause = True
            for literal in clause:
                if (-literal) in literals:
                    continue
                else:
                    isFalseClause = False
            if isFalseClause:
                falseClauses.append(clause)
    return falseClauses


def getUndefinedClauses(literals, clauses):
    if literals:
        definedClauses = getFalseClauses(literals,clauses)
        definedClauses.extend(getTrueClauses(literals,clauses))
        undefinedClauses = []
        for clause in clauses:
            if clause not in definedClauses:
                undefinedClauses.append(clause)
        return undefinedClauses
    else:
        return clauses


def getPureLiterals(literals, clauses):
    undefinedClauses = getUndefinedClauses(literals, clauses)
    pureLiterals = []
    unpureLiterals = literals.copy()
    unpureLiterals.extend(map(lambda x: -x, literals))
    for clause in undefinedClauses:
        for literal in clause:
            if (literal in unpureLiterals) | (-literal in unpureLiterals):
                pass
            elif -literal in pureLiterals:
                pureLiterals.remove(-literal)
                unpureLiterals.extend([literal, -literal])
            elif literal in pureLiterals:
                pass
            else:
                pureLiterals.append(literal)
    return pureLiterals


def getUndefinedVars(literals, clauses):
    undefinedVars = []
    if literals:
        for clause in clauses:
            for literal in clause:
                if (literal not in literals) & (-literal not in literals):
                    if abs(literal) not in undefinedVars:
                        undefinedVars.append(abs(literal))
    else:
        for clause in clauses:
            for literal in clause:
                if abs(literal) not in undefinedVars:
                    undefinedVars.append(abs(literal))
    return undefinedVars
