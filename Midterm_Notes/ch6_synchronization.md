# Chapter 6 — Synchronization Tools（同步工具）

> 📌 **考試範圍提示**：Midterm 包到 **Ch6（Synchronization Tools）**。每年都有 **1 大題（8–25 分）+ 3–4 題 MC**。題型：
> 1. **Race condition — 列出 shared variable 所有可能值**（F19 Q4.3、F20 Q5：每個值 2.5 分！）
> 2. **Semaphore 次序控制填空**（S26 Q5：wait/signal 填 blank）、**semaphore 輸出序列判斷**（F19 Q4.4）
> 3. **用 atomic instruction 寫 spinlock**（S26 Q2.4 swap；Sp21 Q3.1 compare_and_reset）
> 4. **Bounded-waiting test_and_set 算法分析 / 改錯**（S26 MC25、Sp21 Q3.2）
> 5. 定義：**race condition、critical section 三個條件、spinlock 優缺點、binary semaphore vs mutex**
> 6. **Pthread mutex + semaphore 程式輸出**（S26 MC23）

---

## 1. Background（背景）[6.4–6.8]
- **Processes execute concurrently and may be interrupted at any time, partially completing execution.**
- **Concurrent access to shared data may result in data inconsistency.**
- **Maintaining data consistency requires mechanisms to ensure the orderly execution of cooperating processes.**

### 1.1 Producer–Consumer with `counter` [6.5–6.6]
- 用 `counter` 記 buffer 有幾多 item（可以用晒 BUFFER_SIZE 格）：
```c
/* Producer */                          /* Consumer */
while (true) {                          while (true) {
  while (counter == BUFFER_SIZE) ;        while (counter == 0) ;
  buffer[in] = next_produced;             next_consumed = buffer[out];
  in = (in + 1) % BUFFER_SIZE;            out = (out + 1) % BUFFER_SIZE;
  counter++;                              counter--;
}                                       }
```
- 問題：`counter++` / `counter--` **唔係 atomic**。

### 1.2 Race Condition 例子 ⭐⭐ [6.7]
```
counter++  →  register1 = counter;  register1 = register1 + 1;  counter = register1
counter--  →  register2 = counter;  register2 = register2 - 1;  counter = register2
```
**counter = 5 initially**，interleaving：
| Step | Executed | Result |
|---|---|---|
| S0 | producer: register1 = counter | register1 = 5 |
| S1 | producer: register1 = register1 + 1 | register1 = 6 |
| S2 | consumer: register2 = counter | register2 = 5 |
| S3 | consumer: register2 = register2 − 1 | register2 = 4 |
| S4 | producer: counter = register1 | counter = 6 |
| S5 | consumer: counter = register2 | **counter = 4**（正確應該係 5！） |
- 調轉 S4、S5 → counter = 6。**結果取決於執行次序 → race condition。**
- **Kernel race example** [6.8]：P0、P1 同時 `fork()` → race on kernel variable **`next_available_pid`** → **same pid could be assigned to two different processes** unless mutual exclusion。

---

## 2. Race Condition & Critical-Section Problem ⭐⭐⭐ [6.9–6.12]

### 2.1 Race condition 定義（S26 Q2.1 原題，4 分）
> 📝 **Model answer**：*A **race condition** is an undesirable situation where several processes (or threads) access and manipulate shared data concurrently, and the final outcome depends on the particular order (timing) in which the accesses take place. Because the execution order is unpredictable (e.g., context switches at untimely points), the result can be incorrect / non-deterministic. **Example**: two threads execute `counter++` on the same shared counter without synchronization; each loads the old value into a register, increments it and stores it back, so one update can be lost and the final value is wrong (e.g., 5 + 1 − 1 gives 4 or 6 instead of 5).*
- Sp21 MC：「several processes access and manipulate the same data concurrently and the outcome depends on the order」→ **race condition**。
- 根本原因（summary）：**high-level statements (count++) translate into multiple machine instructions, which can be interleaved arbitrarily.**

