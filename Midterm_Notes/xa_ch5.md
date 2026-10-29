# Answer Bank — Chapter 5 CPU Scheduling (anticipated questions)

> Conventions used in every answer: TAT = completion − arrival; WT = TAT − CPU burst; RT = end of the first run on the CPU − arrival (slide 5.12). RR: a new arrival enters the ready queue before the process whose quantum just expired. Priority: smaller number = higher. Ties: FCFS, then smaller ID; SRTF/EDF ties do not preempt. MLFQ and priority + RR: a preempted job returns to the head of its queue with its remaining quantum. Soft real-time: a late job keeps running and counts as one miss.

## [X5-01] ch5 | CPU–I/O burst cycle and burst distribution
Describe the CPU–I/O burst cycle. What does the histogram of CPU-burst times show, and why does it matter for scheduling?

**Answer:**
- **Process execution consists of a cycle of CPU execution and I/O wait — a CPU burst followed by an I/O burst**, alternating until the process ends. While one process waits for I/O, the **CPU scheduler** gives the CPU to another ready process, so some process is running at all times → **maximize CPU utilization** (the goal of multiprogramming).
- Measured CPU bursts follow a **long-tail distribution: many short CPU bursts and a small number of long ones**. An **I/O-bound** program has **many short CPU bursts**; a **CPU-bound** program has **a few long CPU bursts**.
- This distribution is **important for designing the scheduling algorithm**, e.g., choosing the RR quantum (about 80% of bursts shorter than q) and favouring short bursts (SJF, MLFQ) to cut the average waiting time.

## [X5-02] ch5 | Distinguish I/O-bound from CPU-bound processes
Why is it important for the scheduler to distinguish I/O-bound processes from CPU-bound processes?

**Answer:**
Because they use the CPU very differently: an **I/O-bound process runs only short CPU bursts and seldom uses its full quantum**, while a **CPU-bound process runs long bursts and uses its whole quantum**.
- Giving **I/O-bound processes higher priority** lets them start their next I/O quickly, keeping **I/O devices busy** and giving **short response time** to interactive jobs; the CPU-bound process uses the CPU while they wait → better **CPU and device utilization**.
- Treating them alike (e.g., FCFS) makes I/O-bound jobs wait behind a CPU-bound one (**convoy effect**) and leaves the devices idle.
- MLFQ makes this distinction automatically: **CPU-bound jobs sink to lower queues, I/O-bound jobs stay near the top**.

## [X5-03] ch5 | Four scheduling decision points, which preemptive
List the four situations in which CPU-scheduling decisions take place. Which of them are preemptive?

**Answer:**
CPU scheduling may take place when a process:
1. **switches from running to waiting** (e.g., I/O request, `wait()`);
2. **terminates**;
3. **switches from running to ready** (e.g., an **interrupt — timer / quantum expiry**);
4. **switches from waiting to ready** (e.g., **I/O completion**), or a **new process arrives** in the ready queue (new → ready) with a higher priority.

**Cases 1 and 2 are non-preemptive** — the process **gives up the CPU voluntarily** and a new process must be selected. **Cases 3 and 4 are preemptive** — the CPU can be **taken away involuntarily**. A scheduler that acts only in cases 1 and 2 is non-preemptive (cooperative).

## [X5-04] ch5 | Preemptive vs non-preemptive scheduling issues
Distinguish preemptive and non-preemptive scheduling. What problems does preemption introduce?

**Answer:**
- **Non-preemptive**: once a process gets the CPU it **keeps it until it terminates or blocks** (releases it voluntarily). Simple, low overhead, but a long process can **monopolize the CPU** (poor response time, convoy effect). E.g., FCFS, SJF.
- **Preemptive**: the OS can **take the CPU away** on a **timer interrupt (quantum expiry)** or when a **higher-priority / shorter process becomes ready**. Better **response time**, no monopolization. E.g., RR, SRTF, preemptive priority, MLFQ.
- Problems of preemption: (1) **more context switches (overhead)**; (2) **access to shared data** — a process preempted while updating shared data can leave it **inconsistent (race condition)**, so synchronization is needed; (3) **preemption while in kernel mode** — kernel data structures may be left inconsistent; (4) **interrupts during crucial OS activities** — such code must be protected (e.g., interrupts disabled).

## [X5-05] ch5 | Dispatcher and dispatch latency
What is the dispatcher and what does it do? What is dispatch latency, and why should it be small?

**Answer:**
- The **dispatcher** is the module that **gives control of the CPU to the process selected by the CPU scheduler**. It involves: (1) **switching context** from one process to another; (2) **switching to user mode**; (3) **jumping to the proper location in the user program** to restart it.
- **Dispatch latency** is **the time it takes for the dispatcher to stop one process and start another running**. It is **pure overhead** paid on **every context switch** (typically hundreds per second, visible with `vmstat` on Linux), so the dispatcher must be **as fast as possible**.
- The **scheduler decides which process** runs (policy); the **dispatcher performs the switch** (mechanism).

## [X5-06] ch5 | Scheduling criteria to maximize or minimize
Define the CPU-scheduling criteria and state whether each should be maximized or minimized.

**Answer:**
| Criterion | Definition | Goal |
|---|---|---|
| **CPU utilization** | fraction of time the CPU is busy | maximize |
| **Throughput** | number of processes completed per unit time | maximize |
| **Turnaround time** | time to execute a process = completion − arrival (waiting + CPU + I/O time) | minimize |
| **Waiting time** | total time spent waiting in the **ready queue** = turnaround − CPU burst | minimize |
| **Response time** | time from submission until the **first response** is produced (this course: end of first run − arrival) | minimize |
| **Fairness** | adequate CPU allocation to every process | ensure |

The scheduling algorithm **does not change CPU-burst or I/O time; it only changes the waiting time in the ready queue**. Usually the **average** is optimized, and criteria can conflict (e.g., throughput favours short processes).

## [X5-07] ch5 | Response time definition and computation
Define response time. How is it computed in this course for RR and for non-preemptive algorithms, and why is it important?

**Answer:**
- **Response time is the amount of time from when a request is submitted until the first response is produced**; in this course **RT = completion of the first run on the CPU − arrival time**.
- **RR / MLFQ**: the first run ends at the **end of the first quantum** (or at completion if the burst < q). E.g., RR q = 4 with P1 24, P2 3, P3 3 (all at 0): RT = 4, 7, 10 → **avg 7** (FCFS: 24, 27, 30 → avg 27).
- **Non-preemptive (FCFS, SJF, non-preemptive priority)**: the first run is the whole burst, so **RT = turnaround time**.
- It matters for **interactive (time-sharing) systems**, where users need quick feedback; **RR and MLFQ give short response times**, while turnaround time matters more for batch jobs.

## [X5-08] ch5 | Conflicting scheduling criteria
Explain how these pairs of criteria conflict: CPU utilization vs response time; average turnaround vs maximum waiting time; I/O device utilization vs CPU utilization.

**Answer:**
Scheduling criteria **conflict**, so an algorithm improves some at the expense of others:
- **CPU utilization vs response time**: utilization is highest when **context switches are rare** (long quanta, little overhead), but short response time needs **frequent switching** (short quanta), which adds overhead.
- **Average turnaround vs maximum waiting time**: average turnaround is minimized by running the **shortest jobs first (SJF)**, but long jobs may then wait indefinitely (**starvation**), so the maximum waiting time grows.
- **I/O device utilization vs CPU utilization**: CPU utilization is maximized by letting **CPU-bound jobs run long without switching**; I/O utilization is maximized by dispatching **I/O-bound jobs as soon as they are ready** to start their next I/O, which means more context switches.
- In general, **performance and fairness are often at odds**: optimizing turnaround (SJF) sacrifices fairness; RR is fair but has a longer average turnaround.

