"""Example definitions for every strategy in the guide.

Each example drives two things:
  1. the SVG figure (fills, marks, links, unit outlines);
  2. the logical proof in sudoku_model.verify (domains, requirements, claims).

Roles for cell fills:
  focus   - yellow : the cell where the result happens
  pattern - green  : the cells that make the pattern
  pivot   - orange : the centre cell of a wing
  blocked - rose   : a cell that cannot hold the digit
  chain   - violet : a cell in a chain
Marks on candidates:
  key    - blue circle  : the digit that makes the pattern
  key2   - violet circle: a second digit of the pattern
  remove - red circle   : the candidate that you remove
  place  - green circle : the digit that you write in the cell
"""

from sudoku_model import ALL_UNITS

EX: list[dict] = []


def add(**kw):
    EX.append(kw)
    return kw


def row_cells(r, cands):
    """cands: list of 9 items; int = given, str = candidates."""
    givens, cs = {}, {}
    for i, v in enumerate(cands):
        cell = f"{r}{i + 1}"
        if isinstance(v, int):
            givens[cell] = v
        else:
            cs[cell] = [int(ch) for ch in v]
    return givens, cs


def all_digits(unit):
    return [(unit, d) for d in range(1, 10)]


# --------------------------------------------------------------------------
# Level 1: singles
# --------------------------------------------------------------------------
add(
    id="naked_single",
    givens={"E1": 1, "E2": 2, "E9": 3, "A5": 4, "C5": 5, "H5": 6, "D4": 7, "F6": 8},
    cands={"E5": list(range(1, 10))},
    closed=["E5"],
    show_cands={"E5": [9]},
    fills={"E5": "focus"},
    tint=[("row", "E"), ("col", 5), ("box", 5)],
    marks={("E5", 9): "place"},
    claims={"place": [("E5", 9)]},
)

add(
    id="hidden_single",
    givens={"A7": 5, "B5": 5, "G1": 5, "E2": 5, "B2": 8},
    cands={c: [5] for c in ["A1", "A2", "A3", "B1", "B3", "C1", "C2", "C3"]},
    show_cands={"C3": [5], **{c: [] for c in ["A1", "A2", "A3", "B1", "B3", "C1", "C2"]}},
    fills={**{c: "blocked" for c in ["A1", "A2", "A3", "B1", "B3", "C1", "C2"]}, "C3": "focus"},
    outline=[("box", 1)],
    rays=[("A7", "A3"), ("B5", "B3"), ("G1", "C1"), ("E2", "C2")],
    marks={("C3", 5): "place"},
    require=[(("box", 1), 5)],
    claims={"place": [("C3", 5)]},
)

# --------------------------------------------------------------------------
# Level 2: subsets (one row or one box; the unit shows all candidates)
# --------------------------------------------------------------------------
g, c = row_cells("D", ["27", "27", "125", 3, "578", "168", 4, "269", "79"])
add(
    id="naked_pair", view=("D", "D", 1, 9), givens=g, cands=c, all_closed=True,
    fills={"D1": "pattern", "D2": "pattern", "D3": "focus", "D5": "focus",
           "D8": "focus", "D9": "focus"},
    outline=[("row", "D")],
    marks={("D1", 2): "key", ("D1", 7): "key", ("D2", 2): "key", ("D2", 7): "key",
           ("D3", 2): "remove", ("D8", 2): "remove", ("D5", 7): "remove", ("D9", 7): "remove"},
    require=all_digits(("row", "D")),
    claims={"remove": [("D3", 2), ("D8", 2), ("D5", 7), ("D9", 7)]},
)

g, c = row_cells("D", ["18", "1468", "138", 2, "39", 5, "3469", "79", "379"])
add(
    id="hidden_pair", view=("D", "D", 1, 9), givens=g, cands=c, all_closed=True,
    fills={"D2": "pattern", "D7": "pattern"},
    outline=[("row", "D")],
    marks={("D2", 4): "key", ("D2", 6): "key", ("D7", 4): "key", ("D7", 6): "key",
           ("D2", 1): "remove", ("D2", 8): "remove", ("D7", 3): "remove", ("D7", 9): "remove"},
    require=all_digits(("row", "D")),
    claims={"remove": [("D2", 1), ("D2", 8), ("D7", 3), ("D7", 9)]},
)