### 2.2 Critical Section
- **Critical section：a segment of code in which a process may be changing shared variables, updating a table, writing a file, etc.**
- **When one process is in its critical section, no other may be in its critical section.**（**mutual exclusion and critical section imply the same thing**）
- **Critical-section problem：design a protocol that processes can use to cooperate.**
- **General structure** [6.10]：
```c
do {
    entry section        /* request permission */
        critical section
    exit section
        remainder section
} while (true);
```

### 2.3 三個 requirements ⭐⭐⭐（F19 Q4.1 原題）[6.11]
1. **Mutual exclusion** — **if process $P_i$ is executing in its critical section, no other processes can be executing in their critical sections.**
2. **Progress** — **if no process is executing in its critical section and some processes wish to enter, the selection of the process that will enter next cannot be postponed indefinitely**（只有唔喺 remainder section 嘅 process 先參與決定）。
3. **Bounded waiting** — **a bound must exist on the number of times other processes are allowed to enter their critical sections after a process has made a request to enter its critical section and before that request is granted.**（i.e. 等待時間有上限，no starvation）
- Assumptions：**each process executes at a nonzero speed；no assumption about the relative speed of the processes.**
- Summary：**bounded waiting also implies progress.**
- Sp21 MC：CS solution **唔需要**滿足 → **synchronization**（三個係 mutual exclusion, progress, bounded waiting）；mutual exclusion 定義 → A。

### 2.4 Critical sections in the kernel [6.12]
- Kernel data structures（**list of open files**, memory allocation, process table, interrupt handling）都有 race condition。
- **Preemptive kernel** — allows preemption of a process running in kernel mode；**not free from race conditions**，SMP 上更難；但 more responsive（適合 real-time）。
- **Non-preemptive kernel** — runs until it exits kernel mode, blocks, or voluntarily yields → **essentially free of race conditions in kernel mode**（single-processor）。

---

## 3. Synchronization Hardware ⭐⭐ [6.13–6.21]

### 3.1 Disabling interrupts [6.13]
- **Uniprocessor：could simply disable interrupts** → current code runs without preemption。
- **Generally inefficient on multiprocessor/SMP systems**（要 disable 所有 CPU 嘅 interrupts，費時；影響 system clock）。
- 層次：**Hardware**（load/store, disable interrupts, **test&set, compare&swap**）→ **High-level APIs**（locks, semaphores）→ programs。

### 3.2 Atomic instructions [6.14]
- **Atomic = non-interruptible**；保證 instruction 唔會被中途打斷 → no race condition。
- 即使兩個 CPU 同時執行，**they are forced to execute sequentially (serialization)**。
- **Building blocks for more sophisticated synchronization tools.**
- 兩個常用：**`test_and_set()`**（test a memory word and set a value）、**`compare_and_swap()`**（swap contents of two words）。
- S26 MC24：commonly used hardware primitive → **test_and_set()**。

### 3.3 test_and_set ⭐⭐ [6.15–6.16]
```c
boolean test_and_set(boolean *target) {   /* executed atomically */
    boolean rv = *target;
    *target = TRUE;
    return rv;                              /* returns the OLD value */
}
/* lock initialized to FALSE */
do {
    while (test_and_set(&lock)) ;   /* spin while old value was TRUE (lock held) */
        /* critical section */
    lock = false;                   /* release */
        /* remainder section */
} while (true);
```
- 第一個 call 嘅 process 攞到 old = FALSE → 入 CS，同時 lock 變 TRUE；其他人攞到 TRUE → spin。
- ✅ **mutual exclusion**；❌ **bounded waiting**（冇保證輪到邊個）。
- Sp21 MC4（lock init 0）：entry section → **`while (test_and_set(&lock));`**（C）。✗ `while (!test_and_set(&lock))`。

