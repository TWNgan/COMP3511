# Labs 1–6 & PA1 / PA2（實驗課 + 功課考點）

> 📌 **點解要睇**：Midterm email 講明「There may be questions related to **PA** or coding questions using some **APIs we discussed in our lab classes**」；Lab 3 slide 亦講「**PA-related questions in exam** — it is crucial to have a thorough understanding of the project assignments」。S26 Q3.3 直接叫你「refer to the **Lab 3 notes** for open, pipe, read, write」。
> ✅ 本頁所有 fork 數目、semaphore 輸出、race 值、Gantt chart 都已用真 C 程式 / 窮舉 / 模擬器驗證，同 lab 官方答案一致。

---

## L1. Lab 1 — Linux 環境 & Shell 指令

- **Terminal** = 畫面/視窗；**Shell** = 解讀指令嘅程式（bash, tcsh…）→ **shell fetches, interprets, executes** commands（Ch2 [2.8]）。
- 常用指令：

| 指令 | 用途 | 指令 | 用途 |
|---|---|---|---|
| `pwd` | 顯示目前目錄 | `cd dir` / `cd ..` / `cd ~` | 轉目錄 |
| `ls -l -h` / `ls -a` | 列出檔案（詳細 / 包括隱藏） | `mkdir` / `rmdir` | 建立 / 刪除目錄 |
| `cp a b` / `mv a b` / `rm f` | 複製 / 搬或改名 / 刪除 | `cat` / `less` / `head` / `tail` | 睇檔案 |
| `ps` / `ps aux` | 列出 processes（PID） | `kill PID` | 送 signal 畀 process |
| `wc -l` | 數行數 | `sort` / `grep x` | 排序 / 搵字 |
| `diff a b` | 比較檔案（PA 對答案） | `chmod u+x f` | 加執行權限 |
| `du -ah \| sort -rh \| less` | 睇 disk 用量（CS Lab 2 quota 100MB） | `vim` / `nano` | 文字編輯器 |

---

## L2. Lab 2 — C in Linux、編譯流程、Ch1–3 Review

### L2.1 Compile pipeline（同 Ch2 linker/loader 掛鈎）
- 最簡：`gcc prog.c -o prog` → `./prog`（**loader** 將 executable 載入 memory）。
- `gcc -c main.c` → `main.o`（relocatable object）；`gcc -o main main.o -lm` → **linker** 連 math library（`-lm`，用 `<math.h>` 時要加）。
- `-g`：加 debugging info → `gdb prog`；Pthreads：`gcc prog.c -lpthread`（或 `-pthread`）。
- **Makefile**：`target: prerequisites` + 下一行 **TAB**（唔可以用空格）+ command；`make` / `make clean`。

### L2.2 I/O Subsystem 補充（Lab 2 review slides）
- **Buffering** — store data temporarily while being transferred；**Caching** — faster device holding a **copy** of data。
  - ⭐ **分別：a buffer may hold the only existing copy of a data item, whereas a cache only holds a copy on faster storage of an item that resides elsewhere.**
- **Spooling** — hold output for a device that **cannot accept interleaved data**（e.g. **printer**）。
- I/O hardware：**port**（connection point）、**bus**（PCI / PCIe、expansion bus for slow devices）、**controller (host adapter)**；device registers：**data-in, data-out, status, control**。
- **Device driver** presents a **uniform device-access interface** to the I/O subsystem（abstraction）。
- Interrupt 補充：**maskable vs nonmaskable**；**interrupt vector = table of interrupt-handler addresses**；**multilevel interrupts**（high vs low priority）；⭐ **a trap (software interrupt) has a relatively LOW interrupt priority compared with device interrupts**；multi-CPU systems can process interrupts concurrently。
- **DMA controller operates the memory bus directly — momentarily prevents the CPU from accessing main memory**（cycle stealing）；完成後 interrupt。

