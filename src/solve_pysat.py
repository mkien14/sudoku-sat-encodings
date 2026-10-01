import time
from pysat.solvers import Solver
from sudoku_cnf import build_clauses, var
from amo_encodings import AMO_METHODS

def solve(N, puzzle, amo_name, solver_name="glucose3"):
    amo_fn = AMO_METHODS[amo_name]
    t0 = time.time()
    clauses, top = build_clauses(N, puzzle, amo_fn)
    t1 = time.time()
    with Solver(name=solver_name, bootstrap_with=clauses) as s:
        ok = s.solve()
        model = s.get_model() if ok else None
    t2 = time.time()

    grid = None
    if ok:
        grid = [[0]*N for _ in range(N)]
        for x in model:
            if 0 < x <= N**3:
                r = (x-1)//(N*N); c = ((x-1)//N)%N; v = (x-1)%N
                grid[r][c] = v + 1

    return {
        "N": N, "amo": amo_name, "solver": solver_name,
        "sat": ok, "n_vars": top, "n_clauses": len(clauses),
        "encode_time": t1-t0, "solve_time": t2-t1, "grid": grid,
    }