### 3.4 compare_and_swap (CAS) ⭐⭐ [6.17–6.18]
```c
int compare_and_swap(int *value, int expected, int new_value) {  /* atomic */
    int temp = *value;
    if (*value == expected)
        *value = new_value;
    return temp;                           /* returns the OLD value */
}
/* lock initialized to 0 */
do {
    while (compare_and_swap(&lock, 0, 1) != 0) ;   /* spin until old value was 0 */
        /* critical section */
    lock = 0;
        /* remainder section */
} while (true);
```
- ⚠️ 留意 return 值：**CAS 返回 old value** → 用 `!= 0` 判斷。Sp21 MC4 ✗ `while (compare_and_swap(&lock, 0, 1) == 0)`（相反）、✗ `compare_and_swap(&lock, 1, 0) != 0`。

### 3.5 Bounded-waiting Mutual Exclusion with test_and_set ⭐⭐⭐ [6.19–6.20]
```c
/* shared: boolean waiting[n] (all false), boolean lock = false */
do {
    waiting[i] = true;
    key = true;
    while (waiting[i] && key)
        key = test_and_set(&lock);
    waiting[i] = false;
        /* critical section */
    j = (i + 1) % n;
    while ((j != i) && !waiting[j])        /* scan in cyclic order */
        j = (j + 1) % n;
    if (j == i)
        lock = false;          /* no one is waiting, so release the lock */
    else
        waiting[j] = false;    /* unblock process j (hand the lock over directly) */
        /* remainder section */
} while (true);
```
**Sketch proof** [6.20]：
- **Mutual exclusion**：$P_i$ enters CS only if `waiting[i] == false` or `key == false`. `key` becomes false only via `test_and_set()` — **only the first process to execute test_and_set finds key == false**；others wait. `waiting[i]` becomes false only when another process leaves its CS, and **only one waiting[i] is set to false** → mutual exclusion。
- **Progress**：a process exiting its CS **either sets lock = false or sets waiting[j] = false** — both let a waiting process proceed。
- **Bounded waiting**：the exiting process **scans waiting[] in cyclic order (i+1, i+2, …, n−1, 0, …, i−1)** and designates the first waiting one → **any waiting process enters within n − 1 turns**。

> ⚠️ **S26 MC25**（which is NOT correct）→ **A.「test_and_set(&lock) releases the lock after the critical section」**（錯：釋放係 `lock = false` 或者 `waiting[j] = false`；test_and_set 只會 set lock 為 true）。✅ waiting[i] 表示 $P_i$ 想入 CS；✅ `waiting[j] = false` 表示 $P_i$ 將 lock 交畀 $P_j$（lock 冇真正釋放）；✅ 執行 `lock = false` 後 $P_i$ 可以再入 CS。

> 📝 **Sp21 Q3.2（改錯題）**：版本用 `j = i + 1; while (j < n && !waiting[j]) j++; if (j < n) waiting[j] = false;`
> **Problems**：(1) **只 scan index 大過 i 嘅 process → index 細過 i 嘅 process 可能 unbounded waiting**（violates bounded waiting）；(2) **冇 process 等嘅時候 lock 永遠唔會 release** → 其他人之後永遠入唔到（violates progress / deadlock）。
> **Correction**：改返 cyclic scan `j = (i + 1) % n; while ((j != i) && !waiting[j]) j = (j + 1) % n;` 同 `if (j == i) lock = false; else waiting[j] = false;`。

### 3.6 Atomic Variables [6.21]
- **Atomic variable：atomic (uninterruptible) updates on basic data types (integers, booleans)**，用 CAS 實現：
```c
void increment(atomic_int *v) {
    int temp;
    do {
        temp = *v;
    } while (temp != compare_and_swap(v, temp, temp + 1));   /* retry if someone changed v */
}
```

