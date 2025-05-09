from pysat.formula import CNF
from pysat.solvers import Glucose3




def solve_final_exam_dimacs(dimacs_file, k):
    cnf = CNF(from_file= dimacs_file)
    solver = Glucose3()
    solver.append_formula(cnf)

    #solve
    satisfiable = solver.solve()
    if satisfiable:
        print("SAT:")
    else: 
        print("UNSAT, NO SOLUTION")
        return


    #Sat, gt model: 
    model = solver.get_model()
    

    return model
    
