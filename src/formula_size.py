from functools import lru_cache

SAT_ENCODING = {
    "sat_commander": "commander", "sat_product": "product",
    "sat_pysat_pairwise": "pysat_pairwise", "sat_pysat_seqcounter": "pysat_seqcounter",
    "sat_pysat_bitwise": "pysat_bitwise",
}


@lru_cache(maxsize=None)
def _group_size(enc, k):
    from amo_encodings import AMO_METHODS
    clauses, top = AMO_METHODS[enc](list(range(1, k + 1)), k)
    return len(clauses), top - k


def size_of(method, N, n_holes):
    clues = N * N - n_holes
    if method in SAT_ENCODING:
        n_amo, n_aux = _group_size(SAT_ENCODING[method], N)
        groups = 4 * N * N
        return N ** 3 + groups * n_aux, groups * (1 + n_amo) + clues, None
    if method in ("cplex_mip", "gurobi"):
        return N ** 3, None, 4 * N * N + clues
    if method == "cplex_cp":
        return N * N, None, 3 * N + clues
    raise KeyError(f"Phuong phap khong biet: {method}")