# Question Bank 2 — Past-paper Short / Long Questions（附標準答案）

> 所有 fork 數目、Gantt chart、synchronization 值都已經用程式（C fork 程式 / 排程模擬器）驗證 ✅。
> 答案用英文寫（考試照抄）；中文係提示。

---

## [S26-Q2.1] ch6 | Race condition (4 pts)
What is a race condition? Give an example.

**Answer:**
A race condition occurs when two or more processes/threads access and manipulate shared data concurrently, and the final result depends on the order in which the accesses take place; since the order is unpredictable, the result may be incorrect or inconsistent. (2.5) Example: two threads increment the same `counter` without synchronization — `counter++` is load/add/store, so both may load the same old value and one update is lost. (1.5)

## [S26-Q2.2] ch1 | Caching (4 pts)
What is the fundamental idea of caching? Is a high cache hit ratio alone enough to guarantee good performance? Explain by considering hit time and miss penalty.

**Answer:**
Caching temporarily copies a subset of information from a slower but larger storage into a faster but smaller storage so that frequently used data can be accessed more quickly. (2) No — hit ratio is a major criterion but not sufficient (1); performance is the **average access time = hit ratio × hit time + miss ratio × miss time**, which also depends on the hit time and the miss penalty (1). A slow cache or a huge miss penalty can still give poor performance.

## [S26-Q2.3] ch5 | Custom policy fᵢ = 1/(a·cᵢ + b) (4 pts)
The OS keeps $c_i$ = average past CPU burst of $P_i$ and picks the process with the highest $f_i = \dfrac{1}{a\,c_i + b}$ ($a, b > 0$), running it for one quantum or until it gives up the CPU. (a) Does this prioritize I/O-bound over CPU-bound processes? (b) Can it cause starvation?

**Answer:**
(a) **Yes** — I/O-bound processes have small CPU bursts $c_i$, hence a larger $f_i$ and higher priority.
(b) **Yes** — a CPU-bound process (large $c_i$, low $f_i$) can starve if higher-priority I/O-bound processes keep arriving.

## [S26-Q2.4] ch6 | swap spinlock (4 pts)
`swap(x, v)` atomically sets x to v and returns the old value of x. `locked` = 1 when held, 0 otherwise. (a) Write the line that acquires the spinlock with a busy-spin loop. (b) Advantage and disadvantage of a spinlock.

**Answer:**
(a) `while (swap(locked, 1) == 1);`   (release: `locked = 0;`)
(b) Disadvantage: wastes CPU cycles due to busy waiting. Advantage: no context switch is needed when a process must wait on a lock (a context switch can take considerable time) — good for short critical sections on multiprocessors.

## [S26-Q3.1] ch3 | fork tree with break (8 pts)
```c
for (int i = 0; i < n; i++) {
    if (fork()) fork();
    else break;
}
```
(a) n = 2: draw the process tree; total processes and number of breaks. (b) Relationship between total processes and n.

**Answer:**
(a) **7 processes, 3 breaks.** Tree: P0 → P1 (break), P2, P3 (break), P4; P2 → P5 (break), P6.
(b) Each active process per iteration creates 2 children: the first breaks, the second keeps looping → active count doubles: $A_k = 2^k$. After $n$ iterations: active $= 2^n$, stopped $= 1 + 2 + \cdots + 2^{n-1} = 2^n - 1$. **Total** $= 2^{n+1} - 1$ (breaks $= 2^n - 1$).

## [S26-Q3.2] ch3 | fork + exec scenarios (8 pts)
```c
int ret = fork();
if (ret == 0) { printf("Hello1\n"); exec("some_executable"); printf("Hello2\n"); }
else if (ret > 0) { wait(NULL); printf("Hello3\n"); }
else { printf("Hello4\n"); }
```
List all possible scenarios and outputs.

**Answer:**
- Case I — fork succeeds, exec succeeds: **Hello1, Hello3** (exec replaces the image; Hello2 never runs).
- Case II — fork succeeds, exec fails (returns −1): **Hello1, Hello2, Hello3**.
- Case III — fork fails: **Hello4**.
(Hello3 always last because the parent waits.)

## [S26-Q3.3] ch3 | pipe + dup fill-in (8 pts)
Child counts even numbers in 1.txt, parent in 2.txt (file: length then elements, read with scanf); child sends its count via pipe; parent prints the total.

**Answer:**
- Blank 1: `close(0)`  · Blank 2: `dup(fin)` (stdin now refers to the file)
- Blank 3: `if (number % 2 == 0) cnt++`
- Blank 4.1: `fd[1]` · 4.2: `&cnt`   (child: `write(fd[1], &cnt, sizeof(int))`)
- Blank 5.1: `fd[0]` · 5.2: `&child_cnt` (parent: `read(fd[0], &child_cnt, sizeof(int))`)