### L2.3 Lab 2 fork 題（已驗證 ✅）
```c
int main() {
    pid_t pid = fork();  int cnt = 0;
    if (pid == 0) {
        cnt += 10;  pid = fork();
        if (pid != 0) { cnt += 10;  pid = fork(); }
    }
    printf("%d \n", pid);  printf("%d \n", cnt);
    return 0;
}
```
- 4 個 processes 印出：P0（pid≠0, cnt 0）、C1（pid≠0, cnt 20）、C2（pid 0, cnt 10）、C3（pid 0, cnt 20）。
- **non-zero PID 印 2 次；'0' 印 3 次（P0 嘅 cnt + C2、C3 嘅 pid）；'10' 印 1 次。**

**填空：保證輸出 process 3 → 2 → 1**（每個都印 x = 1）：
```c
if (fork()) {            // BLANK1: fork()（> 0 亦可）
    x = x + 1;  wait(0); // BLANK2: wait(0) / wait(NULL)
    printf("...process 1 is %d\n", x);
} else if (fork()) {     // BLANK3: fork()
    x = x + 1;  wait(0); // BLANK4: wait(0)
    printf("...process 2 is %d\n", x);
} else { x = x + 1;  printf("...process 3 is %d\n", x); }
```

---

## L3. Lab 3 — Linux Process & Pipe System Calls（⭐⭐⭐ PA1 + 考試 API）

### L3.1 本 lab 用到嘅 system calls
- **Process**：`getpid`, `getppid`, `sleep`, `fork`, `wait`, `signal`
- **File**：`open`, `read`, `write`, `close`, `pipe`, `dup`, `dup2`
- **Execute**：`execl`, `execlp`, `execle`, `execv`, `execvp`, `execvpe`

| Call | 重點 |
|---|---|
| `pid_t getpid(void)` / `getppid(void)` | 自己 / parent 嘅 PID |
| `unsigned int sleep(unsigned int s)` | 停 s 秒（`usleep` 用 µs；`nanosleep` 更細） |
| `pid_t fork(void)` | child 0、parent child PID、−1 error（set errno）；child 得到 parent address space（text, data, bss, heap, stack）同 **open file descriptors** 嘅**獨立 copy** |
| `pid_t wait(int *status)` | 等任何一個 child；`wait(0)` / `wait(NULL)` 唔要 status；返回 child PID；**課程只用 `wait()`**（`waitpid` 唔使） |
| `signal(SIGINT, handler)` | **signal = software-generated interrupt**；可以用 customized handler 取代 default；**child inherits the customized handler** |

### L3.2 Zombie / Orphan demo（lab 示範）
- **Orphan**：parent 先完（冇 wait）→ shell prompt 出咗嚟之後 child 先繼續印 → child **被 init (PID 1) adopt & reap**。
- **用 wait() 正確**：parent 印完 `wait(0)` → child 印完先返 shell。
- **Zombie**：child 已完但 parent 仲 `sleep(10)` 未 `wait()` → child 喺嗰段時間係 zombie；parent `wait(0)` 後清走。
- **Exit status**：**voluntary** — normal `exit(0)`（return from main / `exit` / `_exit`）、error `exit(1)`；**involuntary** — fatal error（divide by 0, segmentation fault, core dump）、**killed by another process（`kill()`）**。child 終止時：open files flushed & closed、resources de-allocated、**parent notified via a signal**、exit status via `wait()`。

### L3.3 File operations（低階 vs stdio）
```c
fd = open("hello.txt", O_CREAT | O_WRONLY, S_IRUSR | S_IWUSR);   /* permission 600 */
write(fd, "hello\n", 6);  close(fd);
fd = open("hello.txt", O_RDONLY);  read(fd, buffer, 6);  close(fd);
```
- `open/read/write/close`（`<fcntl.h>`, `<unistd.h>`）= **low-level system calls**；`fopen/fread/fwrite/fclose`（`<stdio.h>`）= **high-level C library**。
- ⭐ **PA 唔准用 stdio file ops：`FILE*` 係 C library 嘅 struct，cannot be used in pipe operations**。

