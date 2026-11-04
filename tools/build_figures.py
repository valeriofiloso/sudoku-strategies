"""Build every SVG figure of the guide and prove every example.

Usage (from the guide folder):
    python3 tools/build_figures.py

Output: figures/*.svg. The script stops with an error if one example
claim is not logically correct.
"""

from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))

from examples import EX  # noqa: E402
from sudoku_model import ALL_UNITS, ROWS, domains_of, rc, solve_all, unit_cells, verify  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "figures"
FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"

FILL = {
    "focus": "#FFE27A",
    "pattern": "#B9F0B1",
    "pivot": "#FFC48A",
    "blocked": "#F9D3D6",
    "chain": "#E4D7FF",
}
TINT = "#E6F0FF"
OUTLINE = "#2F6FEB"
MARK = {
    "key": "#2563EB",
    "key2": "#9333EA",
    "remove": "#E11D48",
    "place": "#16A34A",
}
LINK = "#7C3AED"
LEVELS = [
    ("Level 1", "Singles", "#16A34A", "#4ADE80"),
    ("Level 2", "Subsets", "#0891B2", "#22D3EE"),
    ("Level 3", "Intersections", "#2563EB", "#60A5FA"),
    ("Level 4", "Fish", "#4F46E5", "#818CF8"),
    ("Level 5", "Single-digit chains", "#9333EA", "#C084FC"),
    ("Level 6", "Wings", "#DB2777", "#F472B6"),
    ("Level 7", "Chains", "#EA580C", "#FB923C"),
    ("Level 8", "Uniqueness", "#DC2626", "#F87171"),
]

S = 54          # cell size
PAD = 30        # space for labels