## [S26-Q4.1] ch5 | MLFQ Q0 RR4 / Q1 RR8 / Q2 FCFS (8 pts)
P1 (0, 9), P2 (2, 25), P3 (6, 7), P4 (14, 18), P5 (45, 15), P6 (58, 6). New jobs → Q0; full quantum → demote; Q0 arrival preempts Q1/Q2 immediately; preempted job → head of its queue; no demotion when preempted.

**Answer:**
Gantt: `0 P1 4 P2 8 P3 12 P1 14 P4 18 P1 21 P2 29 P3 32 P4 40 P2 45 P5 57 P2 58 P6 64 P2 71 P4 77 P5 80` (P5 45–49 Q0 then 49–57 Q1; P6 58–62 Q0 then 62–64 Q1).
Waiting = completion − arrival − burst: P1 21−0−9 = 12; P2 71−2−25 = 44; P3 32−6−7 = 19; P4 77−14−18 = 45; P5 80−45−15 = 20; P6 64−58−6 = 0 → **avg** $= \frac{140}{6} = 23.33$.
Response (end of first run − arrival): 4, 6, 6, 4, 4 (49−45), 4 (62−58) → **avg** $= \frac{28}{6} = 4.67$ (6.33 also accepted if P5/P6 merged).

## [S26-Q4.2] ch5 | RM / EDF with D < T (10 pts)
(t, d, p): P1 (1, 3, 4), P2 (2, 4, 5), P3 (2, 6, 7), P4 (1, 5, 8); all arrive at 0; draw 0–16; ties → smaller ID; count missed deadlines.

**Answer:**
- **RM** (P1 > P2 > P3 > P4 by period): `0 P1 1 P2 3 P3 4 P1 5 P2 7 P3 8 P1 9 P3 10 P2 12 P1 13 P3 14 P3 15 P2 16` → missed: P3 (d 6, finished 8), P4 (d 5, never), P3 (d 13, finished 14), P4 (d 13, never) → **4 missed**. (U = 1.06 > 1.)
- **EDF**: `0 P1 1 P2 3 P4 4 P3 6 P1 7 P2 9 P1 10 P3 12 P4 13 P2 15 P1 16` → missed: P2 (d 14, finished 15), P1 (d 15, finished 16) → **2 missed**.

## [S26-Q4.3] ch5 | Dynamic priority (9 pts)
Larger value = higher priority; waiting changes priority at rate $\alpha$, running at rate $\beta$; tie → larger ID. P1 (0, 7), P2 (3, 5), P3 (6, 6), P4 (9, 4).

**Answer:**
- (a) $\alpha = 0,\ \beta = 3$, initial 0: **`0 P1 7 P3 13 P4 17 P2 22`**
- (b) $\alpha = 1,\ \beta = 0$, only P1, P2, check every 3: **`0 P1 3 P2 6 P1 9 P2 11 P1 12`**
- (c) $\alpha = 1,\ \beta = -2$, initial 30, check every 3: **`0 P1 3 P2 6 P3 9 P4 12 P1 15 P2 17 P3 20 P4 21 P1 22`**

## [S26-Q5] ch6 | Semaphore ordering (8 pts)
A depends on B and C; B depends on C. s0, s1, s2 initialised to 0. workerA: BLANK1; wait(&s1); print A. workerB: BLANK2; print B; signal(&s2). workerC: BLANK3; print C; BLANK4; signal(&s1).

**Answer:**
BLANK1 `wait(&s2)` · BLANK2 `wait(&s0)` · BLANK3 `/* Nothing */` · BLANK4 `signal(&s0)` → order always C, B, A.

---

## [F19-Q1.1] ch2 | Linker and loader (2 pts)
What do the linker and loader do, respectively?

**Answer:**
The linker combines relocatable object files (and libraries) into a single binary executable file; the loader loads the binary executable file into memory so it can run.

## [F19-Q1.2] ch1 | Locality (3 pts)
What are temporal locality and spatial locality?

**Answer:**
Temporal locality: a memory location accessed recently is likely to be accessed again in the near future. Spatial locality: locations near a recently accessed location are likely to be accessed soon.

## [F19-Q1.3] ch2 | Why separate API and system calls (2 pts)
Two reasons for separating APIs from the underlying system calls?

**Answer:**
(1) Program portability — the API stays the same across platforms. (2) Hide the complex details of system calls from programmers.

## [F19-Q1.4] ch2 | LKM vs layered (3 pts)
Similarity and difference between the loadable-kernel-module approach and the layered approach?

**Answer:**
Similarity: functionality is divided into modules, each with a well-defined interface. Difference: LKM is more flexible — any module can call any other module (no higher/lower layer restriction), and modules can be loaded/removed at run time.

## [F19-Q2.1] ch3 | State transitions (3 pts)
Fill in the actions for: running→ready, ready→running, running→waiting, waiting→ready.

**Answer:**
running→ready: **interrupt**; ready→running: **scheduler dispatch (CPU scheduling)**; running→waiting: **I/O or event wait**; waiting→ready: **I/O or event completion**.

