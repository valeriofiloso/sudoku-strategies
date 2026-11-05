"""Mechanical checks of ASD-STE100 writing rules on README.en.md (the English guide).

Checks:
  * procedural sentence (numbered step) > 20 words
  * descriptive sentence > 25 words
  * paragraph > 6 sentences
  * words that end in -ing (STE does not use -ing forms, except in technical names)
  * passive voice in a step (is/are/be + past participle)
  * contractions
  * words from a list of known unapproved words
It also prints the vocabulary (all distinct words), for a manual review
against the ASD-STE100 dictionary.

Usage:  python3 tools/ste_lint.py [--vocab] [--dict PATH]

--dict PATH  compares each word with an ASD-STE100 Issue 9 word list in
             JSON Lines format (for example the data file
             asdste100_issue9_base.jsonl of the PyPI package
             biz-dfch-ste100vocab). The script prints each word that is
             not an approved word. Technical names are not in the list;
             examine these words manually.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

DOC = Path(__file__).resolve().parent.parent / "README.en.md"

TECH_ING = {"pointing", "claiming", "string", "wing", "y-wing", "xy-wing", "xyz-wing", "wxyz-wing", "w-wing"}
UNAPPROVED = {
    "therefore", "however", "since", "should", "would", "could", "may", "might",
    "ensure", "eliminate", "occur", "appear", "need", "needs", "want", "choose",
    "assume", "suppose", "every", "exactly", "either", "otherwise", "unique",
    "solve", "solved", "solving", "solver", "see", "sees", "seen", "place",
    "placed", "contradiction", "really", "very", "just", "simply", "basically",
}
PASSIVE = re.compile(r"\b(is|are|be|been|was|were)\s+(\w+ed|given|shown|made|put|done|found|written|known)\b", re.I)


def prose_blocks(text: str) -> list[tuple[str, str]]:
    """Return (kind, text) blocks. kind = step | desc. Skip code, html, tables."""
    out = []
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    for block in re.split(r"\n\s*\n", text):
        lines = []
        for ln in block.splitlines():
            s = ln.strip()
            if not s or s.startswith("<") or s.startswith("|") or s.startswith("---"):
                continue
            s = re.sub(r"^>\s?", "", s)
            if s.startswith("[!"):
                continue
            lines.append(s)
        if not lines:
            continue
        steps = [l for l in lines if re.match(r"^\d+\.\s", l)]
        bullets = [l for l in lines if l.startswith("- ")]
        for bl in bullets:
            out.append(("desc", bl[2:]))
        for st in steps:
            out.append(("step", re.sub(r"^\d+\.\s", "", st)))
        rest = [l for l in lines if l not in steps and l not in bullets and not l.startswith("#")]
        if rest:
            out.append(("desc", " ".join(rest)))
    return out


def clean(s: str) -> str:
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)    # links
    s = re.sub(r"`[^`]*`", "CODE", s)
    s = re.sub(r"[*_]", "", s)
    return s


def sentences(s: str) -> list[str]:
    parts = re.split(r"(?<=[.!?:])\s+(?=[A-Z0-9\"(])", s)
    return [p for p in parts if p.strip()]


def words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'+\-]*", s)


def main() -> int:
    text = DOC.read_text(encoding="utf-8")
    problems = []
    vocab: Counter = Counter()
    for kind, block in prose_blocks(text):
        b = clean(block)
        sents = sentences(b)
        if kind == "desc" and len(sents) > 6:
            problems.append(f"PARAGRAPH {len(sents)} sentences: {b[:70]}...")
        for snt in sents:
            ws = words(snt)
            lim = 20 if kind == "step" else 25
            if len(ws) > lim:
                problems.append(f"LENGTH {len(ws)}>{lim} [{kind}]: {snt}")
            for w in ws:
                lw = w.lower()
                vocab[lw] += 1
                if lw.endswith("ing") and lw not in TECH_ING and len(lw) > 4:
                    problems.append(f"-ING '{w}': {snt}")
                if lw in UNAPPROVED:
                    problems.append(f"UNAPPROVED '{w}': {snt}")
                if "'" in w:
                    problems.append(f"CONTRACTION '{w}': {snt}")
            if kind == "step" and PASSIVE.search(snt):
                problems.append(f"PASSIVE '{PASSIVE.search(snt).group(0)}': {snt}")
    for p in problems:
        print(p)
    print(f"\n{len(problems)} problems")
    if "--dict" in sys.argv:
        import json
        approved, rejected = set(), {}
        for ln in open(sys.argv[sys.argv.index("--dict") + 1], encoding="utf-8"):
            e = json.loads(ln)
            n = e["name"].lower()
            if e["status"] == "approved":
                approved.add(n)
                approved.update(x.lower() for x in e["spellings"])
            else:
                rejected[n] = [a["name"] for a in e["alternatives"]]
        print("\nNOT APPROVED IN THE WORD LIST (technical names, numbers or errors):")
        for w in sorted(vocab):
            base = w[:-1] if w.endswith("s") else w
            if w in approved or base in approved:
                continue
            tag = f"REJECTED -> {', '.join(rejected[w])}" if w in rejected else "not in list"
            print(f"  {w:16} {tag}")
    if "--vocab" in sys.argv:
        print("\nVOCABULARY:")
        print(", ".join(sorted(vocab)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
