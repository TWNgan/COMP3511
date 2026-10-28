"""Discrete-time CPU scheduling simulator used to double-check exam answers.

All times are integers. Each algorithm returns a list of (start, end, label) blocks,
merged when the same process runs back-to-back with no scheduling event between.
"""
from collections import deque


def merge(blocks):
    out = []
    for s, e, lab in blocks:
        if out and out[-1][2] == lab and out[-1][1] == s:
            out[-1] = (out[-1][0], e, lab)
        else:
            out.append((s, e, lab))
    return out


def gantt_str(blocks):
    parts = []
    t = None
    for s, e, lab in blocks:
        if t is None or s != t:
            parts.append(str(s))
        parts.append(lab)
        parts.append(str(e))
        t = e
    return " ".join(parts)


def stats(procs, blocks, first_run_end=None):
    """procs: dict name -> (arrival, burst). blocks: merged runs (label = name or 'name@Qk')."""
    comp, first_start = {}, {}
    for s, e, lab in blocks:
        name = lab.split("@")[0]
        if name == "idle":
            continue
        comp[name] = e
        first_start.setdefault(name, s)
    rows = {}
    for n, (a, b) in procs.items():
        tat = comp[n] - a
        wt = tat - b
        rows[n] = dict(arrival=a, burst=b, completion=comp[n], tat=tat, wt=wt,
                       resp_start=first_start[n] - a,
                       resp_course=(first_run_end[n] - a) if first_run_end else None)
    return rows


def print_stats(rows):
    keys = sorted(rows, key=lambda k: int(k[1:]))
    print(f"{'P':4}{'arr':>5}{'bst':>5}{'done':>6}{'TAT':>6}{'WT':>6}{'RT(start)':>11}{'RT(course)':>12}")
    for k in keys:
        r = rows[k]
        rc = r['resp_course'] if r['resp_course'] is not None else '-'
        print(f"{k:4}{r['arrival']:>5}{r['burst']:>5}{r['completion']:>6}{r['tat']:>6}{r['wt']:>6}{r['resp_start']:>11}{rc:>12}")
    n = len(rows)
    print(f"avg TAT = {sum(r['tat'] for r in rows.values())}/{n} = {sum(r['tat'] for r in rows.values())/n:.4g}")
    print(f"avg WT  = {sum(r['wt'] for r in rows.values())}/{n} = {sum(r['wt'] for r in rows.values())/n:.4g}")
    if all(r['resp_course'] is not None for r in rows.values()):
        s = sum(r['resp_course'] for r in rows.values())
        print(f"avg RT(course: end of first run - arrival) = {s}/{n} = {s/n:.4g}")
    s = sum(r['resp_start'] for r in rows.values())
    print(f"avg RT(textbook: first start - arrival) = {s}/{n} = {s/n:.4g}")


# ---------------------------------------------------------------- RR / FCFS
def rr(procs, q=None):
    """q=None -> FCFS. New arrivals at time t are queued BEFORE a process whose quantum expired at t."""
    rem = {n: b for n, (a, b) in procs.items()}
    order = sorted(procs, key=lambda n: (procs[n][0], int(n[1:])))
    queue, t, blocks, run, used = deque(), 0, [], None, 0
    first_end = {}
    pending = deque(order)
    while pending or queue or run:
        while pending and procs[pending[0]][0] <= t:
            queue.append(pending.popleft())
        if run is not None and q is not None and used == q:
            queue.append(run)
            first_end.setdefault(run, t)
            run = None
        if run is None:
            if queue:
                run, used = queue.popleft(), 0
            else:
                blocks.append((t, t + 1, "idle"))
                t += 1
                continue
        blocks.append((t, t + 1, run))
        rem[run] -= 1
        used += 1
        t += 1
        if rem[run] == 0:
            first_end.setdefault(run, t)
            run = None
    return merge(blocks), first_end


# ---------------------------------------------------------------- SJF / SRTF / priority
def pick_min(cands, key):
    return min(cands, key=key)


def sjf(procs, preemptive):
    rem = {n: b for n, (a, b) in procs.items()}
    t, blocks, run = 0, [], None
    first_end, prev = {}, None
    while any(rem.values()):
        ready = [n for n in procs if procs[n][0] <= t and rem[n] > 0]
        if not ready:
            blocks.append((t, t + 1, "idle")); t += 1; continue
        if run is None or preemptive:
            # tie: keep the running one, else earlier arrival, else lower id
            def key(n):
                return (rem[n], 0 if n == run else 1, procs[n][0], int(n[1:]))
            new = pick_min(ready, key)
            if run is not None and new != run and run not in first_end:
                first_end[run] = t
            run = new
        blocks.append((t, t + 1, run))
        rem[run] -= 1
        t += 1
        if rem[run] == 0:
            first_end.setdefault(run, t)
            run = None
    return merge(blocks), first_end