## [F19-Q2.2] ch3 | Socket (2 pts)
Four pieces of information that uniquely define a socket connection?

**Answer:**
Source IP address, source port number, destination IP address, destination port number.

## [F19-Q2.3] ch4 | Thread unique vs shared (3 pts)
Three elements unique to each thread and three shared.

**Answer:**
Unique: program counter, registers (state), stack (thread ID). Shared: code, data (globals/heap), open files.

## [F19-Q2.4] ch3 | Shell system calls (3 pts)
Two system calls a shell must execute to start a new process on UNIX?

**Answer:**
`fork()` — clones the calling process (creates a child); `exec()` — overlays/replaces the child's address space with a new program (loads the program to run).

## [F19-Q2.5] ch5 | Multicore vs SMP, CMT (4 pts)
Two advantages of multicore vs conventional SMP; reason for chip multithreading (hyper-threading).

**Answer:**
Multicore is faster (on-chip communication) and consumes less power than separate single-core chips. CMT exploits **memory stall**: processors are much faster than memory, so a core may spend up to ~50% of its time waiting for data; with multiple hardware threads the core switches to another thread while one waits.

## [F19-Q2.6] ch3 | Lines printed vs n (5 pts)
```c
for (i = 0; i < n; ++i) { if (fork()) printf("Fork!\n"); else printf("Fork!\n"); }
```

**Answer:**
Each iteration doubles the processes and every process prints one line: iteration $i$ prints $2^i$ lines → total $2 + 4 + \cdots + 2^n = 2^{n+1} - 2$ ✅

## [F19-Q2.7] ch3 | fork()==fork() || fork()!=fork() (5 pts)
```c
if (fork() == fork() || fork() != fork()) fork();
printf("Fork!\n");
```

**Answer:**
**23.** After `fork()==fork()` there are 4 processes; only the one that got 0 twice is true → it skips the rest of `||` and forks → 2 lines. The other 3 run `fork()!=fork()` → 12 processes; 9 are true and fork again → 18; 3 false → 3. Total 2 + 18 + 3 = 23 ✅

## [F19-Q3.1] ch5 | Which threads does the OS schedule (4 pts)
Which threads are scheduled by the OS? How does mapping user threads onto kernel threads/LWPs differ from CPU scheduling?

**Answer:**
The OS schedules **kernel-level threads**. Scheduling user threads onto LWPs/kernel threads (PCS) is done by the thread library, usually by programmer-set priority, among threads of the **same process**; CPU scheduling (SCS) chooses which kernel thread runs on a CPU among **all** kernel threads in the system.

## [F19-Q3.2] ch5 | FCFS problem; RR worse than FCFS (3 pts)

**Answer:**
FCFS: **convoy effect** — short processes stuck behind a long one. RR has worse turnaround than FCFS when all processes have the **same CPU burst length that is larger than the quantum** (they all finish near the end).

## [F19-Q3.3] ch5 | MLFQ approximates SJF (3 pts)

**Answer:**
Short interactive jobs finish in the top (high-priority) queue, while long CPU-bound jobs sink to lower queues — so short jobs are served first, like SJF. Advantage: **no prior knowledge of CPU burst times is needed**.

## [F19-Q3.4] ch5 | EDF to t = 38 (6 pts)
P1 (period = deadline 10, t 4), P2 (16, 2), P3 (20, 8).

**Answer:**
`0 P1 4 P2 6 P3 14 P1 18 P2 20 P1 24 P3 32 P1 36 P2 38` (deadline ties at t = 10 and 30 → the running P3 continues). No deadline missed.

## [F19-Q3.5] ch5 | Least Used First (12 pts)
LUF picks the process that has used the fewest CPU cycles; tie → FCFS; preempted process goes to the end of the queue; scheduler runs on completion and on new arrival. P1 (0, 25), P2 (15, 25), P3 (25, 5), P4 (40, 5).

**Answer:**
(a) `0 P1 15 P2 25 P3 30 P2 40 P4 45 P1 55 P2 60`
(b) TAT / RT / WT: P1 55 / 15 / 30; P2 45 / 10 / 20; P3 5 / 5 / 0; P4 5 / 5 / 0.
(c) Similar to SRTF: short jobs tend to get high priority. Different: under LUF a process that has already run a long time is likely to starve; under SRTF a process with a long burst is likely to starve from the beginning.

## [F19-Q3.6] ch5 | FCFS / SJF / RR4 / SRTF (12 pts)
P1 (0, 8), P2 (7, 13), P3 (9, 1), P4 (11, 5), P5 (20, 7), P6 (27, 1).

