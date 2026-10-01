# src/encodings.py
import math
from itertools import combinations
from pysat.card import CardEnc, EncType

def amo_pairwise(lits, top):
    return [[-x, -y] for x, y in combinations(lits, 2)], top

def amo_binary(lits, top):
    m = max(1, (len(lits) - 1).bit_length())
    bits = [top + j + 1 for j in range(m)]
    cl = []
    for i, x in enumerate(lits):
        for j, b in enumerate(bits):
            cl.append([-x, b if (i >> j) & 1 else -b])
    return cl, top + m

def amo_seq(lits, top):
    k = len(lits)
    if k < 2:
        return [], top
    s = [top + i + 1 for i in range(k - 1)]
    cl = [[-lits[0], s[0]]]
    for i in range(1, k - 1):
        cl += [[-lits[i], s[i]], [-s[i-1], s[i]], [-lits[i], -s[i-1]]]
    cl.append([-lits[-1], -s[-1]])
    return cl, top + k - 1

def amo_commander(lits, top, g=3):
    if len(lits) <= 4:
        return amo_pairwise(lits, top)
    cl, cmds = [], []
    for i in range(0, len(lits), g):
        grp = lits[i:i+g]
        cl += amo_pairwise(grp, top)[0]
        top += 1
        cmds.append(top)
        cl += [[-x, top] for x in grp]
    sub, top = amo_commander(cmds, top, g)
    return cl + sub, top

def amo_product(lits, top):
    k = len(lits)
    if k <= 4:
        return amo_pairwise(lits, top)
    p = math.isqrt(k - 1) + 1
    q = -(-k // p)
    rows = [top + i + 1 for i in range(p)]
    cols = [top + p + j + 1 for j in range(q)]
    top += p + q
    cl = []
    for idx, x in enumerate(lits):
        i, j = divmod(idx, q)
        cl += [[-x, rows[i]], [-x, cols[j]]]
    c1, top = amo_product(rows, top)
    c2, top = amo_product(cols, top)
    return cl + c1 + c2, top

def amo_pysat(enc):
    def f(lits, top):
        cnf = CardEnc.atmost(lits=lits, bound=1, top_id=top, encoding=enc)
        return cnf.clauses, max(top, cnf.nv)
    return f

AMO_METHODS = {
    "binomial":    amo_pairwise,
    "binary":      amo_binary,
    "sequential":  amo_seq,
    "commander":   amo_commander,
    "product":     amo_product,
    "pysat_pairwise":   amo_pysat(EncType.pairwise),
    "pysat_seqcounter": amo_pysat(EncType.seqcounter),
    "pysat_bitwise":    amo_pysat(EncType.bitwise),
}