g, c = row_cells("D", ["36", "135", 9, "38", "267", "18", "68", 4, "257"])
add(
    id="naked_triple", view=("D", "D", 1, 9), givens=g, cands=c, all_closed=True,
    fills={"D1": "pattern", "D4": "pattern", "D7": "pattern",
           "D2": "focus", "D5": "focus", "D6": "focus"},
    outline=[("row", "D")],
    marks={("D1", 3): "key", ("D1", 6): "key", ("D4", 3): "key", ("D4", 8): "key",
           ("D7", 6): "key", ("D7", 8): "key",
           ("D2", 3): "remove", ("D5", 6): "remove", ("D6", 8): "remove"},
    require=all_digits(("row", "D")),
    claims={"remove": [("D2", 3), ("D5", 6), ("D6", 8)]},
)

add(
    id="hidden_triple", view=("A", "C", 1, 3),
    givens={"A2": 9},
    cands={"A1": [2, 4, 5, 8], "A3": [1, 3, 4], "B1": [1, 4, 8], "B2": [3, 6, 8],
           "B3": [1, 2, 7], "C1": [4, 6], "C2": [3, 5, 6, 7], "C3": [1, 3, 6]},
    all_closed=True,
    fills={"A1": "pattern", "B3": "pattern", "C2": "pattern"},
    outline=[("box", 1)],
    marks={("A1", 2): "key", ("A1", 5): "key", ("B3", 2): "key", ("B3", 7): "key",
           ("C2", 5): "key", ("C2", 7): "key",
           ("A1", 4): "remove", ("A1", 8): "remove", ("B3", 1): "remove",
           ("C2", 3): "remove", ("C2", 6): "remove"},
    require=all_digits(("box", 1)),
    claims={"remove": [("A1", 4), ("A1", 8), ("B3", 1), ("C2", 3), ("C2", 6)]},
)

g, c = row_cells("D", ["15", "257", "158", "378", "589", 4, "239", "19", 6])
add(
    id="naked_quad", view=("D", "D", 1, 9), givens=g, cands=c, all_closed=True,
    fills={"D1": "pattern", "D3": "pattern", "D5": "pattern", "D8": "pattern",
           "D2": "focus", "D4": "focus", "D7": "focus"},
    outline=[("row", "D")],
    marks={**{(x, d): "key" for x, ds in [("D1", "15"), ("D3", "158"), ("D5", "589"), ("D8", "19")]
              for d in map(int, ds)},
           ("D2", 5): "remove", ("D4", 8): "remove", ("D7", 9): "remove"},
    require=all_digits(("row", "D")),
    claims={"remove": [("D2", 5), ("D4", 8), ("D7", 9)]},
)

g, c = row_cells("D", ["147", "237", "2469", "35", "258", "136", "378", "489", "57"])
add(
    id="hidden_quad", view=("D", "D", 1, 9), givens=g, cands=c, all_closed=True,
    fills={"D1": "pattern", "D3": "pattern", "D6": "pattern", "D8": "pattern"},
    outline=[("row", "D")],
    marks={**{(x, d): "key" for x, ds in [("D1", "14"), ("D3", "469"), ("D6", "16"), ("D8", "49")]
              for d in map(int, ds)},
           ("D1", 7): "remove", ("D3", 2): "remove", ("D6", 3): "remove", ("D8", 8): "remove"},
    require=all_digits(("row", "D")),
    claims={"remove": [("D1", 7), ("D3", 2), ("D6", 3), ("D8", 8)]},
)

# --------------------------------------------------------------------------
# Level 3: intersections (only one digit shows)
# --------------------------------------------------------------------------
add(
    id="pointing", view=("A", "C", 1, 9),
    givens={"B1": 1, "B2": 6, "C1": 4, "C3": 8, "A1": 7},
    cands={"A2": [3], "A3": [3], "A5": [3], "A8": [3], "B6": [3], "C9": [3], "B7": [3]},
    fills={"A2": "pattern", "A3": "pattern", "A5": "focus", "A8": "focus"},
    outline=[("box", 1), ("row", "A")],
    marks={("A2", 3): "key", ("A3", 3): "key", ("A5", 3): "remove", ("A8", 3): "remove"},
    require=[(("box", 1), 3)],
    claims={"remove": [("A5", 3), ("A8", 3)]},
)

