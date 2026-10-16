import math
from itertools import combinations
from pysat.card import CardEnc, EncType

def amo_commander(lits, top, g=3):
    if len(lits) <= 4:
        clauses = [
            [-x, -y]
            for x, y in combinations(lits, 2)
        ]
        return clauses, top

    clauses = []
    commanders = []

    for i in range(0, len(lits), g):
        group = lits[i:i + g]
        clauses.extend(
            [-x, -y]
            for x, y in combinations(group, 2)
        )
        top += 1
        commander = top
        commanders.append(commander)

        for x in group:
            clauses.append([-x, commander])

    sub_clauses, top = amo_commander(
        commanders,
        top,
        g
    )

    clauses.extend(sub_clauses)

    return clauses, top

def amo_product(lits, top):
    k = len(lits)

    if k <= 4:
        clauses = [
            [-x, -y]
            for x, y in combinations(lits, 2)
        ]
        return clauses, top

    p = math.isqrt(k - 1) + 1
    q = (k + p - 1) // p

    rows = [top + i + 1 for i in range(p)]
    cols = [top + p + j + 1 for j in range(q)]

    top += p + q

    clauses = []

    for idx, x in enumerate(lits):
        i, j = divmod(idx, q)

        clauses.append([-x, rows[i]])
        clauses.append([-x, cols[j]])

    row_clauses, top = amo_product(rows, top)
    col_clauses, top = amo_product(cols, top)

    clauses.extend(row_clauses)
    clauses.extend(col_clauses)

    return clauses, top

def amo_pysat(enc):
    def f(lits, top):
        cnf = CardEnc.atmost(lits=lits, bound=1, top_id=top, encoding=enc)
        return cnf.clauses, max(top, cnf.nv)
    return f

AMO_METHODS = {
    "commander": amo_commander,
    "product": amo_product,
    "pysat_pairwise":   amo_pysat(EncType.pairwise),
    "pysat_seqcounter": amo_pysat(EncType.seqcounter),
    "pysat_bitwise":    amo_pysat(EncType.bitwise),
}