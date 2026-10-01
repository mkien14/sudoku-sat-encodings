import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from solve_pysat import solve

PUZZLE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "puzzles")

def load_puzzle(fname):
    with open(os.path.join(PUZZLE_DIR, fname), encoding="utf-8") as f:
        return f.read().strip()

TESTS = [
    (9,  "sudoku_N9_seed1.txt"),
    (16, "sudoku_N16_seed1.txt"),
    (25, "sudoku_N25_seed1.txt"),
]

for N, fname in TESTS:
    puzzle = load_puzzle(fname)
    print(f"\n=== N={N} ===")
    for amo in ["binomial", "binary", "sequential", "commander", "product"]:
        t0 = time.time()
        r = solve(N, puzzle, amo)
        print(f"{amo:12s} bien={r['n_vars']:7d} menh_de={r['n_clauses']:8d} "
              f"ma_hoa={r['encode_time']*1000:7.1f}ms giai={r['solve_time']*1000:8.1f}ms "
              f"{'SAT' if r['sat'] else 'UNSAT'}")