## [X5-09] ch5 | FCFS and the convoy effect
Describe FCFS scheduling. What is the convoy effect, and why is FCFS unsuitable for interactive systems?

**Answer:**
- **FCFS** serves processes **in their order of arrival** to the ready queue (FIFO). It is **non-preemptive**: a process keeps the CPU until it **completes its current CPU burst**. It is simple and **starvation-free**.
- **Convoy effect**: **short processes get stuck behind a long process**, so the **average waiting time is long and depends purely on the arrival order** — bursts 24, 3, 3: order P1, P2, P3 → avg WT (0 + 24 + 27)/3 = **17**; order P2, P3, P1 → (6 + 0 + 3)/3 = **3**. With **one CPU-bound and many I/O-bound** processes, the I/O-bound ones wait behind the CPU-bound one → **low I/O device utilization** (and later an idle CPU).
- **Unsuitable for interactive systems**: without preemption, a process cannot be guaranteed **a share of the CPU at regular intervals**, so response time is poor.

## [X5-10] ch5 | Round-robin mechanism and waiting bound
Explain how Round-Robin scheduling works. What does it guarantee with n processes and time quantum q?

**Answer:**
- RR is **FCFS with preemption**: each process gets a small unit of CPU time, the **time quantum q (usually 10–100 ms)**. When the quantum expires, a **timer interrupt** preempts the process and it is **added to the tail of the ready queue**; if its (remaining) burst is **shorter than q**, it releases the CPU itself and the next process runs at once.
- With n ready processes, each gets **1/n of the CPU time in chunks of at most q**, and **no process waits more than (n − 1)q time units** for its next turn (context-switch time ignored).
- RR is **fair** (FIFO order, equal shares), gives **good response time** for interactive jobs and has **no starvation**; its average waiting time can be long.
- Conventions: a **new arrival at the same instant as a quantum expiry enters the ready queue first**; if the queue is empty when the quantum expires, the process simply continues.

## [X5-11] ch5 | Choosing q from the waiting bound
Ten interactive processes share a CPU under RR, and each must wait at most 90 ms in the ready queue before running again. Find the largest quantum (a) ignoring context switches, (b) if every context switch costs 1 ms.

**Answer:**
(a) RR bound: **no process waits more than (n − 1)q** → $(10 - 1)q \le 90$ → **q ≤ 10 ms**.
(b) Between two turns of a process, the other n − 1 processes each run one quantum and **n context switches** occur → worst wait = $(n-1)q + ns$: $9q + 10 \times 1 \le 90$ → $q \le 80/9$ → **q ≤ 8.9 ms**.
- Trade-off: a smaller q gives a tighter bound (better response) but more switching overhead (efficiency q/(q + s)).

## [X5-12] ch5 | Time quantum size effects, 80% rule
How does the size of the time quantum affect RR performance? State the rule of thumb for choosing it.

**Answer:**
- **q too large** (larger than every CPU burst) → each burst finishes in its first quantum → **RR degenerates to FCFS**.
- **q too small** → too many **context switches**; **q must be large with respect to the context-switch time (usually < 10 µs), otherwise the overhead is too high**. In the limit (tiny q, zero switch cost) RR becomes **processor sharing**: each of n processes appears to have **its own processor running at 1/n the speed**.
- **Average turnaround time does not necessarily improve as q increases**; it improves when **most processes finish their CPU burst within a single quantum**. E.g., bursts 6, 3, 1, 7 (all at 0): avg TAT = 11.0 (q = 1), 10.75 (q = 3), 12.25 (q = 5), 10.5 (q ≥ 6).
- **Rule of thumb: about 80% of CPU bursts should be shorter than the time quantum q.**

## [X5-13] ch5 | RR CPU efficiency with context-switch overhead
(a) RR with context-switch cost s = 0.1 ms: CPU efficiency for q = 10, 1 and 0.1 ms when all processes are CPU-bound?
(b) Ten I/O-bound tasks (each computes 1 ms, then does a 10 ms I/O) and one CPU-bound task, s = 0.1 ms: CPU utilization for q = 1 ms and q = 10 ms?

**Answer:**
(a) Each quantum of useful work q is followed by one switch s → **efficiency = q/(q + s)**:
- q = 10 ms: 10/10.1 = **99.0%**; q = 1 ms: 1/1.1 = **90.9%**; q = 0.1 ms: 0.1/0.2 = **50%** → **a quantum close to the switch time wastes the CPU**. (A process that blocks after a burst b < q gives b/(b + s).)

(b) Each 10 ms I/O finishes before the task's next turn, so the CPU always has a ready task.
- **q = 1 ms**: every task, I/O-bound or CPU-bound, runs 1 ms and then a 0.1 ms switch follows → U = 1/1.1 = **90.9%**.
- **q = 10 ms**: one round = 10 × (1 + 0.1) for the I/O-bound tasks + (10 + 0.1) for the CPU-bound task = 21.1 ms, containing 20 ms of useful work → U = 20/21.1 = **94.8%**.
- A larger quantum means fewer switches per unit of work → higher utilization, at the cost of response time.

## [X5-14] ch5 | Utilization and throughput with switch cost
P1 (10 ms), P2 (4 ms), P3 (6 ms) arrive at time 0; RR with q = 4 ms; each context switch takes 1 ms. Draw the Gantt chart with the switches; find CPU utilization, throughput and average turnaround time, and compare with FCFS.

**Answer:**
Assume no switch before the first process and a 1 ms switch (CS) whenever the CPU moves to a different process.
- RR: `0 P1 4 CS 5 P2 9 CS 10 P3 14 CS 15 P1 19 CS 20 P3 22 CS 23 P1 25` → 5 switches; 20 ms of useful work in 25 ms.
- **CPU utilization** = 20/25 = **80%**; **throughput** = 3 processes / 25 ms = **0.12 per ms (120 per second)**; completions P1 25, P2 9, P3 22 → **avg TAT** = (25 + 9 + 22)/3 = 56/3 = **18.67 ms**.
- FCFS: `0 P1 10 CS 11 P2 15 CS 16 P3 22` → 2 switches; U = 20/22 = **90.9%**; avg TAT = (10 + 15 + 22)/3 = 47/3 = **15.67 ms**.
- RR's extra context switches **lower CPU utilization** — the price paid for better response time.

## [X5-15] ch5 | RR versus FCFS with equal jobs
Is RR always better than FCFS? Four jobs, each needing 6 ms, arrive at time 0. Compare FCFS and RR (q = 2) in average turnaround, waiting and response time.

**Answer:**
**No.**
- FCFS: `0 P1 6 P2 12 P3 18 P4 24` → TAT 6, 12, 18, 24 → avg **15**; WT 0, 6, 12, 18 → avg **9**; RT = TAT → avg **15**.
- RR (q = 2): `0 P1 2 P2 4 P3 6 P4 8 P1 10 P2 12 P3 14 P4 16 P1 18 P2 20 P3 22 P4 24` → TAT 18, 20, 22, 24 → avg **21**; WT 12, 14, 16, 18 → avg **15**; RT 2, 4, 6, 8 → avg **5**.
- **When all jobs have the same length, longer than q, RR has worse turnaround and waiting time** — the jobs are interleaved and all finish near the end, while FCFS finishes them one by one — **but RR gives much better response time**. (Slide 5.15 case: 10 jobs × 100 s, q = 1 s → avg TAT 995.5 s under RR vs 550 s under FCFS.)

## [X5-16] ch5 | SJF optimality and proof sketch
Describe SJF scheduling and explain why it is optimal.