add(
    id="claiming", view=("G", "I", 1, 9),
    givens={"G1": 2, "G3": 5, "G5": 9},
    cands={"G7": [7], "G9": [7], "H8": [7], "I7": [7], "H2": [7], "I4": [7]},
    fills={"G7": "pattern", "G9": "pattern", "H8": "focus", "I7": "focus"},
    outline=[("row", "G"), ("box", 9)],
    marks={("G7", 7): "key", ("G9", 7): "key", ("H8", 7): "remove", ("I7", 7): "remove"},
    require=[(("row", "G"), 7)],
    claims={"remove": [("H8", 7), ("I7", 7)]},
)

# --------------------------------------------------------------------------
# Level 4: fish (only one digit shows)
# --------------------------------------------------------------------------
add(
    id="x_wing",
    cands={c: [4] for c in ["B2", "B7", "G2", "G7", "E2", "I2", "D7", "E5", "H9"]},
    fills={"B2": "pattern", "B7": "pattern", "G2": "pattern", "G7": "pattern",
           "E2": "focus", "I2": "focus", "D7": "focus"},
    tint=[("row", "B"), ("row", "G")],
    outline=[("col", 2), ("col", 7)],
    links=[(("B2", 4), ("B7", 4), "strong"), (("G2", 4), ("G7", 4), "strong")],
    marks={("B2", 4): "key", ("B7", 4): "key", ("G2", 4): "key", ("G7", 4): "key",
           ("E2", 4): "remove", ("I2", 4): "remove", ("D7", 4): "remove"},
    require=[(("row", "B"), 4), (("row", "G"), 4)],
    claims={"remove": [("E2", 4), ("I2", 4), ("D7", 4)]},
)

add(
    id="swordfish",
    cands={c: [2] for c in ["B1", "B5", "E5", "E8", "H1", "H8", "D1", "G5", "C8", "D4", "G3"]},
    fills={**{c: "pattern" for c in ["B1", "B5", "E5", "E8", "H1", "H8"]},
           "D1": "focus", "G5": "focus", "C8": "focus"},
    tint=[("row", "B"), ("row", "E"), ("row", "H")],
    outline=[("col", 1), ("col", 5), ("col", 8)],
    marks={**{(c, 2): "key" for c in ["B1", "B5", "E5", "E8", "H1", "H8"]},
           ("D1", 2): "remove", ("G5", 2): "remove", ("C8", 2): "remove"},
    require=[(("row", "B"), 2), (("row", "E"), 2), (("row", "H"), 2)],
    claims={"remove": [("D1", 2), ("G5", 2), ("C8", 2)]},
)

_jf = ["A2", "A9", "C4", "C6", "F2", "F4", "I6", "I9"]
add(
    id="jellyfish",
    cands={c: [6] for c in _jf + ["D2", "E6", "H4", "G9", "D7", "B5"]},
    fills={**{c: "pattern" for c in _jf},
           "D2": "focus", "E6": "focus", "H4": "focus", "G9": "focus"},
    tint=[("row", "A"), ("row", "C"), ("row", "F"), ("row", "I")],
    outline=[("col", 2), ("col", 4), ("col", 6), ("col", 9)],
    marks={**{(c, 6): "key" for c in _jf},
           ("D2", 6): "remove", ("E6", 6): "remove", ("H4", 6): "remove", ("G9", 6): "remove"},
    require=[(("row", r), 6) for r in "ACFI"],
    claims={"remove": [("D2", 6), ("E6", 6), ("H4", 6), ("G9", 6)]},
)

# --------------------------------------------------------------------------
# Level 5: single-digit chains (only one digit shows)
# --------------------------------------------------------------------------
add(
    id="skyscraper",
    cands={c: [1] for c in ["C2", "H2", "A6", "H6", "A3", "C5", "E8", "G9"]},
    fills={"C2": "pattern", "H2": "pattern", "A6": "pattern", "H6": "pattern",
           "A3": "focus", "C5": "focus"},
    outline=[("col", 2), ("col", 6)],
    links=[(("C2", 1), ("H2", 1), "strong"), (("A6", 1), ("H6", 1), "strong"),
           (("H2", 1), ("H6", 1), "weak")],
    marks={("C2", 1): "key", ("H2", 1): "key", ("A6", 1): "key", ("H6", 1): "key",
           ("A3", 1): "remove", ("C5", 1): "remove"},
    require=[(("col", 2), 1), (("col", 6), 1)],
    claims={"remove": [("A3", 1), ("C5", 1)]},
)

