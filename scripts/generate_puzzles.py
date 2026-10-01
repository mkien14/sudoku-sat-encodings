import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from puzzle_gen import make_puzzle

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "puzzles")
os.makedirs(OUT_DIR, exist_ok=True)

CONFIGS = [
    {"N": 9,  "holes_ratio": 0.6, "seed": 1},
    {"N": 16, "holes_ratio": 0.6, "seed": 1},
    {"N": 25, "holes_ratio": 0.6, "seed": 1},
]

manifest = []
for cfg in CONFIGS:
    puzzle = make_puzzle(cfg["N"], cfg["holes_ratio"], cfg["seed"])
    fname = f"sudoku_N{cfg['N']}_seed{cfg['seed']}.txt"
    path = os.path.join(OUT_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(puzzle)
    manifest.append({**cfg, "file": fname, "holes": puzzle.count(".")})
    print(f"N={cfg['N']:3d} seed={cfg['seed']} -> {fname} "
          f"({puzzle.count('.')}/{cfg['N']**2} o trong)")

with open(os.path.join(OUT_DIR, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)