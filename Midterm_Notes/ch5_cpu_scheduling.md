# Chapter 5 — CPU Scheduling（CPU 排程）

> 📌 **考試範圍提示**：**Ch5 係分數最重嘅一章**（S26：27/100；F19：40/100；F20：27+；Sp21：26）。必考：
> 1. **Gantt chart + average waiting / turnaround / response time**：FCFS、SJF、SRTF、RR、Priority（± RR）、**MLFQ**（每年都有！）、自創 policy（LUF、dynamic priority）
> 2. **RM / EDF** real-time Gantt + missed deadlines
> 3. MC / short：preemptive vs non-preemptive、convoy effect、starvation & aging、MLFQ 優點、RR vs FCFS、exponential averaging、Little's formula、PCS vs SCS、processor affinity、load balancing、hard vs soft real-time
> ⚠️ **Response time 本科定義 = 第一次運行「完結」時間 − arrival time**（slide 5.12），唔係課本「第一次開始」！

---

## 1. Basic Concepts（基本概念）[5.4–5.7]

### 1.1 CPU–I/O Burst Cycle
- **Objective of multiprogramming：have a process running at all times → maximize CPU utilization.**
- **Process execution consists of cycles of CPU execution and I/O wait — CPU burst and I/O burst.**
- [5.5] **Histogram of CPU-burst times：many short CPU bursts, few long ones (long-tail distribution)**。**I/O-bound → many short CPU bursts；CPU-bound → a few long CPU bursts.** 呢個分佈對設計 scheduling algorithm 好重要。
- CPU idle 時，OS 由 ready queue 揀一個 process（除非 ready queue empty）→ 由 **CPU scheduler（process scheduler / short-term scheduler）** 揀。

### 1.2 When does scheduling happen? ⭐⭐ [5.6]
CPU scheduling 可能喺四種情況發生：
1. **Running → waiting**（e.g. I/O request, `wait()`）
2. **Process terminates**
3. **Running → ready**（e.g. **interrupt / timer**）
4. **Waiting → ready**（I/O completion）或者 **new → ready**（新 process 到達，priority 更高）
- **Scheduling under 1 and 2 is non-preemptive (cooperative)** — process **gives up the CPU voluntarily**。
- **Scheduling under 3 and 4 is preemptive.**
- Preemptive 要考慮：**access to shared data (race condition, Ch6)**、**preemption while in kernel mode**、**interrupts during crucial OS activities**。
> 📝 Sp21 MC：CPU scheduling decisions may take place in → **all of the above**（running→waiting、terminates、running→ready）。
> 📝 HW2 MC5：preemptive 例子 → **time quantum expires, running process moved back to the ready queue**（A terminate、B I/O、D wait() 都係自願 → non-preemptive）。

### 1.3 Dispatcher [5.7]
- **Dispatcher module gives control of the CPU to the process selected by the CPU scheduler**：
  1. **switching context** from one process to another
  2. **switching to user mode**
  3. **jumping to the proper location in the user program** to restart it
- **Dispatch latency — time for the dispatcher to stop one process and start another（overhead）。** 應該越快越好。
- `vmstat`（Linux）可睇 context switches 數目（每秒幾百次）。

---

## 2. Scheduling Metrics（排程指標）⭐⭐⭐ [5.8, 5.12]

| Metric | 定義 | 目標 |
|---|---|---|
| **CPU utilization** | **fraction of the time that the CPU is busy** | max |
| **Throughput** | **number of processes completed per unit time**（favors short processes） | max |
| **Turnaround time (TAT)** | **time to execute a particular process = completion time − arrival time** | min |
| **Waiting time (WT)** | **total time spent waiting in the ready queue = TAT − CPU burst** | min |
| **Response time (RT)** | **time from submission until the first response is produced** | min |
| **Fairness** | adequate allocation for different jobs/processes | — |

### 2.1 公式（本科 convention，必背）⭐
> 🧮 **Turnaround = Completion − Arrival**
>
> 🧮 **Waiting = Turnaround − CPU burst**
>
> 🧮 **Response = (completion of the FIRST run) − Arrival**
- **Response time 嘅「first run」完結** = 第一次上 CPU 嘅嗰段（RR / MLFQ 就係 **end of first quantum**，或者 burst 細過 quantum 就係完成時間）[5.12]。
  - Slide 5.13 例：RR q=4，P1(24), P2(3), P3(3) 全部 t=0 到 → **RT：P1 = 4, P2 = 7, P3 = 10，avg = 7**。
  - S26 MLFQ 官方：P1 response = 4 − 0 = 4（P1 跑 0–4）。
  - **非 preemptive (FCFS/SJF) 嘅 RT = TAT**（第一次 run 就跑完）。
- Waiting time 另一個計法（**gap method**）：將 Gantt chart 上 process 唔喺 CPU 嘅時間（由 arrival 起）加埋。兩個方法結果一樣：
  - S26 P2：gap = (4−2)+(21−8)+(40−29)+(57−45)+(64−58) = 44 ✔；formula = 71 − 2 − 25 = 44 ✔。
- S26 MC19 ✅「**Response time is the amount of time from when a request is submitted until the first response is produced**」。✗ WT = arrival 到完成（嗰個係 TAT）；✗ TAT = 等 ready queue 時間（嗰個係 WT）；✗ throughput = CPU busy fraction（嗰個係 utilization）。

---

## 3. FCFS — First-Come, First-Served ⭐ [5.9–5.10]
- 按 **arrival order** 排；**non-preemptive**（跑完 current CPU burst 先放）。
- 例：P1 = 24, P2 = 3, P3 = 3（全部 t=0）
  - 次序 P1, P2, P3：`0 P1 24 P2 27 P3 30` → **WT = 0, 24, 27 → avg 17；TAT avg = (24+27+30)/3 = 27**
  - 次序 P2, P3, P1：`0 P2 3 P3 6 P1 30` → **WT = 6, 0, 3 → avg 3；TAT avg = 13**
- ⭐ **Convoy effect — short processes stuck behind a long process**，令 average waiting time 好長，完全取決於 arrival order。One CPU-bound + many I/O-bound → **low I/O device utilization**。（例：銀行排隊存張支票，前面有人開戶）
> 📝 HW2 MC6：convoy effect → **several short processes wait behind a long process that arrived first**。
> 📝 **F19 Q3.2**：FCFS 問題 = **convoy effect**（short process stuck behind a long process）。

