# Answer Bank — Chapter 6 Synchronization Tools (anticipated questions)

> Conventions used in every answer: a read or write of a single variable is atomic; each thread's statements run in program order; an expression reads its operands left to right; `wait()` and `signal()` are atomic; a process may stay in its remainder section forever. "Bounded waiting" verdicts use the slide definition (number of times other processes enter first). Every possible-value, possible-output and requirement verdict below was checked by exhaustive enumeration of the interleavings (small instances).

## [X6-01] ch6 | Race condition: counter++ / counter-- interleaving
Define a race condition. Using `counter++` (producer) and `counter--` (consumer) with counter = 5, show at the machine level how the result can be wrong. [6.7, 6.9]

**Answer:**
A **race condition** occurs when several processes **access and manipulate shared data concurrently** and the **outcome depends on the particular order** in which the accesses take place. `counter++` and `counter--` are **not atomic**: each becomes **three machine instructions**, and the two sequences can be **interleaved**:
```c
S0: producer  register1 = counter          /* register1 = 5 */
S1: producer  register1 = register1 + 1    /* register1 = 6 */
S2: consumer  register2 = counter          /* register2 = 5 */
S3: consumer  register2 = register2 - 1    /* register2 = 4 */
S4: producer  counter = register1          /* counter = 6   */
S5: consumer  counter = register2          /* counter = 4   */
```
The correct value is 5, but the result is **4** (or **6** if S4 and S5 are swapped): one update is **lost** because both processes read the old value before either stored its result. Fix: make the update a **critical section** executed under **mutual exclusion**.

## [X6-02] ch6 | All possible final values of counter
counter = 5. The producer executes `counter++` once and the consumer executes `counter--` once, concurrently and without synchronization. Give all possible final values of counter.

**Answer:**
**4, 5 or 6.**
- **5**: the two updates do not overlap (one stores before the other loads), which is the correct result.
- **4**: both load 5; the producer stores 6, then the consumer stores 4, so **the increment is lost**.
- **6**: both load 5; the consumer stores 4, then the producer stores 6, so **the decrement is lost**.

No other value is possible: each process stores (the value it loaded) ± 1, and it loads either 5 or the other process's result.

## [X6-03] ch6 | Unprotected counter in a loop: lost updates
In Lab 6 Q3, two threads each execute `++counter` 5,000 times (counter = 0). If the `pthread_mutex_lock()` / `pthread_mutex_unlock()` calls are removed, is the final value still 10,000?

**Answer:**
**No. The result is non-deterministic: any value from 2 to 10,000 is possible** (10,000 only if no update is lost).
- `++counter` is load, add, store; if the other thread stores in between, this thread's store **overwrites (loses)** the other's increments: a **race condition**.
- Worst case 2: T1 loads 0 and is preempted; T2 does 4,999 increments; T1 stores 1; T2 loads 1 and is preempted; T1 does its other 4,999 increments; T2 stores 2.
- With the mutex, `++counter` is a **critical section** executed under mutual exclusion, so the result is always **10,000**.

## [X6-04] ch6 | Race condition inside the kernel
Give an example of a race condition in the kernel. Which kernel data structures must be protected? [6.8, 6.12]

**Answer:**
- Processes **P0 and P1 call `fork()` at the same time**. Both read the kernel variable **`next_available_pid`** before either one updates it, so **the same pid could be assigned to two different processes**, unless updates of the variable are mutually exclusive.
- Other kernel data structures subject to race conditions: the **list of open files** (two processes open files simultaneously), structures for **memory allocation**, the **process list / process table**, and **interrupt handling**.
- How the kernel protects them depends on whether it is **preemptive or non-preemptive**.

## [X6-05] ch6 | Critical section; entry, exit, remainder sections
What is a critical section? Describe the general structure of a process in the critical-section problem. [6.9–6.10]

**Answer:**
A **critical section** is a segment of code in which a process **accesses or updates shared data** (changing shared variables, updating a table, writing a file), so a race condition may occur. The **critical-section problem** is to design a **protocol** such that **when one process is executing in its critical section, no other process is executing in its critical section**.
```c
do {
    entry section       /* request permission to enter */
        critical section
    exit section        /* give up permission, let others in */
        remainder section
} while (true);
```
- **Entry section**: requests permission (e.g., `acquire()`, `wait(mutex)`).
- **Exit section**: releases it (e.g., `release()`, `signal(mutex)`); the **remainder section** is the rest of the code.

## [X6-06] ch6 | Three requirements with violation examples
State the three requirements a solution to the critical-section problem must satisfy, and give one way each can be violated. [6.11]

**Answer:**
1. **Mutual exclusion**: if process $P_i$ is executing in its critical section, **no other process can be executing in its critical section**. *Violated by:* `counter++` without a lock, or a lock whose test and set are not atomic.
2. **Progress**: if no process is in its critical section and some processes wish to enter, **the selection of the process that enters next cannot be postponed indefinitely** (a process in its remainder section must not block the others). *Violated by:* strict alternation with `turn`, or a deadlock in the entry section.
3. **Bounded waiting**: **a bound must exist on the number of times other processes are allowed to enter their critical sections after a process has made a request to enter and before that request is granted** (no starvation). *Violated by:* the simple test_and_set lock.

Mutual exclusion is a **safety** property (no wrong results); progress and bounded waiting are **liveness** properties. Assumption: each process executes at a **nonzero speed**, with **no assumption about the relative speed** of the processes.

## [X6-07] ch6 | Preemptive vs non-preemptive kernels
Compare preemptive and non-preemptive kernels with respect to race conditions. Why might a preemptive kernel still be preferred? [6.12]

**Answer:**
- **Preemptive kernel**: allows a process to be **preempted while it is running in kernel mode**, so it is **not free from race conditions** on kernel data, and it is increasingly difficult to design on **SMP** architectures.
- **Non-preemptive kernel**: a kernel-mode process **runs until it exits kernel mode, blocks, or voluntarily yields the CPU**, so on a **single processor** only one process is active in the kernel at a time: it is **essentially free of race conditions in kernel mode** (on a multiprocessor, processes on different CPUs can still be in the kernel at the same time).
- A preemptive kernel is still preferred because it is **more responsive** (no kernel-mode process can run for an arbitrarily long time while others wait) and **more suitable for real-time** processes.

## [X6-08] ch6 | Disabling interrupts: uniprocessor vs multiprocessor
Can the critical-section problem be solved by disabling interrupts? Answer for uniprocessor and multiprocessor systems. [6.13]