### L3.4 Pipes
- **Key concept：treat a pipe as 2 files**；`int pipe(int pfds[2])` → **pfds[0] read end，pfds[1] write end**。
- Data received **in the order it was sent**；**OS enforces mutual exclusion（only one process at a time）**；**processes sharing the pipe must have the same parent**。
- ⭐ **read/write are blocking**：冇 data 讀 → reader block；pipe 滿 → writer block（pipe size 有限：4 KB page / 64 KB）。
- **Two-way communication → create two pipes**（每個方向一條）。
- Shell pipe `ps aux | grep root | sort | wc -l`：前一個 command 嘅 output 做下一個嘅 input。

### L3.5 exec family
- **6 variants**：`execl, execlp, execle, execv, execvp, execvpe` — **replace the current process image；成功唔會 return；error return −1**。
- 字母意思：**l** = arguments as a **list**（數目已知）；**v** = arguments in a **vector/array**（compile time 唔知數目，PA1 用 `execvp`）；**p** = search **PATH**；**e** = pass **environment**。
```c
execlp("ls", "ls", "-l", "-h", NULL);            /* same as running "ls -l -h" */
char *args[] = {"ls", "-l", "-h", NULL};  execvp("ls", args);
printf("never printed if exec succeeds\n");
```

### L3.6 dup / dup2（redirection 核心）
- `int dup(int oldfd)` — copy 到 **first unused (lowest-numbered) fd**；`int dup2(int oldfd, int newfd)` — copy 到指定 newfd（如已開先 close）；成功返回新 fd，失敗 −1。
- Default：**0 = stdin，1 = stdout，2 = stderr**。
- **Lab 題：以下程式輸出係咩？**
```c
fd = open("output.txt", O_CREAT | O_WRONLY, S_IRUSR | S_IWUSR);
close(1);                 /* close stdout */
dup(fd);                  /* lowest free fd = 1 → stdout now refers to output.txt */
printf("Hello World!\n"); fflush(stdout);
```
  → **螢幕冇嘢顯示；"Hello World!" 寫入 output.txt**。
- **`ls | wc -l` 實作（lab 版本：parent 做 wc）**：
```c
pipe(pfds);
if (fork() == 0) {                 /* child → ls */
    close(1); dup(pfds[1]);        /* stdout = pipe write end */
    close(pfds[0]);
    execlp("ls", "ls", NULL);
} else {                           /* parent → wc -l */
    close(0); dup(pfds[0]);        /* stdin = pipe read end */
    close(pfds[1]);                /* MUST close write end, else wc never sees EOF */
    wait(0);
    execlp("wc", "wc", "-l", NULL);
}
```
- **dup vs dup2**：兩個都得；**dup2 更 flexible、易讀**；如果連續兩個 `close` 再兩個 duplicate，**應該用 dup2 指定位置**。

### L3.7 Lab 3 fork 例題 + 更多歷屆 fork 題（全部驗證 ✅）
| 題目 | Code（重點） | 答案 |
|---|---|---|
| Ex1 | `for (i=0;i<3;i++) fork();` | $2^3 = 8$ |
| Ex2 | `for(i<2){ fork(); for(j<3) if(!fork()){} }` | 8 個連續 fork → $2^8 = 256$ |
| Ex3 | `for(i<10){ if(fork()){fork();fork();} else fork(); }` | 每輪 ×6（parent 4 + child 2）→ $6^{10}$ |
| **Fall 2022 Q3** | `for(i<n){ if (fork() == fork()) printf(...); }` | processes $4^n$；lines $4^0 + 4^1 + \cdots + 4^{n-1} = \dfrac{4^n - 1}{3}$（n=1,2,3：1, 5, 21 行） |
| **Fall 2024 P3.1** | `for(i<M){ pid = fork(); if(!pid) for(j<N) fork(); }` | (a) **child** 執行 line Y（`!pid` true）；(b) M=N=1 → **3**；(c) $(2^N + 1)^M$ |
| **Spring 2025 MC12** | `if (fork() \|\| fork()) { if (fork() && !fork()) fork(); }` | **9** processes（新建 8 個） |

