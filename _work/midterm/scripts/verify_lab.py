"""Verify synchronization and scheduling answers from the lab slides by exhaustive search / simulation."""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from sched import gantt_str, mlfq, priority, rr, sjf, stats, realtime  # noqa: E402


# ------------------------------------------------------------------ race-condition values
def race_values(t1, t2, init):
    """t1/t2: lists of step functions f(shared, regs) -> None. Returns the set of final c values."""
    vals = set()
    n1, n2 = len(t1), len(t2)
    for pos in itertools.combinations(range(n1 + n2), n2):
        sh, r1, r2 = dict(init), {}, {}
        i = j = 0
        for k in range(n1 + n2):
            if k in pos:
                t2[j](sh, r2); j += 1
            else:
                t1[i](sh, r1); i += 1
        vals.add(sh["c"])
    return sorted(vals)


lab6_q7 = race_values(
    [lambda s, r: r.__setitem__("b", s["b"]), lambda s, r: s.__setitem__("a", r["b"] + 1),
     lambda s, r: r.__setitem__("a", s["a"]), lambda s, r: r.__setitem__("b2", s["b"]),
     lambda s, r: s.__setitem__("c", r["a"] - r["b2"])],
    [lambda s, r: s.__setitem__("a", 13), lambda s, r: s.__setitem__("b", 10), lambda s, r: s.__setitem__("c", 2)],
    {"a": 1, "b": 3, "c": 0})
print("Lab6 Q7 race values:", lab6_q7, "(official -6, 1, 2, 3, 10)")


# ------------------------------------------------------------------ semaphore programs (explicit-state search)
def explore(progs, sems, loop=None, max_out=40):
    """progs: dict name -> list of ops ('wait',S) ('signal',S) ('print',x); loop: set of names that repeat forever.
    Returns set of (output, finished_all) at terminal states."""
    loop = loop or set()
    start = (tuple(0 for _ in progs), tuple(sorted(sems.items())), "")
    names = list(progs)
    seen, results, stack = set(), set(), [start]
    while stack:
        pcs, sm, out = stack.pop()
        if (pcs, sm, out) in seen or len(out) > max_out:
            continue
        seen.add((pcs, sm, out))
        sem = dict(sm)
        moved = False
        for idx, nm in enumerate(names):
            ops, pc = progs[nm], pcs[idx]
            if pc >= len(ops):
                if nm in loop:
                    pc = 0
                else:
                    continue
            op = ops[pc]
            if op[0] == "wait" and sem[op[1]] <= 0:
                continue
            ns, no = dict(sem), out
            if op[0] == "wait":
                ns[op[1]] -= 1
            elif op[0] == "signal":
                ns[op[1]] += 1
            else:
                no += op[1]
            np = list(pcs)
            np[idx] = pc + 1
            stack.append((tuple(np), tuple(sorted(ns.items())), no))
            moved = True
        if not moved:
            done = all(pcs[i] >= len(progs[n]) and n not in loop for i, n in enumerate(names))
            results.add((out, done))
    return results


q4 = explore({"A": [("wait", "X"), ("print", "b"), ("signal", "Y"), ("wait", "Y"), ("print", "c"), ("signal", "Y")],
              "B": [("signal", "X"), ("print", "a"), ("wait", "Y"), ("print", "d")]}, {"X": 0, "Y": 0})
print("Lab6 Q4 complete:", sorted(o for o, d in q4 if d), "| stuck:", sorted(o for o, d in q4 if not d))

q5 = explore({"P0": [("wait", "S0"), ("print", "1"), ("signal", "S1"), ("signal", "S2"), ("signal", "S3")],
              "P1": [("wait", "S1"), ("signal", "S0")],
              "P2": [("wait", "S2"), ("signal", "S0"), ("wait", "S3"), ("signal", "S0")]},
             {"S0": 1, "S1": 0, "S2": 0, "S3": 0}, loop={"P0"})
print("Lab6 Q5 number of '1' at terminal states:", sorted(set(len(o) for o, d in q5)), "(official 4)")

q1 = explore({"T1": [("wait", "S1"), ("print", "1"), ("signal", "S2")] * 2,
              "T2": [("wait", "S2"), ("print", "2"), ("signal", "S3")] * 2,
              "T3": [("wait", "S3"), ("print", "3"), ("signal", "S1")] * 2},
             {"S1": 1, "S2": 0, "S3": 0})
print("Lab6 Q1 (S1=1,S2=0,S3=0) orders:", sorted(o for o, d in q1))

f19 = explore({"P1": [("wait", "L"), ("print", "C"), ("signal", "R")],
               "P2": [("wait", "R"), ("print", "A"), ("print", "B"), ("signal", "R")],
               "P3": [("wait", "R"), ("print", "D")]},
              {"L": 3, "R": 0}, loop={"P1", "P2", "P3"}, max_out=14)
reach = set()
for o, d in f19:
    reach.add(o)
print("F19 Q4.4 'CABACDBCABDD' reachable prefix check:", "CABACDBCABDD" in {o[:12] for o in reach} or any(o.startswith("CABACDBCABDD") for o in reach))

# ------------------------------------------------------------------ scheduling examples
print("\nPA2 MLFQ example:", gantt_str(mlfq({"P1": (0, 7), "P2": (1, 1), "P3": (4, 1), "P4": (6, 3)}, [2, 4, None])[0]))
P = {"P1": (0, 7), "P2": (0, 4), "P3": (0, 1), "P4": (0, 4)}
for q in (8, 4, 2):
    b, fe = rr(P, q)
    rows = stats(P, b, fe)
    print("Lab5 RR q=%d:" % q, gantt_str(b), "| avg WT", sum(r["wt"] for r in rows.values()) / 4)
b, fe = sjf(P, False)
print("Lab5 SJF:", gantt_str(b), "| avg WT", sum(r["wt"] for r in stats(P, b, fe).values()) / 4)
P2 = {"P1": (0, 7), "P2": (2, 4), "P3": (4, 1), "P4": (5, 4)}
b, fe = sjf(P2, True)
print("Lab5 SRTF:", gantt_str(b), "| avg WT", sum(r["wt"] for r in stats(P2, b, fe).values()) / 4)
b, fe = priority(P, {"P1": 4, "P2": 1, "P3": 2, "P4": 3}, False)
print("Lab5 Priority:", gantt_str(b), "| avg WT", sum(r["wt"] for r in stats(P, b, fe).values()) / 4)
T = {"P1": (1, 2, 4), "P2": (2, 5, 6), "P3": (3, 7, 9)}
for pol in ("RM", "EDF"):
    b, m = realtime(T, 18, pol)
    print("Lab5 %s:" % pol, gantt_str(b), "| misses:", m)
