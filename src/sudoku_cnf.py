import math

def var(r, c, v, N):
    return r * N * N + c * N + v + 1

def build_clauses(N, puzzle, amo_fn):
    B = math.isqrt(N)
    top = N ** 3
    clauses = []

    def exactly_one(lits):
        nonlocal top, clauses
        clauses.append(list(lits))
        cl, top = amo_fn(lits, top)
        clauses.extend(cl)

    for r in range(N):
        for c in range(N):
            exactly_one([var(r, c, v, N) for v in range(N)])
    for r in range(N):
        for v in range(N):
            exactly_one([var(r, c, v, N) for c in range(N)])
    for c in range(N):
        for v in range(N):
            exactly_one([var(r, c, v, N) for r in range(N)])
    for br in range(B):
        for bc in range(B):
            for v in range(N):
                exactly_one([var(br*B+i, bc*B+j, v, N)
                             for i in range(B) for j in range(B)])
    for idx, ch in enumerate(puzzle):
        if ch not in "0.":
            r, c = divmod(idx, N)
            clauses.append([var(r, c, int(ch, 36) - 1, N)])

    return clauses, top