**Answer:**
- **SJF (shortest-next-CPU-burst)** associates each process with the **length of its next CPU burst** and runs the process with the **shortest next burst** (ties → FCFS). The idea: **get short jobs out of the system sooner** — a big gain for short jobs, a small cost for long ones.
- **SJF is optimal: it gives the minimum average waiting time for a given set of processes.**
- **Proof sketch**: **moving a short process before a long one decreases the waiting time of the short process more than it increases the waiting time of the long process**. Swapping an adjacent pair (long L before short S) changes the total waiting time by S − L < 0, so repeated swaps towards shortest-first can only reduce the average.
- E.g., bursts 6, 8, 7, 3 (all at 0): SJF `0 P4 3 P1 9 P3 16 P2 24` → avg WT (3 + 16 + 9 + 0)/4 = **7**, versus (0 + 6 + 14 + 21)/4 = 10.25 in FCFS order.

## [X5-17] ch5 | SJF implementation difficulty and approximation
Why is SJF difficult to implement in practice? How can it be approximated, and what other drawbacks does it have?

**Answer:**
- **The difficulty is knowing the length of the next CPU request** — the scheduler cannot see the future, so SJF/SRTF are hard to implement and are mainly used as a **benchmark** for practical algorithms.
- **Approximation**: **predict the next CPU burst from the lengths of previous bursts using exponential averaging**, $\tau_{n+1} = \alpha t_n + (1-\alpha)\tau_n$, then pick the process with the **shortest predicted** next burst (a wrong prediction gives a sub-optimal schedule).
- SJF can be applied to an **entire program** (e.g., a run-time estimate supplied with a batch job) or to the **current CPU burst**.
- Other drawbacks: **starvation of long processes** if shorter ones keep arriving; **fairness cannot be enforced**.

## [X5-18] ch5 | Exponential averaging formula and alpha
Explain the exponential averaging formula used to predict the next CPU burst. What happens when α = 0 and when α = 1?

**Answer:**
- $\tau_{n+1} = \alpha t_n + (1-\alpha)\tau_n$, $0 \le \alpha \le 1$: **$t_n$ = actual length of the n-th CPU burst** (most recent information), **$\tau_n$ = the previous prediction** (past history), **α = the relative weight of recent vs past history** (commonly **α = 1/2**).
- **α = 0** → $\tau_{n+1} = \tau_n$: **recent history does not count**. **α = 1** → $\tau_{n+1} = t_n$: **only the actual last CPU burst counts**.
- Expanded: $\tau_{n+1} = \alpha t_n + (1-\alpha)\alpha t_{n-1} + \dots + (1-\alpha)^j \alpha t_{n-j} + \dots + (1-\alpha)^{n+1} \tau_0$ → the prediction depends on **all past bursts (with different weights) and the initial estimate $\tau_0$**; **recent bursts weigh more**, and the effect of older ones **diminishes exponentially** (one more factor 1 − α per step). With α = 1/2, the weight of $\tau_0$ in $\tau_{10}$ is $(1/2)^{10} = 1/1024$ — negligible.

## [X5-19] ch5 | Exponential averaging calculation, alpha 0.5
With α = 0.5 and τ0 = 12 ms, the next four actual CPU bursts are 8, 6, 10 and 4 ms. Predict τ1 to τ4.

**Answer:**
$\tau_{n+1} = 0.5\,t_n + 0.5\,\tau_n$:
- τ1 = 0.5(8) + 0.5(12) = 4 + 6 = **10 ms**
- τ2 = 0.5(6) + 0.5(10) = 3 + 5 = **8 ms**
- τ3 = 0.5(10) + 0.5(8) = 5 + 4 = **9 ms**
- τ4 = 0.5(4) + 0.5(9) = 2 + 4.5 = **6.5 ms**

Check with the expanded form (weights 1/2, 1/4, 1/8, 1/16 on bursts 4, 10, 6, 8 and 1/16 on τ0 = 12): τ4 = 2 + 2.5 + 0.75 + 0.5 + 0.75 = **6.5 ms**.

## [X5-20] ch5 | Exponential averaging: alpha 0.25, solve alpha
(a) α = 0.25, τ0 = 16 ms, actual bursts 8, 2, 15 ms: find τ1, τ2, τ3. (b) A prediction of 10 ms is followed by an actual burst of 4 ms and the new prediction is 8.5 ms: find α.
(c) Using the data of (a), what is τ3 when α = 0 and when α = 1?

**Answer:**
(a) $\tau_{n+1} = 0.25\,t_n + 0.75\,\tau_n$: τ1 = 2 + 12 = **14 ms**; τ2 = 0.5 + 10.5 = **11 ms**; τ3 = 3.75 + 8.25 = **12 ms**. A **small α reacts slowly** — the 15 ms burst raises the guess only from 11 to 12.
(b) $8.5 = 4\alpha + 10(1-\alpha) = 10 - 6\alpha$ → $\alpha = 1.5/6 =$ **0.25**.
(c) **α = 0**: history is ignored → τ3 = τ0 = **16 ms**. **α = 1**: only the last burst counts → τ3 = t2 = **15 ms**.

## [X5-21] ch5 | SRTF definition and comparison with SJF
Describe SRTF scheduling. When must the scheduler be invoked, and how does SRTF compare with SJF?

**Answer:**
- **SRTF (shortest-remaining-time-first) is preemptive SJF**: when a process joins the ready queue (new → ready, or waiting → ready after I/O) with a **CPU burst shorter than the remaining time of the running process**, it **preempts** the running process (equal remaining time → no preemption).
- Hence the scheduler must run **at every arrival to the ready queue (scheduling condition 4)**, not only at completions.
- **SRTF is optimal among preemptive algorithms** for average waiting time and is **always at least as good as SJF**; if all processes arrive at the same time, SRTF = SJF; with equal bursts both behave like **FCFS**.
- Drawbacks: needs the (predicted) burst length, causes **more context switches**, and can **starve long processes** if short ones keep arriving.

## [X5-22] ch5 | FCFS, SJF, SRTF, RR averages calculation
P1 (arrival 0, burst 6), P2 (2, 5), P3 (3, 2), P4 (5, 4). Draw Gantt charts for FCFS, non-preemptive SJF, SRTF and RR (q = 2); find the average waiting, turnaround and response times.

**Answer:**
| Algorithm | Gantt chart | WT P1–P4 → avg | TAT P1–P4 → avg | RT P1–P4 → avg |
|---|---|---|---|---|
| FCFS | `0 P1 6 P2 11 P3 13 P4 17` | 0, 4, 8, 8 → **5** | 6, 9, 10, 12 → **9.25** | = TAT → **9.25** |
| SJF | `0 P1 6 P3 8 P4 12 P2 17` | 0, 10, 3, 3 → **4** | 6, 15, 5, 7 → **8.25** | = TAT → **8.25** |
| SRTF | `0 P1 3 P3 5 P1 8 P4 12 P2 17` | 2, 10, 0, 3 → **3.75** | 8, 15, 2, 7 → **8** | 3, 15, 2, 7 → **6.75** |
| RR q = 2 | `0 P1 2 P2 4 P1 6 P3 8 P2 10 P4 12 P1 14 P2 15 P4 17` | 8, 8, 3, 8 → **6.75** | 14, 13, 5, 12 → **11** | 2, 2, 5, 7 → **4** |

- SJF: only P1 is ready at 0; at t = 6 pick P3 (2), then P4 (4), then P2 (5).
- SRTF: at t = 2, P2 (5) does not preempt P1 (4 left); at t = 3, P3 (2) preempts P1 (3 left); at t = 5, P1 (3) < P4 (4) < P2 (5).
- RR: at t = 2, P2 arrives as P1's quantum expires → queue [P2, P1] (new arrival first); then t = 4 [P1, P3, P2]; t = 6 [P3, P2, P4, P1].
- **SRTF gives the minimum average waiting time; RR gives the best response time but the worst waiting and turnaround times.**

