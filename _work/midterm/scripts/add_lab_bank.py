"""Append the new past-paper / lab exam questions to the question banks (idempotent)."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
N = r"C:\Code\UST\COMP3511\Midterm_Notes"

LONG = r"""

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
"""

MC = r"""

---

## [Lab4-MC] ch4 | Threads share memory, processes do not
```c
void *child(void *arg) { int *counter = (int *) arg; (*counter)++; return NULL; }
int main() {
    int counter = 0;  pthread_t thread;
    pthread_create(&thread, NULL, child, (void *)&counter);
    pthread_join(thread, NULL);
    printf("%d\n", counter);
    counter = 0;
    pid_t pid = fork();
    if (pid) wait(NULL);
    else { child((void *)&counter); exit(0); }
    printf("%d\n", counter);
}
```
What is the output?
- A. 0 then 0
- B. 1 then 0
- C. 0 then 1
- D. 1 then 1

**Answer: B**

解：thread 同 main 共用 `counter` → 印 1；fork 出嚟嘅 child 改嘅係自己嗰份 copy → parent 印 0。**Threads share memory space, processes have separate memory spaces.**（Lab 4）
"""

for fname, block, marker in (("qb2_long_bank.md", LONG, "## [F22-Q3]"), ("qb1_mc_bank.md", MC, "## [Lab4-MC]")):
    path = N + "\\" + fname
    s = io.open(path, encoding="utf-8").read()
    if marker in s:
        print(fname, "already has the new questions")
        continue
    io.open(path, "w", encoding="utf-8", newline="\n").write(s.rstrip("\n") + "\n" + block)
    print(fname, "appended")
