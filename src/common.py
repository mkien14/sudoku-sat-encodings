# src/common.py
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class SolveResult:
    method: str             
    N: int
    sat: bool
    solve_time: float
    encode_time: float = 0.0
    n_vars: int = 0
    n_clauses: int = 0
    grid: Optional[List[List[int]]] = None
    extra: dict = None       # thong tin rieng cua tung solver (vd: so nut branch-and-bound)