**Answer:**
- FCFS `0 P1 8 P2 21 P3 22 P4 27 P5 34 P6 35` — WT 0,1,12,11,7,7 → **6.33**
- SJF `0 P1 8 P2 21 P3 22 P4 27 P6 28 P5 35` — WT 0,1,12,11,8,0 → **5.33**
- RR q=4 `0 P1 8 P2 12 P3 13 P4 17 P2 21 P4 22 P5 26 P2 30 P5 33 P6 34 P2 35` — WT 0,15,3,6,6,6 → **6.0** (corrected official)
- SRTF `0 P1 8 P2 9 P3 10 P2 11 P4 16 P2 20 P5 27 P6 28 P2 35` — WT 0,15,0,0,0,0 → **2.5** (official; keeping P2 on the tie at t=20 also gives 2.5)

## [F19-Q4.1] ch6 | CS requirements (4 pts)

**Answer:**
(1) **Mutual exclusion** — if a process is executing in its CS, no other process can be in its CS. (2) **Progress** — if no process is in its CS and some want to enter, the selection of the next one cannot be postponed indefinitely. (3) **Bounded waiting** — there is a bound on the number of times other processes may enter their CS after a process has requested entry and before that request is granted.

## [F19-Q4.2] ch6 | Binary semaphore vs mutex (3 pts)

**Answer:**
No. A binary semaphore initialised to 1 can be used as a mutex lock, but it can also be used for other synchronization purposes (e.g., initialised to 0 for ordering/signalling).

## [F19-Q4.3] ch6 | Possible values of c (8 pts)
a = 7, b = 2, c = 5. T1: `if (a < 0) c = b - a; else c = b + a;` T2: `b = 8; a = -6;`

**Answer:**
**14, 2, 9, 15, −4** — (a<0 branch: 8−(−6) = 14); else-branch: T2 done before c computed: 8+(−6) = 2; T2 after: 2+7 = 9; b written before read but a after: 8+7 = 15; b read before write, a written before read: 2+(−6) = −4.

## [F19-Q4.4] ch6 | Semaphores L = 3, R = 0 with putc (10 pts)
P1: wait(L); putc('C'); signal(R). P2: wait(R); putc('A'); putc('B'); signal(R). P3: wait(R); putc('D').

**Answer:**
(a) **3** D's. (b) A's: min **0**, max **infinite**. (c) `CABABDCDABCABD` — **No** (after "CABABDCD", R = 0, so P2 cannot print the next A before a third C). (d) `CABACDBCABDD` — **Yes**.

---

## [F20-Q2.1] ch2 | Microkernel (4 pts)

**Answer:**
Main idea: remove all nonessential components from the kernel and implement them as system/user-level programs in separate address spaces; communicate by message passing. Advantage: small kernel, easier to extend and port, more secure and reliable. Disadvantage: performance suffers due to increased system-function overhead (user↔kernel message passing).

## [F20-Q2.2] ch2 | Linker and loader (4 pts)

**Answer:**
Linker: combines several relocatable object modules into a single binary executable image (stored on disk). Loader: loads the executable into memory for execution.

## [F20-Q2.3] ch4 | Heavyweight vs lightweight (4 pts)

**Answer:**
A process is heavyweight because it owns an address space and resources; creating one duplicates program and data. A thread is lightweight — only an execution unit (PC, registers, stack) that shares code, data and files with other threads of its process, so creating it needs no duplication.

## [F20-Q2.4] ch5 | Common vs per-processor ready queue (4 pts)

**Answer:**
Common queue: easy load balancing (no CPU idle while the queue is non-empty) but hard to keep processor affinity (and needs locking). Per-processor queues: natural processor affinity but need push/pull migration for load balancing.

## [F20-Q2.5] ch5 | MLFQ benefits (4 pts)

**Answer:**
(1) Resembles SJF/SRTF performance without prior knowledge of the next CPU burst (2 pts); (2) RR-like good response time for interactive jobs (1); (3) fair — all processes make progress (1).

## [F20-Q3.1] ch3 | Possible outputs (10 pts)
```c
if (fork() == 0) {
    if (fork() > 0) { printf("1"); wait(NULL); printf("2"); }
    else printf("3");
} else printf("4");
```

**Answer:**
Unbuffered: **8** outputs — "2" after "1" and "3"; "4" anywhere: 1342, 1432, 3142, 4132, 3412, 4312, 1324, 3124. Buffered ("1" and "2" flushed together): 3 outputs — 4312, 3412, 3124.

## [F20-Q3.2] ch3 | Count "a" (13 pts)
```c
if (!fork()) { for (int i = 0; i < n; i++) if (fork()) fork(); }
fork(); printf("a");
```

**Answer:**
First fork: the child enters the loop; each iteration every process becomes 3 → $3^n$ processes from the child branch. Plus the original → $3^n + 1$. The final fork doubles → **$2(3^n + 1)$ \"a\"s** ✅

## [F20-Q4.1] ch5 | FCFS / SJF / SRTF (9 pts)
P1 (0, 9), P2 (3, 3), P3 (8, 2), P4 (10, 6), P5 (16, 8), P6 (20, 5).

