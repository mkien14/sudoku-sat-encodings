import time
from docplex.mp.model import Model
from common import SolveResult
from puzzle_gen import symbol_to_value

def solve(N, puzzle, time_limit=3600):
    B = int(N ** 0.5)
    m = Model(name="sudoku_mip")
    m.parameters.emphasis.mip = 1
    m.parameters.randomseed = 0

    t0 = time.time()
    x = {(r, c, v): m.binary_var(name=f"x_{r}_{c}_{v}")
         for r in range(N) for c in range(N) for v in range(N)}

    for r in range(N):
        for c in range(N):
            m.add_constraint(m.sum(x[r, c, v] for v in range(N)) == 1)
    for r in range(N):
        for v in range(N):
            m.add_constraint(m.sum(x[r, c, v] for c in range(N)) == 1)
    for c in range(N):
        for v in range(N):
            m.add_constraint(m.sum(x[r, c, v] for r in range(N)) == 1)
    for br in range(B):
        for bc in range(B):
            for v in range(N):
                m.add_constraint(
                    m.sum(x[br*B+i, bc*B+j, v] for i in range(B) for j in range(B)) == 1
                )
    for idx, ch in enumerate(puzzle):
        if ch not in "0.":
            r, c = divmod(idx, N)
            m.add_constraint(x[r, c, symbol_to_value(ch)] == 1)
    t1 = time.time()

    m.set_time_limit(time_limit)
    sol = m.solve(log_output=False)
    t2 = time.time()

    status = m.solve_details.status if m.solve_details else "unknown"
    timed_out = "time limit" in status.lower()
    ok = sol is not None

    grid = None
    if ok:
        grid = [[0]*N for _ in range(N)]
        for r in range(N):
            for c in range(N):
                for v in range(N):
                    if x[r, c, v].solution_value > 0.5:
                        grid[r][c] = v + 1

    return SolveResult(
        method="cplex_mip", N=N, sat=ok,
        solve_time=t2 - t1, encode_time=t1 - t0, grid=grid,
        n_vars=len(x), extra={"status": status, "timed_out": timed_out},
    )