## [X5-23] ch5 | Priority scheduling and its relation to SJF
Describe priority scheduling (preemptive and non-preemptive). How is SJF related to it?

**Answer:**
- Each process has a **priority number**; the CPU is allocated to the **process with the highest priority** (**smallest integer = highest priority** unless stated otherwise); **equal-priority processes are scheduled in FCFS order** (or RR).
- **Preemptive**: a newly arrived process with a **higher priority preempts** the running process. **Non-preemptive**: a higher-priority arrival is put at the head of the ready queue and waits until the running process finishes its burst.
- **SJF is a special case of priority scheduling where the priority is the inverse of the predicted next CPU burst** (shorter burst = higher priority); SRTF is its preemptive form.
- Main problem: **starvation (indefinite blocking)** of low-priority processes; solution: **aging**.

## [X5-24] ch5 | Starvation and aging
What is starvation? Explain how aging prevents it, with a numerical example.

**Answer:**
- **Starvation (indefinite blocking)**: a process is **ready to run but waits indefinitely for the CPU**, because there are **always higher-priority processes** (or, in SJF/SRTF, shorter jobs) ahead of it.
- **Aging**: **gradually increase the priority of a process the longer it waits**, so it eventually becomes high enough to run (implemented with a **timer for each process in the ready queue**).
- Example: priorities range from 127 (lowest) to 0 (highest); raise a waiting process's priority by 1 every second → even a priority-127 process reaches priority 0 within **127 s (about 2 minutes)**, so its waiting time is bounded.
- In MLFQ, aging is done by **moving long-waiting jobs to a higher queue** (e.g., periodically moving all jobs to the top queue).

## [X5-25] ch5 | Preemptive vs non-preemptive priority calculation
P1 (arrival 0, burst 5, priority 3), P2 (1, 3, 1), P3 (2, 4, 4), P4 (3, 2, 2); smaller number = higher priority. Draw Gantt charts for preemptive and non-preemptive priority scheduling; find the average waiting and turnaround times.

**Answer:**
| Version | Gantt chart | WT P1–P4 → avg | TAT P1–P4 → avg | RT P1–P4 → avg |
|---|---|---|---|---|
| Preemptive | `0 P1 1 P2 4 P4 6 P1 10 P3 14` | 5, 0, 8, 1 → 14/4 = **3.5** | 10, 3, 12, 3 → 28/4 = **7** | 1, 3, 12, 3 → 19/4 = **4.75** |
| Non-preemptive | `0 P1 5 P2 8 P4 10 P3 14` | 0, 4, 8, 5 → 17/4 = **4.25** | 5, 7, 12, 7 → 31/4 = **7.75** | = TAT → **7.75** |

- Preemptive: at t = 1, P2 (priority 1) preempts P1 (3); at t = 3, P4 (2) cannot preempt P2 (1); at t = 4 the order is P4 (2), then P1 (3), then P3 (4).
- Non-preemptive: P1 runs to completion at 5; then by priority P2, P4, P3.

## [X5-26] ch5 | Priority with RR, remaining quantum rule
Preemptive priority scheduling with RR (q = 2) among equal priorities, smaller number = higher priority: P1 (arrival 0, burst 5, priority 2), P2 (0, 4, 2), P3 (3, 2, 1), P4 (4, 3, 2). Draw the Gantt chart; find the average waiting time.

**Answer:**
Rule (Lab 5, S23 official answer): a process **preempted by a higher-priority arrival returns to the head of its priority level and keeps its remaining quantum**; a process whose quantum expires goes to the tail.
- Gantt: `0 P1 2 P2 3 P3 5 P2 6 P1 8 P4 10 P2 12 P1 13 P4 14`
- t = 2: P1's quantum expires → [P2, P1]. t = 3: **P3 (priority 1) preempts P2 after 1 unit** → P2 goes back to the **head with 1 unit of quantum left**. t = 4: P4 joins → [P2, P1, P4]. t = 5: **P2 runs only 5–6**, then P1 6–8, P4 8–10, P2 10–12 (done), P1 12–13 (done), P4 13–14 (done).
- WT = completion − arrival − burst: P1 13 − 0 − 5 = 8; P2 12 − 0 − 4 = 8; P3 5 − 3 − 2 = 0; P4 14 − 4 − 3 = 7 → **avg WT = 23/4 = 5.75** (avg TAT = 37/4 = 9.25).
- Common mistake: giving P2 a fresh quantum at t = 5 (running 5–7) — that produces a wrong chart.

## [X5-27] ch5 | Dynamic priority alpha beta gives FCFS or LIFO
A preemptive scheduler uses dynamic priorities (larger number = higher): a waiting process's priority changes at rate α, a running process's at rate β, and every process enters the ready queue with priority 0. Which algorithm results from (a) β > α > 0, (b) α < β < 0?

**Answer:**
(a) **β > α > 0 → FCFS.** Every priority rises from 0, so a new process (priority 0) is **lower than every process already in the system** and never preempts; the running process rises fastest (β > α), so it is **never preempted**; among the waiting processes, the one that **has waited longest has the highest priority** → processes run in **arrival order**.
(b) **α < β < 0 → LIFO (last-in, first-out).** Every priority falls from 0, so a **new process (priority 0) is higher than all existing ones** and **preempts the running process immediately** → the most recently arrived process always runs first.

## [X5-28] ch5 | Least-recent-CPU policy favours I/O-bound
A scheduler favours the processes that have used the least processor time in the recent past. Why does it favour I/O-bound processes, yet not permanently starve CPU-bound processes?

**Answer:**
- It **favours I/O-bound processes** because they run only **short CPU bursts** before blocking for I/O, so their recent CPU usage is small and they get **high priority**.
- **CPU-bound processes do not starve permanently** because the I/O-bound processes **give up the CPU frequently** to do their I/O, and the CPU-bound process runs in those gaps. Also, usage is measured only over the **recent past**: while a CPU-bound process waits, its recent usage falls and its priority rises (an aging effect).

## [X5-29] ch5 | Multilevel queue scheduling
Describe multilevel queue scheduling. How is the CPU shared among the queues?

**Answer:**
- The ready queue is **partitioned into separate queues based on process type** (e.g., real-time, system, interactive, batch). The **priority is assigned statically**: a process **remains in the same queue for its whole runtime**.
- **Each queue can have its own scheduling algorithm** (e.g., RR for interactive/foreground, FCFS for batch/background).
- **Scheduling among the queues**: (1) **fixed-priority preemptive scheduling** — a lower queue runs only when all higher queues are empty, and an arrival in a higher queue preempts it → **low queues can starve**; or (2) **time slicing** — each queue gets a **certain share of CPU time** (e.g., 60%, 20%, 10%, 10%).
- Priority scheduling with RR is easily implemented as a multilevel queue (one RR queue per priority level). Low scheduling overhead, but **inflexible**.

## [X5-30] ch5 | Multilevel queue versus MLFQ
Compare multilevel queue scheduling with multilevel feedback queue (MLFQ) scheduling.

**Answer:**
| Aspect | Multilevel queue | MLFQ |
|---|---|---|
| Queue membership | **permanent** (by process type) | process **can move between queues** |
| Priority | **static** | **dynamic**, based on observed CPU usage |
| Movement rules | none | **demote** after using a full quantum; **upgrade** by aging |
| Starvation | possible for low queues (fixed priority) | possible, but handled by **aging / periodic reshuffling** |
| Needs burst knowledge | no (classified by type) | no (learns from behaviour) |
| Flexibility / cost | inflexible, low overhead | flexible, but the **most complex** (many parameters) |