---

## 4. RR — Round Robin ⭐⭐⭐ [5.11–5.16]
- **FCFS + preemption**：每個 process 得 **time quantum q**（通常 **10–100 ms**）；用完 → **preempted and added to the end (tail) of the ready queue**。
- **n processes → each gets 1/n of CPU time in chunks of at most q；no process waits more than (n − 1)q time units** ⭐（ignoring context switch）。
- **Timer interrupts every quantum**；如果 burst（或 remaining）< q，process 自己完成就放 CPU。
- 例 [5.13]：q = 4，P1 24, P2 3, P3 3 → `0 P1 4 P2 7 P3 10 P1 14 P1 18 P1 22 P1 26 P1 30`
  - **WT：P1 = 6, P2 = 4, P3 = 7 → avg 5.67；TAT avg = (30+7+10)/3 = 15.67；RT = 4, 7, 10 → avg 7**
- **RR：average waiting time can be long, but more "fair"；better for short jobs than FCFS；better average response time → good for interactive jobs.**

### 4.1 Time quantum 大細 [5.14, 5.16] ⭐
- **q large → RR degenerates to FCFS.**（Sp21 MC 答案：**FCFS**）
- **q small → many context switches; q must be large w.r.t. context-switch time (< 10 µs), otherwise overhead too high.**（q 極細 = **processor sharing**：好似 n 個 processor 每個 1/n 速度）
- **Average turnaround time does not necessarily improve as q increases.**
- **TAT improves if most processes finish their CPU burst within a single quantum.**
- **Rule of thumb：80% of CPU bursts should be shorter than q.**

### 4.2 FCFS vs RR ⭐（F19 Q3.2 考過）[5.15]
- **Is RR always better than FCFS? No!** 例：**10 jobs start at the same time, each needs 100 s, q = 1 s → average turnaround time much worse under RR**（全部差唔多 1000 s 先完；FCFS 平均 550 s），**but average response time much better**。
> 📝 **F19 Q3.2 Model answer**：*RR performs worse than FCFS in turnaround time when all processes have the same (equal) CPU burst times that are longer than the time quantum — the jobs are interleaved and all finish near the end, whereas FCFS finishes them one by one.*
- 一般而言 **no clear winner between FCFS and RR** in TAT/WT — 取決於 burst times、arrival pattern、quantum size。

### 4.3 RR 做 Gantt chart 規則（考試用）
1. 用 **queue**（寫低每個時刻 queue 內容！）。
2. **新到達 process 加入 queue tail**；**quantum 用完嘅 process 都去 tail**。
3. ⚠️ **同一時刻**「新 process 到達」同「running process quantum 用完」→ convention：**新到達嗰個先入 queue，然後先放被 preempt 嗰個**（寫低 assumption）。
4. Process burst 完 → 即刻揀下一個（唔使等 quantum 完）。
5. Queue 空而 running process quantum 用完 → 佢繼續跑（再得一個 quantum）。

---

## 5. SJF / SRTF — Shortest Job First ⭐⭐⭐ [5.17–5.24]

### 5.1 SJF（non-preemptive）
- **Associate each process with the length of its next CPU burst; schedule the shortest.**（更準確叫 **shortest-next-CPU-burst**）
- ⭐ **SJF is optimal — gives the minimum average waiting time for a given set of processes.**
- **Difficulty：knowing the length of the next CPU request.**（所以 practical 難 implement；F20 MC15 答案 **SJF difficult to implement**）
- **Sketch proof**：**moving a short process before a long one decreases the waiting time of the short process more than it increases the waiting time of the long process → average waiting time decreases.**
- 例 [5.18]：P1 = 6, P2 = 8, P3 = 7, P4 = 3。Slide 個 chart **當全部 t = 0 到**：`0 P4 3 P1 9 P3 16 P2 24` → **avg WT = (3 + 16 + 9 + 0)/4 = 7**（slide 答案）。
  - ⚠️ 如果真係跟表入面 arrival（0, 2, 4, 5）：t=0 只有 P1 → `0 P1 6 P4 9 P3 16 P2 24` → WT = 0, 14, 5, 1 → avg 5。考試**一定要睇清楚有冇 arrival time**。

### 5.2 SRTF — Shortest-Remaining-Time-First（preemptive SJF）⭐
- **New arrival with burst shorter than the remaining time of the running process → preempts it.**
- Scheduling 喺 **every arrival (condition 4)** 都要 invoke。
- 例 [5.23]：P1(0,8), P2(1,4), P3(2,9), P4(3,5) → `0 P1 1 P2 5 P4 10 P1 17 P3 26`
  - **avg WT = [(10−1) + (1−1) + (17−2) + (5−3)]/4 = 26/4 = 6.5**

### 5.3 比較 [5.24] ⭐
- **SJF/SRTF are the best for minimizing average waiting time (and average turnaround time).**
- **Provably optimal：SJF among non-preemptive, SRTF among preemptive. SRTF is always at least as good as SJF.**
- **SJF/SRTF = FCFS if all processes have the same CPU burst.**
- **Can lead to starvation of long processes if shorter processes keep arriving；fairness cannot be enforced.**
- F20 MC14：best (min) average waiting time → **SJF**（**SRTF** 亦接受）。

### 5.4 Exponential Averaging（預測下一個 CPU burst）⭐⭐ [5.19–5.22]
> 🧮 **τ(n+1) = α · t(n) + (1 − α) · τ(n)**，0 ≤ α ≤ 1
- **tₙ = actual length of the n-th CPU burst；τₙ₊₁ = predicted value for the next burst**；通常 **α = ½**。
- **α = 0 → τₙ₊₁ = τₙ（recent history does not count）；α = 1 → τₙ₊₁ = tₙ（only the last burst counts）。**
- 展開：**τₙ₊₁ = α tₙ + (1−α) α tₙ₋₁ + … + (1−α)ʲ α tₙ₋ⱼ + … + (1−α)ⁿ⁺¹ τ₀** → **all past values count but recent ones weigh more；past effect diminishes exponentially**（α=0.5，10 rounds 後 (1/2)¹⁰ = 1/1024 可忽略）。
- 預測取決於 **(1) all previous actual bursts with different weights, (2) the initial estimate τ₀**。
- Slide 5.20 例（α = ½, τ₀ = 10）：

