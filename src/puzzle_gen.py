import math
import random

SYMBOLS = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def make_puzzle(N, holes_ratio, seed=None):
    if math.isqrt(N) ** 2 != N:
        raise ValueError(f"N={N} khong phai so chinh phuong")
    if N > len(SYMBOLS):
        raise ValueError(f"N={N} vuot qua so ky hieu ho tro ({len(SYMBOLS)})")

    rnd = random.Random(seed)
    B = math.isqrt(N)

    def shuffled(seq):
        seq = list(seq)
        rnd.shuffle(seq)
        return seq

    def pattern(r, c):
        return (B * (r % B) + r // B + c) % N

    rows = [g * B + r for g in shuffled(range(B)) for r in shuffled(range(B))]
    cols = [g * B + c for g in shuffled(range(B)) for c in shuffled(range(B))]
    nums = shuffled(range(N))
    grid = [[nums[pattern(r, c)] for c in cols] for r in rows]

    cells = [(r, c) for r in range(N) for c in range(N)]
    for r, c in rnd.sample(cells, int(N * N * holes_ratio)):
        grid[r][c] = None

    return "".join("." if v is None else SYMBOLS[v] for row in grid for v in row)


def validate_puzzle(puzzle, N):
    if len(puzzle) != N * N:
        raise ValueError(f"Do dai {len(puzzle)} khong khop N*N={N*N}")
    valid_chars = set(SYMBOLS[:N]) | {"0", "."}
    bad = set(puzzle) - valid_chars
    if bad:
        raise ValueError(f"Ky tu khong hop le: {bad}")