**Answer:**
- **Uniprocessor: yes.** With interrupts disabled while the shared data is modified, the current code **executes without being preempted or interrupted**, so its instructions run in order without interleaving.
- **Multiprocessor / SMP: no, it is generally inefficient.** Disabling interrupts on one CPU **does not stop the other CPUs** from entering their critical sections; disabling them on **all** CPUs requires a message to every processor, which is **time-consuming, delays entry into each critical section and decreases system efficiency** (it also disturbs a system clock that is updated by timer interrupts).
- Disabling interrupts is also a **privileged** operation and is unsafe to give to user programs, so systems use **atomic hardware instructions** (test_and_set, compare_and_swap) and the locks built on them.

## [X6-09] ch6 | Peterson's solution: code and assumption (Lab 6)
Write Peterson's solution for two processes $P_i$ and $P_j$. Explain the shared variables and the assumption it relies on.

**Answer:**
```c
int turn;                          /* shared: whose turn it is      */
boolean flag[2] = {false, false};  /* shared: flag[i] = Pi wants in */

do {                               /* process Pi, j = 1 - i */
    flag[i] = true;                /* I want to enter ...         */
    turn = j;                      /* ... but you may go first    */
    while (flag[j] && turn == j)
        ;                          /* busy wait */
    /* critical section */
    flag[i] = false;               /* I have left */
    /* remainder section */
} while (true);
```
- **`flag[i] == true`** means $P_i$ is ready (wants) to enter its critical section; **`turn`** decides which process enters when both want to.
- It is a **software-only** solution, **restricted to two processes**, and it assumes that **load and store instructions are atomic** (a variable is never read half-written); otherwise the correctness proof does not hold.

## [X6-10] ch6 | Peterson satisfies all three requirements
Prove that Peterson's solution satisfies mutual exclusion, progress and bounded waiting.

**Answer:**
- **Mutual exclusion**: $P_i$ enters only if `flag[j] == false` or `turn == i`. If both try, `flag[0] == flag[1] == true`, and `turn` is **either 0 or 1, not both**, so only one process can pass its while loop (the one that wrote `turn` last waits).
- **Progress**: $P_i$ is stuck only while `flag[j] == true && turn == j`. If $P_j$ does not want to enter, `flag[j] == false` and $P_i$ **enters immediately**; if both want to enter, `turn` admits one of them at once.
- **Bounded waiting**: when $P_j$ leaves, it sets `flag[j] = false`; if it wants to re-enter, it must set `turn = i`, and $P_i$ does not change `turn` while waiting, so **$P_i$ enters after at most one entry by $P_j$**.

## [X6-11] ch6 | Peterson on modern hardware: memory barriers
Why is Peterson's solution not guaranteed to work on modern computer architectures? How can it be fixed, and what are its other drawbacks?

**Answer:**
- To improve performance, **processors and/or compilers may reorder read and write operations that have no dependencies**. Peterson's entry section writes `flag[i]` and `turn` and then reads `flag[j]`, all different variables. If the two writes are reordered, or $P_i$'s read happens before its own write becomes visible to $P_j$, **both processes can be in their critical sections at the same time**.
- Fix: a **memory barrier (memory fence)**, an instruction that forces all earlier loads and stores to complete and become visible to other processors before any later load or store. Alternatively, use **sequentially consistent atomic operations**; the Lab 6 code uses `atomic_store_explicit(&flag[i], true, memory_order_seq_cst)`.
- Other drawbacks: it is **complex even for two processes**, each thread needs **different code**, and it uses **busy waiting** (wastes CPU cycles). This is why the OS provides **mutex locks, semaphores and condition variables**.

## [X6-12] ch6 | Atomic hardware instructions
What does "atomic" mean? Why are atomic hardware instructions useful for synchronization, and why can't every operation simply be made atomic? [6.14]

**Answer:**
- **Atomic = non-interruptible**: the instruction (possibly several machine-level steps, e.g., read and write a word) **executes as one unit that cannot be interrupted**, so **no race condition can occur inside it**. If two such instructions run **simultaneously on different cores**, they are **executed sequentially in some order (serialization)**.
- They are the **building blocks** of more sophisticated tools (spinlocks, mutex locks, semaphores, atomic variables). The two common ones are **`test_and_set()`** (test a memory word and set it) and **`compare_and_swap()`** (compare a word with an expected value and, if equal, swap in a new value).
- Not everything can be atomic: hardware instructions work on **a single word / simple variable**. A **complex data structure** (a linked list, a 1000 × 1000 matrix) cannot be updated by one atomic instruction, so **locks and semaphores** built on these instructions protect larger critical sections.

## [X6-13] ch6 | test_and_set(): definition, lock, bounded waiting
Give the definition of `test_and_set()`, use it to implement mutual exclusion, and state which requirement the solution does not satisfy. [6.15–6.16]

**Answer:**
```c
boolean test_and_set(boolean *target) {  /* executed atomically */
    boolean rv = *target;
    *target = TRUE;
    return rv;                           /* returns the OLD value */
}
boolean lock = FALSE;                    /* shared */
do {
    while (test_and_set(&lock))
        ;                                /* spin: lock was held */
    /* critical section */
    lock = FALSE;
    /* remainder section */
} while (true);
```
- **Mutual exclusion holds**: the first caller gets FALSE (lock free) and enters; the same atomic call sets `lock = TRUE`, so every other caller gets TRUE and spins until `lock = FALSE`. **Progress** also holds.
- **Bounded waiting is NOT satisfied**: when the lock is released, **whichever spinning process executes `test_and_set()` first wins**. There is no order, so an unlucky process can lose every time (starvation). The **waiting[]-array version** fixes this.

## [X6-14] ch6 | compare_and_swap(): definition and lock
Give the definition of `compare_and_swap()` and use it to implement a lock. Why is the loop condition `!= 0`? [6.17–6.18]

**Answer:**
```c
int compare_and_swap(int *value, int expected, int new_value) {
    int temp = *value;                   /* executed atomically */
    if (*value == expected)
        *value = new_value;
    return temp;                         /* always the OLD value */
}
int lock = 0;                            /* 0 = free, 1 = held */
do {
    while (compare_and_swap(&lock, 0, 1) != 0)
        ;                                /* spin */
    /* critical section */
    lock = 0;
    /* remainder section */
} while (true);
```
- `compare_and_swap(&lock, 0, 1)` sets lock to 1 **only if it is 0** and returns the **old** value. A return of **0** means the lock was free and **this process has just taken it**, so it enters; a return of **1** means the lock is held (and unchanged), so it keeps spinning. Hence `!= 0`.
- It satisfies **mutual exclusion and progress**, but **not bounded waiting** (the same race as test_and_set).
- Wrong versions: `== 0` (inverted test) and `compare_and_swap(&lock, 1, 0)` (never sets the lock) both let two processes in.