### 3.7 用其他 atomic instruction 寫 spinlock（考試題型）⭐⭐
**S26 Q2.4 — `swap(x, v)`：atomically sets x = v and returns the old value of x**（`locked` = 1 held / 0 free）：
```c
while (swap(locked, 1) == 1) ;   /* acquire: spin while the old value was 1 */
/* critical section */
locked = 0;                       /* release (or swap(locked, 0)) */
```
**Sp21 Q3.1 — `compare_and_reset(int *a, int old, int new)`：if (*a == old) { *a = new; return 1; } else return 0;**
```c
struct spinlock { int value = 0; };
void acquire(struct spinlock *lock) {
    while (compare_and_reset(&lock->value, 0, 1) == 0) ;   /* spin until we changed 0 → 1 */
}
void release(struct spinlock *lock) {
    lock->value = 0;
}
```
**萬用套路**：搵出「**成功攞到 lock**」時 instruction 嘅 return 值 → `while (instruction(...) 表示失敗) ;` → release 就 set 返 free value。
| Instruction | Acquire | Release |
|---|---|---|
| `test_and_set(&lock)`（return old） | `while (test_and_set(&lock)) ;` | `lock = false;` |
| `compare_and_swap(&lock, 0, 1)`（return old） | `while (compare_and_swap(&lock, 0, 1) != 0) ;` | `lock = 0;` |
| `swap(locked, 1)`（return old） | `while (swap(locked, 1) == 1) ;` | `locked = 0;` |
| `compare_and_reset(&v, 0, 1)`（return 1 = success） | `while (compare_and_reset(&v, 0, 1) == 0) ;` | `v = 0;` |
| 課本 `swap(&lock, &key)`（exchange） | `key = true; while (key == true) swap(&lock, &key);` | `lock = false;` |

---

## 4. Mutex Locks ⭐⭐ [6.22–6.23]
- **Simplest software tool most OSes use.**
- **Protect a critical region by first `acquire()` a lock, then `release()` it** — **both must be atomic**（usually via hardware atomic instructions）。
- Boolean variable **`available`** 表示 lock 有冇得用：
```c
acquire() {
    while (!available) ;   /* busy wait */
    available = false;
}
release() {
    available = true;
}
do { acquire lock;  critical section;  release lock;  remainder section; } while (true);
```
- **This solution requires busy waiting → the lock is called a spinlock.**
- Wait if locked — 等耐咗應該 **sleep / block** 而唔係 spin。

### 4.1 Spinlock 優缺點 ⭐⭐⭐（S26 Q2.4b 原題）
> 📝 **Model answer**：*Disadvantage: a spinlock **wastes CPU cycles due to busy waiting** (the waiting thread keeps looping). Advantage: **no context switch is required** when a process must wait on a lock, and a context switch may take considerable time. So spinlocks are useful when locks are expected to be **held for short times**, especially on **multiprocessor systems**, where one thread can spin on one processor while another thread executes its critical section on another processor.*
- 單 CPU 用 spinlock 冇乜意思（spin 緊嘅 thread 佔住 CPU，持有 lock 嘅 thread 跑唔到）。

---

## 5. Semaphores ⭐⭐⭐ [6.24–6.28]

### 5.1 定義 [6.24]
- **Semaphore S — a (non-negative) integer variable, a generalized lock**；**Dijkstra (late 1960s)**；**main synchronization primitive in original UNIX**。
- **Accessed only through two atomic operations (apart from initialization)：`wait()` and `signal()`**（originally **P()** = *proberen*, to test；**V()** = *verhogen*, to increment）。
- **Atomic → no more than one process can execute wait()/signal() on the same semaphore at the same time (serialization).**
```c
wait(S) {                  signal(S) {
    while (S <= 0) ;           S++;
    S--;                   }
}
```

