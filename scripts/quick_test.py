import sys
sys.path.insert(0, "src")
from solve_pysat import solve

puzzle = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
for amo in ["binomial", "binary", "sequential", "commander", "product"]:
    r = solve(9, puzzle, amo)
    print(f"{amo:12s} biến={r['n_vars']:5d} mệnh_đề={r['n_clauses']:6d} "
          f"mã_hóa={r['encode_time']*1000:.1f}ms giải={r['solve_time']*1000:.1f}ms {r['sat']}")