**Answer:**
- FCFS `0 P1 9 P2 12 P3 14 P4 20 P5 28 P6 33` → (0+6+4+4+4+8)/6 = **4.33**
- SJF `0 P1 9 P3 11 P2 14 P4 20 P6 25 P5 33` → (0+8+1+4+9+0)/6 = **3.67**
- SRTF `0 P1 3 P2 6 P1 8 P3 10 P1 14 P4 20 P6 25 P5 33` → (5+0+0+4+9+0)/6 = **3.0**

## [F20-Q4.2] ch5 | Two-level feedback queue with aging (10 pts)
Q0 RR 4 ms (high), Q1 FCFS; new → Q0; Q0 arrival preempts Q1; preempted Q1 process → head of Q1 with timer reset; a Q1 process whose timer reaches 8 ms rejoins Q0. P1 (0, 9), P2 (3, 3), P3 (8, 2), P4 (10, 9), P5 (13, 4), P6 (18, 5).

**Answer:**
`0 P1 4 P2 7 P1 8 P3 10 P4 14 P5 18 P1 22 P6 26 P4 30 P6 31 P4 32` → WT (13+1+0+13+1+8)/6 = **6**. (P1 ages back to Q0 at 16; P4 at 22.)

## [F20-Q4.3] ch5 | Priority + RR (8 pts)
Smaller number = higher priority; preemptive; same priority → RR q = 4. P1 (0, 9, 2), P2 (3, 3, 1), P3 (8, 5, 4), P4 (10, 2, 4), P5 (16, 8, 5), P6 (20, 5, 3).

**Answer:**
`0 P1 3 P2 6 P1 12 P3 16 P4 18 P3 19 P5 20 P6 25 P5 32` → (3+0+6+6+8+0)/6 = **3.83**

## [F20-Q5] ch6 | Possible values of c (15 pts)
a = 7, b = 2. T1: `if (b < 0) c = b - a; else c = b + a;` T2: `b = -8; a = 6;`

**Answer:**
**−14, −15, −2, −1, 8, 9** (2.5 marks each).

---

## [Sp21-Q1.1] ch3 | pid1/pid2 (5 pts)
```c
pid1 = fork(); pid2 = fork();
if (pid1 > 0) if (pid2 == 0) fork();
```

**Answer:**
**5** — 4 processes after two forks; only the child created by the parent's second fork has pid1 > 0 and pid2 == 0, so one more process ✅

## [Sp21-Q1.2] ch3 | Nested loop (5 pts)
```c
if (fork() == 0) { for (int i = 0; i < 5; i++) if (fork() == 0) fork(); }
fork();
```

**Answer:**
**$(3^5 + 1) \times 2 = 488$** ✅

## [Sp21-Q1.3] ch3 | Output orderings (8 pts)
```c
printf("A\n");
if (fork() == 0) printf("B\n");
else { printf("C\n"); ___A___ }
printf("D\n");
```

**Answer:**
(a) empty: ABDCD, ABCDD, ACBDD, ACDBD. (b) `wait(NULL)`: ABDCD, ABCDD, ACBDD. (c) `printf("E\n")`: ABDCED, ABCDED, ABCEDD, ACBDED, ACBEDD, ACEBDD, ACEDBD.

## [Sp21-Q2.1] ch5 | FCFS / SJF / RR8 / SRTF (10 pts)
P1 (0, 2), P2 (4, 12), P3 (6, 6), P4 (9, 4), P5 (13, 5).

**Answer:**
FCFS 7.2 · SJF 6.6 · RR(8) 7.6 · SRTF 4.2 (Gantt charts in Ch5 §14.9; note the idle gap 2–4).

## [Sp21-Q2.2] ch5 | MLFQ q=2, q=4, FCFS (8 pts)
P1 (0, 10), P2 (10, 8), P3 (8, 30), P4 (16, 2), P5 (22, 8), P6 (6, 22).

**Answer:**
`0 P1 2 P1 6 P6 8 P3 10 P2 12 P6 16 P4 18 P3 22 P5 24 P2 28 P5 32 P1 36 P6 52 P3 76 P2 78 P5 80` → WT 26, 60, 38, 0, 50, 24 → **33**.

## [Sp21-Q2.3] ch5 | EDF vs RM (8 pts)
P1 (1, 3, 3), P2 (2, 4, 4), 0–14, soft real-time.

**Answer:**
EDF `0 P1 1 P2 3 P1 4 P2 6 P1 7 idle 8 P2 10 P1 11 idle 12 P1 13 P2 14`; RM `0 P1 1 P2 3 P1 4 P2 6 P1 7 idle 8 P2 9 P1 10 P2 11 idle 12 P1 13 P2 14`. EDF is better: dynamic deadline-based priorities can meet more deadlines (up to 100% utilization) than RM's static priorities.

## [Sp21-Q3.1] ch6 | compare_and_reset spinlock (4 pts)

**Answer:**
`struct spinlock { int value = 0; };` · acquire: `while (compare_and_reset(&lock->value, 0, 1) == 0) ;` · release: `lock->value = 0;`

