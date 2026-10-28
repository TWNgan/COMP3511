# Playbooks（解題流程 + 預先計好嘅表）

## P1. fork() Playbook

**Step 1 — 規則**
- fork() 返回：**child 0 / parent child-PID (>0) / fail −1（只有 parent，冇 child）**。
- Child 由 **fork() 下一個 operation** 開始，複製晒 variables（包括 loop 嘅 `i`）。
- 短路：`A && B` → A 係 0（child）唔做 B；`A || B` → A 非 0（parent）唔做 B。
- `return` / `exit` / `break` 會停止該 process 嘅 loop；`exec` 成功 = 之後 code 唔執行。

**Step 2 — Pattern 表（每個 iteration、所有 process 都繼續 loop）**

{{FORK_TABLE}}

**Step 3 — 其他已驗證答案**

| Code | 答案 |
|---|---|
| `if (fork() || fork()) fork();` | **5** processes |
| `if (fork() && fork()) fork();` | **4**（P0: T&&T → fork → 2；C1 false → 1；C2 false → 1） |
| `fork(); fork() && fork(); fork();` | **12** |
| `pid1=fork(); pid2=fork(); if(pid1>0) if(pid2==0) fork();` | **5** |
| `if (fork()==fork() \|\| fork()!=fork()) fork(); printf` | **23** lines |
| S26 MC10：loop 3：`if(fork()==0){fork(); printf X; return;}` 之後 printf Y | **7 processes, X = 6, Y = 1** |
| S26 Q3.1：`if(fork()) fork(); else break;` | **2ⁿ⁺¹ − 1** processes, **2ⁿ − 1** breaks（n=2：7, 3） |
| F20 Q3.2：`if(!fork()){loop n: if(fork()) fork();} fork(); printf a` | **2(3ⁿ + 1)** |
| Sp21 Q1.2：`if(fork()==0){loop 5: if(fork()==0) fork();} fork();` | **(3⁵ + 1)×2 = 488** |
| F19 Q2.6：loop n，parent/child 都 printf | **2ⁿ⁺¹ − 2** lines |
| Slide 3.44：loop 10 `fork(); fork();` | **4¹⁰ = 1,048,576** |
| Slide 3.45：loop 10 `if (fork()) fork();` | **3¹⁰ = 59,049** |

**Step 4 — Process tree**：每個 node 寫 PID 名（P0, P1…）同佢喺邊個 iteration 出世；child 繼承 parent 嘅 `i` 值繼續。

**Step 5 — Output ordering**：
1. 同一 process 內嘅 print 次序固定。
2. `wait()`：parent 之後嘅 print > 所有 child（及其子孫，如 child 等咗佢哋）嘅 print。
3. fork 之前印嘅（已 flush）最先。
4. 列所有符合約束嘅排列（topological orders）；可以用「插空位」數：k 個自由字元插入固定序列。

**Step 6 — exec 情況**：(I) fork ✓ exec ✓：child exec 前嘅 print + parent 嘅 print；(II) fork ✓ exec ✗：再加 exec 後嘅 print；(III) fork ✗：只有 `ret < 0` branch。

## P2. Pipe / dup / exec 填空 Playbook

| 要做 | Code |
|---|---|
| 建 pipe（**fork 之前**） | `int fd[2]; pipe(fd);` → **fd[0] read，fd[1] write** |
| Writer | `close(fd[0]); write(fd[1], &x, sizeof(x)); close(fd[1]);` |
| Reader | `close(fd[1]); read(fd[0], &x, sizeof(x)); close(fd[0]);` |
| stdin ← file | `int fin = open(name, O_RDONLY); close(0); dup(fin);`（或 `dup2(fin, 0)`） |
| stdout → file | `int fo = open(name, O_WRONLY|O_CREAT|O_TRUNC, 0644); dup2(fo, 1); close(fo);` |
| stdout → pipe | `dup2(fd[1], 1); close(fd[0]); close(fd[1]); execlp(...)` |
| stdin ← pipe | `dup2(fd[0], 0); close(fd[0]); close(fd[1]); execlp(...)` |
| 等指定 child | `waitpid(pid, &status, 0);` |
| exec 一個 program | `execlp("ls", "ls", "-l", (char *)NULL);` / `execvp(argv[0], argv);`（argv 尾要 NULL） |
| 數偶數（S26） | `if (number % 2 == 0) cnt++;` |

## P3. CPU Scheduling Playbook

**萬用步驟**：(1) 抄表；(2) 由 t=0 起逐個 event（arrival / completion / quantum expiry / check point）；(3) 每個 event 寫 ready queue 內容；(4) 照算法揀；(5) 畫 Gantt（每個 boundary）；(6) C → TAT → WT → RT；(7) 平均連 working；(8) 檢查：最後完成時間 = Σburst + idle。

