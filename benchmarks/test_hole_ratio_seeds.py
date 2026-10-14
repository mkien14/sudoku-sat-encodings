import csv
import os
import sys
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from amo_encodings import AMO_METHODS
from formula_size import size_of
from puzzle_gen import make_puzzle, symbol_to_value
from solve_pysat import solve as solve_sat
from solve_cplex_cp import solve as solve_cp
from solve_cplex_mip import solve as solve_mip
from solve_gurobi import solve as solve_gb

# ======================= CAU HINH =======================
SEEDS = [1, 2, 3]            
TIME_CAP = 600            
EARLY_STOP_AFTER = 2         
CONFIGS = [                  
    (25, [round(0.30 + 0.05 * i, 2) for i in range(13)]),
    (36, [round(0.30 + 0.05 * i, 2) for i in range(13)]),    
    (49, [round(0.30 + 0.05 * i, 2) for i in range(5)]),
    (64, [round(0.30 + 0.05 * i, 2) for i in range(4)]),
    (81, [round(0.30 + 0.05 * i, 2) for i in range(3)]),
]

SAT_ENCODINGS = ["commander", "product", "pysat_pairwise", "pysat_seqcounter", "pysat_bitwise"]
SAT_ENCODINGS_BY_N = {25: SAT_ENCODINGS, 36: SAT_ENCODINGS, 49: SAT_ENCODINGS, 64: SAT_ENCODINGS, 81: SAT_ENCODINGS}

OUT_CSV = os.path.join(ROOT, "benchmarks", "results", "seed_sweep.csv")

EXACT_METHODS = ["cplex_cp", "cplex_mip", "gurobi"]
FIELDS = ["N", "holes_ratio", "seed", "n_holes", "method", "status", "valid",
          "solve_time", "encode_time", "total_time", "n_vars", "n_clauses", "n_constraints", "note"]


def methods_for(N):
    return ["sat_" + e for e in SAT_ENCODINGS_BY_N[N]] + EXACT_METHODS


def all_methods():
    out = []
    for N, _ in CONFIGS:
        for m in methods_for(N):
            if m not in out:
                out.append(m)
    return out


# ---------- Chuan hoa ket qua cua cac solver ----------
def _make_sat_runner(enc):
    def run(N, puzzle, cap):
        r = solve_sat(N, puzzle, enc, time_limit=cap)
        return dict(sat=r["sat"], timed_out=bool(r["timed_out"]), solve_time=r["solve_time"],
                    encode_time=r["encode_time"], grid=r["grid"], note="")
    return run


def _from_result(r):
    extra = r.extra or {}
    return dict(sat=r.sat, timed_out=bool(extra.get("timed_out", False)),
                solve_time=r.solve_time, encode_time=r.encode_time, grid=r.grid,
                note=extra.get("skipped", ""))


EXACT_RUNNERS = {
    "cplex_cp": lambda N, p, cap: _from_result(solve_cp(N, p, time_limit=cap)),
    "cplex_mip": lambda N, p, cap: _from_result(solve_mip(N, p, time_limit=cap)),
    "gurobi": lambda N, p, cap: _from_result(solve_gb(N, p, time_limit=cap)),
}


def get_runner(method):
    if method.startswith("sat_"):
        return _make_sat_runner(method[len("sat_"):])
    return EXACT_RUNNERS[method]


# ---------- Kiem tra nghiem ----------
def verify_grid(grid, puzzle, N):
    if grid is None:
        return False
    h = int(round(N ** 0.5))
    full = set(range(1, N + 1))
    try:
        for r in range(N):
            if set(grid[r]) != full:
                return False
        for c in range(N):
            if {grid[r][c] for r in range(N)} != full:
                return False
        for br in range(h):
            for bc in range(h):
                if {grid[br * h + i][bc * h + j] for i in range(h) for j in range(h)} != full:
                    return False
        for idx, ch in enumerate(puzzle):
            if ch not in "0.":
                r, c = divmod(idx, N)
                if grid[r][c] != symbol_to_value(ch) + 1:
                    return False
    except Exception:
        return False
    return True


def classify(res, valid):
    if res["note"]:
        return "ERROR"                       
    if res["timed_out"]:
        return "TIMEOUT"
    if res["sat"] is True:
        return "SOLVED" if valid else "INVALID"
    if res["sat"] is False:
        return "UNSAT"                       
    return "ERROR"


# ---------- Kiem tra cau hinh + khoi dong ----------
def check_config():
    bad = sorted({e for encs in SAT_ENCODINGS_BY_N.values() for e in encs} - set(AMO_METHODS))
    if bad:
        print(f"Ten encoding khong co trong AMO_METHODS: {bad}")
        print(f"Cac ten hop le: {sorted(AMO_METHODS)}")
        sys.exit(1)
    missing = [N for N, _ in CONFIGS if N not in SAT_ENCODINGS_BY_N]
    if missing:
        print(f"Thieu SAT_ENCODINGS_BY_N cho N = {missing}")
        sys.exit(1)


def check_csv_schema():
    if not os.path.exists(OUT_CSV):
        return
    with open(OUT_CSV, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f), [])
    if header != FIELDS:
        print("Cac cot cua seed_sweep.csv khac voi script hien tai.")
        print("Chay truoc:  python.exe benchmarks\\add_size_columns.py")
        sys.exit(1)


