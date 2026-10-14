import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "src"))
from puzzle_gen import SYMBOLS, symbol_to_value, make_puzzle

def test_symbol_roundtrip():
    for i, ch in enumerate(SYMBOLS):
        assert symbol_to_value(ch) == i

def test_case_sensitive_regression():
    assert symbol_to_value("A") == 9 and symbol_to_value("a") == 35

def test_make_puzzle_deterministic():
    assert make_puzzle(16, 0.5, 1) == make_puzzle(16, 0.5, 1)