## [X6-15] ch6 | Bounded-waiting TAS: waiting[], key, lock
In the algorithm below, explain the roles of `waiting[]`, `key` and `lock`, and why the exiting process sets `waiting[j] = false` instead of `lock = false`. [6.19]
```c
/* shared: boolean waiting[n] (all false), lock = false;  local: key, j */
do {
    waiting[i] = true;
    key = true;
    while (waiting[i] && key)
        key = test_and_set(&lock);
    waiting[i] = false;
    /* critical section */
    j = (i + 1) % n;
    while ((j != i) && !waiting[j])
        j = (j + 1) % n;
    if (j == i)
        lock = false;        /* no one is waiting, so release the lock */
    else
        waiting[j] = false;  /* unblock process j */
    /* remainder section */
} while (true);
```

**Answer:**
- **`waiting[i] == true`**: $P_i$ **wants to enter** its critical section and is waiting in its entry section.
- **`key`** (local) holds the value returned by `test_and_set(&lock)`; **`key == false`** means $P_i$ found the lock free and **acquired it itself**. **`lock`** is TRUE while some process owns the critical section.
- $P_i$ leaves the entry loop when **`key == false`** (it took the free lock) **or `waiting[i] == false`** (another process **handed the lock to it**).
- On exit, `waiting[j] = false` means **$P_i$ releases the lock by handing it directly to the next waiting $P_j$, while `lock` stays TRUE**, so no other process can grab it with test_and_set in between. Because the scan is **cyclic** (i+1, …, n−1, 0, …, i−1), every waiting process gets in **within n − 1 turns**. `lock = false` is executed only when **nobody is waiting**.

## [X6-16] ch6 | Bounded-waiting TAS: sketch proof
Give a sketch proof that the bounded-waiting `test_and_set()` algorithm satisfies mutual exclusion, progress and bounded waiting. [6.20]

**Answer:**
- **Mutual exclusion**: $P_i$ enters only if `waiting[i] == false` or `key == false`. `key` becomes false only by executing `test_and_set()`, and **only the first process to execute it finds key == false**; all others must wait. `waiting[i]` becomes false only when another process **leaves its critical section**, and **only one** `waiting[j]` is set to false per exit. So at most one process is in its critical section.
- **Progress**: a process exiting its critical section **either sets `lock = false` or sets `waiting[j] = false`**; both allow a waiting process to proceed.
- **Bounded waiting**: the exiting process scans `waiting[]` in **cyclic order {i+1, i+2, …, n−1, 0, 1, …, i−1}** and designates the **first** waiting process as the next to enter, so any waiting process enters **within n − 1 turns**.

## [X6-17] ch6 | Broken variants of the bounded-waiting algorithm
In the bounded-waiting TAS algorithm, which requirement fails if (a) the whole exit section is just `lock = false;`, or (b) the exit scan always starts from index 0 instead of i + 1?

**Answer:**
- (a) **Bounded waiting fails** (mutual exclusion and progress still hold). The lock is never handed over, so the algorithm becomes the **simple test_and_set spinlock**: whichever process executes test_and_set first after the release wins, and a process can be overtaken indefinitely.
- (b) **Bounded waiting fails** for n ≥ 3 (mutual exclusion and progress still hold). The exiting process always prefers **low-index** waiters, e.g., $P_0$ and $P_1$ can keep handing the lock to each other while $P_2$ waits forever.
- Correct exit: start at `j = (i + 1) % n`, scan **cyclically**, and execute `lock = false` **when j == i** (nobody waiting). If the lock is never released when nobody waits, progress fails.

## [X6-18] ch6 | Atomic variables: increment() with CAS
What is an atomic variable? Implement `increment()` on an atomic integer using `compare_and_swap()`, and explain why a loop is needed. [6.21]

**Answer:**
An **atomic variable** provides **atomic (uninterruptible) updates on basic data types such as integers and Booleans**; e.g., `increment(&sequence)` increments `sequence` **without interruption**. It is built on compare_and_swap:
```c
void increment(atomic_int *v) {
    int temp;
    do {
        temp = *v;                       /* read the current value */
    } while (temp != compare_and_swap(v, temp, temp + 1));
}
```
- CAS writes `temp + 1` **only if `*v` still equals `temp`**, i.e., no other thread changed `v` since it was read. Because CAS returns the old value, the update succeeded exactly when the return value equals `temp`.
- If another thread changed `v` in between, nothing is written and the loop **retries with the new value**, so **no update is lost** and no lock is needed. Atomic variables protect only a **single variable**; larger critical sections still need locks.

## [X6-19] ch6 | Mutex lock: why acquire() must be atomic
Give the mutex-lock `acquire()` / `release()` code. Why must `acquire()` be atomic? Show what can go wrong otherwise. [6.22–6.23]

**Answer:**
```c
acquire() {                      release() {
    while (!available)               available = true;
        ;   /* busy wait */      }
    available = false;
}
do {
    acquire lock;     critical section;
    release lock;     remainder section;
} while (true);
```
- A process **acquires the lock before entering** its critical section and **releases it when it exits**; the Boolean `available` indicates whether the lock is free.
- If `acquire()` were not atomic, its **test** and **set** could interleave: T1 sees `available == true`, T2 also sees `available == true`, both set it to false and **both enter the critical section**, violating mutual exclusion. So acquire() and release() are implemented with **hardware atomic instructions** (e.g., compare_and_swap).
- The waiting process loops in `while (!available)`, i.e., **busy waiting**, so this lock is called a **spinlock**.

## [X6-20] ch6 | Spinlocks: when to use, not on uniprocessors
When are spinlocks preferable to blocking (sleeping) locks? Why is a spinlock a poor choice on a single-processor system? [6.22]

**Answer:**
- Spinlocks are preferable on **multiprocessor (multicore) systems when locks are held for short times**: a waiting thread **spins on one processor** while the lock holder runs its short critical section **on another processor** and releases the lock soon. **No context switch is required**, and a context switch may take considerable time (rule of thumb: spin if the lock is held for less than the time of two context switches).
- On a **single processor**, the spinning thread occupies the only CPU, so **the lock holder cannot run to release the lock** until the spinner is preempted, and the spinner **wastes its whole time slice**. It should **block (sleep)** instead.
- Likewise, if the wait may be **long**, a thread should block rather than spin, because **busy waiting wastes CPU cycles**.

## [X6-21] ch6 | Semaphore: definition, wait/signal, P and V
Define a semaphore and its two operations (busy-waiting definition). What do P and V stand for? [6.24]

**Answer:**
A **semaphore S** is an **integer variable** (a **generalized lock**, introduced by **Dijkstra**, and the main synchronization primitive of the original UNIX) that, **apart from initialization, is accessed only through two standard atomic operations: `wait()` and `signal()`**, originally **P()** (*proberen*, "to test") and **V()** (*verhogen*, "to increment").
```c
wait(S) {                    signal(S) {
    while (S <= 0)               S++;
        ;  /* busy wait */   }
    S--;
}
```
- `wait(S)`: while S ≤ 0 the process waits; then it **decrements S** (takes a permit). `signal(S)`: **increments S** (returns a permit).
- Both must be executed **atomically**: no two processes may execute wait() or signal() on the same semaphore at the same time (**serialization**).

