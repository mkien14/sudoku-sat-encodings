import sys
import os

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "src"
    )
)

from solve_cplex_cp import solve


N = 36

puzzle_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "puzzles",
    "sudoku_N36_seed1.txt"
)

with open(puzzle_path, encoding="utf-8") as f:
    puzzle = f.read().strip()

print("Starting CP Optimizer...")

r = solve(
    N,
    puzzle,
    time_limit=60
)

print("sat =", r.sat)
print("solve_time =", r.solve_time)

if r.grid:
    print("grid:")
    for row in r.grid:
        print(row)