import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sched import *

print("== Practice S1: MLFQ Q0 RR2 / Q1 RR4 / Q2 FCFS ==")
P = {"P1": (0, 7), "P2": (1, 10), "P3": (3, 3), "P4": (9, 8), "P5": (14, 2)}
b, fe = mlfq(P, [2, 4, None]); print(gantt_str(b)); print_stats(stats(P, b, fe))

print("\n== Practice S2: RM / EDF 0-15 ==")
T = {"P1": (1, 2, 3), "P2": (2, 4, 5), "P3": (2, 7, 8)}
for pol in ("RM", "EDF"):
    b, m = realtime(T, 15, pol); print(pol, gantt_str(b)); print("  misses:", m)
print("U =", 1/3 + 2/5 + 2/8)

print("\n== Practice S3: dynamic priority a=2 b=-1 init 0, check every 2, ties larger id ==")
P = {"P1": (0, 5), "P2": (1, 3), "P3": (2, 4)}
b, tr = dynamic_priority(P, 2, -1, 0, 2); print(gantt_str(b))
for x in tr: print("   ", x)

print("\n== Practice S4: SRTF and RR q=2 ==")
P = {"P1": (0, 6), "P2": (1, 3), "P3": (2, 1), "P4": (4, 2)}
b, fe = sjf(P, True); print("SRTF", gantt_str(b)); print_stats(stats(P, b, fe))
b, fe = sjf(P, False); print("SJF ", gantt_str(b)); print_stats(stats(P, b, fe))
b, fe = rr(P, 2); print("RR2 ", gantt_str(b)); print_stats(stats(P, b, fe))
