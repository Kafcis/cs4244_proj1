import time


class Solver:

    def __init__(self, filename, branchtype,anatype):
        self.filename = filename
        self.cnf, self.vars, self.vcic = Solver.read_file(filename)
        self.newClauses = set()
        self.assignments = dict.fromkeys(list(self.vars), 0)  # set all var to undefined
        self.level = 0
        self.nodes = dict((var, ImplicationNode(var, 0)) for var in list(self.vars))
        self.branching_vars = set()  # update with var that are chosen
        self.branching_history = {}  # key: level value: branch var
        self.propagate_history = {}  # key: level value: prop var list
        self.branching_count = 0
        self.branchtype = branchtype
        self.anatype = anatype

    def run(self):
        t = time.time()
        sat = self.solve()
        duration = time.time() - t
        return sat, duration

    def solve(self):
        self.preprocess()  # doesnt do anything for now
        while not self.AllVariablesAssigned():
            conflict_clause = self.unit_propagate()
            if conflict_clause:
                # there is conflict in unit propagation
                level, new_clause = self.conflict_analyze(conflict_clause)
                if level < 0:
                    return False
                for literal in new_clause:
                    self.vcic[abs(literal)] += 1
                self.newClauses.add(new_clause)
                self.backtrack(level)
                self.level = level  # change back to previous level
            elif self.AllVariablesAssigned():
                break
            else:
                # branching
                self.level += 1
                self.branching_count += 1
                branch_var, branch_value = self.pick_branching_variable()
                self.assignments[branch_var] = branch_value
                self.branching_vars.add(branch_var)
                self.branching_history[self.level] = branch_var
                self.propagate_history[self.level] = []
                self.update_node(branch_var, None)
        # print(self.assignments)
        return True

    def preprocess(self):
        pass

    @staticmethod
    def read_file(filename):
        f = open(filename, "r")
        literals = set()
        clauses = set()
        var_count_in_clauses = dict()
        for line in f:
            if line[0] == "p":
                pLine = line.split(" ")
                count_literals = int(pLine[2])
                count_clauses = int(pLine[-2])
            elif (line[0] == "c") | (line[0] == "0") | (line[0] == "%") | (line[0] == "\n"):
                pass
            else:
                fix = line.split(" ")[:-1]
                if "" in fix:
                    fix.remove("")
                newLiterals = list(map(int, fix))
                newClause = tuple(newLiterals)
                for literal in newClause:
                    if abs(literal) in var_count_in_clauses:
                        var_count_in_clauses[abs(literal)] += 1
                    else:
                        var_count_in_clauses[abs(literal)] = 1
                clauses.add(newClause)
                setliterals = set(newLiterals)
                literals.update(map(abs, setliterals))
        return clauses, literals, var_count_in_clauses

    def compute_value(self, literal):  # is literal true
        if literal < 0:
            return -self.assignments[abs(literal)]
        return self.assignments[abs(literal)]

    def compute_clause(self, clause):  # is clause true, false or undefined
        values = list(map(self.compute_value, clause))
        if 0 in values:
            return 0
        else:
            return max(values)

    def compute_cnf(self):
        return min(map(self.compute_clause, self.cnf))

    def is_unit_clause(self, clause):  # gets unit_lit and a check if it is a unit literal
        values = []
        for literal in clause:
            value = self.compute_value(literal)
            values.append(value)
            if value == 0:
                unit_lit = literal
        if (values.count(-1) == len(clause) - 1) & (values.count(0) == 1):
            is_unit = True
        elif (len(clause) == 1) & (values.count(0) == 1):
            is_unit = True
        else:
            is_unit = False
        return is_unit, unit_lit

    def update_node(self, var, clause):
        node = self.nodes[var]
        node.value = self.assignments[var]
        node.level = self.level
        if clause:  # update the parents since the children will update this node with parenthood
            parents = []
            for literal in clause:
                if abs(literal) != var:
                    parents.append(abs(literal))
            for par in parents:
                node.parents.append(self.nodes[par])
                self.nodes[par].children.append(node)
            node.clause = clause

    def unit_propagate(self):  # do the common sense thing to make sure no conflict
        while True:
            propagate_queue = []  # literals to propagate
            all_clauses = self.cnf.copy()
            all_clauses.update(self.newClauses.copy())
            for clause in all_clauses:
                clause_val = self.compute_clause(clause)
                if clause_val == 1:  # nothing to propagate
                    continue
                if clause_val == -1:  # contradiction gives conflict_clause
                    return clause
                else:
                    is_unit, unit_lit = self.is_unit_clause(clause)
                    if not is_unit:
                        continue
                    unit = (unit_lit, clause)
                    if unit not in propagate_queue:
                        propagate_queue.append(unit)
            if not propagate_queue:
                return None

            for prop_lit, clause in propagate_queue:
                prop_var = abs(prop_lit)
                self.assignments[prop_var] = 1 if prop_lit > 0 else -1  # do next common sense move
                self.update_node(prop_var, clause)
                if self.level in self.propagate_history:
                    self.propagate_history[self.level].append(prop_lit)

    def get_unit_clauses(self):
        unit_clauses = []
        for clause in self.cnf:
            if self.is_unit_clause(clause)[0]:
                unit_clauses.append(clause)
        return unit_clauses

    def AllVariablesAssigned(self):
        for var in self.vars:
            if (var not in self.assignments) | (self.assignments[var] == 0):
                return False
        return True

    def all_unassigned_vars(self):
        unassigned_vars = []
        for var in self.vars:
            if (var in self.assignments) & (self.assignments[var] == 0):
                unassigned_vars.append(var)
        return unassigned_vars

    def pick_branching_variable(self):  # make a better one later
        # branch_var = self.all_unassigned_vars()[0]
        # counter = self.vcic[branch_var]
        # for (var, count) in self.vcic.items():
        #     if (var in self.all_unassigned_vars()) & (count>counter):
        #         branch_var, counter = var, count
        if self.branchtype == 0:
            branch_var = self.all_unassigned_vars()[0]
        elif self.branchtype == 1:
            a = dict()
            for (key, count) in self.vcic.items():
                if key in self.all_unassigned_vars():
                    a[key] = count

            branch_var = max(a, key=a.get)
            a.clear()

        # branch_var = self.all_unassigned_vars()[0]
        return branch_var, 1  # var and branch level

    def conflict_analyze(self, conflict_clause):
        def next_recent_assigned(clause):
            for var in reversed(assign_history):
                remaining_vars = clause.copy()
                if var in clause:
                    remaining_vars.remove(var)
                    return var, remaining_vars
                elif -var in clause:
                    remaining_vars.remove(-var)
                    return var, remaining_vars

        if self.level == 0:
            return -1, None
        # confirm ok manual assignments + implied assignments
        assign_history = [self.branching_history[self.level]] + self.propagate_history[self.level]
        conflict_literals = conflict_clause
        checked_literals = set()
        curr_level_literals = set()
        prev_level_literals = set()
        while True:
            for literal in conflict_literals:
                if self.nodes[abs(literal)].level == self.level:
                    curr_level_literals.add(literal)
                else:
                    prev_level_literals.add(literal)
            if len(curr_level_literals) == 1:
                break
            last_assigned, remaining_vars = next_recent_assigned(curr_level_literals)
            checked_literals.add(abs(last_assigned))
            curr_level_literals = set(remaining_vars)
            propagate_clause = self.nodes[abs(last_assigned)].clause  # what clause implied the literal
            conflict_literals = []
            if propagate_clause:
                for lit in propagate_clause:
                    if abs(lit) not in checked_literals:
                        conflict_literals.append(lit)
        new_clause = []
        for lit in (curr_level_literals | prev_level_literals):
            new_clause.append(lit)
        clause = tuple(new_clause)
        if prev_level_literals:
            level = 0
            for lit in prev_level_literals:
                if level < self.nodes[abs(lit)].level:
                    level = self.nodes[abs(lit)].level
        else:
            level = self.level - 1

        return level, clause


    def backtrack(self, level):
        for var, node in self.nodes.items():
            if node.level <= level:  # remove propagated children
                children = []
                for child in node.children:
                    if child.level <= level:
                        children.append(child)
                node.children = children
            else:  # reset the propagated vars
                node.value = 0
                node.level = -1
                node.parents = []
                node.children = []
                node.clause = None
                self.assignments[node.var] = 0
        branch_vars = []
        for var in self.vars:
            if (self.assignments[var] != 0) & (len(self.nodes[var].parents) == 0):
                branch_vars.append(vars)
        self.branching_vars = set(branch_vars)

        levels = list(self.propagate_history.keys())
        for key in levels:
            if key <= level:
                continue
            self.branching_history.pop(key)
            self.propagate_history.pop(key)


class ImplicationNode:

    def __init__(self, var, value):
        self.var = var
        self.value = value
        self.level = -1
        self.parents = []
        self.children = []
        self.clause = None

    def ancestors(self):
        parents = set(self.parents)
        for parent in self.parents:
            for p in parent.ancestors():
                parents.add(p)
        return list(parents)


# hello = Solver("einstein")
# print(hello.run())
lol = 0
hi = 0
for i in range(1, 100):
    # filename = "tests/uf250-0" + str(i) + ".cnf"
    # filename = "tests/uf20-0" + str(i) + ".cnf"
    # filename = "tests/uf100-0" + str(i) + ".cnf"
    # filename = "tests/uf50-0" + str(i) + ".cnf"
    filename = "tests/uf150-0" + str(i) + ".cnf"
    a = Solver(filename, 1,0)
    # (q, w) = a.run()
    # b = Solver(filename, 1,1)
    # (r, s) = b.run()

    print(a.run())
    # hi += 1
    # if s > w:
    #     lol += 1
    #     print(lol / hi)

hello = Solver("CNF1_unsat", 1,1)
print(hello.run())