| i | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| CPU burst tᵢ | 6 | 4 | 6 | 4 | 13 | 13 | 13 | … |
| guess τᵢ | 10 | 8 | 6 | 6 | 5 | 9 | 11 | 12 |
- **HW2 MC9**：τ = 10, t = 6, α = 0.25 → 0.25×6 + 0.75×10 = 1.5 + 7.5 = **9 ms**。

---

## 6. Priority Scheduling ⭐⭐ [5.25–5.27]
- **Each process has a priority number；CPU allocated to the highest priority（本科：smallest integer = highest priority，除非題目另講）。**
- **Preemptive**（higher-priority arrival preempts）或 **non-preemptive**。
- **Equal priority → FCFS order**（或者 RR）。
- **SJF is a special case of priority scheduling where priority = inverse of predicted next CPU burst.**
- ⭐ **Problem：Starvation (indefinite blocking) — low-priority processes may never execute.**
- ⭐ **Solution：Aging — gradually increase the priority of a process as it waits**（需要每個 process 喺 ready queue 有 timer）。
- Sp21 MC：main problem of priority scheduling → **some processes may never execute (starvation)**；HW2 MC7：aging → **address starvation by gradually increasing the priority of a waiting process**。
- 例 [5.26]（all t=0；P1 10/3, P2 1/1, P3 2/4, P4 1/5, P5 5/2）→ `0 P2 1 P5 6 P1 16 P3 18 P4 19`，**avg WT = (6+0+16+18+1)/5 = 8.2**
- **Priority + RR** [5.27]：**run the highest priority；same priority → round-robin**。例 q = 2（burst/priority：P1 4/3, P2 5/2, P3 8/2, P4 7/1, P5 3/3，全部 t=0）→ `0 P4 7 P2 9 P3 11 P2 13 P3 15 P2 16 P3 20 P1 22 P5 24 P1 26 P5 27`
  - P4（priority 1）先跑完；P2、P3（priority 2）RR；P2 喺 16 完咗之後 P3 獨自跑到 20；最後 P1、P5（priority 3）RR。

![Priority scheduling with round-robin, q = 2 [5.27]](img/ch5_p27.png)


---

## 7. Multilevel Queue（多級佇列）⭐ [5.28–5.29]
- **Priority scheduling combined with RR**；**priority assigned statically；a process remains in the same queue for its whole runtime.**
- **Partition processes into queues based on process type**（例：real-time → system → interactive → batch）。
- **Each queue can have its own scheduling algorithm.**
- **Scheduling among queues**：(1) **fixed-priority preemptive scheduling**（高 queue 空先輪到低 queue → 可能 starvation）或 (2) **time-slice**（each queue gets a certain % of CPU time，e.g. 60%, 20%, 10%, 10%）。
- Sp21 MC：Multilevel queue（固定）有 starvation（free from starvation 嘅只有 **FCFS 同 RR**）。

---

## 8. MLFQ — Multilevel Feedback Queue ⭐⭐⭐（每年必考 Gantt）[5.30–5.35]
- **A process can move between queues；aging can be implemented this way → flexibility.**
- **MLFQ 由以下 parameters 定義**：
  1. **number of queues**
  2. **scheduling algorithm for each queue**
  3. **method to upgrade a process**（to higher queue）
  4. **method to demote a process**（to lower queue）
  5. **method to determine which queue a process enters when it needs service**

### 8.1 Slide example 規則（考試照用）[5.31] ⭐
- Q0 – RR（slide 5.31: q = 8；例子 5.32–5.34 用 **q = 4**）；Q1 – RR（q = 16 / **8**）；Q2 – **FCFS**
- **A new job always enters Q0 (RR, FCFS order)；it also preempts jobs from Q1 or Q2 currently running.**
- **Gets q₀ in Q0；if not finished → moved to Q1.** **In Q1 gets q₁ additional；if still not complete → preempted and moved to Q2.**
- ⭐ **If a job from Q1 or Q2 is preempted by a new job from Q0, it joins the HEAD of Q1 or Q2, with the remaining quantum (Q1) or remaining CPU burst (Q2).**（**唔會**攞一個全新 quantum；**唔會**因為被 preempt 而 demote）
- **Q1 job 只會喺 Q0 空先跑；Q2 job 只會喺 Q0 和 Q1 都空先跑。**
- **Q1 job 永遠唔會 preempt Q2 job**（因為冇 process 直接 arrive 去 Q1）— summary 重點。
- **A job in Q0 is never preempted**（Q0 內部只有 RR）。
- **Burst ≤ q₀ + q₁（e.g. 4 + 8 = 12）嘅 job 永遠唔會落 Q2。**
- **This approximates SRTF：CPU-bound jobs drop like a rock；short-running I/O-bound jobs stay near the top.**

### 8.2 Lecture example [5.32–5.34]（Q0 q=4, Q1 q=8, Q2 FCFS）
| Process | Arrival | Burst |
|---|---|---|
| P1 | 0 | 10 |
| P2 | 2 | 15 |
| P3 | 5 | 2 |
| P4 | 12 | 14 |
| P5 | 18 | 6 |
```
0 P1 4 P2 8 P3 10 P1 12 P4 16 P1 18 P5 22 P1 24 P2 32 P4 40 P5 42 P2 45 P4 47
 Q0   Q0   Q0   Q1   Q0   Q1   Q0   Q1   Q1   Q1   Q1   Q2   Q2
```
- t=4 P1 用完 Q0 quantum → Q1；t=8 P2 → Q1；t=10 P3 完；P1 喺 Q1 跑；t=12 P4 到 → preempt P1（P1 返 Q1 head，剩 6 quantum）；t=16 P4 → Q1 tail；P1 繼續（剩 quantum 6）；t=18 P5 到 → preempt P1；t=22 P5 → Q1；P1 跑到 24 完成（Q1 總共用 2+2+2 = 6 ≤ 8）；P2 24–32 用完 Q1 quantum → Q2；P4 32–40 → Q2；P5 40–42 完成；P2 42–45 完；P4 45–47 完。
- **WT：P1 = 14, P2 = 28, P3 = 3, P4 = 21, P5 = 18 → avg = 84/5 = 16.8** ✅

