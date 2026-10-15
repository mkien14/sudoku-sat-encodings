import csv
import os
import shutil
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from formula_size import size_of

PATH = os.path.join(ROOT, "benchmarks", "results", "seed_sweep.csv")
FIELDS = ["N", "holes_ratio", "seed", "n_holes", "method", "status", "valid",
          "solve_time", "encode_time", "total_time", "n_vars", "n_clauses", "n_constraints", "note"]

with open(PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

if not os.path.exists(PATH + ".bak"):            
    shutil.copyfile(PATH, PATH + ".bak")
for r in rows:
    v, c, k = size_of(r["method"], int(r["N"]), int(r["n_holes"]))
    r["n_vars"] = "" if v is None else v
    r["n_clauses"] = "" if c is None else c
    r["n_constraints"] = "" if k is None else k

with open(PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)

print(f"Da them cot kich thuoc cho {len(rows)} dong. Ban sao goc: {PATH}.bak")
print("Vi du N=81:")
for r in rows:
    if r["N"] == "81" and r["seed"] == "1" and r["holes_ratio"] in ("0.3", "0.30"):
        print(f"  {r['method']:22s} n_vars={r['n_vars']:>8}  n_clauses={r['n_clauses']:>9}  n_constraints={r['n_constraints']:>7}")