import time
from common import SolveResult
from puzzle_gen import symbol_to_value

def solve(N, puzzle, time_limit=3600):
    try:
        import gurobipy as gp
        from gurobipy import GRB
    except ImportError:
        return SolveResult(method="gurobi", N=N, sat=False, solve_time=0.0,
                            extra={"skipped": "gurobipy chua cai dat"})

    try:
        B = int(N ** 0.5)
        m = gp.Model("sudoku_gurobi")
        m.Params.OutputFlag = 0
        m.Params.MIPFocus = 1
        m.Params.Seed = 0
        m.Params.TimeLimit = time_limit

        t0 = time.time()
        x = m.addVars(N, N, N, vtype=GRB.BINARY, name="x")
        for r in range(N):
            for c in range(N):
                m.addConstr(gp.quicksum(x[r, c, v] for v in range(N)) == 1)
        for r in range(N):
            for v in range(N):
                m.addConstr(gp.quicksum(x[r, c, v] for c in range(N)) == 1)
        for c in range(N):
            for v in range(N):
                m.addConstr(gp.quicksum(x[r, c, v] for r in range(N)) == 1)
        for br in range(B):
            for bc in range(B):
                for v in range(N):
                    m.addConstr(gp.quicksum(
                        x[br*B+i, bc*B+j, v] for i in range(B) for j in range(B)) == 1)
        for idx, ch in enumerate(puzzle):
            if ch not in "0.":
                r, c = divmod(idx, N)
                m.addConstr(x[r, c, symbol_to_value(ch)] == 1)
        t1 = time.time()

        m.optimize()
        t2 = time.time()

        ok = m.Status in (GRB.OPTIMAL, GRB.SUBOPTIMAL)
        timed_out = (m.Status == GRB.TIME_LIMIT)
        grid = None
        if ok:
            grid = [[0]*N for _ in range(N)]
            for r in range(N):
                for c in range(N):
                    for v in range(N):
                        if x[r, c, v].X > 0.5:
                            grid[r][c] = v + 1

        return SolveResult(method="gurobi", N=N, sat=ok,
                            solve_time=t2-t1, encode_time=t1-t0, grid=grid, n_vars=N**3,
                            extra={"status": m.Status, "timed_out": timed_out})

    except gp.GurobiError as e:
        if "license" in str(e).lower() or "no Gurobi license" in str(e):
            return SolveResult(method="gurobi", N=N, sat=False, solve_time=0.0,
                                extra={"skipped": f"chua co license: {e}"})
        raise