add(
    id="kite",
    cands={c: [5] for c in ["B2", "B8", "A3", "G3", "G8", "E6", "I5"]},
    fills={"B2": "pattern", "B8": "pattern", "A3": "pattern", "G3": "pattern", "G8": "focus"},
    outline=[("row", "B"), ("col", 3), ("box", 1)],
    links=[(("B2", 5), ("B8", 5), "strong"), (("A3", 5), ("G3", 5), "strong"),
           (("B2", 5), ("A3", 5), "weak")],
    marks={("B2", 5): "key", ("B8", 5): "key", ("A3", 5): "key", ("G3", 5): "key",
           ("G8", 5): "remove"},
    require=[(("row", "B"), 5), (("col", 3), 5)],
    claims={"remove": [("G8", 5)]},
)

add(
    id="turbot",
    cands={c: [7] for c in ["B1", "F1", "F5", "D6", "B6", "H3", "C8"]},
    fills={"B1": "pattern", "F1": "pattern", "F5": "pattern", "D6": "pattern", "B6": "focus"},
    outline=[("col", 1), ("box", 5)],
    links=[(("B1", 7), ("F1", 7), "strong"), (("F1", 7), ("F5", 7), "weak"),
           (("F5", 7), ("D6", 7), "strong")],
    marks={("B1", 7): "key", ("F1", 7): "key", ("F5", 7): "key", ("D6", 7): "key",
           ("B6", 7): "remove"},
    require=[(("col", 1), 7), (("box", 5), 7)],
    claims={"remove": [("B6", 7)]},
)

add(
    id="empty_rectangle",
    givens={"E5": 3},
    cands={c: [8] for c in ["E4", "E6", "D5", "F5", "B8", "E8", "B5", "H2", "A1"]},
    fills={"E4": "pattern", "E6": "pattern", "D5": "pattern", "F5": "pattern",
           "B8": "pattern", "E8": "pattern", "B5": "focus"},
    outline=[("box", 5), ("col", 8)],
    tint=[("row", "E"), ("col", 5)],
    links=[(("B8", 8), ("E8", 8), "strong")],
    marks={("E4", 8): "key", ("E6", 8): "key", ("D5", 8): "key", ("F5", 8): "key",
           ("B8", 8): "key2", ("E8", 8): "key2", ("B5", 8): "remove"},
    require=[(("box", 5), 8), (("col", 8), 8)],
    claims={"remove": [("B5", 8)]},
)

# --------------------------------------------------------------------------
# Level 6: wings (bivalue cells are complete; target cells are open)
# --------------------------------------------------------------------------
add(
    id="xy_wing",
    cands={"E5": [2, 7], "E1": [2, 9], "H5": [7, 9], "H1": [3, 9]},
    closed=["E5", "E1", "H5"],
    fills={"E5": "pivot", "E1": "pattern", "H5": "pattern", "H1": "focus"},
    links=[(("E5", 2), ("E1", 2), "weak"), (("E5", 7), ("H5", 7), "weak")],
    marks={("E5", 2): "key", ("E5", 7): "key2", ("E1", 2): "key", ("H5", 7): "key2",
           ("E1", 9): "place", ("H5", 9): "place", ("H1", 9): "remove"},
    claims={"remove": [("H1", 9)]},
)

add(
    id="xyz_wing",
    cands={"E5": [1, 2, 3], "E2": [1, 3], "F6": [2, 3], "E4": [3, 8], "E6": [3, 5]},
    closed=["E5", "E2", "F6"],
    fills={"E5": "pivot", "E2": "pattern", "F6": "pattern", "E4": "focus", "E6": "focus"},
    outline=[("box", 5)],
    marks={("E5", 3): "place", ("E2", 3): "place", ("F6", 3): "place",
           ("E5", 1): "key", ("E2", 1): "key", ("E5", 2): "key2", ("F6", 2): "key2",
           ("E4", 3): "remove", ("E6", 3): "remove"},
    claims={"remove": [("E4", 3), ("E6", 3)]},
)