- **Fall 2022 解釋**：每輪每個 process 變 4 個（2 個 fork）→ $4^n$；每輪只有「兩個 fork 都返回 0」嗰個 grandchild 印 → 第 k 輪印 $4^{k-1}$ 行。
- **Fall 2024 解釋**：設 $f(k)$ = 剩 k 輪時一個 process 最終變幾多個：parent 自己繼續 → $f(k-1)$；child 做 N 次 fork 變 $2^N$ 個、每個都繼續 → $2^N f(k-1)$；所以 $f(k) = (1 + 2^N) f(k-1)$，$f(M) = (2^N + 1)^M$。
- **Short-circuit 圖解（lab）**：

| Pattern | 共幾多 processes | 入 if-clause | 入 else-clause |
|---|---|---|---|
| `fork() && fork()` | 3 | **1**（兩個都 > 0） | 2 |
| `fork() \|\| fork()` | 3 | **2** | 1（兩個都 = 0） |

  - S25 MC12：外層 `||` → 2 個入 if、1 個入 else；內層 `fork() && !fork()` → 1 個入 inner if（再 fork → 2）、2 個唔入 → 每個變 4 → $2 \times 4 + 1 = 9$。
- **Tips（lab）**：見到 loop → **展開成冇 loop 嘅等價 statements**；nested loop → 先展開內層；`if (fork())` → 分別諗 parent 同 child 行咩。

### L3.8 PA1 — Simplified Linux Shell（考試可能問）
- 6 種 command pattern：`cmd`、`cmd < in`、`cmd > out`、`cmd < in > out`、`cmd > out < in`、`cmd1 | cmd2 | …`（最多 8 段）。
- **`cd` 唔可以用 exec 做**（要改 shell 自己嘅 working directory）→ **`chdir(path)`**（0 成功 / −1 失敗）。
- **唔准用 `system()` / `popen()`**（會開另一個 shell 代你做）。
- **Redirection** = `open` + `dup/dup2` 取代 stdin/stdout；**multi-level pipe** = 將 2-level pipe 寫成 for-loop。
- `execvp` 嘅 argv array 尾要放 **NULL**（所以 8 個 arguments 要 size 9）。
- **Ctrl-C** → `signal(SIGINT, handler)`，SIGINT = **2**；start/end PID 要一致（冇多餘 processes）。
- Plagiarism：JPlag 檢測，**提供同抄襲雙方都 0 分**。

---

## L4. Lab 4 — Named Pipes & Pthreads

### L4.1 Anonymous vs Named pipes（lab 版本）
- Anonymous：unidirectional；cannot be accessed outside the creating process；parent–child；ceases after processes terminate。
- Named (FIFO)：bidirectional；no parent–child needed；several processes（多 writers）；**appear as files**（`mkfifo()`）；**exist until explicitly deleted**。
- ⭐ FIFO 細節：
  - **open / read / write 係 blocking**：**FIFO 要兩端都有 process open 先會 unblock**（冇 reader 時 writer 會 block）；用 **`O_NONBLOCK`** 可以變 non-blocking。
  - **Data read once then discarded**（唔似 regular file 可以重讀）→ **cannot broadcast to multiple recipients**。
  - 實際上 **一條 FIFO 唔適合雙向**（寫完即刻讀可能讀返自己個 message）→ 雙向用兩條。
  - **Writes ≤ PIPE_BUF bytes are atomic**；更大可能同其他 writer 交錯。