### 8.3 MLFQ advantages ⭐⭐（F19 Q3.3、F20 Q2.5 必背）[5.35]
- Used in **BSD Unix, Solaris, Windows NT and later**。
1. **It does not need prior knowledge of the next CPU burst time**（SJF/SRTF 需要）
2. **It handles interactive jobs well — better response time than RR**（short jobs 喺 top queue 完成）
3. **It produces similar performance to SJF/SRTF**
4. **It is "fair" — makes progress on CPU-bound jobs**
- **Starvation** 可以用 **reshuffling jobs periodically**（e.g. 一段時間後將所有 jobs 搬返 top queue）解決。
> 📝 **F20 Q2.5 Model answer**：*(1) MLFQ resembles the performance of SJF/SRTF without requiring prior knowledge of the next CPU burst time; (2) like RR, it gives good response time to interactive (short, I/O-bound) jobs since they finish in the top queues; (3) it is fair — all processes, long or short, make progress (and starvation can be avoided by periodically moving jobs up / aging).*
> 📝 **F19 Q3.3**：*MLFQ approximates SJF because short (interactive, I/O-bound) jobs finish within the top high-priority queue(s), while long CPU-bound jobs are demoted to lower queues — so short jobs get served first like SJF. Its major advantage over SJF is that it does not require knowing the CPU burst times in advance.*
> ⚠️ S26 MC20 ✅「**Each queue can use a different scheduling algorithm**」；✗ processes never move；✗ requires burst times known；✗ non-preemptive。Sp21 MC ✅「**handles interactive jobs well by delivering similar performance as SJF**」；✗ needs prior knowledge；✗ classification permanent；✗ won't suffer starvation。

### 8.4 MLFQ 做題 checklist ✍️
1. 每個時間點寫低：**Q0、Q1、Q2 內容（同次序）**、running process、佢喺邊個 queue、**剩餘 quantum**、**剩餘 burst**。
2. 事件：**arrival**（入 Q0 tail；如果 running 係 Q1/Q2 → preempt，被 preempt 嘅返 **head** of own queue，保留剩餘 quantum）；**quantum 用完**（未完成 → 降一級，入 tail）；**完成**。
3. Gantt 上標 **process@Queue**（HW2 要求 label queue）。
4. **同一 process 由 Q0 用完 quantum 立即喺 Q1 繼續跑**（因為 Q0 空）→ Gantt 可合併，但計 response time 要用 Q0 quantum 完結時間（S26 P5：49 − 45 = 4）。
5. **題目規則永遠優先**（S26 第 8 條、F20 aging timer、HW2 「retains unused quantum」）。

---

## 9. Thread Scheduling ⭐⭐ [5.36–5.37]
- **On modern OSes, kernel-level threads are scheduled (by the OS); user-level threads are managed by the thread library.**
- **LWP (lightweight process)** — intermediate data structure；**appears as a virtual processor on which user threads are scheduled to run；each LWP attached to a kernel thread**。
- ⭐ **Process-Contention Scope (PCS)** — **under many-to-one and many-to-many models, the thread library schedules user-level threads onto an LWP**；**competition among threads belonging to the same process**；typically **by priority set by programmers**（thread library 通常唔會調整 priority）；PCS typically **preempts the running thread in favour of a higher-priority user thread**。
- ⭐ **System-Contention Scope (SCS)** — **the kernel schedules kernel threads onto an available CPU**；**competition among all threads in the system** → 就係 CPU scheduling。
- **One-to-one systems (Windows, Linux, Solaris) schedule threads using only SCS.**
> 📝 HW2 MC8：thread library 揀 user thread run on LWP → **PCS, because the competing threads belong to the same process**。
> 📝 **F19 Q3.1**：*The OS schedules kernel-level threads. Mapping user threads onto kernel threads/LWPs (PCS) is done by the thread library, based on priorities set by the programmer, among the user threads of the same process; CPU scheduling (SCS) decides which kernel thread runs on a CPU among all kernel threads in the system.*

---

## 10. Multiple-Processor Scheduling ⭐⭐ [5.38–5.46]

### 10.1 AMP vs SMP [5.38–5.39]
- Multiprocessor 而家包括 **multicore CPUs, multithreaded cores, NUMA systems, heterogeneous multiprocessing**。
- **Asymmetric multiprocessing (AMP)** — **only one processor (the master server) accesses kernel data structures**（唔使 data sharing）；**all scheduling decisions, I/O processing, system activities handled by the master**；other processors execute only user code；⭐ **the master server can become a potential bottleneck**。
- **Symmetric multiprocessing (SMP)** — **each processor is self-scheduling**，with **one common ready queue** or **a private ready queue per processor**；每個 processor 嘅 scheduler examine ready queue 揀 thread。
  - Common queue：**must ensure two processors don't choose the same thread（race condition）** 同 processes 唔會 lost。
  - **All modern OSes support SMP**（Windows, Linux, macOS, Android, iOS）。
> 📝 **F20 Q2.4 Model answer（common vs per-processor ready queue）**：*A single common ready queue achieves **load balancing** easily — no processor is idle while the queue is non-empty — but it is hard to keep **processor affinity** (a thread may run on a different CPU each time, losing its cache contents) and the shared queue needs locking (possible race condition/contention). Per-processor private ready queues naturally provide processor affinity (and no contention on a shared queue), but need extra mechanisms such as **push/pull migration** to balance the load.*

### 10.2 Multicore & Multithreaded cores (CMT) ⭐ [5.40–5.44]
- **Multiple cores on the same chip — faster and consume less power, but complicate scheduling.**
- ⭐ **Memory stall：when a processor accesses memory, it spends a significant amount of time waiting for data to become available（modern processors much faster than memory, esp. on cache miss）。**（處理器可能 50% 時間喺等 memory）
- **Chip multithreading (CMT)**（**Intel = hyperthreading**）：**multiple hardware threads per core；each hardware thread has its own architectural state (PC, register set) and appears as a logical CPU**。
- **If one thread stalls waiting for memory, the core switches to another hardware thread.**
- **Dual-threaded dual-core → 4 logical processors；quad-core × 2 threads → 8 logical processors；UltraSPARC T3：16 cores × 8 threads = 128 logical processors。**
- **Two levels of scheduling**：
  1. **OS decides which software (kernel) thread runs on each logical CPU（= CPU scheduling）**
  2. **Each core decides which hardware thread runs on the physical core（e.g. RR on UltraSPARC T3）**