## [X6-22] ch6 | Why wait() and signal() must be atomic
Why must `wait()` and `signal()` be executed atomically? How is this guaranteed on uniprocessor and multiprocessor systems?

**Answer:**
- Otherwise two processes could **both test `S > 0` (e.g., S = 1) before either decrements it**, so **both pass `wait()`** and enter the critical section (mutual exclusion violated); S can even end at −1, or an update of S can be lost. Hence **no two processes may execute wait()/signal() on the same semaphore at the same time**; this is itself a critical-section problem.
- **Uniprocessor**: **disable interrupts** while wait() and signal() execute, so their instructions cannot be interleaved.
- **Multiprocessor (SMP)**: disabling interrupts on every core is difficult and slow, so wait() and signal() are protected with **atomic hardware instructions: compare_and_swap() or spinlocks**. Busy waiting is not eliminated entirely, but it is limited to these **very short** code sections instead of the application's critical section.

## [X6-23] ch6 | Counting vs binary semaphore; semaphore vs mutex
Distinguish counting and binary semaphores, and explain how a semaphore differs from a mutex lock. [6.25]

**Answer:**
- **Counting semaphore**: its integer value ranges over an **unrestricted domain**. It controls access to a resource with a **finite number of instances** and is **initialized to the number of resources available** (`wait()` takes an instance, `signal()` returns one).
- **Binary semaphore**: its value is **only 0 or 1**. Initialized to **1**, it **behaves like a mutex lock**, but it can also be used in other ways, e.g., initialized to **0** to **enforce an execution order** (S1 before S2).
- **Semaphore vs mutex lock**: a mutex lock has a **binary value** (available or not) and is used only for **mutual exclusion**; a semaphore has an **integer value** (a generalized lock) that can also **count resources** and **signal events / enforce order** between processes. (A Pthreads mutex should be unlocked by the thread that locked it, whereas any thread may `sem_post()` a semaphore.)

## [X6-24] ch6 | Mutual exclusion with a semaphore: initial value
Show how a semaphore provides mutual exclusion among n processes. What happens if it is initialized to 0 or to 2 instead of 1?

**Answer:**
```c
semaphore mutex = 1;          /* shared */
do {
    wait(mutex);
        /* critical section */
    signal(mutex);
        /* remainder section */
} while (true);
```
- **Initialized to 1**: the first `wait()` takes the only permit (mutex = 0) and all others **block** until `signal(mutex)`, so **at most one process is in its critical section**.
- **Initialized to 0**: there is no permit, so **no process can ever enter**; all of them block forever (deadlock).
- **Initialized to 2**: **two processes can be in their critical sections at the same time**, violating mutual exclusion.

## [X6-25] ch6 | Ordering S1 before S2 (synch = 0)
Processes P1 and P2 run concurrently. Use a semaphore to guarantee that statement S1 (in P1) executes before statement S2 (in P2). Why must it be initialized to 0? [6.25]

**Answer:**
```c
semaphore synch = 0;
P1:   S1;  signal(synch);
P2:   wait(synch);  S2;
```
- If P2 reaches `wait(synch)` first, synch is 0, so **P2 blocks** until P1 finishes S1 and calls `signal(synch)`. If P1 runs first, synch becomes 1 and P2 passes `wait()` immediately, but S1 is already done. **Either way S2 starts only after S1 completes.**
- If synch were initialized to **1**, P2 could pass `wait()` before S1 runs, so the order would not be enforced.
- General rule: **"X before Y" needs a semaphore initialized to 0, with `signal()` right after X and `wait()` right before Y.**

## [X6-26] ch6 | Counting semaphore: at most k users
A server has 3 identical database connections, so at most 3 threads may use them at the same time. Write the synchronization with a semaphore. What happens if 5 threads request a connection together?

**Answer:**
```c
semaphore conn = 3;     /* number of available instances */
wait(conn);             /* take a connection (block if none left) */
    /* use the connection */
signal(conn);           /* return it, waking one waiter if any */
```
- A **counting semaphore initialized to k (the number of instances)** lets **at most k** threads pass `wait()` until someone calls `signal()`.
- With 5 requests, **3 proceed and 2 block**; in the waiting-queue implementation conn = **−2** (2 waiting). Each `signal()` wakes one waiter.
- It limits the number of users to k but gives **no mutual exclusion among them**; shared data that they update still needs a separate **mutex initialized to 1**.

## [X6-27] ch6 | Rendezvous and barrier with semaphores
Threads A and B: a1 must execute before b2, and b1 before a2 (a rendezvous). Give a semaphore solution, then extend it to a barrier for n threads.

**Answer:**
```c
semaphore aArrived = 0, bArrived = 0;
A:   a1;  signal(aArrived);  wait(bArrived);  a2;
B:   b1;  signal(bArrived);  wait(aArrived);  b2;
```
- Each thread **signals its own arrival first, then waits for the other**, so neither second statement starts before both first statements finish. If **both wait before signalling**, each waits for a signal that is never sent: **deadlock**.
- **Barrier for n threads** (no thread passes until all n have arrived):
```c
int count = 0;  semaphore mutex = 1, barrier = 0;
wait(mutex);
count++;
if (count == n) signal(barrier);   /* the last to arrive opens it */
signal(mutex);
wait(barrier);
signal(barrier);                   /* turnstile: let the next one through */
/* critical point: all n threads have arrived */
```

## [X6-28] ch6 | Semaphore without busy waiting: block() and wakeup()
How can a semaphore be implemented without busy waiting? Give the code and explain `block()` and `wakeup()`. [6.26–6.27]

**Answer:**
Each semaphore has an integer **value** and a **waiting queue** (a list of processes):
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
- **`block()`** suspends the calling process and places it on the semaphore's **waiting queue** (running → waiting) instead of spinning, so **no CPU time is wasted**. **`wakeup(P)`** removes P from the waiting queue and places it on the **ready queue**; `signal()` calls it only if value ≤ 0 after the increment, i.e., someone is waiting.
- The decrement/increment is done **before** the value is tested (unlike the busy-waiting version), so the value **can become negative**, and **its magnitude is the number of processes waiting** on the semaphore.
- Better than busy waiting when waits can be **long**; the spinning version is better only for **very short** waits on multiprocessors (no context switch).

## [X6-29] ch6 | Tracing a semaphore value with a waiting queue
A semaphore S (waiting-queue implementation) is initialized to 2. Five processes call `wait(S)`, and then another process calls `signal(S)` twice. What is the value of S, and how many processes are still blocked?