- **`popen(cmd, "r"/"w")` / `pclose(fp)`**（`<stdio.h>`）：fork 一個 child 執行 cmd，返回 `FILE*` 連住佢嘅 stdout（"r"）或 stdin（"w"）；`pclose` 等佢完並返回 termination status。（**PA1 禁用**）
- FIFO producer：`if (access(FIFO_NAME, F_OK) == -1) mkfifo(FIFO_NAME, 0777);` → `open(FIFO_NAME, O_WRONLY)` → `write` loop → `close`；consumer：`open(..., O_RDONLY)` → `read` until 0 → `close`。
- `access(path, how)`：`F_OK` 存在、`R_OK`/`W_OK`/`X_OK` 權限；0 = OK，−1 = 唔得。

### L4.2 Exam example — 兩條 ordinary pipes 雙向通訊（填空）
```c
char buffer[10] = {};  int p2c[2], c2p[2];
pipe(p2c);                                  /* BLANK1 */
pipe(c2p);                                  /* BLANK2 */
pid_t pid = fork();
if (pid == 0) {                             /* child */
    const char msg[] = "Child";
    close(c2p[0]);
    write(c2p[1], msg, 6);                  /* BLANK3（5 亦接受） */
    close(p2c[1]);
    read(p2c[0], buffer, 7);                /* BLANK4（6 亦接受） */
    printf("Child received the message: %s\n", buffer);
} else {                                    /* parent */
    const char msg[] = "Parent";
    close(c2p[1]);
    read(c2p[0], buffer, 6);                /* BLANK5（5 亦接受） */
    close(p2c[0]);
    write(p2c[1], msg, 7);                  /* BLANK6（6 亦接受） */
    printf("Parent received the message: %s\n", buffer);
}
```
- 輸出：`Parent received the message: Child` / `Child received the message: Parent`。

### L4.3 Pthreads
```c
int sum;                                   /* shared by the threads */
void *runner(void *param) {
    int upper = atoi(param);  sum = 0;
    for (int i = 1; i <= upper; i++) sum += i;
    pthread_exit(0);
}
int main(int argc, char *argv[]) {
    pthread_t tid;  pthread_attr_t attr;
    pthread_attr_init(&attr);                       /* default attributes */
    pthread_create(&tid, &attr, runner, argv[1]);   /* id, attr, start routine, arg */
    pthread_join(tid, NULL);                        /* wait for the thread */
    printf("sum = %d\n", sum);
}
```
- `pthread_t` = thread id；`pthread_attr_t` = attributes（stack size, scheduling info）；compile **`-lpthread`**。
- Join 多個 threads：`for (i = 0; i < 10; i++) pthread_join(workers[i], NULL);`
- **Thread trace**：main 印 "main: begin" → create T1、T2 → join → "main: end"；**threads run independently, order depends on scheduling**（T2 可以喺 T1 之前行）。
- **兩個 threads 各印 "begin of X" 同 "end of X"** → 中間 4 行有 $\binom{4}{2} = 6$ 種次序（每個 thread 自己 begin 先過 end），"main: start" 最先、"main: finish" 最尾 → **6 possible outputs**。

### L4.4 Exam example — thread vs process 共享 memory（MC）
```c
void *child(void *arg) { int *counter = (int *)arg; (*counter)++; return NULL; }
int main() {
    int counter = 0;  pthread_t thread;
    pthread_create(&thread, NULL, child, (void *)&counter);
    pthread_join(thread, NULL);
    printf("%d\n", counter);                 /* 1: thread shares memory */
    counter = 0;
    pid_t pid = fork();
    if (pid) wait(NULL);
    else { child((void *)&counter); exit(0); }
    printf("%d\n", counter);                 /* 0: child process has its own copy */
}
```
- 選項 A `0 0`、B `1 0`、C `0 1`、D `1 1` → **答案 B（1 / 0）**。**Key：threads share memory space but processes have separate memory spaces.**

---

## L5. Lab 5 — Scheduling Review & PA2（MLFQ）

