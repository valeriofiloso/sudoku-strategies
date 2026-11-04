"""Search for a BUG+1 example grid (used once to make the example in examples.py).

Usage: python3 tools/find_bug.py [seed]
"""
import random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sudoku_model import ALL_UNITS, unit_cells, name, solve_all, peers

random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 3)

def solved_grid():
    g = {}
    cells = [name(r, c) for r in range(9) for c in range(9)]
    def rec(i):
        if i == 81:
            return True
        c = cells[i]
        ds = list(range(1, 10)); random.shuffle(ds)
        for d in ds:
            if all(not (g.get(o) == d and peers(c, o)) for o in g):
                g[c] = d
                if rec(i + 1):
                    return True
                del g[c]
        return False
    rec(0)
    return g

units = [set(unit_cells(u)) for u in ALL_UNITS]

def try_once(T, n):
    cells = [name(r, c) for r in range(9) for c in range(9)]
    U = set(random.sample(cells, n))
    if any(len(U & u) == 1 for u in units):
        return None
    X = random.choice(sorted(U)); c = T[X]
    # unit membership
    cu = {x: [u for u in units if x in u] for x in U}
    tv = [{T[x] for x in (U & u)} for u in units]
    need = []  # remaining multiset per unit
    for i, u in enumerate(units):
        m = {d: 1 for d in tv[i]}
        if X in u:
            m[c] = 2
        need.append(m)
    uidx = {x: [i for i, u in enumerate(units) if x in u] for x in U}
    order = sorted(U, key=lambda x: x != X)
    extra = {}
    def rec(k):
        if k == len(order):
            return all(all(v == 0 for v in m.values()) for m in need)
        x = order[k]
        if x == X:
            opts = [(a, b) for a in range(1, 10) for b in range(a + 1, 10) if c not in (a, b)]
        else:
            opts = [(a,) for a in range(1, 10) if a != T[x]]
        random.shuffle(opts)
        for o in opts:
            okk = True
            for i in uidx[x]:
                for a in o:
                    if need[i].get(a, 0) <= 0:
                        okk = False
            if not okk:
                continue
            if len(o) == 2 and o[0] == o[1]:
                continue
            for i in uidx[x]:
                for a in o:
                    need[i][a] -= 1
            extra[x] = o
            if rec(k + 1):
                return True
            for i in uidx[x]:
                for a in o:
                    need[i][a] += 1
            del extra[x]
        return False
    if not rec(0):
        return None
    return U, X, extra


def try_U(T, U, X):
    c = T[X]
    U = set(U) | {X}
    if any(len(U & u) == 1 for u in units):
        return None
    tv = [{T[x] for x in (U & u)} for u in units]
    need = []
    for i, u in enumerate(units):
        m = {d: 1 for d in tv[i]}
        if X in u:
            m[c] = 2
        need.append(m)
    uidx = {x: [i for i, u in enumerate(units) if x in u] for x in U}
    order = sorted(U, key=lambda x: (x != X, x))
    extra = {}
    cnt=[0]
    def rec(k):
        cnt[0]+=1
        if cnt[0]>200000: return False
        if k == len(order):
            return all(all(v == 0 for v in m.values()) for m in need)
        x = order[k]
        if x == X:
            opts = [(a, b) for a in range(1, 10) for b in range(a + 1, 10) if c not in (a, b)]
        else:
            opts = [(a,) for a in range(1, 10) if a != T[x]]
        random.shuffle(opts)
        for o in opts:
            if any(need[i].get(a, 0) <= 0 for i in uidx[x] for a in o):
                continue
            for i in uidx[x]:
                for a in o: need[i][a] -= 1
            extra[x] = o
            if rec(k + 1): return True
            for i in uidx[x]:
                for a in o: need[i][a] += 1
            del extra[x]
        return False
    if not rec(0): return None
    return U, X, extra

allc=[name(r, c) for r in range(9) for c in range(9)]
req = [(u, d) for u in ALL_UNITS for d in range(1, 10)]
import time; t0=time.time()
found=False
while time.time()-t0<240 and not found:
    T = solved_grid()
    blanks = random.sample(allc, random.choice([40,45,50]))
    dom = {x: (set(range(1,10)) if x in blanks else {T[x]}) for x in allc}
    sols = solve_all(dom, req, limit=6)
    others=[s for s in sols if s!=T]
    if not others: continue
    for Tp in others:
        D=[x for x in allc if T[x]!=Tp[x]]
        for X in random.sample(allc, 81):
            res=try_U(T, D, X)
            if not res: continue
            U,X,extra=res
            dom = {x: ({T[x], *extra[x]} if x in U else {T[x]}) for x in allc}
            s1 = solve_all(dom, req, limit=5)
            if len(s1)!=1: continue
            d2=dict(dom); d2[X]=dom[X]-{T[X]}
            s2=solve_all(d2, req, limit=5)
            print("FOUND n=",len(U),"X=",X,"c=",T[X],"bug sols=",len(s2))
            for r in "ABCDEFGHI":
                print(" ".join("".join(map(str, sorted(dom[f"{r}{c}"]))).ljust(4) for c in range(1, 10)))
            found=True; break
        if found: break
print("done", found)