MLFQ therefore **separates processes by their CPU-burst behaviour**: CPU-bound jobs drop to low queues, while I/O-bound and interactive jobs stay high.

## [X5-31] ch5 | MLFQ defining parameters
What parameters define a multilevel feedback queue scheduler?

**Answer:**
An MLFQ scheduler is defined by:
1. **the number of queues**;
2. **the scheduling algorithm for each queue** (e.g., RR with its own quantum per queue, FCFS in the last queue);
3. **the method used to determine when to upgrade a process** to a higher-priority queue (e.g., aging);
4. **the method used to determine when to demote a process** to a lower-priority queue (e.g., after it uses a full quantum);
5. **the method used to determine which queue a process will enter when it needs service** (e.g., every new job enters Q0).

Because a process can move between queues, **aging can be implemented this way**, which gives MLFQ its **flexibility**.

## [X5-32] ch5 | MLFQ rules: demotion, preemption, head of queue
MLFQ with Q0 (RR, q = 8 ms), Q1 (RR, q = 16 ms), Q2 (FCFS). (a) Where does a new job go, and when is it demoted? (b) A Q1 job that has used 5 ms of its quantum is preempted by a new arrival: where does it go, with how much quantum? (c) Can a Q1 job preempt a Q2 job? (d) Which jobs never reach Q2?

**Answer:**
(a) A new job **enters the tail of Q0** (RR, FCFS order) and **preempts a running Q1 or Q2 job**. A job that **uses its full quantum without finishing is demoted to the tail of the next queue** (Q0 → Q1 → Q2). A running Q0 job is never preempted by an arrival (the arrival waits in Q0).
(b) It returns to the **head of Q1** and later resumes with its **remaining quantum, 16 − 5 = 11 ms**; it is **not demoted** and does **not get a fresh quantum** (a job never receives more than 16 ms in Q1). A preempted Q2 job returns to the head of Q2 with its remaining burst.
(c) **No.** No job arrives directly at Q1; a job enters Q1 only by using a full Q0 quantum, i.e., while a Q0 job is running. A Q2 job runs only when Q0 and Q1 are empty, and only a new arrival to Q0 can preempt it.
(d) Jobs with a CPU burst **≤ 8 + 16 = 24 ms** finish within Q0 and Q1. This is how MLFQ **approximates SRTF: CPU-bound jobs drop like a rock; short-running I/O-bound jobs stay near the top**.

## [X5-33] ch5 | MLFQ disadvantages and remedies
What are the disadvantages of MLFQ, and how can they be handled?

**Answer:**
- **Starvation**: with fixed priority among queues, long CPU-bound jobs in the lowest queue may **never run if new or short jobs keep arriving** → handled by **aging / reshuffling jobs among the queues periodically**, e.g., **after some period, move all jobs to the top queue**.
- **Complexity**: it is the **most general but most complex** scheduler — the number of queues, each queue's quantum and algorithm, and the upgrade/demote/entry rules must all be **chosen and tuned** for the workload.
- **Changing behaviour**: a job demoted during a CPU-bound phase stays at low priority even if it later becomes interactive, unless an **upgrade (aging) rule** moves it back up.
- (Its advantages: no prior knowledge of burst times, good response time for interactive jobs, SJF/SRTF-like performance, and fair progress for CPU-bound jobs.)

## [X5-34] ch5 | MLFQ Gantt calculation, remaining quantum
MLFQ: Q0 RR (q = 4), Q1 RR (q = 8), Q2 FCFS; new jobs enter Q0 and preempt Q1/Q2; a preempted job returns to the head of its queue with its remaining quantum.
P1 (arrival 0, burst 14), P2 (3, 5), P3 (9, 3), P4 (15, 2). Draw the Gantt chart; find the average waiting, turnaround and response times.

**Answer:**
- Gantt: `0 P1 4 P2 8 P1 9 P3 12 P1 15 P4 17 P1 21 P2 22 P1 24`
- Queues: P1@Q0 0–4, P2@Q0 4–8, P1@Q1 8–9, P3@Q0 9–12, P1@Q1 12–15, P4@Q0 15–17, P1@Q1 17–21, P2@Q1 21–22, P1@Q2 22–24.
- t = 4: P1 used its Q0 quantum → Q1. t = 8: P2 → Q1 behind P1; P1 runs from Q1. t = 9: P3 preempts P1 (1 of 8 used) → P1 to the **head of Q1 with 7 left**. t = 15: P4 preempts P1 (**4 left**). t = 17–21: P1 uses its last 4 units (1 + 3 + 4 = 8) with 2 ms of burst left → **demoted to Q2**; P2 finishes in Q1 at 22; P1 finishes in Q2 at 24.

| P | Arrival | Burst | Completion | TAT | WT | RT |
|---|---|---|---|---|---|---|
| P1 | 0 | 14 | 24 | 24 | 10 | 4 |
| P2 | 3 | 5 | 22 | 19 | 14 | 5 |
| P3 | 9 | 3 | 12 | 3 | 0 | 3 |
| P4 | 15 | 2 | 17 | 2 | 0 | 2 |

- **Avg WT = 24/4 = 6; avg TAT = 48/4 = 12; avg RT = 14/4 = 3.5.**
- Resetting P1's quantum after each preemption (the common mistake) would wrongly let P1 finish in Q1.

## [X5-35] ch5 | Algorithm property comparison table
Compare FCFS, SJF, SRTF, RR, priority, multilevel queue and MLFQ: preemptive? need the next-burst length? can starve? main property.

**Answer:**
| Algorithm | Preemptive? | Needs next-burst length? | Starvation? | Key property |
|---|---|---|---|---|
| FCFS | No (must be non-preemptive) | No | No | simplest; convoy effect |
| SJF | No | Yes (predicted) | Yes (long jobs) | minimum avg WT among non-preemptive |
| SRTF | Yes (on arrival) | Yes (predicted) | Yes (long jobs) | minimum avg WT (preemptive) |
| RR | Yes (timer) | No | No | fair, good response; depends on q |
| Priority | Either | No | Yes → aging | SJF is a special case |
| Multilevel queue | Yes (fixed priority among queues) | No | Yes (low queues) | permanent queues, low overhead |
| MLFQ | Yes | No | Possible → aging / reshuffle | approximates SJF/SRTF, good response |

## [X5-36] ch5 | Which algorithm: quick judgement answers
Which scheduling algorithm (a) minimizes average waiting time, (b) suits interactive systems best, (c) is free from starvation, (d) is hard to implement, (e) must be non-preemptive, (f) is used in BSD Unix, Solaris and Windows?

**Answer:**
| Question | Answer | Reason |
|---|---|---|
| (a) Minimum average waiting (and turnaround) time | **SJF** (non-preemptive), **SRTF** (preemptive) | provably optimal: short jobs first |
| (b) Best for interactive systems / response time | **RR** or **MLFQ** | short quanta; MLFQ keeps interactive jobs in the top queues |
| (c) Free from starvation | **FCFS and RR** | every process reaches the head of the queue |
| (d) Difficult to implement | **SJF / SRTF** | the next CPU-burst length is unknown |
| (e) Must be non-preemptive | **FCFS** | each burst runs to completion |
| (f) Used in BSD Unix, Solaris, Windows | **MLFQ** | no prior burst knowledge; adapts to behaviour |
| Periodic real-time, static priority | **RM** | shorter period = higher priority |
| Real-time up to 100% utilization | **EDF** | dynamic, deadline-based priority |

## [X5-37] ch5 | Equivalences between scheduling algorithms
State the relation between: (a) RR and FCFS; (b) SJF and priority; (c) priority and FCFS; (d) MLFQ and FCFS; (e) SJF/SRTF and FCFS; (f) RR and SJF.