def priority(procs, prio, preemptive, smaller_is_higher=True):
    rem = {n: b for n, (a, b) in procs.items()}
    t, blocks, run = 0, [], None
    first_end = {}
    sign = 1 if smaller_is_higher else -1
    while any(rem.values()):
        ready = [n for n in procs if procs[n][0] <= t and rem[n] > 0]
        if not ready:
            blocks.append((t, t + 1, "idle")); t += 1; continue
        if run is None or preemptive:
            def key(n):
                return (sign * prio[n], 0 if n == run else 1, procs[n][0], int(n[1:]))
            new = min(ready, key=key)
            if run is not None and new != run and run not in first_end:
                first_end[run] = t
            run = new
        blocks.append((t, t + 1, run))
        rem[run] -= 1
        t += 1
        if rem[run] == 0:
            first_end.setdefault(run, t)
            run = None
    return merge(blocks), first_end


# ---------------------------------------------------------------- MLFQ
def mlfq(procs, quanta):
    """quanta: e.g. [4, 8, None]. New jobs enter Q0 tail. A job that uses its full quantum at level k
    moves to the tail of level k+1. A job preempted by a higher-level arrival goes back to the HEAD of
    its own queue and keeps the rest of its quantum. Labels are 'Pn@Qk'."""
    L = len(quanta)
    rem = {n: b for n, (a, b) in procs.items()}
    level = {}
    qleft = {}
    queues = [deque() for _ in range(L)]
    pending = deque(sorted(procs, key=lambda n: (procs[n][0], int(n[1:]))))
    t, blocks, run = 0, [], None
    first_end = {}
    while pending or any(queues) or run:
        while pending and procs[pending[0]][0] <= t:
            n = pending.popleft()
            level[n], qleft[n] = 0, quanta[0]
            queues[0].append(n)
        if run is not None:
            lv = level[run]
            if any(queues[k] for k in range(lv)):
                queues[lv].appendleft(run)   # preempted: head of its own queue
                first_end.setdefault(run, t)
                run = None
        if run is None:
            for k in range(L):
                if queues[k]:
                    run = queues[k].popleft()
                    break
            else:
                blocks.append((t, t + 1, "idle")); t += 1; continue
        blocks.append((t, t + 1, f"{run}@Q{level[run]}"))
        rem[run] -= 1
        if qleft[run] is not None:
            qleft[run] -= 1
        t += 1
        if rem[run] == 0:
            first_end.setdefault(run, t)
            run = None
        elif qleft[run] == 0:
            first_end.setdefault(run, t)
            nl = level[run] + 1
            level[run], qleft[run] = nl, quanta[nl]
            queues[nl].append(run)
            run = None
    return merge(blocks), first_end


# ---------------------------------------------------------------- dynamic priority (S2026 Q4.3 style)
def dynamic_priority(procs, alpha, beta, init, check_every=1, tie_larger_id=True, horizon=1000):
    """Larger value = higher priority. Priority = init + alpha*waited + beta*ran.
    The scheduler decides at t=0, every `check_every` units of the current slice, and immediately
    whenever the CPU becomes free (process finished)."""
    rem = {n: b for n, (a, b) in procs.items()}
    waited = {n: 0 for n in procs}
    ran = {n: 0 for n in procs}
    t, blocks, run, slice_used = 0, [], None, 0
    trace = []
    while any(rem.values()) and t < horizon:
        ready = [n for n in procs if procs[n][0] <= t and rem[n] > 0]
        if not ready:
            blocks.append((t, t + 1, "idle")); t += 1; continue
        if run is None or slice_used == check_every:
            pr = {n: init + alpha * waited[n] + beta * ran[n] for n in ready}
            best = max(ready, key=lambda n: (pr[n], int(n[1:]) if tie_larger_id else -int(n[1:])))
            trace.append((t, dict(pr), best))
            run, slice_used = best, 0
        for n in ready:
            if n == run:
                ran[n] += 1
            else:
                waited[n] += 1
        blocks.append((t, t + 1, run))
        rem[run] -= 1
        slice_used += 1
        t += 1
        if rem[run] == 0:
            run = None
    return merge(blocks), trace


