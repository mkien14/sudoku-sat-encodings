import threading
import time
from pysat.solvers import Solver
from amo_encodings import AMO_METHODS
from sudoku_cnf import build_clauses

def solve(
    N,
    puzzle,
    amo_name,
    solver_name="glucose3",
    time_limit=None,
):
    if amo_name not in AMO_METHODS:
        raise ValueError(
            f"Invalid AMO method '{amo_name}'. "
            f"Supported methods: {list(AMO_METHODS.keys())}"
        )

    amo_fn = AMO_METHODS[amo_name]

    t0 = time.perf_counter()
    clauses, top = build_clauses(N, puzzle, amo_fn)
    t1 = time.perf_counter()
    n_clauses = len(clauses)

    solver = None
    timer = None
    timed_out_flag = {"v": False}
    solver_ref = {"solver": None}
    result = None
    model = None
    t2 = None

    def interrupt_solver():
        timed_out_flag["v"] = True
        current_solver = solver_ref["solver"]

        if current_solver is not None:
            try:
                current_solver.interrupt()
            except Exception:
                pass

    try:
        if time_limit is not None and time_limit > 0:
            timer = threading.Timer(time_limit, interrupt_solver)
            timer.daemon = True
            timer.start()

        solver = Solver(
            name=solver_name,
            bootstrap_with=clauses,
        )
        solver_ref["solver"] = solver

        if (
            time_limit is not None
            and time_limit > 0
            and timed_out_flag["v"]
        ):
            result = None
            t2 = time.perf_counter()
        else:
            if time_limit is not None and time_limit > 0:
                result = solver.solve_limited(
                    expect_interrupt=True,
                )
            else:
                result = solver.solve()

            t2 = time.perf_counter()

        if timer is not None:
            timer.cancel()

        model = solver.get_model() if result is True else None

    finally:
        if timer is not None:
            timer.cancel()

        if solver is not None:
            solver.delete()

    grid = None

    if model is not None:
        grid = [[0] * N for _ in range(N)]

        for literal in model:
            if 0 < literal <= N**3:
                r = (literal - 1) // (N * N)
                c = ((literal - 1) // N) % N
                v = (literal - 1) % N
                grid[r][c] = v + 1

    return {
        "N": N,
        "amo": amo_name,
        "solver": solver_name,
        "sat": result,
        "timed_out": (
            result is None
            and timed_out_flag["v"]
        ),
        "n_vars": top,
        "n_clauses": n_clauses,
        "encode_time": t1 - t0,
        "solve_time": t2 - t1,
        "grid": grid,
    }