- 三層 mapping [5.44]：user thread → LWP/kernel thread（**PCS**, thread library）；kernel (software) thread → logical CPU / hardware thread（**CPU scheduling**, OS）；hardware thread → core（**core 自己，typically RR**）。
> 📝 **F19 Q2.5**：multicore 優點 = **faster + less power**；CMT 原因 = **memory stall** — 一個 hardware thread 等 memory 時 core 可以跑另一個 thread（S26 MC22 ✅「another thread may run when one thread stalls waiting for memory」）。

### 10.3 Processor Affinity ⭐⭐ [5.45]
- **When a thread has run on a processor, that processor's cache holds its memory accesses → the thread has affinity for that processor.**
- **High cost of invalidating and repopulating caches → most SMP systems try to avoid migrating processes between processors.**
- ⭐ **Per-processor ready queues provide processor affinity for free!**
- **Soft affinity — OS attempts to keep a process on the same processor but doesn't guarantee it（可以 migrate during load balancing）。**
- **Hard affinity — a process specifies a subset of processors it may run on.**（Linux：soft affinity + `sched_setaffinity()` for hard affinity）
- **NUMA**：CPU 存取近佢嘅 memory 較快 → affinity to both processor and memory。
> 📝 **HW2 Q2.4**：hard affinity {CPU0, CPU1}，CPU2 idle → **No**，hard affinity must be respected；load balancing 只可以將 T 由 CPU0 搬去 CPU1。

### 10.4 Load Balancing ⭐ [5.46]
- **Keep workload evenly distributed**（只喺 per-processor private queues 時需要）。
- **Push migration — a specific task periodically checks loads and pushes tasks from overloaded to idle/less-busy CPUs.**
- **Pull migration — an idle processor pulls a waiting task from a busy processor.**
- **Not mutually exclusive — often both implemented (Linux CFS).**
- ⭐ **Load balancing often counteracts the benefits of processor affinity**（natural tension）。
- S26 MC22 ✗「**The motivation of placing multiple cores on the same chip is to simplify the scheduler**」（其實 complicate scheduling）；✅ AMP master bottleneck；✅ memory stall → run another thread；✅ affinity keeps process on same CPU for cache。

---

## 11. Real-Time CPU Scheduling ⭐⭐⭐ [5.47–5.52]

### 11.1 Hard vs Soft ⭐
- **Real-time scheduling demands performance guarantee — predictability.**
- **Hard real-time — a task must be serviced by its deadline; service after the deadline is the same as no service.**
- **Soft real-time — no guarantee when a critical real-time process will be scheduled; only guarantees it will be given preference over noncritical processes.**
- **Real-time OS scheduler must support a priority-based algorithm with preemption**（但 preemptive priority-based 只保證 **soft** real-time）。
- Sp21 MC ✅「**Soft real-time systems guarantee only that the process will be prioritized over non-critical processes**」；✗ doesn't demand guarantee；✗ hard RT can service after deadline；✗ priority without preemption。

### 11.2 Periodic tasks [5.48]
- 參數：**processing time t, deadline d, period p，0 ≤ t ≤ d ≤ p**；**rate = 1/p**。
- **Admission control**：process announces deadline；scheduler **admits only if it can guarantee completion by the deadline**。
- **CPU utilization of task i = tᵢ / pᵢ；total U = Σ tᵢ/pᵢ**（U > 1 → 一定有 miss）。

### 11.3 Rate-Monotonic (RM) ⭐⭐ [5.49–5.50]
- **Static priority = inverse of period：shorter period → higher priority**（rationale：**tasks requiring CPU more often get higher priority**）。**Preemptive.**
- **RM is optimal among static-priority algorithms：if a set can't be scheduled by RM, no other static-priority algorithm can.**
- **Only handles periodic processes with constant processing time.**
- 例 [5.49]：P1 (p=50, t=20), P2 (p=100, t=35)：U = 0.40 + 0.35 = 75% → OK：`0 P1 20 P2 50 P1 70 P2 75 idle 100`
- 例 [5.50]：P1 (50, 25), P2 (80, 35)：U = 0.50 + 0.44 = **94%** → `0 P1 25 P2 50 P1 75 P2 85` → **P2 misses its deadline (80) by finishing at 85**。

![RM: P2 misses its deadline at 80 [5.50]](img/ch5_p50.png)

- 課本 bound（slides 冇，但好用）：**RM guaranteed if U ≤ N(2^{1/N} − 1)**：N=1 → 1；**N=2 → 0.828**；N=3 → 0.780；N=4 → 0.757；N→∞ → ln 2 ≈ 0.693。超過 bound **唔一定** miss（要畫 Gantt 確認）。

### 11.4 EDF — Earliest Deadline First ⭐⭐ [5.51–5.52]
- **Dynamic priorities according to deadline：earlier (absolute) deadline → higher priority.** Preemptive。
- 例 [5.51]（P1 50/25, P2 80/35）：`0 P1 25 P2 60 P1 85 P2 100 P1 125 P2 145 idle 150` → **no deadline missed**（t=50 時 P2 deadline 80 < P1 新 deadline 100 → P2 繼續）。

![EDF: same tasks, no deadline missed [5.51]](img/ch5_p51.png)

- **EDF does not require processes to be periodic, nor a constant CPU time per burst；only requirement：announce its deadline when it becomes runnable.**
- ⭐ **EDF is theoretically optimal — can meet all deadlines with CPU utilization up to 100%**（但實際上 context switching + interrupt handling 令佢做唔到 100%）。
- S26 MC21：assigns priorities according to deadlines → **EDF**。
> 📝 **Sp21 Q2.3(b)**：*EDF is better — unlike RM with static priorities, EDF uses dynamic priorities based on deadlines, which can increase the fraction of met deadlines (schedulable up to 100% utilization).*
> 📝 **HW2 Q2.5**（A: p=50,t=25；B: p=80,t=35；t=50 時 A 新 instance deadline 100，B 剩 10 deadline 80）→ **No**：**RM 揀 A**（shorter period，static）→ B 75–85 **miss 80**；**EDF 揀 B**（deadline 80 < 100）→ B 50–60 ✓，A 60–85 ✓。

