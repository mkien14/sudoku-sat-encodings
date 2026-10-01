import pytest
from pysat.solvers import Glucose3
from amo_encodings import AMO_METHODS

CUSTOM_METHODS = {
    name: fn for name, fn in AMO_METHODS.items() if not name.startswith("pysat_")
}

def run_amo(amo_fn, lits):
    """Sinh mệnh đề AMO, trả về (clauses, top)."""
    top = max(lits)
    return amo_fn(lits, top)


@pytest.mark.parametrize("name", CUSTOM_METHODS.keys())
@pytest.mark.parametrize("k", range(1, 9))          # k nhỏ để brute force xong nhanh
def test_amo_correctness(name, k):
    """Với mọi tổ hợp gán giá trị cho k literal gốc, solver phải đồng ý
    đúng khi và chỉ khi tổ hợp đó có tối đa 1 literal đúng."""
    amo_fn = CUSTOM_METHODS[name]
    lits = list(range(1, k + 1))
    clauses, _ = run_amo(amo_fn, lits)

    with Glucose3(bootstrap_with=clauses) as s:
        for mask in range(1 << k):
            assumptions = [x if (mask >> (x - 1)) & 1 else -x for x in lits]
            expected_ok = bin(mask).count("1") <= 1
            actual_ok = s.solve(assumptions=assumptions)
            assert actual_ok == expected_ok, (
                f"{name}: k={k}, mask={mask:0{k}b} — "
                f"ky vong {'SAT' if expected_ok else 'UNSAT'}, "
                f"nhung solver tra ve {'SAT' if actual_ok else 'UNSAT'}"
            )


@pytest.mark.parametrize("name", CUSTOM_METHODS.keys())
def test_no_variable_collision(name):
    """Kiem tra ham co tra ve top hop le: top moi phai >= top cu."""
    amo_fn = CUSTOM_METHODS[name]
    lits = [101, 102, 103, 104, 105]
    clauses, new_top = run_amo(amo_fn, lits)
    assert new_top >= max(lits)
    used = {abs(l) for cl in clauses for l in cl}
    aux_vars = used - set(lits)
    assert all(v > max(lits) for v in aux_vars), (
        f"{name}: bien phu {aux_vars} trung hoac nho hon literal goc"
    )