| Algorithm | 揀邊個 | 幾時重新揀 | 注意 |
|---|---|---|---|
| **FCFS** | 最早到 | 完成時 | non-preemptive；convoy effect |
| **SJF** | **已到達**嘅最短 burst | 完成時 | 一旦開始跑到完 |
| **SRTF** | 最短 **remaining** | 完成 + **每個 arrival** | tie → keep running |
| **RR (q)** | queue head | 完成 / quantum 用完 | 新 arrival 先入 queue，再放被 preempt 嘅 |
| **Priority NP** | 最高 priority（細數字） | 完成時 | tie → FCFS |
| **Priority P** | 最高 priority | 完成 + 高 priority arrival | |
| **Priority + RR** | 最高 priority；同級 RR | 完成 / quantum / 高 priority arrival | 同級得一個就繼續跑 |
| **MLFQ** | 最高非空 queue 嘅 head | 完成 / quantum / 高層 arrival | preempted → **head + 剩餘 quantum** |
| **Dynamic priority** | 計 init + α·waited + β·ran | 每 check interval / 完成 | tie 跟題目 |
| **LUF**（F19） | 用 CPU 最少 | 完成 + arrival | descheduled → tail |
| **RM** | period 最短 | 每個 release / 完成 | static |
| **EDF** | absolute deadline 最早 | 每個 release / 完成 | dynamic；tie → keep running |

**MLFQ 追蹤表（考試用 rough paper 畫）**：

```
t   | event            | Q0        | Q1 (rem q)   | Q2      | run (queue, q left, burst left)
0   | P1 arrives       | P1        |              |         | P1@Q0 q=4 b=9
4   | P1 q used        | P2        | P1(8)        |         | P2@Q0 ...
```

**RM / EDF 追蹤**：列 release times：task i 喺 0, pᵢ, 2pᵢ… release；deadline = release + dᵢ。逐個 time unit 揀；記低每個 job 完成時間，比較 deadline。

## P4. Synchronization Playbook

**Race 可能值（F19 Q4.3 / F20 Q5 type）**
1. 將 T1 拆做 atomic steps：**read for condition → read b → read a → write c**（`c = b + a` 由左至右讀）。
2. T2 嘅 writes（次序固定）可以插入任何 gap。
3. 分 branch（condition read 前 / 後寫）→ 每個 read 見新值 / 舊值 → 計 c。
4. 列晒所有 **distinct** 值 + 每個值嘅 interleaving。

**Semaphore 次序**：每條 dependency「X 要喺 Y 前」→ semaphore s = 0：**X 尾 `signal(s)`、Y 頭 `wait(s)`**；多個前置 → 多個 `wait`。

**Semaphore 序列可行性**：逐字追蹤每個 semaphore 嘅值同每個 process 做到邊；任何 `wait` 時值必須 > 0；有 loop 嘅 process 可以重複。

**Spinlock 任何 atomic instruction**：`while (instr(...) 返回「攞唔到」) ;` + release 寫返 free 值：

| Instruction（return） | acquire | release |
|---|---|---|
| `test_and_set(&lock)`（old） | `while (test_and_set(&lock)) ;` | `lock = false;` |
| `compare_and_swap(&lock,0,1)`（old） | `while (compare_and_swap(&lock,0,1) != 0) ;` | `lock = 0;` |
| `swap(locked,1)`（old） | `while (swap(locked,1) == 1) ;` | `locked = 0;` |
| `compare_and_reset(&v,0,1)`（1 = 成功） | `while (compare_and_reset(&v,0,1) == 0) ;` | `v = 0;` |

**Bounded-waiting TAS 檢查點**：(1) **cyclic scan** `j=(i+1)%n … j!=i`；(2) **冇人等就 `lock = false`**；(3) 有人等就 **`waiting[j] = false`**（直接交 lock）；三個性質：ME（只有第一個 TAS 得 key=false / 只放一個 waiting）、progress（exit 一定放 lock 或者叫醒一個）、bounded waiting（≤ n−1 turns）。

## P5. 預先計好嘅表 Pre-computed Tables

**Amdahl speedup = 1/(S + (1−S)/N)**（S = serial fraction；parallel = 1 − S）

{{AMDAHL_TABLE}}

**Powers（fork 用）**

{{POW_TABLE}}

**RM utilization bound N(2^{1/N} − 1)**

{{RM_TABLE}}

**Exponential averaging（α = ½）權重**：tₙ ½、tₙ₋₁ ¼、tₙ₋₂ ⅛、tₙ₋₃ 1/16、… τ₀ (½)ⁿ⁺¹。α = 0.25：tₙ 0.25、tₙ₋₁ 0.1875、tₙ₋₂ 0.1406、… τ 權重 0.75ⁿ⁺¹。
