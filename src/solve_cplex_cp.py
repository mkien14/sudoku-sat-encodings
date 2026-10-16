import time
from docplex.cp.model import CpoModel
from common import SolveResult
from puzzle_gen import symbol_to_value

def solve(N, puzzle, time_limit=3600):
    B = int(N ** 0.5)
    m = CpoModel()

    t0 = time.time()
    x = [[m.integer_var(1, N, name=f"x_{r}_{c}") for c in range(N)] for r in range(N)]

    for r in range(N):
        m.add(m.all_diff(x[r]))
    for c in range(N):
        m.add(m.all_diff([x[r][c] for r in range(N)]))
    for br in range(B):
        for bc in range(B):
            m.add(m.all_diff(
                [x[br*B+i][bc*B+j] for i in range(B) for j in range(B)]
            ))
    for idx, ch in enumerate(puzzle):
        if ch not in "0.":
            r, c = divmod(idx, N)
            m.add(x[r][c] == symbol_to_value(ch) + 1)
    t1 = time.time()

    sol = m.solve(TimeLimit=time_limit, LogVerbosity="Quiet")
    t2 = time.time()

    status = sol.get_solve_status() if sol is not None else "NoSolveResult"
    ok = status in ("Feasible", "Optimal")
    timed_out = status == "Unknown"          

    grid = None
    if ok:
        grid = [[sol[x[r][c]] for c in range(N)] for r in range(N)]

    return SolveResult(
        method="cplex_cp", N=N, sat=ok,
        solve_time=t2 - t1, encode_time=t1 - t0, grid=grid,
        extra={"status": status, "timed_out": timed_out},
    )