### 11.5 RM / EDF 做題方法 ✍️
1. 列出每個 task 嘅 **release times**（0, p, 2p, …）同 **absolute deadlines**（release + d；冇講 d 就 d = p）。
2. 每個 time unit（或者每個事件：release / completion）揀：
   - **RM**：ready jobs 入面 **period 最短**（固定）嗰個。
   - **EDF**：ready jobs 入面 **absolute deadline 最早**嗰個。
3. **Ties**：題目有講就跟（S26：**smaller process ID**）；冇講：**keep the running job（唔 preempt）**（F19、Sp21 官方答案都係咁），再唔得就 smaller ID。寫低 assumption。
4. **Soft real-time：miss 咗 deadline 嘅 job 會繼續跑完**（Sp21 hint；S26 官方亦係咁），但 count 為 missed。
5. 數 **missed deadlines**：每個 deadline ≤ 時限範圍嘅 job，完成時間 > deadline（或者未完成）→ miss。
6. 先計 U = Σt/p 做 sanity check。

**S26 Q4.2**（P1 t=1 d=3 p=4；P2 2/4/5；P3 2/6/7；P4 1/5/8；0–16，ties → smaller ID）：
- **RM**（priority P1 > P2 > P3 > P4）：`0 P1 1 P2 3 P3 4 P1 5 P2 7 P3 8 P1 9 P3 10 P2 12 P1 13 P3 14 P3 15 P2 16`
  - P3 job (d=6) finishes 8 ✗；P4 never runs → misses d=5 ✗ and d=13 ✗；P3 job2 (d=13) finishes 14 ✗ → **RM misses 4 deadlines**（U = 0.25+0.4+0.286+0.125 = 1.06 > 1）
- **EDF**：`0 P1 1 P2 3 P4 4 P3 6 P1 7 P2 9 P1 10 P3 12 P4 13 P2 15 P1 16`
  - P2 job3 (d=14) finishes 15 ✗；P1 job4 (d=15) finishes 16 ✗ → **EDF misses 2 deadlines**

**Sp21 Q2.3**（P1 1/3/3, P2 2/4/4，0–14）：
- **EDF**：`0 P1 1 P2 3 P1 4 P2 6 P1 7 idle 8 P2 10 P1 11 idle 12 P1 13 P2 14`（t=9 tie deadline 12 → keep P2）
- **RM**：`0 P1 1 P2 3 P1 4 P2 6 P1 7 idle 8 P2 9 P1 10 P2 11 idle 12 P1 13 P2 14`
- 兩者都冇 miss（U = 0.833）。

**F19 Q3.4**（EDF；P1 p=d=10 t=4；P2 16/2；P3 20/8；到 38）：
- `0 P1 4 P2 6 P3 14 P1 18 P2 20 P1 24 P3 32 P1 36 P2 38`（t=10、t=30 deadline tie → keep P3 running）

---

## 12. Algorithm Evaluation [5.53–5.60]
- 先定 **criteria**（e.g. maximize CPU utilization **subject to max response time 300 ms**；maximize throughput such that TAT ∝ execution time）。
- **Deterministic modeling** — **takes a particular predetermined workload and defines the performance of each algorithm for that workload**；**simple and fast, gives exact numbers, but requires exact input and answers apply only to those cases**。
  - 例 [5.54–5.55]：5 processes at t=0：P1 10, P2 29, P3 3, P4 7, P5 12 → **FCFS avg WT = 28；non-preemptive SJF = 13；RR (q=10) = 23**。
- **Queueing models / analysis** — CPU = server with ready queue；用 **distributions**（exponential, described by mean）；可計 utilization、average queue length、wait time；**classes of algorithms and distributions handled are limited；assumptions often unrealistic**。
  - ⭐ **Little's Formula：n = λ × W**（**n = average queue length, λ = average arrival rate, W = average waiting time in queue**）；**valid for any scheduling algorithm and arrival distribution**（steady state，arrival rate < service rate）。
  - 例：λ = 7/s，n = 14 → **W = 2 s**；**HW2 MC10**：λ = 3/s，n = 12 → **W = 4 s**。
- **Simulations** — programming a model of the system；**more accurate**；data from **random number generators (distributions)** 或 **trace files**（real system 記錄）。
- **Implementation** — 真系統測試，最準但 **high cost & high risk**；環境會變；可調 parameters；APIs 改 priority（Java, POSIX, Windows）。

---

## 13. Gantt Chart 萬用流程（考試步驟）✍️⭐⭐⭐
1. **抄表**：Process / Arrival / Burst（/ Priority）。
2. **由 t = 0 開始逐個事件推進**（events：arrival、completion、quantum expiry、check point）。每個事件寫低 **ready queue**（同 MLFQ 各層）。
3. **揀 process 規則**：
   | Algorithm | 揀邊個 | Preempt? |
   |---|---|---|
   | FCFS | earliest arrival | No |
   | SJF | shortest burst among **arrived** | No |
   | SRTF | shortest **remaining** | Yes, on arrival |
   | RR | head of queue | Yes, quantum expiry |
   | Priority (NP / P) | highest priority | P: on higher arrival |
   | Priority + RR | highest priority；same → RR | Yes |
   | MLFQ | highest non-empty queue | Yes（Q0 arrival preempts Q1/Q2） |
   | RM | shortest period | Yes |
   | EDF | earliest absolute deadline | Yes |
4. **CPU idle**：冇 process ready 就畫 **idle**（Sp21 FCFS `0 P1 2 idle 4 P2…`）。
5. **畫 Gantt**：每段標 **start time / process / end time**；所有 boundary 時間都要寫（partial credit 靠呢個）。
6. **計 table**：Completion → **TAT = C − A** → **WT = TAT − Burst** → **RT = end of first run − A**。
7. **Average**：寫出 **(a+b+…)/n = x**（S26：140/6 = 23.33）。
8. **Sanity check**：總 burst 加 idle = 最後完成時間；每個 WT ≥ 0。

### 13.1 Tie-breaking（寫 assumption！）
- 同時到達、同 burst/priority：**FCFS → lower process ID**。
- **SRTF**：新到達 burst = running remaining → 一般 **keep running**（唔 preempt）；F19 官方 preempt 咗，但兩種 avg WT 一樣 2.5。
- **RR**：新到達 + quantum expiry 同一時刻 → **新到達先入 queue**。
- **EDF**：deadline 相同 → **keep running**，否則 smaller ID（或者跟題目）。
- **Dynamic priority（S26 Q4.3）**：題目講「same priority → larger ID first」— **跟題目**！