def cand_xy(cell: str, d: int, r0: int, c0: int) -> tuple[float, float]:
    r, c = rc(cell)
    x = PAD + (c - c0) * S + ((d - 1) % 3 + 0.5) * S / 3
    y = PAD + (r - r0) * S + ((d - 1) // 3 + 0.5) * S / 3
    return x, y


def grid_svg(ex: dict) -> str:
    rv0, rv1, cv0, cv1 = ex.get("view", ("A", "I", 1, 9))
    r0, r1 = ROWS.index(rv0), ROWS.index(rv1)
    c0, c1 = cv0 - 1, cv1 - 1
    nr, nc = r1 - r0 + 1, c1 - c0 + 1
    W, H = PAD + nc * S + 12, PAD + nr * S + 12
    o: list[str] = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'width="{W}" height="{H}" font-family="{FONT}">')
    o.append('<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" '
             'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
             '<path d="M0,0 L10,5 L0,10 z" fill="#E11D48"/></marker></defs>')
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="14" fill="#FFFFFF"/>')

    def inview(cell):
        r, c = rc(cell)
        return r0 <= r <= r1 and c0 <= c <= c1

    def cx(c):
        return PAD + (c - c0) * S

    def ry(r):
        return PAD + (r - r0) * S

    # labels
    for c in range(c0, c1 + 1):
        o.append(f'<text x="{cx(c) + S / 2}" y="{PAD - 10}" text-anchor="middle" '
                 f'font-size="13" fill="#6B7280">{c + 1}</text>')
    for r in range(r0, r1 + 1):
        o.append(f'<text x="{PAD - 14}" y="{ry(r) + S / 2 + 5}" text-anchor="middle" '
                 f'font-size="13" fill="#6B7280">{ROWS[r]}</text>')

    # tints, then fills
    tinted = set()
    for u in ex.get("tint", []):
        tinted |= set(unit_cells(u))
    for cell in tinted:
        if inview(cell):
            r, c = rc(cell)
            o.append(f'<rect x="{cx(c)}" y="{ry(r)}" width="{S}" height="{S}" fill="{TINT}"/>')
    for cell, role in ex.get("fills", {}).items():
        if inview(cell):
            r, c = rc(cell)
            o.append(f'<rect x="{cx(c)}" y="{ry(r)}" width="{S}" height="{S}" fill="{FILL[role]}"/>')

    # thin lines
    for c in range(c0, c1 + 2):
        o.append(f'<line x1="{cx(c)}" y1="{ry(r0)}" x2="{cx(c)}" y2="{ry(r1 + 1)}" '
                 f'stroke="#C3C9D3" stroke-width="1"/>')
    for r in range(r0, r1 + 2):
        o.append(f'<line x1="{cx(c0)}" y1="{ry(r)}" x2="{cx(c1 + 1)}" y2="{ry(r)}" '
                 f'stroke="#C3C9D3" stroke-width="1"/>')
    # box lines
    for c in range(c0, c1 + 2):
        if c % 3 == 0 or c in (c0, c1 + 1):
            o.append(f'<line x1="{cx(c)}" y1="{ry(r0)}" x2="{cx(c)}" y2="{ry(r1 + 1)}" '
                     f'stroke="#1F2937" stroke-width="2.4"/>')
    for r in range(r0, r1 + 2):
        if r % 3 == 0 or r in (r0, r1 + 1):
            o.append(f'<line x1="{cx(c0)}" y1="{ry(r)}" x2="{cx(c1 + 1)}" y2="{ry(r)}" '
                     f'stroke="#1F2937" stroke-width="2.4"/>')

    # rays (hidden single)
    for a, b in ex.get("rays", []):
        (ra, ca), (rb, cb) = rc(a), rc(b)
        x1, y1 = cx(ca) + S / 2, ry(ra) + S / 2
        x2, y2 = cx(cb) + S / 2, ry(rb) + S / 2
        # stop the arrow at the edge of the target cell
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5
        x2 -= dx / L * S * 0.32
        y2 -= dy / L * S * 0.32
        x1 += dx / L * S * 0.3
        y1 += dy / L * S * 0.3
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="#E11D48" stroke-opacity="0.55" stroke-width="5" '
                 f'stroke-linecap="round" marker-end="url(#arr)"/>')

    # outlines
    for u in ex.get("outline", []):
        cells = [x for x in unit_cells(u) if inview(x)]
        if not cells:
            continue
        rs = [rc(x)[0] for x in cells]
        cs = [rc(x)[1] for x in cells]
        x, y = cx(min(cs)) + 2, ry(min(rs)) + 2
        w, h = (max(cs) - min(cs) + 1) * S - 4, (max(rs) - min(rs) + 1) * S - 4
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="none" '
                 f'stroke="{OUTLINE}" stroke-width="3.2"/>')

    # givens
    for cell, d in ex.get("givens", {}).items():
        if inview(cell):
            r, c = rc(cell)
            o.append(f'<text x="{cx(c) + S / 2}" y="{ry(r) + S / 2 + 11}" text-anchor="middle" '
                     f'font-size="31" fill="#111827">{d}</text>')

    # links (under the candidate marks)
    for (a, da), (b, db), kind in ex.get("links", []):
        x1, y1 = cand_xy(a, da, r0, c0)
        x2, y2 = cand_xy(b, db, r0, c0)
        dash = ' stroke-dasharray="7 6"' if kind == "weak" else ""
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{LINK}" stroke-width="3" stroke-linecap="round" '
                 f'stroke-opacity="0.85"{dash}/>')

    # candidates
    marks = ex.get("marks", {})
    show = ex.get("show_cands", {})
    for cell, ds in ex.get("cands", {}).items():
        if not inview(cell):
            continue
        for d in show.get(cell, ds):
            x, y = cand_xy(cell, d, r0, c0)
            m = marks.get((cell, d))
            if m:
                o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.6" fill="{MARK[m]}"/>')
                o.append(f'<text x="{x:.1f}" y="{y + 4.6:.1f}" text-anchor="middle" '
                         f'font-size="13" font-weight="700" fill="#FFFFFF">{d}</text>')
            else:
                o.append(f'<text x="{x:.1f}" y="{y + 4.6:.1f}" text-anchor="middle" '
                         f'font-size="13" fill="#374151">{d}</text>')
    o.append("</svg>")
    return "\n".join(o)


def banner_svg(i: int) -> str:
    lvl, title, c1, c2 = LEVELS[i]
    W, H = 900, 96
    dots = "".join(
        f'<circle cx="{W - 250 + k * 28}" cy="{H / 2}" r="9" '
        f'fill="#FFFFFF" fill-opacity="{0.95 if k <= i else 0.3}"/>'
        for k in range(8))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
            f'height="{H}" font-family="{FONT}">'
            f'<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{c1}"/>'
            f'<stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" rx="18" fill="url(#g)"/>'
            f'<text x="32" y="40" font-size="17" font-weight="600" fill="#FFFFFF" '
            f'fill-opacity="0.85" letter-spacing="2">{lvl.upper()}</text>'
            f'<text x="32" y="74" font-size="30" font-weight="800" fill="#FFFFFF">{escape(title)}</text>'
            f'{dots}</svg>')


