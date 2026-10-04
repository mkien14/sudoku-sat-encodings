import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

puzzle = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
N = 9

print("=== CPLEX CP ===")
try:
    from solve_cplex_cp import solve as solve_cp
    r = solve_cp(N, puzzle)
    print(f"sat={r.sat}  solve_time={r.solve_time:.3f}s  encode_time={r.encode_time:.3f}s")
    if r.grid:
        for row in r.grid:
            print(" ".join(str(v) for v in row))
except Exception as e:
    print(f"LOI: {e}")

print("\n=== CPLEX MIP ===")
try:
    from solve_cplex_mip import solve as solve_mip
    r = solve_mip(N, puzzle)
    print(f"sat={r.sat}  solve_time={r.solve_time:.3f}s  encode_time={r.encode_time:.3f}s  n_vars={r.n_vars}")
    if r.grid:
        for row in r.grid:
            print(" ".join(str(v) for v in row))
except Exception as e:
    print(f"LOI: {e}")

# Bo comment khi da co Gurobi license + cai dat xong
# print("\n=== Gurobi ===")
# try:
#     from solve_gurobi import solve as solve_gb
#     r = solve_gb(N, puzzle)
#     print(f"sat={r.sat}  solve_time={r.solve_time:.3f}s  encode_time={r.encode_time:.3f}s  n_vars={r.n_vars}")
#     if r.grid:
#         for row in r.grid:
#             print(" ".join(str(v) for v in row))
# except Exception as e:
#     print(f"LOI: {e}")