---

## 14. Past-paper 計算題全集（全部用程式驗證 ✅）

### 14.1 S26 Q4.1 MLFQ（Q0 RR4, Q1 RR8, Q2 FCFS；preempted → head of own queue）
| P | Arr | Burst |
|---|---|---|
| P1 | 0 | 9 |
| P2 | 2 | 25 |
| P3 | 6 | 7 |
| P4 | 14 | 18 |
| P5 | 45 | 15 |
| P6 | 58 | 6 |
```
0 P1 4 P2 8 P3 12 P1 14 P4 18 P1 21 P2 29 P3 32 P4 40 P2 45 P5 57 P2 58 P6 64 P2 71 P4 77 P5 80
(Q0)(Q0)(Q0)(Q1)(Q0)(Q1)(Q1)(Q1)(Q1)(Q2)(Q0→Q1 at 49)(Q2)(Q0→Q1 at 62)(Q2)(Q2)(Q2)
```
- WT：P1 12, P2 44, P3 19, P4 45, P5 20, P6 0 → **avg = 140/6 = 23.33**
- RT（end of first run − arrival）：P1 4, P2 6, P3 6, P4 4, P5 4 (49−45), P6 4 (62−58) → **avg = 28/6 = 4.67**

### 14.2 S26 Q4.3 Dynamic priority（larger = higher；waiting rate α，running rate β；tie → larger ID）
- P1 (0, 7), P2 (3, 5), P3 (6, 6), P4 (9, 4)
- (a) α = 0, β = 3（running process priority 上升，waiting 不變 → 一旦 run 就霸住）：**`0 P1 7 P3 13 P4 17 P2 22`**
  - t=7：P2, P3 都係 0 → tie → larger ID → **P3**；t=13：P2 (0), P4 (0) → **P4**。
- (b) α = 1, β = 0，只考慮 P1、P2，每 3 個 unit check：**`0 P1 3 P2 6 P1 9 P2 11 P1 12`**
  - t=3：P1 = 0 (ran 3), P2 = 0 → tie → P2；t=6：P1 = 3, P2 = 0 → P1；t=9：P1 = 3, P2 = 3 → tie → P2；t=11 P2 完 → P1。
- (c) α = 1, β = −2，初始 30，每 3 unit check：**`0 P1 3 P2 6 P3 9 P4 12 P1 15 P2 17 P3 20 P4 21 P1 22`**
  - t=3：P1 = 30−6 = 24, P2 = 30 → P2；t=6：P1 27, P2 24, P3 30 → P3；t=9：P1 30, P2 27, P3 24, P4 30 → tie → P4；t=12：P1 33 → P1；t=15：P1 27, P2 33, P3 30, P4 27 → P2（17 完）；t=17：P1 29, P3 32, P4 29 → P3（20 完）；t=20：P1 32, P4 32 → tie → P4（21 完）；t=21：P1。

### 14.3 S26 Q2.3 自訂 policy（fᵢ = 1/(a·cᵢ + b)，揀 fᵢ 最大）
- (a) **Yes** — I/O-bound processes have small average CPU bursts cᵢ → larger fᵢ → higher priority.
- (b) **Yes** — a CPU-bound process (large cᵢ, low fᵢ) can starve if higher-priority I/O-bound processes keep arriving.

### 14.4 F19 Q3.5 LUF (Least Used First)（揀用 CPU 最少嘅；tie → FCFS；preempt on arrival）
- P1 (0, 25), P2 (15, 25), P3 (25, 5), P4 (40, 5)
- **`0 P1 15 P2 25 P3 30 P2 40 P4 45 P1 55 P2 60`**

| P | TAT | RT | WT |
|---|---|---|---|
| P1 | 55 | 15 | 30 |
| P2 | 45 | 10 | 20 |
| P3 | 5 | 5 | 0 |
| P4 | 5 | 5 | 0 |

- LUF vs SRTF：相似 — short jobs 較易有高 priority；分別 — **LUF 令跑咗好耐嘅 process 易 starve**；SRTF 令 **long burst 嘅 process 一開始就 starve**。

### 14.5 F19 Q3.6（P1 0/8, P2 7/13, P3 9/1, P4 11/5, P5 20/7, P6 27/1）
| Alg | Gantt | WT (P1..P6) | Avg |
|---|---|---|---|
| FCFS | 0 P1 8 P2 21 P3 22 P4 27 P5 34 P6 35 | 0,1,12,11,7,7 | **6.33** |
| SJF | 0 P1 8 P2 21 P3 22 P4 27 P6 28 P5 35 | 0,1,12,11,8,0 | **5.33** |
| RR q=4 | 0 P1 8 P2 12 P3 13 P4 17 P2 21 P4 22 P5 26 P2 30 P5 33 P6 34 P2 35 | 0,15,3,6,6,6 | **6.0**（corrected） |
| SRTF | 0 P1 8 P2 9 P3 10 P2 11 P4 16 P2 20 P5 27 P6 28 P2 35（官方，tie 時 preempt） | 0,15,0,0,0,0 | **2.5** |
- SRTF 另一答案（tie 時 keep P2）：`… 16 P2 27 P6 28 P5 35` → WT 0,7,0,0,8,0 → avg 都係 **2.5**。
- 注意 SJF：t=8 只有 P2 到咗 → P2 跑到 21（non-preemptive）。

### 14.6 F20 Q4.1（P1 0/9, P2 3/3, P3 8/2, P4 10/6, P5 16/8, P6 20/5）
| Alg | Gantt | WT | Avg |
|---|---|---|---|
| FCFS | 0 P1 9 P2 12 P3 14 P4 20 P5 28 P6 33 | 0,6,4,4,4,8 | **4.33** |
| SJF | 0 P1 9 P3 11 P2 14 P4 20 P6 25 P5 33 | 0,8,1,4,9,0 | **3.67** |
| SRTF | 0 P1 3 P2 6 P1 8 P3 10 P1 14 P4 20 P6 25 P5 33 | 5,0,0,4,9,0 | **3.0** |