### L5.1 Review 例題（P1 7, P2 4, P3 1, P4 4，全部 t=0，已驗證 ✅）
| Algorithm | Gantt | avg WT |
|---|---|---|
| FCFS / RR q=8 | `0 P1 7 P2 11 P3 12 P4 16` | $\frac{0+7+11+12}{4} = 7.5$ |
| RR q=4 | `0 P1 4 P2 8 P3 9 P4 13 P1 16` | $\frac{9+4+8+9}{4} = 7.5$ |
| RR q=2 | `0 P1 2 P2 4 P3 5 P4 7 P1 9 P2 11 P4 13 P1 16` | $\frac{9+7+4+9}{4} = 7.25$ |
| SJF | `0 P3 1 P2 5 P4 9 P1 16`（P2、P4 同長 → 先 P2） | $\frac{9+1+0+5}{4} = 3.75$ |
| Priority（4,1,2,3） | `0 P2 4 P3 5 P4 9 P1 16` | $\frac{9+0+4+5}{4} = 4.5$ |
- **SRTF**（P1 0/7, P2 2/4, P3 4/1, P4 5/4）：`0 P1 2 P2 4 P3 5 P2 7 P4 11 P1 16` → $\frac{9+1+0+2}{4} = 3$。
- 觀察：q 大過最長 burst → RR = FCFS；q 細咗 avg WT 唔一定變差（7.25 < 7.5）。

### L5.2 ⭐ Priority + RR 有唔同 arrival time（HW / Exam 熱門）
- ⚠️ **Common mistake：reset the time quantum of a preempted process.** 正確：**被高 priority 新 process preempt 嘅 process 要記住佢剩餘嘅 quantum**（同 MLFQ 規則一樣）。
- **Spring 2023 midterm 官方答案**（q = 2）：`0 P1 1 P2 4 P1 5 P3 7 P1 8 P4 10 P1 11 P3 13 P5 15 P1 16 P3 18 P5 20 P3 22 P5 24`
  - P1 喺 0–1 跑咗 1 unit 被 P2（高 priority）preempt → 4–5 **只跑剩低嘅 1 unit quantum** 然後輪到 P3（同 priority RR）。8–10 同樣：P4 preempt P1，P1 10–11 用返剩低 1 unit。
  - 由 Gantt 推返嘅 table（模擬器重現完全一致 ✅）：P1 (0, 5, pr 2)、P2 (1, 3, pr 1)、P3 (2, 8, pr 2)、P4 (8, 2, pr 1)、P5 (9, 6, pr 2)，細數字 = 高 priority。

### L5.3 RM / EDF 例題（deadline < period）
- P1 (t=1, d=2, p=4)、P2 (2, 5, 6)、P3 (3, 7, 9)；$U = \frac14 + \frac26 + \frac39 = 0.917$。
- **RM**（P1 > P2 > P3）：`0 P1 1 P2 3 P3 4 P1 5 P3 6 P2 8 P1 9 P3 …` → **P3 first job finishes at 10 > deadline 7 → misses 1 deadline**。
- **EDF**：`0 P1 1 P2 3 P3 4 P1 5 P3 7 P2 8 P1 9 P2 10 P3 12 …` → **no deadline missed**。

### L5.4 PA2 — N-level MLFQ simulator
- **N = 1–4 queues，last queue must be FCFS**（input 用大數 e.g. 1000 代表 FCFS），**≤ 10 processes**。
- Input：`queue_num = 3`、`time_quantum = 2 4 1000`、`process_table_size`、`process_table`（`P1 0 7` …）；`#` 開頭 / 空行忽略。
- Assumptions：**sorted by arrival**；**first arrival = 0**；**no two processes arrive at the same time**；**CPU never idle**；Gantt ≤ 300 steps。
- 用法：`./mlfq < input.txt > output.txt`（**input/output redirection**）；用 `diff --side-by-side your-out.txt sample-out.txt`（`--suppress-common-lines`）對答案。
- Output：parsed values + **`Gantt Chart = 0 P1 2 P2 3 P1 4 P3 5 P1 6 P4 8 P1 10 P4 11 P1 12`**。
- **Step-by-step 例子（Q0 q=2, Q1 q=4, Q2 FCFS；P1 0/7, P2 1/1, P3 4/1, P4 6/3）**，已用模擬器驗證 ✅：
  - t=1 P2 到 → **no preemption**（P1 都喺 Q0）；t=2 P1 用完 Q0 quantum → Q1；P2 跑。
  - t=3 P2 完 → P1（Q1，quantum 4）；t=4 P3 到 → **P1 preempted**（剩 burst 4，**剩 quantum 3**）。
  - t=5 P3 完 → P1；t=6 P4 到 → P1 preempted（剩 quantum 2）；P4 6–8 用完 Q0 → Q1 tail。
  - t=8 Q1 = [P1, P4] → P1 跑 2 → quantum 用完（剩 burst 1）→ Q2；t=10 P4 跑 1 完；t=11 P1（Q2）跑到 12。