## [Sp21-Q3.2] ch6 | Fix the bounded-waiting algorithm (7 pts)

**Answer:**
Problems: (1) only processes with index > i are checked → lower-index processes can wait unboundedly; (2) the lock is never released when nobody is waiting. Fix: cyclic scan `j = (i + 1) % n; while ((j != i) && !waiting[j]) j = (j + 1) % n; if (j == i) lock = 0; else waiting[j] = false;`

---

## [HW1-Q2.1] ch1 | AMAT + locality (6 pts)
Hit ratio 90%, hit time 2 ns, miss time 50 ns.

**Answer:**
$0.9 \times 2 + 0.1 \times 50 =$ **6.8 ns**. Temporal: recently accessed items are likely accessed again (e.g., loop counter, loop body instructions). Spatial: items near recent accesses are likely accessed soon (e.g., sequential array elements a[i], a[i+1]).

## [HW1-Q2.2] ch1 | Multiprogramming vs time sharing (6 pts)

**Answer:**
Multiprogramming keeps several jobs in memory; when one waits for I/O, the CPU switches to another, so the CPU always has work → higher utilization. Time sharing switches among jobs so frequently (timer + CPU scheduling) that users can interact with each program while it runs → short response time, interactive computing.

## [HW1-Q2.3] ch3 | State sequence (6 pts)

**Answer:**
New → Ready → Running → Waiting → Ready → Running → Ready → Running → Terminated. When leaving Running, the PCB saves the process state, program counter, CPU registers, plus updated scheduling, accounting and I/O-status information.

## [HW1-Q2.4] ch2 | read(): user → kernel → user (6 pts)

**Answer:**
(1) read() in libc puts the system-call number and parameters in registers and executes a trap instruction. (2) The trap switches to kernel mode; the kernel indexes the system-call table and runs the read service. (3) The kernel stores the return value and executes return-from-trap, which switches back to user mode and resumes after the call.

## [HW1-Q2.5] ch3 | Parent → child through a pipe (6 pts)

**Answer:**
Call `pipe(fd)` **before** `fork()`; after fork, the parent (writer) closes `fd[0]` and writes to `fd[1]`; the child (reader) closes `fd[1]` and reads from `fd[0]`; close the used ends when done.

## [HW1-Q3.1] ch3 | Values of x (15 pts)

**Answer:**
C1: 3, C2: 5, P: 2 (each process has its own copy of x). Outputs: "C1: 3, C2: 5, P: 2" or "C2: 5, C1: 3, P: 2". Moving the first wait before `x *= 2` guarantees C1, C2, P order; values unchanged.

## [HW1-Q3.2] ch3 | exec worker (15 pts)

**Answer:**
3 processes (parent → child → grandchild; the grandchild execs worker). X is not printed (successful exec never returns). Outputs: A P W C D · A W P C D · A W C P D.

## [HW1-Q3.3] ch3 | Pipe parent → child (10 pts)

**Answer:**
(a) Parent closes fd[0], writes to fd[1]; child closes fd[1], reads fd[0]; parent → child. (b) "Child: 12" then "Parent: done" — read blocks until data arrives, and the parent waits for the child. (c) No — separate pipe() calls after fork create two unrelated pipes, with no shared descriptors.

---

## [HW2-Q2.1] ch4 | Different PC/registers (6 pts)

**Answer:**
Yes — each thread has its own PC, register set and stack; saved in its **TCB** when not running.

## [HW2-Q2.2] ch4 | Many-to-one on 4 cores (6 pts)

**Answer:**
No — all user threads map to one kernel thread, which runs on one core at a time; only concurrency, no parallelism (and one blocking call blocks all).

## [HW2-Q2.3] ch4 | Ctrl+C (6 pts)

**Answer:**
Asynchronous (generated by an event external to the process). Yes — install a user-defined handler with `signal(SIGINT, handler)` to override the default (terminate).

## [HW2-Q2.4] ch5 | Hard affinity (6 pts)

**Answer:**
No — hard affinity restricts T to CPU 0 and CPU 1; load balancing may move it between those two only.

## [HW2-Q2.5] ch5 | RM vs EDF at t = 50 (6 pts)

**Answer:**
No. RM picks A (shorter period, static) → B finishes at 85 and misses 80. EDF picks B (deadline 80 < 100) → B finishes at 60, A at 85; both meet deadlines.

## [HW2-Q3.1] ch4 | Amdahl (10 pts)

**Answer:**
(a) $\dfrac{1}{0.2 + 0.8/4} =$ **2.5**. (b) $N \to \infty$: $\dfrac{1}{0.2} =$ **5**.

## [HW2-Q3.2] ch5 | SRTF and RR q=3 (20 pts)
P1 (0, 7), P2 (1, 3), P3 (4, 5), P4 (10, 2).

**Answer:**
SRTF `0 P1 1 P2 4 P3 9 P1 10 P4 12 P1 17` → avg WT 2.5, avg TAT 6.75. RR(3) `0 P1 3 P2 6 P1 9 P3 12 P1 13 P4 15 P3 17` → avg WT 4.75, avg TAT 9.

