# Exam-Day Essentials（考場一頁通）

## E1. 必背公式卡 Formula Card

| 主題 | 公式 | 例 |
|---|---|---|
| **Average access time** [1.32] | **AMAT = h × T_hit + (1 − h) × T_miss**（若畀 penalty：T_miss = T_hit + penalty） | 0.9×2 + 0.1×50 = **6.8 ns** |
| **Amdahl's Law** [4.12] | **speedup ≤ 1 / (S + (1 − S)/N)**；N→∞：**1/S**；S = **serial** | S=0.25, N=2 → **1.6** |
| Amdahl 反解 | **S = (1/X − 1/N) / (1 − 1/N)** | X=3, N=4 → S = 1/9 |
| **Turnaround** [5.8] | **TAT = completion − arrival** | |
| **Waiting** [5.8] | **WT = TAT − burst**（= Gantt 上嘅 gaps 總和） | |
| **Response（本科）** [5.12] | **RT = end of FIRST run − arrival**（RR/MLFQ：第一個 quantum 完；non-preemptive：= TAT） | RR4：P1=4, P2=7, P3=10 |
| **Exponential averaging** [5.19] | **τ(n+1) = α·t(n) + (1 − α)·τ(n)** | α=.25, t=6, τ=10 → **9** |
| **Little's formula** [5.57] | **n = λ × W** | λ=3/s, n=12 → **W=4 s** |
| **RR bound** [5.11] | 冇 process 等多過 **(n − 1)·q** | |
| **RT utilization** [5.49] | **U = Σ tᵢ / pᵢ**；**U > 1 ⇒ 一定 miss** | 25/50 + 35/80 = 0.94 |
| **RM bound**（課本） | 保證可排：**U ≤ N(2^{1/N} − 1)**：N=1 1.000、2 0.828、3 0.780、4 0.757、5 0.743、∞ 0.693 | |
| **EDF** [5.52] | U ≤ 1（D = T 時）理論上可排 | |
| **fork 數目** | n 個無條件 fork → **2ⁿ**；`if(fork()) fork();` 每輪 ×3 | 見 Playbook P1 |
| **Bounded buffer (in/out)** [3.54] | 最多 **BUFFER_SIZE − 1** items | |
| **Semaphore（blocking）** [6.26] | value < 0 ⇒ **\|value\| = 等緊嘅 processes 數** | |
| **Storage units** [1.28] | KB = 1024 B；MB = 1024²；GB = 1024³；networks 用 **bits** | |

## E2. 本科 Conventions（考試照用，唔確定就寫 assumption）

1. **Response time = completion of the first run − arrival**（slide 5.12；S26 官方答案照用）。
2. **RR**：quantum 用完 → **tail**；同一時刻有新 arrival → **新 arrival 先入 queue**。
3. **MLFQ**：新 job → **Q0 tail**；用晒 quantum 仍未完 → **降一級 tail**；**被高 queue 新 arrival preempt → 返自己 queue 嘅 HEAD，保留剩餘 quantum（Q1）/ 剩餘 burst（Q2），唔會降級**；Q0 job 唔會被 preempt；Q1 job 唔會 preempt Q2 job。
4. **Priority**：**細數字 = 高 priority**（除非題目話 larger = higher，例如 S26 dynamic priority）。
5. **Ties**：題目有講就跟（S26：smaller ID；dynamic priority：larger ID）；冇講：FCFS（早到先）→ 細 ID；**SRTF / EDF 平手 → 唔 preempt running process**。
6. **Soft real-time**：miss 咗 deadline 嘅 job **繼續跑完**，但計一次 miss。
7. **fork 題**：除非另有說明，假設 **printf 即時 flush**、**fork 全部成功**。
8. **Gantt chart**：每段寫 **start / process / end**；idle 都要畫；MLFQ 標 queue（P1@Q0）。

## E3. 最易中伏 Top Traps（MC 前睇一次）