**Answer:**
**S = −1, and one process is still blocked.**
- Five waits: $2 - 5 = -3$, so the first **two** processes pass and **three** are blocked in the queue ($|-3| = 3$).
- Two signals: $-3 + 2 = -1$; each signal finds the value ≤ 0 and **wakes one** blocked process (moves it to the ready queue), so **one** remains blocked ($|-1| = 1$).
- Rule: S ≥ 0 means S permits are free and nobody waits; S < 0 means no permit is free and $|S|$ processes are waiting.

## [X6-30] ch6 | Deadlock with two semaphores
S and Q are semaphores initialized to 1. Show how P0 and P1 below can deadlock, and how to prevent it. [6.28]
```c
P0: wait(S);  wait(Q);  ...  signal(S);  signal(Q);
P1: wait(Q);  wait(S);  ...  signal(Q);  signal(S);
```

**Answer:**
- **Deadlock**: two or more processes are **waiting indefinitely for an event that can be caused only by one of the waiting processes**.
- P0 executes `wait(S)` and then P1 executes `wait(Q)`. When P0 executes `wait(Q)`, it must wait until P1 executes `signal(Q)`; but P1 is waiting in `wait(S)` until P0 executes `signal(S)`. Since **these signal() operations can never be executed, P0 and P1 are deadlocked**. It happens only under some interleavings, so it is **extremely difficult to debug**.
- Prevention: make **every process acquire the semaphores in the same order** (e.g., both execute `wait(S); wait(Q);`), so a circular wait cannot form.

## [X6-31] ch6 | Starvation (indefinite blocking) vs deadlock
What is starvation in the context of semaphores, and how does it differ from deadlock? [6.28]

**Answer:**
- **Starvation (indefinite blocking)**: a process **may never be removed from the semaphore queue in which it is suspended**, e.g., if processes are removed from the queue in **LIFO (last-in, first-out) order or by priority**, newer or higher-priority processes can always be chosen ahead of it.
- Remedy: remove waiting processes in **FIFO order**, so every waiting process is eventually woken.
- **Deadlock**: a set of processes all wait for each other and **none can proceed**. **Starvation**: the system keeps running and **other processes make progress**, but one process waits forever. Both are **liveness** failures, and a deadlock-free system can still suffer starvation.

## [X6-32] ch6 | Verdict table for classic CS protocols
For each entry/exit protocol (two processes with j = 1 − i, unless noted), state whether mutual exclusion (ME), progress and bounded waiting (BW) hold.

**Answer:**
| Protocol (entry … exit) | ME | Progress | BW | Reason |
|---|---|---|---|---|
| `while (turn != i);` … `turn = j;` | Yes | **No** | Yes¹ | strict alternation: a process in its remainder section blocks the other |
| `while (flag[j]); flag[i] = true;` … `flag[i] = false;` | **No** | Yes | **No** | both test before either sets its flag |
| `flag[i] = true; while (flag[j]);` … `flag[i] = false;` | Yes | **No** | Yes¹ | both set their flags, then both wait forever (deadlock) |
| Peterson: `flag[i] = true; turn = j; while (flag[j] && turn == j);` … `flag[i] = false;` | Yes | Yes | Yes | `turn` breaks the tie; at most one overtake |
| Peterson with `turn = j;` and `flag[i] = true;` swapped | **No** | Yes | **No** | both can slip through |
| `while (test_and_set(&lock));` … `lock = false;` | Yes | Yes | **No** | any spinning process may win; starvation |
| `while (compare_and_swap(&lock, 0, 1) != 0);` … `lock = 0;` | Yes | Yes | **No** | same race as test_and_set |
| Bounded-waiting TAS (`waiting[]`, cyclic scan), n processes | Yes | Yes | Yes | lock handed to the next waiter: ≤ n − 1 turns |
| `acquire()` whose test and set are not atomic | **No** | Yes | **No** | both see `available == true` |

¹ Yes by the slide definition (the number of entries by others is bounded: at most one with strict alternation, none when each process sets its flag before testing), but the waiting time is still unbounded because progress fails.

## [X6-33] ch6 | Strict alternation using only turn
Shared `int turn = 0;` Process $P_i$ (j = 1 − i): `do { while (turn != i); /* CS */ turn = j; /* remainder */ } while (true);` Does this solve the critical-section problem?

**Answer:**
**No. It satisfies mutual exclusion but violates progress.**
- **Mutual exclusion: yes.** $P_i$ enters only when `turn == i`, and `turn` has a single value, so only one process can be in its critical section.
- **Progress: no.** It forces **strict alternation**: if `turn == 1` and $P_1$ stays in its **remainder section** (does not want to enter), $P_0$ **cannot enter although the critical section is free**; the decision is postponed indefinitely by a process that is not even competing.
- **Bounded waiting: yes by the definition.** After $P_i$ requests, $P_j$ can enter **at most once** before `turn` passes to $P_i$; but $P_i$ still waits forever if $P_j$ never returns (the progress failure).

## [X6-34] ch6 | Flag checked before it is set
Shared `boolean flag[2] = {false, false};` Process $P_i$: `while (flag[j]); flag[i] = true; /* CS */ flag[i] = false;` Which requirements hold?

**Answer:**
**Mutual exclusion is violated, so it is not a solution.**
- Interleaving: $P_0$ tests `flag[1]` (false) and passes; before $P_0$ sets `flag[0]`, $P_1$ tests `flag[0]` (false) and passes; both set their flags and **both enter the critical section**. The **test and the set are not one atomic step**.
- **Progress holds**: a process waits only while the other's flag is up, i.e., while the other is in its critical section, and the flag is cleared on exit.
- **Bounded waiting fails**: $P_i$ raises its flag only after passing the test, so its request is invisible; $P_j$ can leave and re-enter any number of times while $P_i$ keeps seeing `flag[j] == true`.

## [X6-35] ch6 | Flag set before checking: deadlock
Shared `boolean flag[2] = {false, false};` Process $P_i$: `flag[i] = true; while (flag[j]); /* CS */ flag[i] = false;` Which requirements hold?

**Answer:**
**Mutual exclusion holds, but progress is violated: the processes can deadlock.**
- **Mutual exclusion**: each process raises its flag **before** testing the other's, so if both are interested, the one that raises its flag later sees the other's flag and waits; they cannot both enter.
- **Progress: no.** $P_0$ sets `flag[0] = true`, then $P_1$ sets `flag[1] = true`; now **each waits for the other's flag to become false, forever** (deadlock), although the critical section is empty.
- **Bounded waiting**: neither process can overtake one whose flag is up, but after a deadlock the waiting time is unbounded. Peterson's `turn` variable breaks exactly this tie.

## [X6-36] ch6 | Peterson variants that break mutual exclusion
In Peterson's solution, what happens if (a) `flag[i] = true;` and `turn = j;` are swapped, or (b) a process sets `turn = i;` instead of `turn = j;`?