**Answer:**
- (a) **RR with a quantum larger than every CPU burst = FCFS**; RR with a very small quantum ≈ **processor sharing**.
- (b) **SJF = priority scheduling with priority = inverse of the predicted next CPU burst**; SRTF = preemptive priority on the remaining time.
- (c) **FCFS = priority scheduling with priority = arrival time** (the job that has been in the system longest has the highest priority); priority scheduling with all-equal priorities is FCFS.
- (d) **The lowest queue of an MLFQ is FCFS**; MLFQ as a whole **approximates SRTF/SJF**.
- (e) **SJF/SRTF = FCFS when all CPU bursts are equal**; SRTF = SJF when all processes arrive at the same time.
- (f) **RR and SJF: no direct relation.**
- Also: a multilevel queue with one RR queue per priority level = priority scheduling with RR.

## [X5-38] ch5 | How FCFS, RR, MLFQ treat short jobs
Explain how much FCFS, RR and MLFQ discriminate in favour of short processes.

**Answer:**
- **FCFS — discriminates against short jobs**: a short job that arrives after long jobs must wait for all of them (**convoy effect**).
- **RR — treats all jobs equally**: each job gets the same quantum in turn, so a **short job finishes after only a few quanta** and leaves the system sooner, but it gets no extra priority.
- **MLFQ — strongly favours short jobs**: short (interactive, I/O-bound) jobs **finish in the high-priority top queues**, while long CPU-bound jobs are **demoted to lower queues** — similar to **SJF/SRTF** without knowing the burst lengths.

## [X5-39] ch5 | PCS versus SCS and LWP
Distinguish process-contention scope (PCS) from system-contention scope (SCS). What is an LWP?

**Answer:**
On systems with both thread levels, **the OS schedules kernel-level threads**; user-level threads are managed by the **thread library** (the OS is unaware of them).

| | **PCS** | **SCS** |
|---|---|---|
| Who schedules | **thread library** | **kernel** (CPU scheduler) |
| What | user-level threads onto an available **LWP** (kernel thread) | **kernel threads onto a CPU** |
| Competition among | **threads of the same process** | **all threads in the system** |
| Models | many-to-one, many-to-many | all; **one-to-one systems (Windows, Linux, Solaris) use only SCS** |
| Policy | usually **priority set by the programmer** (the library does not adjust it); preempts for a higher-priority user thread | the OS CPU-scheduling algorithm |

An **LWP (lightweight process)** is an **intermediate data structure between user and kernel threads**; it **appears as a virtual processor** on which the thread library schedules user threads to run, and each LWP is **attached to a kernel thread**.

## [X5-40] ch5 | AMP versus SMP
Compare asymmetric multiprocessing (AMP) and symmetric multiprocessing (SMP) for CPU scheduling.

**Answer:**
| | **AMP** | **SMP** |
|---|---|---|
| Scheduling | **all scheduling decisions, I/O processing and system activities are handled by one processor — the master server** | **each processor is self-scheduling** |
| Kernel data | **only the master accesses kernel data structures** → no data sharing needed | all processors access shared kernel data → must **synchronize** |
| Other processors | execute **only user code** | run both kernel and user code |
| Ready queue | kept by the master | **one common ready queue** or a **private queue per processor** |
| Drawback | **the master can become a bottleneck** | more complex: two processors must not pick the same thread, and no process may be lost |
| Use | simple designs | **all modern OSes** (Windows, Linux, macOS, Android, iOS) |

## [X5-41] ch5 | Common versus per-processor ready queues
In SMP, what race condition can a single common ready queue cause? Compare common and per-processor ready queues in load balancing, processor affinity and locking.

**Answer:**
With a common queue, **two processors may choose to schedule the same thread** (or a thread may be lost) unless the queue is **locked — a race condition**.

| | **Common ready queue** | **Per-processor (private) ready queues** |
|---|---|---|
| Load balancing | **automatic** — no CPU is idle while the queue is non-empty | needs **push / pull migration** |
| Processor affinity | hard to keep — a thread may run on a different CPU each time (cold cache) | **natural — affinity "for free"** (warm cache) |
| Locking | the shared queue must be locked → contention | little sharing, no global-queue contention |

## [X5-42] ch5 | Memory stall and chip multithreading
What is a memory stall, and how do multithreaded multicore processors (CMT) exploit it? How many logical CPUs does the OS see on a quad-core processor with 2 hardware threads per core?

**Answer:**
- Multicore = **multiple processor cores on the same chip**: **faster and consumes less power**, but **complicates scheduling**.
- **Memory stall**: when a processor accesses memory it **spends a significant amount of time waiting for the data**, because modern processors are **much faster than memory**, especially on a **cache miss**.
- **Chip multithreading (CMT; Intel: hyperthreading)** gives each core **multiple hardware threads**, each with its own **architectural state (PC, register set)**, so each appears to the OS as a **logical CPU**. **If one hardware thread stalls on memory, the core switches to another hardware thread**, so useful work continues during the stall.
- **Logical CPUs = cores × hardware threads per core**: 4 × 2 = **8** (dual-core dual-threaded = 4; UltraSPARC T3: 16 × 8 = 128).

## [X5-43] ch5 | Two levels of multicore thread scheduling
Describe the two levels of scheduling on a multithreaded multicore processor, and the full mapping from user threads to cores.

**Answer:**
1. **OS level**: the operating system decides **which software (kernel) thread runs on each logical CPU (hardware thread)** — this is the **CPU scheduling** of this chapter, using any algorithm.
2. **Core level**: each **core decides which of its hardware threads runs on the physical core**, e.g., simple **round-robin** (UltraSPARC T3).
- Full mapping: **user thread → LWP / kernel thread** (thread library, **PCS**) → **kernel (software) thread → hardware thread / logical CPU** (OS, **SCS**) → **hardware thread → physical core** (core hardware, typically RR).

## [X5-44] ch5 | Processor affinity: soft, hard, NUMA
What is processor affinity? Distinguish soft and hard affinity, and explain how NUMA affects it.

**Answer:**
- **Processor affinity**: a thread has **affinity for the processor it runs on**, because that processor's **cache holds the thread's recently accessed memory**. Migration means **invalidating and repopulating caches** (high cost), so most SMP systems **try to avoid migrating** processes; **per-processor ready queues provide affinity for free**.
- **Soft affinity**: the OS **attempts to keep a process on the same processor but does not guarantee it** — the process may **migrate during load balancing**.
- **Hard affinity**: a process **specifies the subset of processors on which it may run** (e.g., Linux `sched_setaffinity()`); many systems, such as Linux, provide both.
- **NUMA**: a CPU accesses **its local memory faster** than remote memory, so a thread should run on a CPU near its memory → **affinity to both the processor and the memory**.

## [X5-45] ch5 | Load balancing: push, pull, affinity conflict
Explain push and pull migration. Why does load balancing conflict with processor affinity?

**Answer:**
- **Load balancing keeps the workload evenly distributed** across processors; it is needed when **each processor has its own private ready queue** (a common queue balances itself).
- **Push migration**: a **specific task periodically checks the load on each processor** and, if it finds an imbalance, **pushes tasks from overloaded CPUs to idle or less-busy CPUs**.
- **Pull migration**: an **idle processor pulls a waiting task from a busy processor**.
- They are **not mutually exclusive** — often **both are implemented** (e.g., Linux CFS).
- **Conflict**: a migrated thread **loses its cache contents** (and on NUMA its local memory), so **load balancing often counteracts the benefits of processor affinity** — a natural tension between balancing the load and minimizing memory access time (e.g., migrate only when the imbalance exceeds a threshold).