### 5.2 Counting vs Binary [6.25] ⭐
- **Counting semaphore** — **value ranges over an unrestricted domain**；**control access to a resource with a finite number of instances**（**initialize to the number of available resources**）；wait = 攞一個，signal = 還一個。
- **Binary semaphore** — **value only 0 or 1**；**can behave like a mutex lock**，但亦可以用嚟做其他同步。
- **Ordering example**（S1 喺 S2 之前執行）：`synch = 0`
```c
P1:  S1;  signal(synch);          P2:  wait(synch);  S2;
```
> 📝 **F19 Q4.2：Binary semaphore = mutex lock?** → ***No.*** *A binary semaphore initialized to 1 can be used as a mutex lock, but a binary semaphore can also be used for other synchronization purposes, e.g., initialized to 0 to enforce execution order / signaling between processes. (Also a mutex lock is owned — the thread that locks it must unlock it — whereas any process can signal a semaphore.)*

### 5.3 Implementation with no busy waiting ⭐⭐ [6.26–6.27]
- **Each semaphore has a waiting queue**（each entry：value + pointer to next record）。
- **block()** — place the invoking process on the waiting queue（suspend）；**wakeup(P)** — remove a process from the waiting queue and put it in the **ready queue**。
```c
typedef struct { int value; struct process *list; } semaphore;
wait(semaphore *S) {
    S->value--;
    if (S->value < 0) { add this process to S->list; block(); }
}
signal(semaphore *S) {
    S->value++;
    if (S->value <= 0) { remove a process P from S->list; wakeup(P); }
}
```
- ⭐ **Increment/decrement is done BEFORE checking the value**（同 busy-waiting 版相反）。
- ⭐ **Semaphore value may become negative；if negative, its magnitude = number of processes waiting on it.**（busy-waiting classical 版永遠唔會 negative）

### 5.4 Deadlock and Starvation ⭐ [6.28]
- **Deadlock — two or more processes waiting indefinitely for an event that can be caused only by one of the waiting processes.**
```
S = Q = 1
P0: wait(S); wait(Q); ... signal(S); signal(Q);
P1: wait(Q); wait(S); ... signal(Q); signal(S);
```
  P0 wait(S)、P1 wait(Q) 之後：P0 等 Q（要 P1 signal），P1 等 S（要 P0 signal）→ **deadlock**（extremely difficult to debug）。
- **Starvation (indefinite blocking) — a process may never be removed from the semaphore queue**，例如用 **LIFO order** 或者按 priority 移除 queue 入面嘅 processes。

---

## 6. 做題方法 ✍️⭐⭐⭐

### 6.1 Race condition 所有可能值（F19 Q4.3、F20 Q5）
**步驟**：
1. 將每個 thread 拆成 **atomic reads/writes**（`c = b + a` → read b, read a, write c；**if 條件嘅 read 係另一個 read**！）。
2. 另一個 thread 嘅 writes 可以插喺任何 read 之間（**次序保持**）。
3. 按 **「條件 read 嗰陣見到嘅值」分 branch**，再按「每個 read 見到新值定舊值」分 sub-case。
4. 列出所有 **distinct** 值（唔好漏！每個值獨立計分）。

**F19 Q4.3**：a = 7, b = 2, c = 5；T1：`if (a < 0) c = b - a; else c = b + a;`；T2：`b = 8; a = -6;`
| Case | T1 見到 | c |
|---|---|---|
| T2 全部喺 T1 之前 → a<0 branch | b = 8, a = −6 | 8 − (−6) = **14** |
| else branch；T2 喺 c 計之前完成 | b = 8, a = −6 | 8 + (−6) = **2** |
| else；T2 喺 T1 之後 | b = 2, a = 7 | **9** |
| else；write b 喺 read b 前，write a 喺 read a 後 | b = 8, a = 7 | **15** |
| else；read b 喺 write b 前，write a 喺 read a 前 | b = 2, a = −6 | **−4** |
→ **{14, 2, 9, 15, −4}**

**F20 Q5**：a = 7, b = 2；T1：`if (b < 0) c = b - a; else c = b + a;`；T2：`b = -8; a = 6;`
- b<0 branch（write b 喺條件 read 之前）：a 新 → −8 − 6 = **−14**；a 舊 → −8 − 7 = **−15**
- else branch，第二次 read b 見到新值（−8）：a 新 → −8 + 6 = **−2**；a 舊 → −8 + 7 = **−1**
- else branch，第二次 read b 見到舊值（2）：a 新 → 2 + 6 = **8**；a 舊 → 2 + 7 = **9**
→ **{−14, −15, −2, −1, 8, 9}**