**Answer:**
**Both versions violate mutual exclusion** (progress still holds; bounded waiting is lost).
- (a) `turn = j; flag[i] = true;`: $P_0$ sets `turn = 1`; $P_1$ sets `turn = 0`, sets `flag[1] = true`, finds `flag[0] == false` and **enters**; $P_0$ sets `flag[0] = true`, finds `turn == 0` (not 1) and **enters**. Both are in their critical sections. This is exactly what **instruction reordering** can do to the correct code, hence **memory barriers**.
- (b) `turn = i`: $P_0$ sets `flag[0] = true; turn = 0;`, finds `flag[1] == false` and **enters**; $P_1$ sets `flag[1] = true; turn = 1;`, finds `turn == 1` (not 0) and **enters**. Both are in their critical sections.
- Correct rule: **raise your own flag first, then give the turn to the other process** (`turn = j`); whoever writes `turn` last waits.

## [X6-37] ch6 | Semaphores for a precedence graph
Six concurrent processes P1–P6 execute statements S1–S6 with precedence S1→S2, S1→S3, S2→S4, S3→S4, S3→S5, S4→S6, S5→S6. Enforce it with semaphores and give their initial values.

**Answer:**
**Rule:** for each edge X → Y use a semaphore **initialized to 0**; X calls `signal()` **after** it finishes, and Y calls `wait()` **before** it starts. Compactly, use **one semaphore per statement that has predecessors**, waited on **once per incoming edge**:
```c
semaphore s2 = 0, s3 = 0, s4 = 0, s5 = 0, s6 = 0;
P1:                         S1;  signal(s2); signal(s3);
P2:  wait(s2);              S2;  signal(s4);
P3:  wait(s3);              S3;  signal(s4); signal(s5);
P4:  wait(s4); wait(s4);    S4;  signal(s6);   /* after S2 and S3 */
P5:  wait(s5);              S5;  signal(s6);
P6:  wait(s6); wait(s6);    S6;                /* after S4 and S5 */
```
- All semaphores start at **0**, so no statement can start before every predecessor has signalled; S1 needs no wait.
- The possible execution orders are exactly the topological orders **123456, 123546, 132456, 132546, 135246**, and no execution deadlocks.
- Equivalent per-edge version: 7 semaphores (e12, e13, e24, e34, e35, e46, e56), e.g., P4: `wait(e24); wait(e34); S4; signal(e46);`.

## [X6-38] ch6 | Strict alternation of threads with semaphores
Thread A prints "ping" and thread B prints "pong" in infinite loops. Make the output strictly alternate, starting with ping. Generalize to k threads in a fixed cyclic order.

**Answer:**
```c
semaphore ping = 1, pong = 0;
A:  while (true) { wait(ping);  print("ping");  signal(pong); }
B:  while (true) { wait(pong);  print("pong");  signal(ping); }
```
- **Exactly one permit circulates**: ping = 1 lets A go first; each thread waits on its own semaphore and signals the **next** thread's, so the output is always ping pong ping pong ….
- **k threads T1 → T2 → … → Tk → T1**: one semaphore per thread, **the first initialized to 1 and all others to 0**; each Ti executes `wait(own semaphore); critical section; signal(next thread's semaphore);`, and Tk signals T1's semaphore.
- If two semaphores started at 1, two threads could run together; if all started at 0, the threads would deadlock.

## [X6-39] ch6 | Fill in the blanks: TAS, CAS, increment
Fill in the blanks (`lock` is initially false / 0):
```c
/* (a) */  while (__1__) ;          /* critical section */   __2__;
/* (b) */  while (compare_and_swap(&lock, __3__, __4__) __5__ 0) ;
           /* critical section */   __6__;
/* (c) */  void increment(atomic_int *v) {
               int temp;
               do { temp = __7__; } while (temp != __8__);
           }
```

**Answer:**
- **1** `test_and_set(&lock)` · **2** `lock = false`
- **3** `0` · **4** `1` · **5** `!=` · **6** `lock = 0`
- **7** `*v` · **8** `compare_and_swap(v, temp, temp + 1)`
- Reason: both instructions **return the old value**. A process has the lock exactly when the old value was **free (false / 0)**, so it spins **while** the returned value says "held"; release is an ordinary store of the free value.

## [X6-40] ch6 | Spinlock from a new instruction: fetch_and_add
`fetch_and_add(int *x, int a)` atomically adds a to `*x` and returns the old value of `*x`. Use it to build a spinlock that also satisfies bounded waiting.

**Answer:**
A **ticket lock**: each process takes a ticket and waits until its number is served.
```c
int next_ticket = 0, now_serving = 0;          /* shared */
void acquire() {
    int my = fetch_and_add(&next_ticket, 1);   /* unique ticket */
    while (now_serving != my)
        ;                                      /* spin */
}
void release() {
    fetch_and_add(&now_serving, 1);            /* serve the next ticket */
}
```
- **Mutual exclusion**: `fetch_and_add()` is atomic, so tickets are **unique**, and only the process whose ticket equals `now_serving` may enter. **Progress**: each release serves the next ticket, and a newcomer with no one waiting gets in at once.
- **Bounded waiting**: processes enter in **ticket (FIFO) order**, so a waiting process is overtaken **at most n − 1 times**.
- General recipe for any atomic instruction: find the return value that means "I got the lock", spin while the instruction does not return it, and release by storing the free value (e.g., `while (swap(locked, 1) == 1) ;` then `locked = 0;`).

## [X6-41] ch6 | Possible values of c: worked example
Shared `int a = 3, b = 5, c = 0;` Thread 1: `if (a > 0) c = a + b; else c = b - a;` Thread 2: `a = -1; b = 10;` Reads and writes are atomic, each thread's order is preserved, and expressions read their operands left to right. Give all possible final values of c.