## [X5-46] ch5 | Hard versus soft real-time
Distinguish hard and soft real-time systems. What must a real-time CPU scheduler support?

**Answer:**
- **Hard real-time**: stricter — a **task must be serviced by its deadline; service after the deadline has expired is the same as no service at all** (e.g., airbag or flight control).
- **Soft real-time**: **no guarantee as to when a critical real-time process will be scheduled**; it **guarantees only that the real-time process will be given preference over non-critical processes** (e.g., video streaming).
- Real-time scheduling demands **performance guarantees — predictability**. The scheduler **must support a priority-based algorithm with preemption**, so a ready high-priority real-time task gets the CPU at once; but **a preemptive priority-based scheduler alone guarantees only soft real-time**. Hard real-time also needs deadline guarantees (**admission control**, RM/EDF analysis).

## [X5-47] ch5 | Event, interrupt and dispatch latency
Define event latency, interrupt latency and dispatch latency in a real-time system. (Textbook topic; the slides define only dispatch latency, slide 5.7.)

**Answer:**
- **Event latency**: the time from **when an event occurs to when it is serviced**. Two latencies affect real-time performance:
- **Interrupt latency**: the time from **the arrival of an interrupt at the CPU to the start of the routine that services it** — the CPU finishes the current instruction, determines the interrupt type and **saves the state of the current process**. For hard real-time it must be **bounded** (interrupts may be disabled only briefly).
- **Dispatch latency**: the time for the **dispatcher to stop one process and start another**. **Preemptive kernels** keep it low; its **conflict phase** consists of (1) **preemption of any process running in the kernel** and (2) **release by low-priority processes of resources needed by a high-priority process**.

## [X5-48] ch5 | Periodic tasks, utilization, admission control
Describe the characteristics of a periodic real-time task. What is the CPU utilization of a task set, and what is admission control?

**Answer:**
- A periodic task requires the CPU at **constant intervals (periods)**: **processing time t, deadline d, period p, with 0 ≤ t ≤ d ≤ p**; its **rate is 1/p**. One job is released every p time units and must finish by its deadline (often d = p, i.e., by the start of the next period).
- **CPU utilization of task i** = $t_i/p_i$; total $U = \sum_i t_i/p_i$. E.g., (t, p) = (20, 50) and (35, 100): U = 0.40 + 0.35 = **75%**. If **U > 1**, the CPU is overloaded and **some deadlines must be missed**.
- **Admission control**: a process **announces its deadline requirements** to the scheduler, which **admits it only if it can guarantee that the process will complete on time** and otherwise rejects it.

## [X5-49] ch5 | Rate-monotonic scheduling and missed deadlines
Explain rate-monotonic (RM) scheduling. Why can RM miss a deadline even when U < 1?

**Answer:**
- **RM schedules periodic tasks using a static priority policy with preemption**: **priority = inverse of the period — shorter period (higher rate) = higher priority**, because tasks that need the CPU more often get higher priority. Priorities never change.
- **RM is optimal among static-priority algorithms**: if a task set **cannot be scheduled by RM, no other static-priority algorithm can schedule it**. It handles only **periodic tasks with a constant processing time**.
- **Deadlines can be missed with U < 1**, because the static priority ignores how close each deadline is. E.g., P1 (t = 25, p = 50), P2 (t = 35, p = 80): U = 0.50 + 0.44 = 94%; P1 preempts P2 at 50: `0 P1 25 P2 50 P1 75 P2 85` → **P2 misses its deadline 80, finishing at 85**.
- RM is guaranteed only if $U \le N(2^{1/N} - 1)$ (0.828 for N = 2; tends to ln 2 ≈ 0.693 for large N) — a sufficient, not necessary, condition.

## [X5-50] ch5 | Earliest-deadline-first scheduling
Explain EDF scheduling and its advantages over RM. Why can it not reach 100% CPU utilization in practice?

**Answer:**
- **EDF assigns priorities dynamically according to the deadline: the earlier the (absolute) deadline, the higher the priority**; priorities are re-evaluated whenever a job becomes runnable; it is preemptive.
- **EDF does not require processes to be periodic, nor a constant amount of CPU time per burst — the only requirement is that a process announces its deadline when it becomes runnable.**
- **Theoretically optimal**: it can schedule processes so that **each meets its deadline with CPU utilization up to 100%** (U ≤ 1 when deadline = period). E.g., P1 (25, 50), P2 (35, 80): `0 P1 25 P2 60 P1 85 P2 100 P1 125 P2 145 idle 150` — at t = 50, P2's deadline 80 is earlier than P1's 100, so P2 continues → **no deadline missed** (RM misses 80).
- **In practice 100% is impossible** because of the cost of **context switching and interrupt handling**.

## [X5-51] ch5 | RM versus EDF comparison
Compare rate-monotonic and earliest-deadline-first scheduling.

**Answer:**
| | **Rate-monotonic (RM)** | **Earliest-deadline-first (EDF)** |
|---|---|---|
| Priority | **static** — inverse of period (shorter = higher) | **dynamic** — earlier absolute deadline = higher |
| Task model | **periodic, constant processing time** | periodic or not, burst may vary; must **announce its deadline** |
| Preemption | yes | yes |
| Optimality | **optimal among static-priority algorithms** | **theoretically optimal** overall |
| Schedulable if (d = p) | $U \le N(2^{1/N} - 1)$ guarantees it (sufficient only) | **$U \le 1$** (necessary and sufficient) |
| Cost | priorities fixed once: simple, predictable | priorities recomputed at each release: more overhead |
| Example P1 (25, 50), P2 (35, 80) | **P2 misses deadline 80** | **all deadlines met** |

## [X5-52] ch5 | Schedulability test with utilization bound
Using CPU utilization (deadline = period), decide whether each task set (t, p) is schedulable by RM and by EDF: (a) (1, 4), (2, 6), (1, 10); (b) (2, 5), (4, 7); (c) (2, 4), (4, 8); (d) (3, 5), (3, 6).

**Answer:**
RM bound $N(2^{1/N} - 1)$: N = 1: 1.000; N = 2: 0.828; N = 3: 0.780; N = 4: 0.757; N = 5: 0.743; large N: 0.693. **EDF: schedulable iff U ≤ 1.**
- (a) U = 1/4 + 2/6 + 1/10 = 0.250 + 0.333 + 0.100 = **0.683 ≤ 0.780** → **RM guaranteed**; EDF also schedulable.
- (b) U = 2/5 + 4/7 = 0.400 + 0.571 = **0.971 > 0.828** → RM **not guaranteed — draw the timeline** (RM actually misses at t = 7; see the next entry); **EDF schedulable** (U ≤ 1).
- (c) U = 2/4 + 4/8 = **1.00 > 0.828**, yet RM meets every deadline: `0 T1 2 T2 4 T1 6 T2 8`, repeating → the RM bound is **sufficient, not necessary**; EDF also schedulable (U = 1).
- (d) U = 3/5 + 3/6 = **1.10 > 1** → **overloaded: neither RM nor EDF (nor any algorithm) can meet all deadlines**.

## [X5-53] ch5 | RM and EDF timelines, missed deadlines
Soft real-time: P1 (t = 2, period = deadline = 5) and P2 (t = 4, period = deadline = 7), both released at 0. Draw the RM and EDF schedules for 0–14 and count the missed deadlines.