## [HW2-Q3.3] ch5 | MLFQ (10 pts)
Q0 RR4, Q1 RR8, Q2 FCFS; P1 (0, 20), P2 (1, 5), P3 (11, 2); preempted Q1 job keeps the unused part of its quantum.

**Answer:**
`0 P1(Q0) 4 P2(Q0) 8 P1(Q1) 11 P3(Q0) 13 P1(Q1) 18 P2(Q1) 19 P1(Q2) 27`. At t = 11, P1 goes to the head of Q1 (ahead of P2) with 5 ms of its Q1 quantum left.


---

## [F22-Q3] ch3 | fork() == fork() in a loop (10 pts)
```c
int main() {
    int i, n;
    scanf("%d", &n);
    for (i = 0; i < n; i++) {
        if (fork() == fork()) {
            printf("fork() == fork()!\n");
            fflush(stdout);
        }
    }
    return 0;
}
```
(a) Number of processes and of printed lines for n = 1, 2, 3. (b) In terms of n.

**Answer:**
(a) n = 1: 4 processes, 1 line; n = 2: 16, 5; n = 3: 64, 21.
(b) Each iteration every process does two forks → ×4, so **$4^n$ processes**. In each iteration only the grandchild that received 0 from both forks sees equal return values, so the iteration that starts with $4^{k}$ processes prints $4^{k}$ lines. Total lines $= 4^0 + 4^1 + \cdots + 4^{n-1} = \dfrac{4^n - 1}{3}$. ✅ (verified)

## [F24-P3.1] ch3 | fork in nested loops (10 pts)
```c
for (i = 0; i < M; i++) {
    pid_t pid = fork();          // line X
    if (!pid) {
        for (j = 0; j < N; j++)  // line Y
            fork();
    }
}
```
(a) Which process executes line Y? (b) M = N = 1: how many processes? (c) In terms of M and N.

**Answer:**
(a) The **child** — `!pid` is true only where `fork()` returned 0.
(b) **3** — the parent forks a child (2), the child forks once in the inner loop (3).
(c) Let $f(k)$ be the number of processes one process becomes with $k$ outer iterations left: the parent continues ($f(k-1)$) and the child becomes $2^N$ processes that all continue ($2^N f(k-1)$), so $f(k) = (2^N + 1)\,f(k-1)$ and the total is $(2^N + 1)^M$. ✅ (verified)

## [S25-MC12] ch3 | Nested short-circuit forks
```c
if (fork() || fork()) {
    if (fork() && !fork()) {
        fork();
    }
}
```
How many processes are there in total (suppose all fork() succeed)?

**Answer:**
**9.** `fork() || fork()`: 2 processes enter the if-clause, 1 the else-clause. Inside, `fork() && !fork()`: 1 process enters the inner if and forks once (→ 2), 2 processes skip it → each outer-if process becomes 4. Total $2 \times 4 + 1 = 9$ (8 newly created). ✅ (verified)

## [S23-PRR] ch5 | Preemptive priority + RR with different arrivals (q = 2)
Smaller number = higher priority; processes with equal priority share the CPU round-robin with q = 2; a higher-priority arrival preempts. Process table reconstructed from the official answer: P1 (0, 5, 2), P2 (1, 3, 1), P3 (2, 8, 2), P4 (8, 2, 1), P5 (9, 6, 2).

**Answer:**
`0 P1 1 P2 4 P1 5 P3 7 P1 8 P4 10 P1 11 P3 13 P5 15 P1 16 P3 18 P5 20 P3 22 P5 24` (official Gantt). A preempted process **keeps the remaining part of its quantum** — P1 runs only 1 unit at 4–5 and at 10–11. Resetting the quantum is the common mistake. Avg WT $= \frac{11+0+12+0+9}{5} = 6.4$.

## [Lab2-Q1] ch3 | Counting printed values
```c
pid_t pid = fork();  int cnt = 0;
if (pid == 0) {
    cnt += 10;  pid = fork();
    if (pid != 0) { cnt += 10;  pid = fork(); }
}
printf("%d \n", pid);  printf("%d \n", cnt);
```
How many non-zero PIDs, how many '0's and how many '10's are printed?

**Answer:**
4 processes print (pid, cnt): P0 (≠0, 0), C1 (≠0, 20), C2 (0, 10), C3 (0, 20) → **2** non-zero PIDs, **3** zeros, **1** ten. ✅ (verified)

## [Lab2-Q2] ch3 | Force the order process 3 → 2 → 1
```c
int x = 0;
if (BLANK1) { x = x + 1; BLANK2; printf("The value x in process 1 is %d\n", x); }
else if (BLANK3) { x = x + 1; BLANK4; printf("The value x in process 2 is %d\n", x); }
else { x = x + 1; printf("The value x in process 3 is %d\n", x); }
```
Fill the blanks so the output is always process 3, then 2, then 1 (each printing x = 1).