---

## L6. Lab 6 — Synchronization Review（Sample Questions）

### L6.1 Peterson's solution（software-only，2 processes）
```c
/* P_i (j = 1 - i) */
do {
    flag[i] = true;  turn = j;
    while (flag[j] && turn == j) ;   /* busy wait */
        /* critical section */
    flag[i] = false;
        /* remainder section */
} while (true);
```
- Shared：**`flag[2]`**（想入 CS）、**`turn`**（輪到邊個）；**assumption：load and store are atomic**。
- **Proof**：ME — 兩個都想入時 `turn` 只可以係 0 或 1 → 只有一個過到 while；Progress — 冇人喺 CS 就即刻入；**Bounded waiting — 最多等對方一次**（對方出嚟會設 `flag[j] = false`，再想入就要設 `turn = i`）。
- 缺點：**複雜（只限兩個 process）、每個 thread code 唔同、busy waiting 浪費 CPU** → OS 提供 mutex / semaphore / condition variable。

### L6.2 POSIX primitives 速查
- Mutex：`pthread_mutex_init(&m, NULL)` → `lock` → access → `unlock` → `destroy`；**thread 持 lock 時 crash → 其他人 block**。
- Semaphore（`<semaphore.h>`）：`sem_init(&s, pshared, value)`（**pshared = 0：同一 process 嘅 threads 共用**）、`sem_wait`、`sem_post`、`sem_destroy`。

| Initial value | 行為 | 用途 |
|---|---|---|
| **1** | 一個 permit | **mutual exclusion（當 mutex）** |
| **0** | wait() 一定 block 直至有人 signal | **ordering**（等其他 thread 做完先） |
| **N** | N 個 permits | **管理 N 個相同 resources** |

- Condition variable：`pthread_cond_wait(&cond, &mutex)` **atomically releases the mutex and sleeps；signalled → re-acquires the mutex before returning**；用 **`while (!ready)`** 包住；`pthread_cond_signal` / `pthread_cond_broadcast`。
- Lab note：**semaphore ≈ integer S + a mutex protecting it + a condition variable whose condition is "S > 0"**。

### L6.3 Sample Questions（官方答案，已驗證 ✅）
- **Q0**：binary semaphore = mutex？→ **No** — init 1 可以當 mutex，但 init 0 可以做其他用途（ordering）。
- **Q1**：T1：`wait(S1); CS; signal(S2)`；T2：`wait(S2); CS; signal(S3)`；T3：`wait(S3); CS; signal(S1)` 要 T1, T2, T3, T1… → **S1 = 1, S2 = 0, S3 = 0**。
- **Q2**（P0 → P1 → P2 循環，填 BLANK）：**S0 = 1, S1 = 0, S2 = 0**；P0：`wait(S0)` … **`signal(S1)`**；P1：**`wait(S1)`** … **`signal(S2)`**；P2：**`wait(S2)`** … `signal(S0)`。
- **Q3**（mutex 填空）：`pthread_mutex_t* m = (pthread_mutex_t*) arg;`、`pthread_mutex_lock(m);`、`pthread_mutex_unlock(m);` → **purpose：protect the shared counter；final counter = 10,000**（兩個 threads 各加 5,000）。（`void*` 要 cast 返 `pthread_mutex_t*`，因為 thread function signature 一定係 `void *f(void *)`。）
- **Q4**（X = Y = 0）：A：`wait(X); "b"; signal(Y); wait(Y); "c"; signal(Y);` B：`signal(X); "a"; wait(Y); "d";`
  - **Both complete：abcd, bacd, bcad（3 種）**；如果 B 先攞到 Y → A 永遠 block → **bad, abd**（A 唔會完成）。