| ❌ 錯誤講法 | ✅ 正確 |
|---|---|
| Main memory is nonvolatile / registers slower than memory | volatile；registers 最快；**main memory byte addressable** |
| von Neumann：instructions 同 data 分開存 | **same memory**（stored-program） |
| Speedup with N CPUs = N | **< N**（contention / overhead） |
| NUMA：所有 memory 同樣 latency | **remote memory slower** |
| VM 一定比 native 快 | minor slowdown |
| printf() 係 system call | printf **calls write()** system call |
| API 比 system call 快 / 可以 bypass protection | 優點 = **portability + hide details（convenient）** |
| Microkernel performance 好過 monolithic | **worse**（message passing） |
| Layered：任何 layer 可 call 任何 layer | 嗰個係 **LKM**；layered 只 call 下層 |
| LKM 要 recompile kernel + reboot | 可以 **run time load/remove** |
| Policy = how | **Policy = what；mechanism = how** |
| Interrupts 全部同一 priority / 只由 I/O 產生 | 有 **priority levels**；**trap = software interrupt** |
| DMA 每個 byte interrupt 一次 | **block 完先 interrupt 一次** |
| Mode bit 1 = kernel | **1 = user，0 = kernel** |
| Context switch = user→kernel mode switch | context switch = **save/restore process state**；越複雜 OS 越慢 |
| fork() 令 parent 等 child | 要 **wait()** |
| child 改 global variable → parent 都變 | 各自 **copy** |
| exec() 成功會 return | **唔會 return** |
| Zombie 仲行緊 code / 冇 PID | terminated，**PID + PCB 仍在**，等 parent wait() |
| Ordinary pipe 任何 process 用到 | **parent–child only**、單向、用完消失 |
| Named pipe 用完自動消失 | **explicitly delete**；UNIX FIFO **half-duplex** |
| Threads 有自己 address space / files | **share** code、data、heap、files；**own** PC、registers、**stack** |
| Concurrency = 同時執行 | 同時 = **parallelism**；concurrency 單核都得 |
| Many-to-many 易 implement / user thread map 去多個 kernel threads | **difficult**；冇 one-to-many |
| 所有 signals deliver 畀所有 threads | sync → causing thread；部分 async → all |
| Asynchronous cancellation = 定期 check | 嗰個係 **deferred**（Pthreads default） |
| FCFS 可以 preemptive | **FCFS must be non-preemptive** |
| RR 一定比 FCFS 好 | 同長度 jobs 時 **TAT 更差** |
| q 越大 TAT 越好 | 唔一定；q 太大 → **FCFS** |
| MLFQ 要知 burst / 永不 starve | **唔使知**；可能 starve（要 aging/reshuffle） |
| Multilevel queue 可搬 queue | 只有 **MLFQ** 可以 |
| Multicore 簡化 scheduling | **complicates**（faster + less power） |
| Hard RT 遲咗都得 / RT scheduler 唔使 preemption | 遲 = 冇服務；要 **priority + preemption** |
| EDF 要 periodic | **唔需要**；只需 announce deadline |
| Little's formula 只適用 FCFS | **any algorithm** |
| "Synchronization" 係 CS 三條件之一 | **ME + progress + bounded waiting** |
| test_and_set 返回新值 / 會 release lock | 返回 **old value**；release = `lock = false` |
| Binary semaphore = mutex | 可當 mutex，但**更通用**（init 0 做 ordering） |

## E4. 答題模板 Answer Templates

**Short question（2–4 分）**：*[Definition sentence with keywords]. [Why / how — one sentence]. [Example or advantage/disadvantage].*

**Gantt + averages**：
```
Gantt:  0 P1 4 P2 8 P3 12 ...           (每個 boundary 都寫)
P | Arr | Burst | Comp | TAT=C-A | WT=TAT-B | RT=end1-A
avg WT  = (w1 + w2 + ... + wn) / n = x.xx
avg TAT = (t1 + ... + tn) / n = x.xx
Assumptions: ties -> ..., new arrival enters queue before preempted process.
```

**fork 題**：*Draw tree → count per level → formula → final number*；output 題：*constraints (wait / same process order) → list all interleavings*。

**Race values**：*Case 1 (branch …): interleaving … → c = …* 逐個列。

**Semaphore 填空**：用 init-0 semaphore：**先做者 `signal(s)`，後做者開頭 `wait(s)`**；冇需要嘅 blank 寫 **`/* Nothing */`**。