def warm_up():
    print("Khoi dong (warm-up), ket qua khong duoc ghi lai ...")
    puzzle = make_puzzle(9, 0.5, 0)
    for method in all_methods():
        t0 = time.time()
        try:
            res = get_runner(method)(9, puzzle, 60)
        except Exception as e:
            print(f"  [{method}] LOI: {type(e).__name__}: {e}")
            sys.exit(1)
        if res["note"]:
            print(f"  [{method}] khong dung duoc: {res['note']}")
            sys.exit(1)
        ok = verify_grid(res["grid"], puzzle, 9)
        print(f"  [{method}] nghiem_hop_le={ok}  {time.time() - t0:.2f}s")
        if not ok:
            print("  -> Nghiem khong hop le o N=9, dung lai de kiem tra code truoc.")
            sys.exit(1)


# ---------- Resume + early-stop ----------
def load_done():
    done, hist = set(), {}
    if not os.path.exists(OUT_CSV):
        return done, hist
    with open(OUT_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    keep = [r for r in rows if r["status"] != "ERROR"]
    if len(keep) != len(rows):                    
        print(f"Bo {len(rows) - len(keep)} dong ERROR khoi CSV de chay lai.")
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(keep)
    for row in keep:
        key = (int(row["N"]), f"{float(row['holes_ratio']):.2f}",
               int(row["seed"]), row["method"])
        done.add(key)
        if row["status"] != "SKIPPED":
            hist.setdefault((key[0], key[1], key[3]), []).append(row["status"])
    return done, hist


def should_skip(statuses):
    if not EARLY_STOP_AFTER:
        return False
    return len(statuses) >= EARLY_STOP_AFTER and all(s == "TIMEOUT" for s in statuses)


def make_row(N, ratio, seed, n_holes, method, status, valid, solve_t, enc_t, note):
    total = round(solve_t + enc_t, 4) if (solve_t is not None and enc_t is not None) else ""
    n_vars, n_clauses, n_cons = size_of(method, N, n_holes)
    return {"N": N, "holes_ratio": f"{ratio:.2f}", "seed": seed, "n_holes": n_holes,
            "method": method, "status": status, "valid": valid,
            "solve_time": "" if solve_t is None else round(solve_t, 4),
            "encode_time": "" if enc_t is None else round(enc_t, 4),
            "total_time": total,
            "n_vars": "" if n_vars is None else n_vars,
            "n_clauses": "" if n_clauses is None else n_clauses,
            "n_constraints": "" if n_cons is None else n_cons,
            "note": note}


def run_one(method, N, puzzle):
    try:
        res = get_runner(method)(N, puzzle, TIME_CAP)
        solved = res["sat"] is True and not res["timed_out"]
        valid = verify_grid(res["grid"], puzzle, N) if solved else ""
        status = classify(res, valid is True)
        return status, valid, res["solve_time"], res["encode_time"], res["note"]
    except Exception as e:
        return "ERROR", "", None, None, f"{type(e).__name__}: {e}"


def main():
    check_config()
    check_csv_schema()
    warm_up()
    done, hist = load_done()
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    new_file = not os.path.exists(OUT_CSV)
    t_start = time.time()
    n_new = 0

    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
            f.flush()

        for seed in SEEDS:
            for N, ratios in CONFIGS:
                for ratio in ratios:
                    todo = [m for m in methods_for(N) if (N, f"{ratio:.2f}", seed, m) not in done]
                    if not todo:
                        continue
                    puzzle = make_puzzle(N, ratio, seed)
                    n_holes = puzzle.count(".")
                    print(f"\n[{(time.time() - t_start) / 60:6.1f} phut] seed={seed} N={N} "
                          f"ratio={ratio:.2f} (o trong={n_holes}/{N * N})")
                    for method in todo:
                        hk = (N, f"{ratio:.2f}", method)
                        if should_skip(hist.get(hk, [])):
                            row = make_row(N, ratio, seed, n_holes, method, "SKIPPED", "",
                                           None, None,
                                           f"{EARLY_STOP_AFTER} seed truoc deu TIMEOUT")
                            print(f"    {method:20s} SKIPPED")
                        else:
                            status, valid, st, et, note = run_one(method, N, puzzle)
                            row = make_row(N, ratio, seed, n_holes, method, status, valid,
                                           st, et, note)
                            if status != "ERROR":
                                hist.setdefault(hk, []).append(status)
                            msg = f"    {method:20s} {status:8s}"
                            if st is not None:
                                msg += f" solve={st:8.2f}s encode={et:6.2f}s"
                            if note:
                                msg += f"  note={note}"
                            if status in ("UNSAT", "INVALID"):
                                msg += "   <-- BAT THUONG, kiem tra code!"
                            print(msg)
                        w.writerow(row)
                        f.flush()
                        n_new += 1

    print(f"\nXong. Them {n_new} dong, mat {(time.time() - t_start) / 60:.1f} phut. "
          f"Ket qua: {OUT_CSV}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDa dung. Chay lai cung lenh de tiep tuc tu cho dang do.")