# ---------------------------------------------------------------- RM / EDF
def realtime(tasks, horizon, policy):
    """tasks: dict name -> (C, D_rel, T). Jobs released at k*T with absolute deadline k*T + D.
    Late jobs keep running (not dropped). Ties -> smaller task id (then earlier job)."""
    jobs = []  # [task, release, deadline, remaining]
    t, blocks = 0, []
    finished = []  # (task, release, deadline, finish)
    while t < horizon:
        for n, (C, D, T) in tasks.items():
            if t % T == 0:
                jobs.append([n, t, t + D, C])
        ready = [j for j in jobs if j[3] > 0]
        if not ready:
            blocks.append((t, t + 1, "idle")); t += 1; continue
        if policy == "RM":
            key = lambda j: (tasks[j[0]][2], int(j[0][1:]), j[1])
        else:
            key = lambda j: (j[2], int(j[0][1:]), j[1])
        j = min(ready, key=key)
        blocks.append((t, t + 1, j[0]))
        j[3] -= 1
        t += 1
        if j[3] == 0:
            finished.append((j[0], j[1], j[2], t))
    misses = []
    for n, r, d, rem in jobs:
        if d <= horizon:
            fin = next((f for (tn, tr, td, f) in finished if tn == n and tr == r), None)
            if fin is None or fin > d:
                misses.append((n, r, d, fin))
    return merge(blocks), misses


if __name__ == "__main__":
    print("== S2026 midterm Q4.1 MLFQ (4, 8, FCFS) ==")
    P = {"P1": (0, 9), "P2": (2, 25), "P3": (6, 7), "P4": (14, 18), "P5": (45, 15), "P6": (58, 6)}
    b, fe = mlfq(P, [4, 8, None])
    print(gantt_str(b))
    print_stats(stats(P, b, fe))

    print("\n== Lecture 5.32 MLFQ (4, 8, FCFS) ==")
    P = {"P1": (0, 10), "P2": (2, 15), "P3": (5, 2), "P4": (12, 14), "P5": (18, 6)}
    b, fe = mlfq(P, [4, 8, None])
    print(gantt_str(b))
    print_stats(stats(P, b, fe))

    print("\n== HW2 Q3 MLFQ (4, 8, FCFS) ==")
    P = {"P1": (0, 20), "P2": (1, 5), "P3": (11, 2)}
    b, fe = mlfq(P, [4, 8, None])
    print(gantt_str(b))

    print("\n== Lecture 5.13 RR q=4 ==")
    P = {"P1": (0, 24), "P2": (0, 3), "P3": (0, 3)}
    b, fe = rr(P, 4)
    print(gantt_str(b))
    print_stats(stats(P, b, fe))

    print("\n== Lecture 5.23 SRTF ==")
    P = {"P1": (0, 8), "P2": (1, 4), "P3": (2, 9), "P4": (3, 5)}
    b, fe = sjf(P, True)
    print(gantt_str(b))
    print_stats(stats(P, b, fe))

    print("\n== HW2 SRTF / RR3 ==")
    P = {"P1": (0, 7), "P2": (1, 3), "P3": (4, 5), "P4": (10, 2)}
    b, fe = sjf(P, True); print(gantt_str(b)); print_stats(stats(P, b, fe))
    b, fe = rr(P, 3); print(gantt_str(b)); print_stats(stats(P, b, fe))

    print("\n== Lecture 5.26 priority (non-preemptive, small = high), all arrive 0 ==")
    P = {"P1": (0, 10), "P2": (0, 1), "P3": (0, 2), "P4": (0, 1), "P5": (0, 5)}
    pr = {"P1": 3, "P2": 1, "P3": 4, "P4": 5, "P5": 2}
    b, fe = priority(P, pr, False)
    print(gantt_str(b)); print_stats(stats(P, b, fe))

    print("\n== S2026 Q4.2 RM / EDF 0-16 ==")
    T = {"P1": (1, 3, 4), "P2": (2, 4, 5), "P3": (2, 6, 7), "P4": (1, 5, 8)}
    for pol in ("RM", "EDF"):
        b, m = realtime(T, 16, pol)
        print(pol, gantt_str(b))
        print("  misses:", m)

    print("\n== S2026 Q4.3 dynamic priority ==")
    P = {"P1": (0, 7), "P2": (3, 5), "P3": (6, 6), "P4": (9, 4)}
    b, tr = dynamic_priority(P, 0, 3, 0, 1)
    print("(a)", gantt_str(b))
    P2 = {"P1": (0, 7), "P2": (3, 5)}
    b, tr = dynamic_priority(P2, 1, 0, 0, 3)
    print("(b)", gantt_str(b))
    for x in tr: print("    ", x)
    b, tr = dynamic_priority(P, 1, -2, 30, 3)
    print("(c)", gantt_str(b))
    for x in tr: print("    ", x)