### 6.2 Semaphore 次序（dependency）題（S26 Q5）
**規則**：「X 必須喺 Y 之前完成」→ 用一個 **init 0** 嘅 semaphore s：**X 完成後 `signal(s)`；Y 開始前 `wait(s)`**。每個 dependency edge 一個 semaphore。

**S26 Q5**：A depends on B and C；B depends on C（即 C → B → A，且 C → A）；s0, s1, s2 全部 init 0。
```c
workerA: /*BLANK1*/ wait(&s2);   wait(&s1);  printf("A");          // 等 B (s2) 同 C (s1)
workerB: /*BLANK2*/ wait(&s0);   printf("B");  signal(&s2);        // 等 C (s0)，完成通知 A
workerC: /*BLANK3*/ /* Nothing */ printf("C"); /*BLANK4*/ signal(&s0); signal(&s1);
```
- **BLANK1 = wait(&s2)，BLANK2 = wait(&s0)，BLANK3 = /* Nothing */，BLANK4 = signal(&s0)** → 輸出一定係 **C B A**。

### 6.3 Semaphore 輸出序列題（F19 Q4.4）
```c
semaphore L = 3, R = 0;
P1: while (true) { wait(L); putc('C'); signal(R); }
P2: while (true) { wait(R); putc('A'); putc('B'); signal(R); }
P3: while (true) { wait(R); putc('D'); }
```
**方法：數 token**。L = 3 → **P1 最多印 3 個 C**（冇人 signal L）。每個 C 產生 1 個 R token；**P2 借 token 印 AB 後還返**；**P3 食咗 token 唔還**。
- (a) D 數目 = R token 總數 = **3**
- (b) A：**最少 0**（P3 搶晒 token），**最多 infinite**（P2 無限借還）
- (c) `CABABDCDABCABD` → **No**：印到 `C A B A B D C D` 時 C 印咗 2 次、D 食咗 2 個 token → R = 0，下一個 `A`（P2 需要 wait(R)）冇 token，要等第 3 個 C 先得。
- (d) `CABACDBCABDD` → **Yes**：C(R=1) A(P2 借→0) B(還→1) A(借→0) C(→1) D(食→0) B(還→1) C(→2) A(借→1) B(還→2) D(→1) D(→0) ✓
- **技巧**：逐個字元追蹤 semaphore 值同每個 process「做到邊」；任何時刻 token 唔可以 < 0。

### 6.4 Pthread 程式輸出題（S26 MC23）
```c
int counter = 0; pthread_mutex_t mtx; sem_t sem;   /* sem_init(&sem, 0, 0) */
worker1: lock; counter += 2; printf("A %d;", counter); unlock; sem_post(&sem);
worker2: sem_wait(&sem); lock; counter += 3; printf("B %d;", counter); unlock;
```
- sem 初始 0 → worker2 一定等 worker1 post → **輸出 `A 2; B 5;`**（答案 A）。mutex 保證 counter 更新互斥。

---

## 7. 補充：Peterson（Lab 6）& classic problems（Ch7 預覽）

### 7.1 Peterson's Solution（two processes, software-only；**Lab 6 有教 + 證明**，見 Labs notes L6.1）
```c
int turn; boolean flag[2];          /* Pi uses j = 1 - i */
do {
    flag[i] = true;  turn = j;
    while (flag[j] && turn == j) ;
        /* critical section */
    flag[i] = false;
        /* remainder section */
} while (true);
```
- 滿足 mutual exclusion、progress、bounded waiting（兩個 process）；但 **modern architectures may reorder instructions → not guaranteed to work** without memory barriers。

