import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "src"))
import pytest
from pysat.solvers import Glucose3
from amo_encodings import AMO_METHODS

CUSTOM_METHODS = {
    name: fn
    for name, fn in AMO_METHODS.items()
    if not name.startswith("pysat_")
}

def run_amo(amo_fn, lits):
    top = max((abs(x) for x in lits), default=0)
    return amo_fn(lits, top)

@pytest.mark.parametrize("name", AMO_METHODS.keys())
@pytest.mark.parametrize("k", range(1, 9))
def test_amo_correctness(name, k):
    amo_fn = AMO_METHODS[name]
    lits = list(range(1, k + 1))

    clauses, _ = run_amo(amo_fn, lits)

    with Glucose3(bootstrap_with=clauses) as solver:
        for mask in range(1 << k):
            assumptions = [
                x if (mask >> (x - 1)) & 1 else -x
                for x in lits
            ]

            expected_ok = bin(mask).count("1") <= 1

            actual_ok = solver.solve(assumptions=assumptions)

            assert actual_ok == expected_ok, (
                f"Phương pháp: {name}; "
                f"số biến: {k}; "
                f"phép gán: {mask:0{k}b}; "
                f"kết quả mong đợi: "
                f"{'SAT' if expected_ok else 'UNSAT'}; "
                f"kết quả thực tế: "
                f"{'SAT' if actual_ok else 'UNSAT'}"
            )

@pytest.mark.parametrize("name", AMO_METHODS.keys())
def test_no_variable_collision(name):
    amo_fn = AMO_METHODS[name]
    lits = [101, 102, 103, 104, 105]

    clauses, new_top = run_amo(amo_fn, lits)

    assert new_top >= max(lits), (
        f"Phương pháp {name}: "
        f"ID biến lớn nhất sau mã hóa nhỏ hơn ID biến đầu vào lớn nhất."
    )

    input_vars = {abs(x) for x in lits}

    used_vars = {
        abs(lit)
        for clause in clauses
        for lit in clause
    }

    aux_vars = used_vars - input_vars

    assert all(v > max(input_vars) for v in aux_vars), (
        f"Phương pháp {name}: "
        f"biến phụ bị trùng hoặc có ID nhỏ hơn biến đầu vào: "
        f"{aux_vars}"
    )

    assert all(v <= new_top for v in used_vars), (
        f"Phương pháp {name}: "
        f"có biến được sử dụng vượt quá ID biến lớn nhất new_top."
    )

@pytest.mark.parametrize("name", AMO_METHODS.keys())
def test_empty_and_singleton_inputs(name):
    amo_fn = AMO_METHODS[name]

    for lits in ([], [1]):
        top = max(lits, default=0)
        clauses, new_top = amo_fn(lits, top)

        assert clauses == [], (
            f"Phương pháp {name}: "
            f"không mong đợi mệnh đề CNF khi đầu vào là {lits}."
        )

        assert new_top >= top, (
            f"Phương pháp {name}: "
            f"ID biến lớn nhất sau mã hóa nhỏ hơn ID ban đầu."
        )