add(
    id="wxyz_wing",
    cands={"E5": [1, 2, 3, 4], "E1": [1, 4], "E8": [2, 4], "D6": [3, 4],
           "E4": [4, 9], "E6": [4, 7]},
    closed=["E5", "E1", "E8", "D6"],
    fills={"E5": "pivot", "E1": "pattern", "E8": "pattern", "D6": "pattern",
           "E4": "focus", "E6": "focus"},
    outline=[("box", 5), ("row", "E")],
    marks={("E5", 4): "place", ("E1", 4): "place", ("E8", 4): "place", ("D6", 4): "place",
           ("E4", 4): "remove", ("E6", 4): "remove"},
    claims={"remove": [("E4", 4), ("E6", 4)]},
)

add(
    id="w_wing",
    cands={"A2": [1, 5], "B5": [1, 5], "C2": [1, 7], "C5": [1], "B3": [5, 7]},
    closed=["A2", "B5"],
    fills={"A2": "pattern", "B5": "pattern", "C2": "chain", "C5": "chain", "B3": "focus"},
    outline=[("row", "C")],
    links=[(("C2", 1), ("C5", 1), "strong"), (("A2", 1), ("C2", 1), "weak"),
           (("B5", 1), ("C5", 1), "weak")],
    marks={("A2", 1): "key2", ("B5", 1): "key2", ("C2", 1): "key2", ("C5", 1): "key2",
           ("A2", 5): "place", ("B5", 5): "place", ("B3", 5): "remove"},
    require=[(("row", "C"), 1)],
    claims={"remove": [("B3", 5)]},
)

# --------------------------------------------------------------------------
# Level 7: XY-Chain
# --------------------------------------------------------------------------
add(
    id="xy_chain",
    cands={"A1": [1, 2], "A5": [2, 3], "D5": [3, 4], "D9": [1, 4], "A9": [1, 6], "D1": [1, 8]},
    closed=["A1", "A5", "D5", "D9"],
    fills={"A1": "chain", "A5": "chain", "D5": "chain", "D9": "chain",
           "A9": "focus", "D1": "focus"},
    links=[(("A1", 2), ("A5", 2), "weak"), (("A5", 3), ("D5", 3), "weak"),
           (("D5", 4), ("D9", 4), "weak")],
    marks={("A1", 1): "place", ("D9", 1): "place",
           ("A1", 2): "key", ("A5", 2): "key", ("A5", 3): "key2", ("D5", 3): "key2",
           ("D5", 4): "key", ("D9", 4): "key",
           ("A9", 1): "remove", ("D1", 1): "remove"},
    claims={"remove": [("A9", 1), ("D1", 1)]},
)

# --------------------------------------------------------------------------
# Level 8: BUG+1 (a full, real grid; found and proved by tools/find_bug.py)
# --------------------------------------------------------------------------
_BUG = """
69 17 59 2 4 15 67 3 8
17 8 3 16 69 159 25 4 27
4 2 56 7 3 8 56 1 9
5 9 8 4 7 3 1 2 6
2 4 1 5 8 6 9 7 3
3 6 7 9 1 2 8 5 4
69 13 2 13 69 7 4 8 5
8 37 4 36 5 19 27 69 12
17 5 69 8 2 4 3 69 17
"""


def _parse_bug():
    givens, cands = {}, {}
    for r, line in zip("ABCDEFGHI", _BUG.strip().splitlines()):
        for c, tok in enumerate(line.split(), start=1):
            cell = f"{r}{c}"
            if len(tok) == 1:
                givens[cell] = int(tok)
            else:
                cands[cell] = [int(ch) for ch in tok]
    return givens, cands


_bg, _bc = _parse_bug()
add(
    id="bug_plus_one",
    givens=_bg, cands=_bc, all_closed=True,
    fills={**{c: "chain" for c in _bc}, "B6": "focus"},
    outline=[("row", "B"), ("col", 6), ("box", 2)],
    marks={("B6", 1): "place", ("B6", 5): "remove", ("B6", 9): "remove",
           ("B1", 1): "key", ("B4", 1): "key", ("A6", 1): "key", ("H6", 1): "key"},
    require=[(u, d) for u in ALL_UNITS for d in range(1, 10)],
    claims={"place": [("B6", 1)], "remove": [("B6", 5), ("B6", 9)]},
)