### 14.7 F20 Q4.2 Two-level feedback queue with aging（Q0 RR4；Q1 FCFS；Q1 timer 8 ms → 返 Q0；被 preempt 返 Q1 head 並 reset timer）
- P1 0/9, P2 3/3, P3 8/2, P4 10/9, P5 13/4, P6 18/5
- **`0 P1 4 P2 7 P1 8 P3 10 P4 14 P5 18 P1 22 P6 26 P4 30 P6 31 P4 32`**
- 關鍵：t=8 P1（Q1）被 P3 preempt → Q1 head，timer reset 8；t=16 P1 timer 到 8 → 升返 Q0；t=22 P4（14 入 Q1）timer 到 8 → 升 Q0。
- WT = 13, 1, 0, 13, 1, 8 → **avg = 6**

### 14.8 F20 Q4.3 Priority + RR（smaller = higher；preemptive；same priority RR q=4）
- P1 0/9/2, P2 3/3/1, P3 8/5/4, P4 10/2/4, P5 16/8/5, P6 20/5/3
- **`0 P1 3 P2 6 P1 12 P3 16 P4 18 P3 19 P5 20 P6 25 P5 32`**
- WT = 3, 0, 6, 6, 8, 0 → **avg = 23/6 = 3.83**

### 14.9 Sp21 Q2.1（P1 0/2, P2 4/12, P3 6/6, P4 9/4, P5 13/5）
| Alg | Gantt | WT | Avg |
|---|---|---|---|
| FCFS | 0 P1 2 idle 4 P2 16 P3 22 P4 26 P5 31 | 0,0,10,13,13 | **7.2** |
| SJF | 0 P1 2 idle 4 P2 16 P4 20 P5 25 P3 31 | 0,0,19,7,7 | **6.6** |
| RR q=8 | 0 P1 2 idle 4 P2 12 P3 18 P4 22 P2 26 P5 31 | 0,10,6,9,13 | **7.6** |
| SRTF | 0 P1 2 idle 4 P2 6 P3 12 P4 16 P5 21 P2 31 | 0,15,0,3,3 | **4.2** |

### 14.10 Sp21 Q2.2 MLFQ（Q0 q=2, Q1 q=4, Q2 FCFS）
- P1 0/10, P2 10/8, P3 8/30, P4 16/2, P5 22/8, P6 6/22
- **`0 P1 2 P1 6 P6 8 P3 10 P2 12 P6 16 P4 18 P3 22 P5 24 P2 28 P5 32 P1 36 P6 52 P3 76 P2 78 P5 80`**
  - (Q0)(Q1)(Q0)(Q0)(Q0)(Q1)(Q0)(Q1)(Q0)(Q1)(Q1)(Q2)(Q2)(Q2)(Q2)(Q2)
- WT：P1 26, P2 60, P3 38, P4 0, P5 50, P6 24 → **avg = 33**

### 14.11 HW2（P1 0/7, P2 1/3, P3 4/5, P4 10/2）
- **SRTF**：`0 P1 1 P2 4 P3 9 P1 10 P4 12 P1 17` → WT 10,0,0,0 → **avg WT 2.5；avg TAT 6.75**
- **RR q=3**：`0 P1 3 P2 6 P1 9 P3 12 P1 13 P4 15 P3 17` → WT 6,2,8,3 → **avg WT 4.75；avg TAT 9**
- **MLFQ（Q0 4, Q1 8, Q2 FCFS；P1 0/20, P2 1/5, P3 11/2）**：`0 P1(Q0) 4 P2(Q0) 8 P1(Q1) 11 P3(Q0) 13 P1(Q1) 18 P2(Q1) 19 P1(Q2) 27`
  - t=11 P1 被 P3 preempt → **Q1 head（喺 P2 前面），剩 5 ms quantum**（唔係新 8 ms）。

---

## 15. 常見陷阱 & MC 速查

| 敘述 | 真/假 |
|---|---|
| Scheduling on running→waiting / terminate = non-preemptive | ✅ |
| Timer interrupt (quantum expiry) = preemptive | ✅ |
| FCFS is preemptive | ❌（**FCFS must be non-preemptive** — Sp21 MC） |
| SJF gives minimum average waiting time | ✅ |
| SJF easy to implement | ❌（need next burst length） |
| SRTF ≥ SJF in performance | ✅ |
| RR with very large q → FCFS | ✅ |
| RR always better TAT than FCFS | ❌ |
| RR: no process waits more than (n−1)q | ✅ |
| Small q → high context-switch overhead | ✅ |
| Priority scheduling problem = starvation；solution = aging | ✅ |
| Multilevel queue: processes move between queues | ❌（MLFQ 先可以） |
| MLFQ requires known burst times | ❌ |
| MLFQ: each queue different algorithm | ✅ |
| Starvation-free: FCFS and RR | ✅（Sp21 MC 答案 A：1, 4） |
| OS schedules user threads (SCS) | ❌（PCS 由 thread library；SCS 係 kernel threads） |
| One-to-one systems only use SCS | ✅ |
| AMP: master can be a bottleneck | ✅ |
| Multicore simplifies scheduling | ❌ |
| Per-processor queues give affinity for free | ✅ |
| Load balancing may counteract affinity | ✅ |
| Hard RT: service after deadline acceptable | ❌ |
| RM: static priority by period | ✅ |
| EDF: dynamic priority by deadline | ✅ |
| EDF requires periodic tasks | ❌ |
| EDF optimal, up to 100% utilization (theory) | ✅ |
| Little's formula n = λW only for FCFS | ❌（any algorithm） |
| Response time (course) = first start − arrival | ❌（**end of first run − arrival**） |

---

## 16. 自我測驗
1. P1(0,5), P2(1,3), P3(2,1)：SRTF Gantt？（`0 P1 1 P2 2 P3 3 P2 5 P1 9`；WT = 4,1,0 → 5/3）
2. 10 個 jobs 各 100 s 同時到，RR q=1 vs FCFS 平均 TAT？（RR ≈ 995.5 s；FCFS = 550 s）
3. α = 0.5，τ₀ = 10，bursts 6, 4 → τ₂？（τ₁ = 8；τ₂ = 6）
4. 兩個 tasks：A (t=2, p=5)、B (t=4, p=10)：U = 0.8，RM 得唔得？（0.8 ≤ 0.828 → guaranteed）
5. PCS vs SCS？
6. Push vs pull migration？