### 7.2 Classic problems with semaphores（Ch7 預覽）
- **Bounded buffer**：`mutex = 1, full = 0, empty = n`
```c
Producer: wait(empty); wait(mutex); add item; signal(mutex); signal(full);
Consumer: wait(full);  wait(mutex); remove item; signal(mutex); signal(empty);
```
  - ⚠️ 調轉 `wait(mutex)` 同 `wait(empty)` 次序 → 可能 **deadlock**。
- **First readers–writers**：`rw_mutex = 1, mutex = 1, read_count = 0`；第一個 reader `wait(rw_mutex)`，最後一個 reader `signal(rw_mutex)`；writers 可能 **starve**。
- **Condition variables (POSIX)**：`pthread_cond_wait(&cond, &mutex)`（必須持有 mutex；wait 時**釋放 mutex 並 sleep**，醒後**重新 acquire**）；`pthread_cond_signal(&cond)`。

---

## 8. 常見陷阱 & MC 速查

| 敘述 | 真/假 |
|---|---|
| Race condition: outcome depends on order of access | ✅ |
| counter++ is a single atomic machine instruction | ❌ |
| CS requirements: mutual exclusion, progress, bounded waiting | ✅ |
| "Synchronization" is one of the 3 CS requirements | ❌ |
| Bounded waiting implies progress | ✅（summary） |
| Disabling interrupts works well on multiprocessors | ❌（only uniprocessor） |
| Atomic = non-interruptible | ✅ |
| test_and_set returns the new value | ❌（old value） |
| CAS returns old value | ✅ |
| Simple TAS lock satisfies bounded waiting | ❌ |
| Bounded-waiting TAS: waiting process enters within n−1 turns | ✅ |
| test_and_set releases the lock | ❌ |
| Spinlock wastes CPU but avoids context switch | ✅ |
| Spinlocks useful on multiprocessors for short critical sections | ✅ |
| Semaphore accessed only by wait/signal (except init) | ✅ |
| P() = wait, V() = signal | ✅ |
| Binary semaphore = mutex lock (equivalent) | ❌（can be used as one, but more general） |
| Counting semaphore initialized to # of resources | ✅ |
| Blocking semaphore value can be negative = # waiting | ✅ |
| Non-preemptive kernel essentially free of race conditions (uniprocessor) | ✅ |
| LIFO semaphore queue may cause starvation | ✅ |
| Wrong order of wait() on two semaphores may deadlock | ✅ |

---

## 9. Past-paper 題目（Ch6）
- **S26**：MC23（A 2; B 5;）、MC24（test_and_set）、MC25（A 錯）、Q2.1 race condition（4 分）、Q2.4 swap spinlock + 優缺點（4 分）、Q5 semaphore 填空（8 分）
- **F19**：Q4.1 三個條件（4 分）、Q4.2 binary semaphore vs mutex（3 分）、Q4.3 c 可能值（8 分）、Q4.4 semaphore 序列（10 分）
- **F20**：Q5 c 可能值（15 分！）
- **Sp21**：MC mutual exclusion、MC CS 唔需要 synchronization、MC race condition、MC4 TAS entry、Q3.1 compare_and_reset spinlock（4 分）、Q3.2 bounded waiting 改錯（7 分）

---

## 10. 自我測驗
1. 寫出 CS 三個 requirements 嘅定義（英文）。
2. 用 `test_and_set` 寫 lock；點解唔滿足 bounded waiting？
3. 一個 semaphore value = −3 代表咩？（3 個 processes 喺 waiting queue）
4. x = 0；T1：`x = x + 1`；T2：`x = x * 2`（每句 read/write 分開）→ 可能值？（**2**: T1→T2；**1**: T2→T1；**1**: T1 read 0, T2 read 0 & write 0, T1 write 1；**0**: T2 read 0, T1 write 1, T2 write 0 → {0, 1, 2}）
5. 三個 threads 要 A → B → C 次序，用最少 semaphores 寫出來。（s1 = s2 = 0；A; signal(s1) | wait(s1); B; signal(s2) | wait(s2); C）