**Answer:**
**c ∈ {4, 6, 8, 9, 11, 13}.**
Method: split Thread 1 into atomic steps (**read a for the condition**, then the branch's reads in order, then **write c**). Thread 2's writes keep their order (`a = -1` before `b = 10`) but may fall into any gap. Branch on what each read sees:

| Branch | Where Thread 2's writes fall | Thread 1 reads | c |
|---|---|---|---|
| then (condition saw a = 3) | both after Thread 1 | a = 3, b = 5 | 3 + 5 = **8** |
| then | `a = -1` before the 2nd read of a; `b = 10` after the read of b | a = −1, b = 5 | −1 + 5 = **4** |
| then | both before the 2nd read of a | a = −1, b = 10 | −1 + 10 = **9** |
| then | both between the 2nd read of a and the read of b | a = 3, b = 10 | 3 + 10 = **13** |
| else (condition saw a = −1) | `b = 10` after the read of b | b = 5, a = −1 | 5 − (−1) = **6** |
| else | `b = 10` before the read of b | b = 10, a = −1 | 10 − (−1) = **11** |

Check: in the else branch a is already −1, so only b varies (2 values); in the then branch all four pairs a ∈ {3, −1}, b ∈ {5, 10} are reachable (4 values); 6 values in total.

## [X6-42] ch6 | Can both threads read 0?
Shared `x = 0, y = 0;` T1: `x = 1; r1 = y;` T2: `y = 1; r2 = x;` Which results (r1, r2) are possible? Can both be 0?

**Answer:**
**(0, 1), (1, 0) and (1, 1) are possible; (0, 0) is impossible** when each thread's order is preserved.
- (0, 1): T1 runs entirely before T2. (1, 0): T2 runs entirely before T1. (1, 1): both writes happen before both reads (e.g., `x = 1; y = 1; r1 = y; r2 = x;`).
- (0, 0) would need `r1 = y` before `y = 1` **and** `r2 = x` before `x = 1`; with program order this forms the cycle x = 1 → r1 = y → y = 1 → r2 = x → x = 1, which cannot happen.
- On modern CPUs that **reorder** a write after a later independent read, (0, 0) **can** occur: the same effect that breaks Peterson's solution. A **memory barrier** between the write and the read prevents it.

## [X6-43] ch6 | Possible outputs with two semaphores
Semaphores `s = 0, t = 0`. P1: `print("A"); signal(s); wait(t); print("C");` P2: `print("B"); wait(s); signal(t); print("D");` List all possible outputs.

**Answer:**
**ABCD, ABDC, BACD, BADC**: four outputs, and the program never deadlocks.
- Program order: **A before C** and **B before D**.
- P2 passes `wait(s)` only after P1's `signal(s)`, which follows A, so **A comes before D**. P1 passes `wait(t)` only after P2's `signal(t)`, which follows B, so **B comes before C**.
- Hence A and B (in either order) both precede C and D (in either order): 2 × 2 = 4 outputs.
- Method: write the program-order constraints, add a "signal before the matching wait" constraint for each semaphore, list every order that satisfies them, and check whether some process can block forever.

## [X6-44] ch6 | Counting permits: what gets printed
Semaphores `A = 2, B = 0`. P1: `while (true) { wait(A); print("x"); signal(B); }` P2: `while (true) { wait(B); wait(B); print("y"); signal(A); }` What is printed?

**Answer:**
**Always exactly `xxyx`; then both processes block forever (deadlock).**
- A's 2 initial permits let P1 print **x x** (A = 0, B = 2).
- P2 needs **two** B permits per y: it prints **y** (B = 0) and returns **one** A permit, so P1 prints one more **x** (A = 0, B = 1).
- Now P2 takes the single B permit and blocks on its second `wait(B)`, while P1 blocks on `wait(A)`; nobody can signal, so the processes are deadlocked. In total, 3 x's and 1 y are printed.
- Method: **count permits (tokens)**; every print consumes permits, so trace the semaphore values until every process is blocked.

## [X6-45] ch6 | Misusing wait() and signal() around a CS
`mutex` is a semaphore initialized to 1. What goes wrong if a process (a) swaps the calls: `signal(mutex); CS; wait(mutex);` (b) writes `wait(mutex); CS; wait(mutex);` (c) omits `wait(mutex)`, (d) omits `signal(mutex)`, or (e) calls `signal(mutex)` twice?

**Answer:**
- (a) **Mutual exclusion violated**: `signal()` first raises mutex to 2, so **several processes may be executing in their critical sections simultaneously**.
- (b) **Deadlock**: the process **permanently blocks on the second `wait()`** (mutex is 0), and every other process then blocks on its first `wait()`.
- (c) **Mutual exclusion violated**: the process enters its critical section without permission.
- (d) The lock is never released, so **all other processes block forever** (no progress).
- (e) mutex becomes 2, so later **two processes can be inside together** (mutual exclusion violated).
- Rule: **too many signals or too few waits violate mutual exclusion; too many waits or too few signals make processes block forever.**

## [X6-46] ch6 | Bounded buffer: wrong order of wait()
In the bounded-buffer producer, what happens if `wait(empty); wait(mutex);` is changed to `wait(mutex); wait(empty);`? Is swapping `signal(mutex); signal(full);` harmful too?

**Answer:**
- **Deadlock is possible.** When the buffer is **full** (empty = 0), the producer acquires `mutex` and then **blocks on `wait(empty)` while holding `mutex`**; the consumer then blocks on `wait(mutex)`, so it can never remove an item and call `signal(empty)`. Both wait forever. (Symmetrically, a consumer doing `wait(mutex); wait(full);` on an empty buffer deadlocks.)
- Rule: **wait on the counting semaphore (empty / full) first, then on mutex**; never block while holding the mutex.
- Swapping the two **signal()** calls is **harmless**: `signal()` never blocks, so correctness is not affected.

## [X6-47] ch6 | Bounded-buffer solution (Ch7 preview / Lab 6)
Give a semaphore solution to the bounded-buffer (producer–consumer) problem with n buffers, and justify each initial value.

**Answer:**
```c
semaphore mutex = 1;   /* mutual exclusion for the buffer pool */
semaphore empty = n;   /* number of empty buffers */
semaphore full  = 0;   /* number of full buffers (items) */

/* producer */
while (true) {
    /* produce an item in next_produced */
    wait(empty);
    wait(mutex);
    /* add next_produced to the buffer */
    signal(mutex);
    signal(full);
}
/* consumer */
while (true) {
    wait(full);
    wait(mutex);
    /* remove an item from the buffer to next_consumed */
    signal(mutex);
    signal(empty);
    /* consume the item in next_consumed */
}
```
- **mutex = 1**: only one process accesses the buffer pool at a time.
- **empty = n**: all n buffers are empty at the start; the producer **blocks when the buffer is full** (empty = 0).
- **full = 0**: there are no items at the start; the consumer **blocks when the buffer is empty** (full = 0).

## [X6-48] ch6 | First readers–writers solution (Ch7 preview / Lab 6)
Give the semaphore solution to the first readers–writers problem. Why can writers starve? If a writer is writing and n readers arrive, where do the readers wait?

**Answer:**
```c
semaphore rw_mutex = 1;  /* used by writers and the first/last reader */
semaphore mutex = 1;     /* protects read_count */
int read_count = 0;      /* readers reading or waiting to read */

/* writer */
wait(rw_mutex);
    /* writing is performed */
signal(rw_mutex);

/* reader */
wait(mutex);
read_count++;
if (read_count == 1) wait(rw_mutex);    /* first reader locks out writers */
signal(mutex);
    /* reading is performed */
wait(mutex);
read_count--;
if (read_count == 0) signal(rw_mutex);  /* last reader lets writers in */
signal(mutex);
```
- **Readers share** the object (only the first reader waits on `rw_mutex`); a **writer has exclusive access** (no other writer and no reader).
- **No reader is kept waiting unless a writer has already gained access**, so readers have priority: a **continuous stream of readers can starve writers** (and delay updates of the object).
- If a writer is writing and n readers arrive, the **first reader waits on `rw_mutex`** (while holding `mutex`), and the other **n − 1 readers wait on `mutex`**.

## [X6-49] ch6 | Dining philosophers: deadlock and remedies (Ch7 preview)
Each chopstick is a semaphore initialized to 1, and philosopher i executes `wait(chopstick[i]); wait(chopstick[(i + 1) % 5]); eat; signal(chopstick[i]); signal(chopstick[(i + 1) % 5]);`. How can this deadlock, and how can deadlock be prevented?

**Answer:**
- **Deadlock**: if all five philosophers become hungry at the same time and **each picks up its left chopstick**, all chopsticks are taken and **each waits forever for its right chopstick**.
- Remedies: (1) allow **at most four philosophers** at the table at the same time; (2) let a philosopher pick up the chopsticks **only if both are available** (picking them up in a critical section); (3) use an **asymmetric** solution: an **odd** philosopher picks up the left chopstick first, an **even** one the right chopstick first.
- A deadlock-free solution does **not** necessarily prevent **starvation**.

## [X6-50] ch6 | POSIX condition variables (Lab 6)
Why does `pthread_cond_wait()` take a mutex as its second argument, and why is it called inside a `while` loop?

**Answer:**
```c
/* waiting thread */                   /* signalling thread */
pthread_mutex_lock(&mutex);            pthread_mutex_lock(&mutex);
while (!ready)                         ready = 1;
    pthread_cond_wait(&cond, &mutex);  pthread_cond_signal(&cond);
pthread_mutex_unlock(&mutex);          pthread_mutex_unlock(&mutex);
```
- A condition variable is always used with a **mutex that protects the condition** (`ready`), and the mutex must be **held** when calling wait or signal.
- `pthread_cond_wait()` **atomically releases the mutex and puts the caller to sleep**; otherwise no other thread could acquire the mutex to change `ready` and signal. **Before returning, it re-acquires the mutex.**
- The **while** loop re-checks the condition after waking, because the condition may have changed again before the mutex was re-acquired (or the wakeup was spurious). The condition must live in a shared variable because `pthread_cond_signal()` with no waiting thread has **no effect** (unlike `sem_post()`, which is remembered). The waiting thread **sleeps instead of busy waiting**.

## [X6-TF] ch6 | True / False quick verdicts
| Statement | T/F | Why (≤ 12 words) |
|---|---|---|
| A race condition requires two processes to access shared data at exactly the same instant. | F | Concurrent (interleaved) access is enough; not necessarily simultaneous. |
| `counter++` can compile into several machine instructions that may be interleaved. | T | Load, add, store; another thread can run in between. |
| Progress allows a process in its remainder section to block others from entering. | F | Only processes wishing to enter take part in the decision. |
| Bounded waiting bounds how many times others may enter before a waiting process. | T | Definition of bounded waiting [6.11]. |
| A correct CS solution may assume all processes run at the same speed. | F | Only nonzero speed; no assumption about relative speed. |
| Mutual exclusion is a safety property; progress and bounded waiting are liveness properties. | T | No wrong results vs. no pointless blocking or starvation. |
| A non-preemptive kernel is essentially free of race conditions in kernel mode on one CPU. | T | Runs until it exits kernel mode, blocks, or yields. |
| A preemptive kernel is free from race conditions on kernel data. | F | A kernel-mode process can be preempted mid-update. |
| Disabling interrupts is an efficient CS solution on multiprocessor systems. | F | Must message all CPUs; slow, and other CPUs keep running. |
| Peterson's solution works for any number of processes. | F | Restricted to two processes. |
| Peterson's solution assumes that load and store instructions are atomic. | T | Otherwise the correctness proof does not hold. |
| Peterson's solution may fail on CPUs that reorder independent reads and writes. | T | Needs memory barriers or sequentially consistent atomics. |
| In Peterson's solution, a waiting process enters after at most one entry by the other. | T | Bounded waiting with bound 1. |
| `test_and_set()` returns the new value of its target. | F | Returns the old value and sets the target TRUE. |
| Two `test_and_set()` calls on different cores may interleave their steps. | F | Atomic: executed sequentially in some arbitrary order. |
| `compare_and_swap()` always stores `new_value` into `*value`. | F | Only if `*value == expected`; always returns the old value. |
| In the bounded-waiting TAS algorithm, any waiting process enters within n − 1 turns. | T | The exit section scans `waiting[]` in cyclic order. |
| Executing `waiting[j] = false` in the bounded-waiting algorithm sets `lock` to FALSE. | F | Hands the lock directly to Pj; `lock` stays TRUE. |
| An atomic variable can make an update of a whole linked list atomic. | F | Only single basic variables such as integers and Booleans. |
| Calls to a mutex lock's `acquire()` and `release()` must be atomic. | T | Otherwise two threads might both acquire the lock. |
| A spinlock is a good choice on a single-processor system. | F | The lock holder cannot run while the waiter spins. |
| Apart from initialization, a semaphore is accessed only through `wait()` and `signal()`. | T | Two atomic operations [6.24]. |
| P() corresponds to `signal()` and V() to `wait()`. | F | P (proberen) = wait; V (verhogen) = signal. |
| A binary semaphore is exactly equivalent to a mutex lock. | F | It can also enforce ordering when initialized to 0. |
| A counting semaphore initialized to k lets at most k processes pass `wait()` before any `signal()`. | T | Initial value = number of available instances. |
| Under the busy-waiting definition, a semaphore's value can become negative. | F | Only the waiting-queue implementation goes negative. |
| `wakeup(P)` moves P from the semaphore's waiting queue to the ready queue. | T | P runs later, when the scheduler selects it. |
| `signal()` on a semaphore wakes up all processes waiting on it. | F | It removes at most one process from the queue. |
| Removing processes from a semaphore queue in LIFO order can cause starvation. | T | An early waiter may never be removed [6.28]. |
| A deadlock-free solution is always starvation-free. | F | One process can starve while others keep progressing. |
| The bounded-buffer semaphores start as mutex = 1, empty = n, full = 0. | T | n empty slots and no items initially. |
| In the first readers–writers solution, writers may starve. | T | Readers have priority while readers keep arriving. |
| `pthread_cond_wait()` releases the mutex while the caller sleeps. | T | It re-acquires the mutex before returning. |
| Strict alternation using only `turn` satisfies progress. | F | A process in its remainder section blocks the other. |