**Answer:**
BLANK1 `fork()` · BLANK2 `wait(0)` · BLANK3 `fork()` · BLANK4 `wait(0)` (`fork() > 0` / `wait(NULL)` also fine). Each process waits for the child it created, so 3 prints before 2, and 2 before 1; every process has its own copy of x, so each prints 1.

## [Lab4-EX1] ch3 | Two ordinary pipes for two-way communication
Parent sends "Parent" to the child and the child sends "Child" to the parent using `p2c[2]` and `c2p[2]`. Fill BLANK1–BLANK6 (create pipes; child writes then reads; parent reads then writes).

**Answer:**
BLANK1 `pipe(p2c)` · BLANK2 `pipe(c2p)` · BLANK3 `write(c2p[1], msg, 6)` · BLANK4 `read(p2c[0], buffer, 7)` · BLANK5 `read(c2p[0], buffer, 6)` · BLANK6 `write(p2c[1], msg, 7)` (5 / 6 bytes also accepted). Output: "Parent received the message: Child" and "Child received the message: Parent".

## [Lab6-Q1] ch6 | Semaphores for strict thread order
T1: `wait(S1); CS; signal(S2);` T2: `wait(S2); CS; signal(S3);` T3: `wait(S3); CS; signal(S1);` — initial values for the order T1, T2, T3, T1, …?

**Answer:**
**S1 = 1, S2 = 0, S3 = 0** (only T1 can start; each thread passes the turn to the next).

## [Lab6-Q2] ch6 | P0 → P1 → P2 ordering blanks
S0 = BLANK1, S1 = BLANK2, S2 = BLANK3; P0: `wait(S0); CS; BLANK4;` P1: `BLANK5; CS; BLANK6;` P2: `BLANK7; CS; signal(S0);`

**Answer:**
S0 = **1**, S1 = **0**, S2 = **0**; BLANK4 `signal(S1)`; BLANK5 `wait(S1)`; BLANK6 `signal(S2)`; BLANK7 `wait(S2)`.

## [Lab6-Q3] ch6 | Mutex blanks
`void *add(void *arg) { pthread_mutex_t* m = BLANK1; for (5000 times) { BLANK2; ++counter; BLANK3; } }` — two threads run `add` with `&mutex`. Missing code? Purpose? Final counter?

**Answer:**
BLANK1 `(pthread_mutex_t*) arg` · BLANK2 `pthread_mutex_lock(m)` · BLANK3 `pthread_mutex_unlock(m)`. Purpose: protect the shared variable `counter` (critical section). Final value **10,000**.

## [Lab6-Q4] ch6 | Possible outputs with semaphores X, Y = 0
Process A: `wait(X); print "b"; signal(Y); wait(Y); print "c"; signal(Y);` Process B: `signal(X); print "a"; wait(Y); print "d";`

**Answer:**
If both complete: **abcd, bacd, bcad**. If B takes Y first, A blocks forever at its second `wait(Y)` → **bad, abd** (A never finishes). ✅ (verified by exhaustive search)

## [Lab6-Q5] ch6 | Counting semaphore permits
S0 = 1, S1 = S2 = S3 = 0. P0: `while(true){ wait(S0); print '1'; release(S1); release(S2); release(S3); }` P1: `wait(S1); release(S0);` P2: `wait(S2); release(S0); wait(S3); release(S0);` — how many '1's?

**Answer:**
**4** — S0 permits: initial 1 + P1 gives 1 + P2 gives 2. After the first print P0 releases S1, S2, S3, so P1 and P2 can produce all of them; then P0 blocks forever. ✅ (verified)

## [Lab6-Q6] ch6 | Readers–writers with two mutexes
Fill the reader's blanks (mutex protects read_count; rw_mutex protects the data).

**Answer:**
Entry: `pthread_mutex_lock(&mutex); read_count++; if (read_count == 1) pthread_mutex_lock(&rw_mutex); pthread_mutex_unlock(&mutex);` Exit: `pthread_mutex_lock(&mutex); read_count--; if (read_count == 0) pthread_mutex_unlock(&rw_mutex); pthread_mutex_unlock(&mutex);` The first reader locks writers out and the last reader lets them in.

## [Lab6-Q7] ch6 | Race condition values
a = 1, b = 3, c = 0. Thread 1: `a = b + 1; c = a - b;` Thread 2: `a = 13; b = 10; c = 2;` All possible final values of c?

**Answer:**
**−6, 1, 2, 3, 10** — 2 if T2's `c = 2` is last; 1 (T1 reads a=4, b=3 then T2 runs; or T2 first then a = 11, c = 11 − 10); −6 (T1 reads a=4, then T2 sets b=10); 3 (T2 runs after T1's `a = 4`, T1 reads a=13, b=10); 10 (T1 reads a=13 and b=3 between T2's writes). ✅ (verified by exhaustive search)