**Answer:**
U = 2/5 + 4/7 = 0.971. Releases and deadlines: P1 at 0, 5, 10 (deadlines 5, 10, 15); P2 at 0, 7 (deadlines 7, 14).
- **RM** (P1 has higher priority, period 5 < 7): `0 P1 2 P2 5 P1 7 P2 10 P1 12 P2 14`. At t = 5, P1 preempts P2 (P2 has 1 unit left); at t = 7, P2's first job is unfinished → **misses deadline 7**; it keeps running (soft real-time) and finishes at 8; P2's second job runs 8–10 and 12–14 → meets deadline 14. **RM: 1 missed deadline.**
- **EDF**: `0 P1 2 P2 6 P1 8 P2 12 P1 14`. At t = 5, P2's deadline 7 < P1's new deadline 10 → **P2 continues** and finishes at 6; at t = 10, P2's deadline 14 < P1's 15 → P2 continues to 12. **EDF: 0 missed deadlines.**
- EDF wins because its **dynamic priorities follow the deadlines**, whereas RM's static priority ran P1 (deadline 10) ahead of P2 (deadline 7).

## [X5-54] ch5 | Algorithm evaluation methods
How are CPU-scheduling algorithms evaluated? Compare deterministic modeling, queueing models, simulation and implementation.

**Answer:**
First **define the criteria** and their relative importance, e.g., **maximize CPU utilization under the constraint that the maximum response time is 300 ms**, or **maximize throughput such that turnaround time is (on average) linearly proportional to total execution time**. Then evaluate:

| Method | How | Advantages | Disadvantages |
|---|---|---|---|
| **Deterministic modeling** | takes a **particular predetermined workload** and computes each algorithm's performance (Gantt chart) | **simple, fast, exact numbers** | **requires exact input; results apply only to that workload** |
| **Queueing models** | CPU and devices as a **network of servers with queues**; arrival and service **distributions** (often exponential) give utilization, average queue length, waiting time (Little's formula) | handles stochastic workloads mathematically | **only a few classes of algorithms and distributions** are tractable; assumptions are often **unrealistic** |
| **Simulation** | **programs a model of the system**; a clock advances the state; driven by **random numbers from distributions** or by **trace files** of a real system | **more accurate** (traces give the real order of events) | still limited accuracy; can be expensive (computation, storage, coding) |
| **Implementation** | codes the scheduler into a **real OS** and measures it on real workloads | **most accurate** | **high cost and high risk** (new bugs); the environment keeps changing |

E.g., deterministic: P1–P5 = 10, 29, 3, 7, 12 ms at t = 0 → avg WT FCFS 28, non-preemptive SJF 13, RR (q = 10) 23 → SJF is best for this workload. Flexible systems also let system managers **tune the scheduling parameters**, and APIs (Java, POSIX, Windows) can change a process's or thread's priority.

## [X5-55] ch5 | Little's formula calculations
State Little's formula and its assumptions. (a) n = 14, λ = 7/s: find W. (b) λ = 20/s, W = 0.5 s: find n. (c) n = 6, W = 300 ms: find λ.
(d) 120 processes arrive per minute and each waits 250 ms on average: find n.

**Answer:**
- **Little's formula: $n = \lambda \times W$**, where **n = average queue length**, **λ = average arrival rate into the queue**, **W = average waiting time in the queue**. It holds in **steady state** (processes leaving the queue = processes arriving; the arrival rate must be smaller than the service rate) and is **valid for any scheduling algorithm and arrival distribution**.
- (a) W = n/λ = 14/7 = **2 s**.
- (b) n = λW = 20 × 0.5 = **10 processes**.
- (c) λ = n/W = 6/0.3 = **20 processes/s**.
- (d) Convert units first: λ = 120/60 = 2 per s; n = 2 × 0.25 = **0.5 process** on average.

## [X5-TF] ch5 | True / False quick verdicts
| Statement | T/F | Why (≤ 12 words) |
|---|---|---|
| Scheduling when a process switches from running to waiting is non-preemptive. | T | The process gives up the CPU voluntarily (condition 1). |
| A process moving from waiting to ready can trigger preemption. | T | Condition 4: it may have a higher priority. |
| The dispatcher decides which process runs next. | F | The scheduler selects; the dispatcher performs the context switch. |
| CPU utilization and throughput measure the same thing. | F | Utilization = busy fraction; throughput = completions per unit time. |
| A better scheduling algorithm shortens a process's CPU burst. | F | It only changes time spent waiting in the ready queue. |
| Under this course's definition, FCFS response time equals turnaround time. | T | Non-preemptive: the first run ends when the burst completes. |
| FCFS can suffer the convoy effect but never starves a process. | T | Short jobs wait behind long ones; the queue always advances. |
| In RR, a process whose quantum expires rejoins the head of the ready queue. | F | It is added to the tail of the ready queue. |
| A larger time quantum always lowers RR's average turnaround time. | F | Not monotonic; a very large q degenerates to FCFS. |
| RR with a quantum larger than every CPU burst behaves like FCFS. | T | Every burst finishes within its first quantum. |
| About 80% of CPU bursts should be shorter than the time quantum. | T | Rule of thumb for choosing q (slide 5.16). |
| A very small quantum always improves RR performance. | F | Switch overhead dominates; efficiency q/(q + s) falls. |
| SJF gives the minimum average waiting time for a given set of processes. | T | Running shorter jobs first always lowers total waiting time. |
| SRTF can give a larger average waiting time than SJF. | F | SRTF is always at least as good as SJF. |
| SRTF must invoke the scheduler whenever a process joins the ready queue. | T | A shorter arrival may preempt the running process. |
| In exponential averaging, α = 0 makes the prediction equal the last burst. | F | α = 0 keeps old prediction; α = 1 uses last burst. |
| Exponential averaging gives older bursts exponentially smaller weights. | T | Each older term is multiplied by another factor (1 − α). |
| Aging lowers the priority of processes that have run for a long time. | F | Aging raises the priority of processes that wait long. |
| Non-preemptive priority scheduling cannot cause starvation. | F | Higher-priority arrivals are always chosen first at each completion. |
| In a multilevel queue, fixed-priority scheduling among queues can starve low queues. | T | Lower queues run only when all higher queues are empty. |
| In MLFQ, a job demoted for using its full quantum joins the head of the lower queue. | F | Demoted jobs join the tail; only preempted jobs return to head. |
| In MLFQ, a Q1 job preempted by a new arrival keeps its remaining quantum. | T | It returns to the head of Q1 without a fresh quantum. |
| In MLFQ, a Q1 job can preempt a running Q2 job. | F | No job enters Q1 while a Q2 job is running. |
| Under many-to-many, the kernel chooses which user thread runs on an LWP. | F | The thread library does: process-contention scope (PCS). |
| In AMP, every processor accesses the kernel data structures. | F | Only the master does; others execute user code only. |
| With one common ready queue, explicit load balancing is unnecessary. | T | An idle CPU simply takes the next thread from the queue. |
| Soft affinity guarantees that a process never migrates. | F | It only attempts; migration may occur during load balancing. |
| A dual-core CPU with 2 hardware threads per core shows 4 logical CPUs. | T | 2 cores × 2 hardware threads = 4 logical processors. |
| A preemptive priority-based scheduler guarantees hard real-time deadlines. | F | It guarantees only soft real-time functionality. |
| RM is optimal among all real-time scheduling algorithms. | F | Optimal only among static-priority algorithms; EDF is optimal overall. |
| If U ≤ 1, RM meets every deadline. | F | RM is guaranteed only if $U \le N(2^{1/N} - 1)$. |
| Exceeding the RM utilization bound means some deadline will be missed. | F | The bound is sufficient, not necessary; draw the timeline. |
| In theory, EDF meets all deadlines up to 100% utilization when deadline = period. | T | Optimal; switching and interrupts prevent 100% in practice. |
| Little's formula holds for any scheduling algorithm in steady state. | T | Valid for any algorithm and arrival distribution. |
| Deterministic-modeling results hold for any workload. | F | They apply only to the exact workload that was modelled. |
