"""Shared model for the guide figures: cell names, units, and a small
constraint checker that proves each example's claims.

Cell names follow the app convention: rows A-I (top to bottom),
columns 1-9 (left to right). "E5" is row E, column 5.

Verification model
------------------
Each example lists only the cells and candidates that matter. A cell's
domain is its shown candidates; an "open" cell also gets the value 0,
which stands for "a digit that the figure does not show". All non-zero
values must be different inside each row, column and box. A list of
(unit, digit) requirements states the premises of the pattern, for
example "row B must contain a 4". The checker enumerates every
assignment and confirms that:
  * at least one assignment exists (the premises are consistent);
  * each claimed removal (cell, digit) never holds;
  * each claimed placement (cell, digit) always holds.
"""

from __future__ import annotations

from itertools import product

ROWS = "ABCDEFGHI"


def rc(cell: str) -> tuple[int, int]:
    """'E5' -> (4, 4) zero-based (row, col)."""
    return ROWS.index(cell[0]), int(cell[1]) - 1


def name(r: int, c: int) -> str:
    return f"{ROWS[r]}{c + 1}"


def box_of(cell: str) -> int:
    r, c = rc(cell)
    return (r // 3) * 3 + c // 3


def unit_cells(unit: tuple[str, object]) -> list[str]:
    kind, key = unit
    if kind == "row":
        r = ROWS.index(key)
        return [name(r, c) for c in range(9)]
    if kind == "col":
        c = int(key) - 1
        return [name(r, c) for r in range(9)]
    if kind == "box":
        b = int(key) - 1
        r0, c0 = (b // 3) * 3, (b % 3) * 3
        return [name(r0 + i, c0 + j) for i in range(3) for j in range(3)]
    raise ValueError(kind)


ALL_UNITS = (
    [("row", r) for r in ROWS]
    + [("col", c) for c in range(1, 10)]
    + [("box", b) for b in range(1, 10)]
)


def peers(a: str, b: str) -> bool:
    ra, ca = rc(a)
    rb, cb = rc(b)
    return a != b and (ra == rb or ca == cb or box_of(a) == box_of(b))


def solve_all(domains: dict[str, set[int]], require: list[tuple[tuple, int]],
              limit: int = 100000) -> list[dict[str, int]]:
    """Enumerate assignments with backtracking (small examples only)."""
    cells = sorted(domains, key=lambda x: len(domains[x]))
    req = [(set(unit_cells(u)) & set(domains), d) for u, d in require]
    out: list[dict[str, int]] = []
    assign: dict[str, int] = {}

    def ok(cell: str, v: int) -> bool:
        if v == 0:
            return True
        return all(not (assign[o] == v and peers(cell, o)) for o in assign)

    def req_ok(final: bool) -> bool:
        for cs, d in req:
            if any(assign.get(c) == d for c in cs):
                continue
            if final:
                return False
            if not any(c not in assign and d in domains[c] for c in cs):
                return False
        return True

    def rec(i: int) -> None:
        if len(out) >= limit:
            return
        if i == len(cells):
            if req_ok(True):
                out.append(dict(assign))
            return
        cell = cells[i]
        for v in sorted(domains[cell]):
            if ok(cell, v):
                assign[cell] = v
                if req_ok(False):
                    rec(i + 1)
                del assign[cell]

    rec(0)
    return out


def domains_of(ex: dict) -> dict[str, set[int]]:
    dom: dict[str, set[int]] = {}
    for cell, d in ex.get("givens", {}).items():
        dom[cell] = {d}
    closed = set(ex.get("closed", []))
    for cell, cs in ex.get("cands", {}).items():
        s = set(cs)
        if cell not in closed and not ex.get("all_closed"):
            s.add(0)
        dom[cell] = s
    return dom


def verify(ex: dict) -> str:
    dom = domains_of(ex)
    sols = solve_all(dom, ex.get("require", []))
    if not sols:
        raise AssertionError(f"{ex['id']}: premises have no assignment")
    for cell, d in ex.get("claims", {}).get("remove", []):
        bad = [s for s in sols if s.get(cell) == d]
        if bad:
            raise AssertionError(f"{ex['id']}: removal {cell}={d} can hold: {bad[0]}")
    for cell, d in ex.get("claims", {}).get("place", []):
        bad = [s for s in sols if s.get(cell) != d]
        if bad:
            raise AssertionError(f"{ex['id']}: placement {cell}={d} can fail: {bad[0]}")
    return f"{ex['id']}: OK ({len(sols)} assignments checked)"