- **Q5**（S0 = 1, S1 = S2 = S3 = 0）：P0 loop：`wait(S0); print '1'; release(S1); release(S2); release(S3);`；P1：`wait(S1); release(S0);`；P2：`wait(S2); release(S0); wait(S3); release(S0);` → **'1' 印 4 次**（S0 permits：initial 1 + P1 1 + P2 2 = 4）。
- **Q6**（readers–writers，用兩個 mutex）：
```c
/* reader */
pthread_mutex_lock(&mutex);
read_count++;
if (read_count == 1) pthread_mutex_lock(&rw_mutex);    /* first reader locks out writers */
pthread_mutex_unlock(&mutex);
    /* reading */
pthread_mutex_lock(&mutex);
read_count--;
if (read_count == 0) pthread_mutex_unlock(&rw_mutex);  /* last reader lets writers in */
pthread_mutex_unlock(&mutex);
/* writer */
pthread_mutex_lock(&rw_mutex);  /* writing */  pthread_mutex_unlock(&rw_mutex);
```
- **Q7**（race values）：a = 1, b = 3, c = 0；T1：`a = b + 1; c = a - b;`；T2：`a = 13; b = 10; c = 2;` → **c ∈ {−6, 1, 2, 3, 10}**。
  - 2：T2 嘅 `c = 2` 最後寫；1：T1 讀 a=4、b=3 後 T2 全做完，或者 T2 先全做（a = 11, c = 11 − 10）；−6：T1 讀 a=4 後 T2 全做（b=10）；3：T1 寫 a=4 → T2 全做 → T1 讀 a=13, b=10；10：T1 寫 a=4 → T2 寫 a=13 → T1 讀 a=13, b=3 → T2 寫 b, c → T1 寫 c = 10。
  - 方法：**列出每個 read 可能見到嘅值（a ∈ {4, 11, 13}, b ∈ {3, 10}）+ 邊個最後寫 c**，再剔走不可能組合（a=11 表示 b 已經係 10）。

---

## L7. 常見陷阱（Labs / PA）

| 敘述 | 真/假 |
|---|---|
| PA 可以用 `fopen`/`FILE*` 做 pipe | ❌（FILE* 唔用得喺 pipe operations） |
| `wait(0)` 同 `wait(NULL)` 一樣 | ✅ |
| `dup(fd)` 一定返回 1 | ❌（返回 lowest unused fd；要先 `close(1)`） |
| `exec*()` 成功後會返回 0 | ❌（唔會 return；失敗 −1） |
| `execvp` 嘅 argv 唔使 NULL 結尾 | ❌ |
| `cd` 可以用 `execvp("cd", …)` 做 | ❌（要 `chdir`） |
| FIFO 開 write end 時冇 reader 會 block | ✅ |
| FIFO 啲 data 可以畀多個 reader 各讀一次（broadcast） | ❌ |
| Child 會繼承 parent 嘅 customized signal handler | ✅ |
| Threads share memory，processes 唔 share | ✅ |
| Priority + RR 被 preempt 後 quantum 重新計 | ❌（保留剩餘 quantum） |
| PA2：最後一層 queue 係 FCFS | ✅ |
| Peterson：assume load/store atomic | ✅ |
| `sem_init(&s, 0, 0)` 嘅 0（第二個）表示 threads 共用 | ✅（pshared = 0） |
| Condition wait 會放開 mutex | ✅（醒返會重新攞） |
