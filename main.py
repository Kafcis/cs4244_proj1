import numpy as py
import Formula
import DPLL
import CDCL
import time


def checkSat(filename):
    formula = Formula.Formula(filename)
    literal = []
    a = DPLL.DPLL(literal, formula.cnfArray)


    return a

# t0 = time.time()
for i in range(1, 100):
    # filename = "tests/uf250-0" + str(i) + ".cnf"
    filename = "tests/uf20-0" + str(i) + ".cnf"
    checkSat(filename)

t1 = time.time()
# print(t1-t0)

print(checkSat("CNF1_unsat"))
# checkSat("CNF2_sat")
# checkSat("CNF3_test")
# print(DPLL.getUnitLiteral([-2], [1, 2, 3]))
