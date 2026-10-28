import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sched import *

def show(title, P, b, fe):
    print(title); print("  ", gantt_str(b)); 
    rows = stats(P, b, fe); 
    print("   WT:", {k: rows[k]['wt'] for k in sorted(rows, key=lambda k:int(k[1:]))}, "avg", round(sum(r['wt'] for r in rows.values())/len(rows),4))
    print("   TAT:", {k: rows[k]['tat'] for k in sorted(rows, key=lambda k:int(k[1:]))}, "avg", round(sum(r['tat'] for r in rows.values())/len(rows),4))
    print("   RT(course):", {k: rows[k]['resp_course'] for k in sorted(rows, key=lambda k:int(k[1:]))})

print("===== F19 Q3.6")
P = {"P1":(0,8),"P2":(7,13),"P3":(9,1),"P4":(11,5),"P5":(20,7),"P6":(27,1)}
b,fe = rr(P,None); show("FCFS",P,b,fe)
b,fe = sjf(P,False); show("SJF",P,b,fe)
b,fe = rr(P,4); show("RR4",P,b,fe)
b,fe = sjf(P,True); show("SRTF",P,b,fe)

print("===== F20 Q4.1")
P = {"P1":(0,9),"P2":(3,3),"P3":(8,2),"P4":(10,6),"P5":(16,8),"P6":(20,5)}
b,fe = rr(P,None); show("FCFS",P,b,fe)
b,fe = sjf(P,False); show("SJF",P,b,fe)
b,fe = sjf(P,True); show("SRTF",P,b,fe)

print("===== Sp21 Q2.1")
P = {"P1":(0,2),"P2":(4,12),"P3":(6,6),"P4":(9,4),"P5":(13,5)}
b,fe = rr(P,None); show("FCFS",P,b,fe)
b,fe = sjf(P,False); show("SJF",P,b,fe)
b,fe = rr(P,8); show("RR8",P,b,fe)
b,fe = sjf(P,True); show("SRTF",P,b,fe)

print("===== Sp21 Q2.2 MLFQ 2,4,FCFS")
P = {"P1":(0,10),"P2":(10,8),"P3":(8,30),"P4":(16,2),"P5":(22,8),"P6":(6,22)}
b,fe = mlfq(P,[2,4,None]); show("MLFQ",P,b,fe)

print("===== Sp21 Q2.3 EDF/RM 0-14")
T = {"P1":(1,3,3),"P2":(2,4,4)}
for pol in ("EDF","RM"):
    b,m = realtime(T,14,pol); print(pol, gantt_str(b), "misses", m)

print("===== F19 Q3.4 EDF 0-38")
T = {"P1":(4,10,10),"P2":(2,16,16),"P3":(8,20,20)}
b,m = realtime(T,38,"EDF"); print("EDF", gantt_str(b), "misses", m)
b,m = realtime(T,38,"RM"); print("RM ", gantt_str(b), "misses", m)

print("===== F20 Q4.3 priority (small=high) preemptive + RR q=4 within same priority")
