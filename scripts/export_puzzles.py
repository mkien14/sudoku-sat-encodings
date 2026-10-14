# scripts/export_puzzles.py
"""
Xuat chinh xac cac de da dung trong thuc nghiem (moi (N, ti le, seed) trong seed_sweep.csv)
ra mot file CSV de nguoi khac doi chieu duoc, thay cho cac file de roi rac cu.

    python.exe scripts\\export_puzzles.py
Ket qua: data/puzzles/seed_sweep_puzzles.csv  (cot: N, holes_ratio, seed, n_holes, puzzle)
Ky tu '.' la o trong; moi ky tu khac la gia tri theo puzzle_gen.SYMBOLS (phan biet hoa/thuong).
"""
import csv
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from puzzle_gen import make_puzzle

SRC = os.path.join(ROOT, "benchmarks", "results", "seed_sweep.csv")
OUT = os.path.join(ROOT, "data", "puzzles", "seed_sweep_puzzles.csv")

combos = set()
with open(SRC, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        combos.add((int(row["N"]), round(float(row["holes_ratio"]), 2), int(row["seed"])))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["N", "holes_ratio", "seed", "n_holes", "puzzle"])
    for N, ratio, seed in sorted(combos):
        p = make_puzzle(N, ratio, seed)
        w.writerow([N, f"{ratio:.2f}", seed, p.count("."), p])
print(f"Da ghi {len(combos)} de vao {OUT}")