def cover_svg() -> str:
    W, H = 900, 260
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" font-family="{FONT}">',
         '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
         '<stop offset="0" stop-color="#0F172A"/><stop offset="1" stop-color="#312E81"/>'
         '</linearGradient></defs>',
         f'<rect width="{W}" height="{H}" rx="22" fill="url(#g)"/>']
    # rainbow mini grid
    cols = [lv[3] for lv in LEVELS] + ["#FACC15"]
    digits = [5, 3, 0, 0, 7, 0, 0, 0, 0, 6, 0, 0, 1, 9, 5, 0, 0, 0, 0, 9, 8, 0, 0, 0, 0, 6, 0,
              8, 0, 0, 0, 6, 0, 0, 0, 3, 4, 0, 0, 8, 0, 3, 0, 0, 1, 7, 0, 0, 0, 2, 0, 0, 0, 6,
              0, 6, 0, 0, 0, 0, 2, 8, 0, 0, 0, 0, 4, 1, 9, 0, 0, 5, 0, 0, 0, 0, 8, 0, 0, 7, 9]
    gx, gy, cs = 690, 28, 22.4
    for k in range(81):
        r, c = divmod(k, 9)
        col = cols[(r // 3) * 3 + c // 3]
        o.append(f'<rect x="{gx + c * cs:.1f}" y="{gy + r * cs:.1f}" width="{cs - 2:.1f}" '
                 f'height="{cs - 2:.1f}" rx="4" fill="{col}" fill-opacity="{0.9 if digits[k] else 0.25}"/>')
        if digits[k]:
            o.append(f'<text x="{gx + c * cs + cs / 2 - 1:.1f}" y="{gy + r * cs + cs / 2 + 4:.1f}" '
                     f'text-anchor="middle" font-size="12" font-weight="700" fill="#0F172A">{digits[k]}</text>')
    o.append('<text x="40" y="96" font-size="50" font-weight="800" fill="#FFFFFF">Sudoku</text>')
    o.append('<text x="40" y="150" font-size="50" font-weight="800" fill="#FDE68A">Strategies</text>')
    o.append('<text x="42" y="196" font-size="17" fill="#C7D2FE">23 strategies, 8 levels, '
             'one logic: remove the candidates that cannot be correct.</text>')
    o.append('<text x="42" y="228" font-size="14" fill="#A5B4FC" letter-spacing="1.5">'
             'WRITTEN IN ASD-STE100 SIMPLIFIED TECHNICAL ENGLISH</text>')
    o.append("</svg>")
    return "\n".join(o)


MAP = [
    ["Naked Single", "Hidden Single"],
    ["Naked Pair", "Hidden Pair", "Naked Triple", "Hidden Triple", "Naked Quad", "Hidden Quad"],
    ["Pointing", "Claiming"],
    ["X-Wing", "Swordfish", "Jellyfish"],
    ["Skyscraper", "2-String Kite", "Turbot Fish", "Empty Rectangle"],
    ["XY-Wing", "XYZ-Wing", "WXYZ-Wing", "W-Wing"],
    ["XY-Chain"],
    ["BUG+1"],
]


def map_svg() -> str:
    W, rowh = 900, 50
    H = 20 + rowh * len(MAP) + 10
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" rx="18" fill="#FFFFFF"/>']
    for i, names in enumerate(MAP):
        lvl, title, c1, c2 = LEVELS[i]
        y = 20 + i * rowh
        o.append(f'<rect x="18" y="{y}" width="170" height="38" rx="19" fill="{c1}"/>')
        o.append(f'<text x="103" y="{y + 25}" text-anchor="middle" font-size="14" '
                 f'font-weight="700" fill="#FFFFFF">{lvl}: {escape(title.split()[0])}</text>')
        x = 200
        for n in names:
            w = 20 + 7.3 * len(n)
            o.append(f'<rect x="{x}" y="{y + 3}" width="{w:.0f}" height="32" rx="16" '
                     f'fill="{c2}" fill-opacity="0.22" stroke="{c1}" stroke-width="1.5"/>')
            o.append(f'<text x="{x + w / 2:.0f}" y="{y + 24}" text-anchor="middle" '
                     f'font-size="13" font-weight="600" fill="#1F2937">{escape(n)}</text>')
            x += w + 8
    o.append("</svg>")
    return "\n".join(o)


def legend_svg() -> str:
    items_fill = [("focus", "Result cell"), ("pattern", "Pattern cell"),
                  ("pivot", "Pivot cell"), ("chain", "Chain cell"), ("blocked", "Blocked cell")]
    items_mark = [("key", "Pattern digit"), ("key2", "Other pattern digit"),
                  ("remove", "Remove this candidate"), ("place", "Correct digit")]
    W, H = 900, 150
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" rx="16" fill="#FFFFFF" stroke="#E5E7EB"/>']
    x = 22
    for role, label in items_fill:
        o.append(f'<rect x="{x}" y="18" width="28" height="28" rx="5" fill="{FILL[role]}" stroke="#9CA3AF"/>')
        o.append(f'<text x="{x + 36}" y="38" font-size="14" fill="#1F2937">{label}</text>')
        x += 36 + 8 * len(label) + 30
    x = 22
    for role, label in items_mark:
        o.append(f'<circle cx="{x + 14}" cy="78" r="11" fill="{MARK[role]}"/>')
        o.append(f'<text x="{x + 14}" y="83" text-anchor="middle" font-size="13" '
                 f'font-weight="700" fill="#FFFFFF">7</text>')
        o.append(f'<text x="{x + 34}" y="83" font-size="14" fill="#1F2937">{label}</text>')
        x += 34 + 8 * len(label) + 34
    y = 122
    o.append(f'<line x1="22" y1="{y}" x2="82" y2="{y}" stroke="{LINK}" stroke-width="3"/>')
    o.append(f'<text x="92" y="{y + 5}" font-size="14" fill="#1F2937">Strong link</text>')
    o.append(f'<line x1="220" y1="{y}" x2="280" y2="{y}" stroke="{LINK}" stroke-width="3" stroke-dasharray="7 6"/>')
    o.append(f'<text x="290" y="{y + 5}" font-size="14" fill="#1F2937">Weak link</text>')
    o.append(f'<rect x="410" y="{y - 13}" width="60" height="26" rx="6" fill="none" '
             f'stroke="{OUTLINE}" stroke-width="3"/>')
    o.append(f'<text x="480" y="{y + 5}" font-size="14" fill="#1F2937">Unit of the pattern</text>')
    o.append(f'<rect x="650" y="{y - 13}" width="26" height="26" rx="4" fill="{TINT}" stroke="#9CA3AF"/>')
    o.append(f'<text x="686" y="{y + 5}" font-size="14" fill="#1F2937">Base unit</text>')
    o.append("</svg>")
    return "\n".join(o)


ANATOMY = dict(
    id="anatomy",
    givens={},
    cands={},
    tint=[("row", "C"), ("col", 7)],
    fills={**{c: "chain" for c in unit_cells(("box", 5))}, "C7": "focus"},
    outline=[("row", "C"), ("col", 7), ("box", 5)],
)


def anatomy_svg() -> str:
    s = grid_svg(ANATOMY)
    extra = (f'<text x="{PAD + 6 * S + S / 2}" y="{PAD + 2 * S + S / 2 + 6}" text-anchor="middle" '
             f'font-size="15" font-weight="700" fill="#92400E">C7</text>'
             f'<text x="{PAD + 1 * S}" y="{PAD + 2 * S + S / 2 + 6}" text-anchor="middle" '
             f'font-size="14" font-weight="700" fill="#1D4ED8">row C</text>'
             f'<text x="{PAD + 6 * S + S / 2}" y="{PAD + 7 * S + S / 2 + 6}" text-anchor="middle" '
             f'font-size="13" font-weight="700" fill="#1D4ED8">col 7</text>'
             f'<text x="{PAD + 4 * S + S / 2}" y="{PAD + 4 * S + S / 2 + 6}" text-anchor="middle" '
             f'font-size="14" font-weight="700" fill="#6D28D9">box 5</text>')
    return s.replace("</svg>", extra + "</svg>")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # 1. prove every example
    for ex in EX:
        print(verify(ex))
    # extra proof for BUG+1: without the digit 1 in B6 the grid has no solution
    bug = next(e for e in EX if e["id"] == "bug_plus_one")
    dom = domains_of(bug)
    dom["B6"] = dom["B6"] - {1}
    n = len(solve_all(dom, bug["require"], limit=5))
    assert n == 0, "BUG+1: the grid without 1 in B6 must have no solution"
    full = solve_all(domains_of(bug), bug["require"], limit=5)
    assert len(full) == 1, "BUG+1: the grid must have one solution only"
    print("bug_plus_one: OK (B6 without 1 -> 0 solutions; full grid -> 1 solution)")
    # 2. write figures
    for ex in EX:
        (OUT / f"{ex['id']}.svg").write_text(grid_svg(ex), encoding="utf-8")
    for i in range(len(LEVELS)):
        (OUT / f"level{i + 1}.svg").write_text(banner_svg(i), encoding="utf-8")
    (OUT / "cover.svg").write_text(cover_svg(), encoding="utf-8")
    (OUT / "map.svg").write_text(map_svg(), encoding="utf-8")
    (OUT / "legend.svg").write_text(legend_svg(), encoding="utf-8")
    (OUT / "anatomy.svg").write_text(anatomy_svg(), encoding="utf-8")
    print(f"wrote {len(list(OUT.glob('*.svg')))} figures to {OUT}")


if __name__ == "__main__":
    main()
