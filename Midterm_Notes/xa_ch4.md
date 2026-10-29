## [X4-01] ch4 | thread definition, thread vs process
What is a thread? Compare a thread with a process. [4.6, 4.14–4.16]

**Answer:**
A **thread is a basic unit of CPU utilization**: an independently scheduled **instance of execution** within a process, represented by a **thread ID, a program counter (PC), a register set and a stack**. A process is an **address space** (code, data, open files, other resources) **plus one or more threads**.

| | Process | Thread |
|---|---|---|
| Role | **"passive" part: address space encapsulates protection** | **"active" component: encapsulates concurrency** |
| Memory | own address space, separate from other processes | **shares the address space** of its process |
| Creation | **heavyweight** (new address space, copy of program and data) | **lightweight** (new TCB and stack only) |
| Context switch | costly (address space changes) | **cheaper within a process** (address space stays) |
| Communication | needs **IPC** (shared memory / message passing) | directly through shared global data and heap |
| OS record | **PCB** | **TCB** (points to its PCB) |

## [X4-02] ch4 | shared vs private per-thread state
What do threads of the same process share, and what does each thread keep private? Why must each thread have its own stack and registers? [4.6, 4.16]

**Answer:**
- **Shared by all threads of a process:** **code (text), data (global variables), heap, open files (file descriptors, network connections) and signals** (signal handlers), i.e., the address space and OS resources.
- **Private to each thread (kept in its TCB):** **thread ID, program counter, register set and stack**.
- **Why private:** each thread is an **independent flow of control** at a different instruction, so it needs its own **PC and registers**; its **stack** holds its own call frames (**parameters, temporary/local variables, saved PC**), which would overwrite each other if shared.
- Private does not mean protected: all stacks lie in the same address space, so a thread can still reach another thread's local variable through a pointer (e.g., main passes `&counter` to a thread).

## [X4-03] ch4 | four benefits of multithreading, examples
State the four benefits of multithreaded programming and give an example of each. [4.7]

**Answer:**
- **Responsiveness**: **may allow continued execution if part of a process (one thread) is blocked**, which matters for interactive applications. E.g., a word processor keeps responding to keystrokes while another thread does **background spelling and grammar checking**.
- **Resource sharing**: **threads share the resources of a process by default** (same address space), **easier than shared memory or message passing** between processes. E.g., a browser thread retrieves data from the network into a buffer that the display thread reads directly.
- **Economy**: **thread creation is much cheaper than process creation (less time and memory)**, and **context switching between threads of a process is faster** than between processes. E.g., a web server creates a thread, not a process, per client request.
- **Scalability**: **a process can take advantage of multicore architectures**, because its threads run in parallel on different cores. E.g., data mining, graphics or AI work split across 8 cores.

## [X4-04] ch4 | thread creation and switching cheaper
Explain why creating a thread, and switching between two threads of the same process, are cheaper than doing the same for processes. [4.4, 4.14]

**Answer:**
**Threads of a process share its address space and resources, so only the thread-specific state has to be created or switched.**
- **Creation:** a new process needs a **new address space and copies of program, data and resources** (PCB, memory, open files), so it is **heavyweight**. A new thread needs only **a new TCB and a stack**; the process-specific data structures are unchanged, so it is **lightweight**.
- **Context switch T1 → T2 (same process):** **save T1's register state and restore T2's**; **the address space remains the same, so the overhead is much smaller**. **Switching to a thread of a different process costs more**, because the address space must also be switched.

## [X4-05] ch4 | disadvantages of threads vs processes
Give two disadvantages of using multiple threads instead of multiple processes. When would separate processes be preferable? [4.9, 4.16]

**Answer:**
**(1) There is no protection between threads, and (2) shared data needs synchronization.**
- All threads run in **one address space**, and the address space is what **encapsulates protection**. A buggy thread can **corrupt shared data or crash the whole process**, e.g., an illegal memory access terminates the program and all its threads. Separate address spaces **keep a buggy program from thrashing the entire system**.
- Shared globals and heap invite **race conditions**: **if there is a data dependency, synchronization is required**, and **different paths of execution make testing and debugging difficult**.
- Prefer processes when tasks are **independent or untrusted** and **fault isolation** matters more than cheap sharing.

## [X4-06] ch4 | multicore programming challenges
List and briefly explain the challenges of programming for multicore systems. [4.9]

**Answer:**
**Five challenges:**
1. **Dividing tasks**: find **separate, concurrent tasks** in the application.
2. **Balance**: each task should perform an **"equal" amount of work**; a task that contributes little value may not be worth a separate core.
3. **Data splitting**: **data used by the tasks must be divided to run on separate cores**.
4. **Data dependency**: when one task uses data produced by another, **synchronization is required**.
5. **Testing and debugging**: **different paths of execution** (many possible interleavings) **make debugging difficult**.

## [X4-07] ch4 | concurrency vs parallelism
Distinguish concurrency from parallelism. Can there be concurrency without parallelism? Parallelism without concurrency? [4.9–4.10]

**Answer:**
- **Concurrency supports more than one task making progress**; on a **single processor core, the scheduler provides concurrency by multiplexing over time**.
- **Parallelism means a system can perform more than one task simultaneously**, which requires **multiple cores or processors**.
- **Concurrency without parallelism: yes**, e.g., 4 threads time-sliced on one core.
- **Parallelism without concurrency: no.** Tasks running simultaneously are all making progress, so every parallel system is also concurrent (not vice versa).
- E.g., 8 threads on 4 cores run in parallel across the cores and concurrently (interleaved) within each core.

## [X4-08] ch4 | data vs task parallelism, classify examples
Explain data and task parallelism using an array of N integers on a dual-core system. Classify: (a) a blur filter applied to four image quadrants on four cores; (b) a video player with one thread decoding video, one decoding audio and one handling the UI. [4.11]

**Answer:**
- **Data parallelism distributes subsets of the same data across multiple cores and performs the same operation on each core.** Thread A on core 0 sums elements 0 … N/2 − 1, thread B on core 1 sums N/2 … N − 1, and the two partial sums are added.
- **Task parallelism distributes threads (tasks) across cores, each thread performing a unique operation.** On the same array, thread A computes the **mean** on core 0 while thread B finds the **maximum** on core 1.
- They are **not mutually exclusive**: an application may use **both (hybrid)**.
- (a) **Data parallelism** (same filter, different subsets of the image). (b) **Task parallelism** (different operations).

## [X4-09] ch4 | Amdahl's law statement, limit 1/S
State Amdahl's Law. What happens to the speedup as the number of cores N → ∞, and why does the serial portion have a "disproportionate effect"? [4.12–4.13]

**Answer:**
$\text{speedup} \le 1/(S + (1-S)/N)$, where **S = serial portion, 1 − S = parallel portion, N = number of processing cores**. It gives the **theoretical speedup in latency of a task at a fixed workload** gained by adding cores.
- **As N → ∞, (1 − S)/N → 0, so the speedup approaches 1/S**: the serial part takes the same time however many cores are added.
- **Disproportionate effect:** with only 10% serial (S = 0.1), 8 cores give $1/(0.1 + 0.9/8) = 1/0.2125 \approx 4.71$, not 8, and unlimited cores give at most $1/0.1 = 10$.

## [X4-10] ch4 | Amdahl speedup, 60% parallel
An application is 60% parallel. Using Amdahl's Law, find the maximum speedup on 4 cores, on 16 cores, and with unlimited cores. [4.12]

**Answer:**
**S = serial portion = 1 − 0.6 = 0.4** (the 60% is the parallel part).
- N = 4: $1/(0.4 + 0.6/4) = 1/(0.4 + 0.15) = 1/0.55 \approx$ **1.82**
- N = 16: $1/(0.4 + 0.6/16) = 1/(0.4 + 0.0375) = 1/0.4375 \approx$ **2.29**
- N → ∞: $1/S = 1/0.4 =$ **2.5**

Four times as many cores raise the speedup only from 1.82 to 2.29, because the 40% serial part dominates.

## [X4-11] ch4 | Amdahl serial fraction from measured speedup
A program runs 4 times faster on 8 cores than on 1 core. Assuming Amdahl's Law holds with equality, what fraction of it is serial? What is the maximum speedup with unlimited cores? [4.12]

**Answer:**
$4 = 1/(S + (1-S)/8)$ → $S + (1-S)/8 = 0.25$ → multiply by 8: $8S + 1 - S = 2$ → $7S = 1$ → **S = 1/7 ≈ 0.143 (14.3% serial, 85.7% parallel)**.
Maximum speedup as N → ∞ $= 1/S =$ **7**.
Template: measured speedup X on N cores gives $S = (N/X - 1)/(N - 1)$. Check: $(8/4 - 1)/(8 - 1) = 1/7$.

## [X4-12] ch4 | Amdahl cores needed for target speedup
An application is 10% serial. How many cores are needed for a speedup of at least 5? Can it ever reach a speedup of 12? [4.12]

**Answer:**
$1/(0.1 + 0.9/N) \ge 5$ → $0.1 + 0.9/N \le 0.2$ → $0.9/N \le 0.1$ → **N ≥ 9 cores**. Check: $1/(0.1 + 0.9/9) = 1/0.2 = 5$, while 8 cores give only 4.71.
**12 is impossible:** the **speedup approaches 1/S = 1/0.1 = 10 as N → ∞** and never exceeds it.
Template: $N \ge (1 - S)/(1/X - S)$, valid only when the target X < 1/S.

## [X4-13] ch4 | doubling cores vs halving serial part
A program has serial fraction S = 0.2 and runs on N = 4 cores. Which helps more: doubling the cores or halving the serial portion? Does the answer change if N = 8? [4.12]

**Answer:**
- **N = 4** (now $1/(0.2 + 0.8/4) = 2.5$): doubling the cores gives $1/(0.2 + 0.8/8) = 1/0.3 \approx$ **3.33**; halving S gives $1/(0.1 + 0.9/4) = 1/0.325 \approx$ **3.08**. So **doubling the cores helps more**.
- **N = 8** (now $1/0.3 \approx 3.33$): doubling the cores gives $1/(0.2 + 0.8/16) = 1/0.25 =$ **4**; halving S gives $1/(0.1 + 0.9/8) = 1/0.2125 \approx$ **4.71**. So **halving the serial part helps more**.
- **Rule:** halving S beats doubling N exactly when **S > 1/N** (S·N > 1). As cores increase, the **serial portion dominates**, and only reducing S raises the ceiling **1/S** (here from 5 to 10).

## [X4-14] ch4 | why real speedup is lower
Measured speedups on N cores are usually lower than Amdahl's Law predicts. Why? [4.9, 4.12]

**Answer:**
**Amdahl's Law is a theoretical upper bound (≤): it assumes the parallel part splits perfectly over N cores with zero overhead.** In practice there is also:
- **Overhead** of creating, managing and context-switching threads.
- **Synchronization:** **data dependencies** force threads to wait for each other (locks, joins).
- **Imbalance:** tasks rarely perform an **"equal" amount of work**, so the slowest thread decides the finish time.
- **Contention** for shared memory, bus and caches, and other processes competing for the same cores.

## [X4-15] ch4 | multithreading on a single core
Can a multithreaded program finish faster than its single-threaded version on a single-core CPU? Explain. [4.9, 4.14]

**Answer:**
**Yes if the threads perform I/O (or otherwise block); no for purely CPU-bound work.**
- One core gives only **concurrency (multiplexing over time)**, not parallelism, so CPU-bound threads gain no speedup and add context-switch overhead.
- Threads **enable overlap of I/O with other activities within a single program: one thread runs on the CPU while another thread of the process is doing I/O**. The total time drops and the program stays **responsive**.
- This needs kernel threads (one-to-one or many-to-many). Under **many-to-one**, a blocking I/O call **blocks the entire process**, so there is no overlap.

## [X4-16] ch4 | Thread Control Block contents
What does the OS keep in a Thread Control Block (TCB)? How is the TCB related to the PCB? [4.15]

**Answer:**
**Each thread has a TCB holding its private execution state, its scheduling and accounting information, and a pointer to its enclosing process (PCB).**
- **Execution state:** CPU registers, program counter, **pointer to stack** (saved here while the thread is not running).
- **Scheduling info:** thread state, priority, CPU time. **Accounting info.**
- **Various pointers** that link the TCB into **scheduling queues**.
- **Pointer to enclosing process (PCB):** process-wide information (**process ID**, memory/address space, open files) stays in the **PCB** and is shared by all its threads, so the **PID is not in the TCB**.

## [X4-17] ch4 | process state with multiple threads
A process has three threads: one running, one waiting for a disk read, one ready. What is the state of the process? Where are the threads' TCBs? [4.17–4.18]

**Answer:**
**Each thread has its own state** (new, ready, running, waiting, terminated), recorded in its **TCB**; the threads are scheduled individually, so one thread of the process can be running while another waits and a third is ready.
- Running thread: executing on the CPU; it is **resident in the registers**.
- Ready thread: its TCB is in the **ready queue**.
- Waiting thread: its TCB is in the **disk unit's device queue**. **TCBs are organized into queues based on their states**, one queue per device/signal/condition, **each with its own scheduling policy**.

## [X4-18] ch4 | user threads vs kernel threads
Distinguish user-level threads from kernel-level threads. [4.19–4.20]

**Answer:**
**User threads are created and managed by a user-level thread library and are unknown to the kernel; kernel threads are supported, managed and scheduled by the OS.**

| | User threads | Kernel threads |
|---|---|---|
| Managed by | **user-level threads library** | **operating system** |
| Known to kernel | **no, visible only to programmers** | yes; each has a **TCB** |
| Scheduling | **cannot be scheduled on a CPU directly** | **the only threads the OS schedules on CPUs** |
| Creation cost | lower | **more overhead** (kernel allocates resources) |
| Examples | Pthreads / Windows / Java thread APIs | Windows, Linux, macOS, iOS, Android |

**A mapping must exist between user threads and kernel threads** (many-to-one, one-to-one, many-to-many).

## [X4-19] ch4 | thread libraries, Pthreads specification
What is a thread library? Name the three primary thread libraries. Is Pthreads an implementation? [4.20]

**Answer:**
**A thread library provides the programmer with an API for creating and managing threads** (user threads) in programs.
- Three primary libraries: **POSIX Pthreads** (POSIX API, UNIX/Linux), **Windows threads** (Win32 API), **Java threads** (Java API).
- **Pthreads is a specification, not an implementation:** the **POSIX standard (IEEE 1003.1c)** defines the API for thread creation and synchronization, and **different UNIX-like OSes implement it differently**.
- User threads are the **concurrent and modular entities** of a program that the OS maps onto kernel threads.

## [X4-20] ch4 | pthread_create arguments, pthread_join purpose
Explain the arguments of `pthread_create()` and the purpose of `pthread_join()`. What can go wrong if `main()` never calls `pthread_join()`? [4.20, 4.33]

**Answer:**
**`pthread_create()` starts a new thread that runs `start_routine(arg)`; `pthread_join()` makes the caller wait until that thread terminates.**
```c
int pthread_create(pthread_t *tid,
                   const pthread_attr_t *attr,
                   void *(*start_routine)(void *),
                   void *arg);
```
- **tid** receives the new **thread identifier**; **attr** holds the thread **attributes** (stack size, scheduling info; **NULL or `pthread_attr_init()` = default**); **start_routine** is the function where the thread **begins execution**; **arg** is the **single `void *` argument passed to it**. Returns **0 on success**.
- **`pthread_join(tid, &ret)` blocks the caller until thread tid terminates** and collects its return value (**create/join strategy**: the parent thread waits for its child thread).
- Without a join, **main may return first, and returning from main calls `exit()`, which terminates the whole process including all its threads**. A worker may be killed before it finishes (e.g., `sum` is printed before it is computed).
- Compile and link with **`gcc prog.c -lpthread`**.

## [X4-21] ch4 | passing arguments, returning thread results
A start routine takes only one `void *` argument. How do you pass several values to a thread, and how does the thread return a result to the thread that joins it? [4.20, 4.33]

**Answer:**
**Pack the values in a struct, pass its address as `arg`, and return a pointer with `return` or `pthread_exit()`; the joining thread receives it through `pthread_join()`.**
```c
struct args { int lo, hi; long sum; };
void *worker(void *p) {
    struct args *a = (struct args *)p;  /* cast back */
    a->sum = 0;
    for (int i = a->lo; i <= a->hi; i++) a->sum += i;
    return a;                     /* = pthread_exit(a) */
}
/* in main: */
struct args a = {1, 100, 0};  void *res;
pthread_create(&tid, NULL, worker, &a);
pthread_join(tid, &res);  /* res == &a; sum = 5050 */
```
- **Never return the address of the thread's local variable**: it lives on the thread's **private stack**, which is gone once the thread terminates. Return heap memory (`malloc`), a global, or a field of the argument struct.

## [X4-22] ch4 | passing &i to threads bug
What is wrong with this code? What can it print, and how would you fix it? [4.20, 4.33]
```c
void *show(void *arg) {
    printf("%d\n", *(int *)arg);  return NULL;
}
int main() {
    pthread_t t[3];  int i, j;
    for (i = 0; i < 3; i++)
        pthread_create(&t[i], NULL, show, &i);
    for (j = 0; j < 3; j++) pthread_join(t[j], NULL);
}
```

**Answer:**
**All three threads get the address of the same variable `i`, which main keeps changing. This is a race condition, so the output is unpredictable.**
- Thread k reads `i` only when it gets scheduled, so it prints some value **from k to 3**, in any order: `0 1 2`, `1 2 3`, `2 3 3` and `3 3 3` are all possible.
- **Fix: give each thread its own copy:** `int id[3]; … id[i] = i; pthread_create(&t[i], NULL, show, &id[i]);` (or pass the value itself as `(void *)(long)i` and read it back with `(int)(long)arg`).

## [X4-23] ch4 | pthread_exit vs return vs exit
In a multithreaded program, what is the difference between a thread calling `pthread_exit()`, returning from its start routine, and calling `exit()`? What happens when `main()` returns? [4.20, 4.33]

**Answer:**
- **`pthread_exit(v)` or `return v` from the start routine terminates only the calling thread**; v goes to the thread that calls `pthread_join()` on it. The other threads keep running.
- **`exit()` called by any thread terminates the entire process, i.e., all of its threads.** **Returning from `main()` is the same as calling `exit()`.**
- So `main()` should **`pthread_join()` its workers** first, or end with `pthread_exit()`, which ends only the main thread; the process then ends when its last thread terminates.

## [X4-24] ch4 | Pthreads trace, possible outputs
`f(arg)` prints the string `arg`. How many different outputs are possible? List them. [4.20, 4.33]
```c
printf("M1\n");
pthread_create(&t1, NULL, f, "A");
pthread_create(&t2, NULL, f, "B");
printf("M2\n");
pthread_join(t1, NULL);  pthread_join(t2, NULL);
printf("M3\n");
```

**Answer:**
**6 possible outputs.** **M1 is always first** (no thread exists yet) and **M3 is always last** (both joins return only after A and B are printed). **A, B and M2 can appear in any order**, because a created thread is only placed in the ready queue and **runs independently, depending on scheduling**: 3! = 6.
M1, then one of {M2 A B, M2 B A, A M2 B, B M2 A, A B M2, B A M2}, then M3.

## [X4-25] ch4 | compare four multithreading models
Compare the many-to-one, one-to-one, many-to-many and two-level models. [4.21–4.26]

**Answer:**
**They differ in how user threads are mapped to kernel threads, which decides blocking behaviour and parallelism:**

| Model | Mapping | One thread makes a blocking system call | Parallel on multicore? | Main drawback | Examples |
|---|---|---|---|---|---|
| **Many-to-one** | many user threads → **one** kernel thread | **entire process blocks** | **No: only one kernel thread can be active at a time** | no parallelism; blocking | Solaris Green Threads, GNU Portable Threads |
| **One-to-one** | **each** user thread → its own kernel thread | others keep running | **Yes** | **creating a user thread requires creating a kernel thread** (overhead); **threads per process may be restricted** | **Windows, Linux** (most OSes now) |
| **Many-to-many** | many user threads → **smaller or equal number** of kernel threads | others run on other kernel threads | **Yes** | **difficult to implement** | Windows ThreadFiber package |
| **Two-level** | many-to-many **+ a user thread may be bound to a kernel thread** | others run on other kernel threads | **Yes** | complex, like many-to-many | — |

Concurrency: **many-to-one < many-to-many < one-to-one (maximum)**. **No model maps one user thread to several kernel threads.**

## [X4-26] ch4 | blocking system call, many-to-one vs one-to-one
A process has 4 user threads on a 4-core machine. Thread T1 calls `read()` on a slow disk. What happens to T2–T4 under (a) the many-to-one model, (b) the one-to-one model? [4.22–4.23]

**Answer:**
(a) **Many-to-one: T2–T4 are blocked too, because the entire process is blocked.** All four user threads are mapped to **one kernel thread**; T1's blocking system call blocks that kernel thread, and the OS has no other kernel thread of this process to schedule. Even before the call, **only one thread can run at a time, so 3 cores are idle for this process** (concurrency, no parallelism).
(b) **One-to-one: T2–T4 keep running.** Each has its own kernel thread; only T1's kernel thread waits, and the others are scheduled **in parallel on the other cores**. This is why one-to-one **provides the maximum concurrency**.

## [X4-27] ch4 | why most OSes use one-to-one
The one-to-one model has more overhead than many-to-one, yet most operating systems (Windows, Linux) use it. Why? [4.23, 4.26]

**Answer:**
**It gives maximum concurrency and true parallelism, and its cost (a limit on the number of kernel threads) matters less as the number of cores grows.**
- A blocking thread does not block the others, and **multiple threads run in parallel on multiprocessor or multicore systems**.
- Drawback: **creating a user-level thread mandates creating a corresponding kernel thread**; kernel threads **consume resources (memory, I/O, etc.)**, so the number of threads per process may be **restricted**. But **with an increasing number of processing cores, limiting the number of kernel threads has become less important.**
- It is simpler than **many-to-many, which is most flexible but difficult to implement in practice**.

## [X4-28] ch4 | many-to-many and two-level models
Explain the many-to-many and two-level models. What do they offer over one-to-one, and why is many-to-many rarely used? [4.24–4.26]

**Answer:**
- **Many-to-many multiplexes many user-level threads onto a smaller or equal number of kernel threads, specific to a particular application or machine**: an application **may be allocated more kernel threads on an 8-core system than on a 4-core system**. The thread library decides which user thread runs on which kernel thread (**process-contention scope, PCS**).
- It offers: programmers can create **as many user threads as needed, not restricted by the number of kernel threads**; the **OS can create a sufficient number of kernel threads in advance (thread pool)**; a blocking call does not block the whole process; threads still run in parallel.
- **Two-level model: like many-to-many, but it also allows a user thread to be bound to a kernel thread**, so that thread always has a kernel thread of its own.
- Rarely used because it is **most flexible but difficult to implement in practice**, and with many cores one-to-one is good enough. Example: **Windows with the ThreadFiber package**.

## [X4-29] ch4 | LWP, scheduler activations, upcalls
What is a lightweight process (LWP)? How do the kernel and the thread library cooperate under the many-to-many model?

**Answer:**
- **An LWP is an intermediate data structure between user and kernel threads. To the user-thread library, an LWP appears to be a virtual processor on which the application can schedule a user thread to run** (many-to-one / many-to-many mapping; this choice is **PCS**).
- **Each LWP is attached to a kernel thread, and it is the kernel threads that the OS schedules on the CPUs. If a kernel thread blocks (e.g., waiting for I/O), the LWP blocks as well**, and so does the user thread running on it.
- **The OS coordinates with the thread library so that the number of kernel threads (LWPs) given to the process is dynamically adjusted for best performance.** The textbook calls this **scheduler activation**: the kernel tells the library about events (e.g., a thread is about to block) by an **upcall** and gives it a new LWP, on which the library runs another user thread.

## [X4-30] ch4 | thread pool benefits
What is a thread pool? Why is serving requests from a thread pool better than creating a new thread for each request? [4.24]

**Answer:**
**A thread pool is a set of threads created in advance (at start-up) that wait in a pool for work.** A request is handed to an idle pool thread, which **returns to the pool** when done instead of terminating. (The many-to-many model likewise lets the OS **create a sufficient number of kernel threads in advance**.)
- **Faster:** an existing thread services the request at once, with no **thread-creation delay** per request.
- **Bounded resources:** the pool **limits the number of threads that exist at any one time**, so a burst of requests cannot exhaust memory and CPU (each kernel thread **consumes resources**).
- **Flexibility:** **separating the task to be performed from the mechanics of creating the task** allows different strategies for running it (e.g., run after a delay or periodically).

## [X4-31] ch4 | fork() and exec() in multithreaded process
If one thread of a multithreaded process calls `fork()`, should the child duplicate all threads or only the calling thread? What happens when a thread calls `exec()`? [4.28]

**Answer:**
**It depends on whether the child calls exec(); some UNIX systems provide two versions of fork() for this reason.**
- **If exec() is called immediately after forking, duplicate only the calling thread.** **Duplicating all threads is unnecessary, as the program specified in exec() will replace the entire process.**
- **If the child does not call exec(), duplicate all threads**, so the child is a full copy of the parent. (Linux/POSIX `fork()` duplicates **only the calling thread**.)
- **exec() works as normal: it replaces the entire process, including all threads** (same PID). E.g., if a worker thread calls `execlp("echo", "echo", "X", NULL)` while main waits in `pthread_join()`, only `X` is printed and main never resumes.

## [X4-32] ch4 | fork + pthread_create loop with join
How many processes are there in total, how many threads are created by `pthread_create()`, and how many times are `T` and `M` printed? (Assume each `printf` is output immediately.) [4.28]
```c
void *work(void *arg) { printf("T\n"); return NULL; }
int main() {
    pthread_t tid;
    for (int i = 0; i < 2; i++) {
        fork();
        pthread_create(&tid, NULL, work, NULL);
        pthread_join(tid, NULL);
    }
    printf("M\n");
}
```

**Answer:**
**4 processes and 6 threads created; T is printed 6 times and M 4 times.**
- i = 0: fork gives **2 processes**; each creates and joins one thread: 2 threads, 2 × T.
- i = 1: each process forks, giving **4 processes**; each creates and joins one thread: 4 threads, 4 × T.
- Threads created **= 2 + 4 = 6** (10 threads if each process's main thread is counted). Each of the 4 processes prints M once after the loop.
- Every worker is joined before the next `fork()`, so each fork happens in a single-threaded process and fork semantics do not matter.

## [X4-33] ch4 | fork + pthread_create in a branch
Assume `fork()` duplicates only the calling thread (Linux). How many processes (including the original) are there, and how many threads are created by `pthread_create()`? [4.28]
```c
pid_t pid = fork();
if (pid > 0) {
    pthread_create(&t1, NULL, work, NULL);
    fork();
}
pthread_create(&t2, NULL, work, NULL);
```

**Answer:**
**3 processes and 4 threads created.**
- First fork: P0 (parent, pid > 0) and P1 (child, pid == 0).
- Only P0 enters the `if`: it creates thread t1, then forks P2. **P2 gets only a copy of the calling (main) thread**, not t1. P2 continues after that `fork()`, so it also reaches the last line.
- P0, P1 and P2 each run the last `pthread_create()`: 3 more threads.
- Processes = **3**; threads created = 1 + 3 = **4** (7 threads in total with the 3 main threads).

## [X4-34] ch4 | thread shares, fork copies global
What is printed? [4.6]
```c
int count = 0;
void *inc(void *arg) { count++; return NULL; }
int main() {
    pthread_t t;
    pthread_create(&t, NULL, inc, NULL);
    pthread_join(t, NULL);
    if (fork() == 0) {
        pthread_create(&t, NULL, inc, NULL);
        pthread_join(t, NULL);
        printf("child: %d\n", count);
        return 0;
    }
    wait(NULL);
    printf("parent: %d\n", count);
}
```

**Answer:**
**`child: 2`, then `parent: 1`.**
- The first thread **shares the process's global data**, so its `count++` updates main's `count` to 1.
- `fork()` gives the child **its own copy** of the address space (count = 1); the child's thread increments the child's copy to **2**.
- The parent's copy stays **1**, and `wait(NULL)` makes the parent print last.
- **Key: threads share memory; processes have separate memory.**

## [X4-35] ch4 | fork called inside a thread
Assume `fork()` duplicates only the calling thread (Linux). How many processes are there, and how many times are `A` and `B` printed? [4.28]
```c
void *work(void *arg) {
    fork();
    printf("A\n");
    return NULL;
}
int main() {
    pthread_t t;
    pthread_create(&t, NULL, work, NULL);
    pthread_join(t, NULL);
    printf("B\n");
}
```

**Answer:**
**2 processes; A is printed 2 times and B once.**
- The worker thread calls `fork()`, so **the child process contains only a copy of the calling (worker) thread**, not main.
- Parent: the worker prints A; main's `pthread_join()` returns and main prints B.
- Child: its only thread prints A and returns from `work`. As the last thread of the child, this ends the child process, and **there is no main thread in the child to print B**.
- (If fork() duplicated all threads, the child would also contain main, and B would be printed twice.)

## [X4-36] ch4 | fork + pthread_create loop, formula
Assume `fork()` duplicates only the calling thread. For n = 3, how many processes exist after the loop, and how many threads are created by `pthread_create()`? Give formulas in n. [4.28]
```c
for (int i = 0; i < n; i++) {
    fork();
    pthread_create(&tid[i], NULL, work, NULL);
}
```

**Answer:**
**n = 3: 8 processes and 14 threads created.** In general: $2^n$ processes and $2 + 4 + \cdots + 2^n = 2^{n+1} - 2$ threads.
- In each iteration, every process's **main thread** forks (2, 4, 8 processes), then each process creates one thread (+2, +4, +8 = 14).
- A child receives only a copy of the calling main thread, **not the worker threads already running in its parent**, so earlier workers are never duplicated.

## [X4-37] ch4 | what is a signal, handling steps
What is a signal? Describe how a signal is handled. Can a program change how a signal is handled? [4.29–4.30]

**Answer:**
**A signal is used in UNIX systems to notify a process that a particular event has occurred.** A **signal handler** processes it in this pattern:
1. The signal is **generated** by a particular event (e.g., division by 0, Ctrl-C, a timer expiring, process termination).
2. The signal is **delivered** to a process (or thread).
3. The signal is **handled by one of two signal handlers: default or user-defined.**
- **Every signal has a default handler that the kernel uses**: some signals are ignored, while others (e.g., an illegal memory access) are handled by **terminating the program**.
- **Yes: a user-defined signal handler can override the default handler**, e.g., `signal(SIGINT, handler);` (SIGKILL and SIGSTOP cannot be caught).

## [X4-38] ch4 | synchronous vs asynchronous signals
Distinguish synchronous and asynchronous signals, with two examples of each. Why is the first kind called synchronous? [4.29]

**Answer:**
- **Synchronous signals** are caused by an operation of the running process itself, e.g., an **illegal memory access** (segmentation fault) or a **division by 0**. They are **delivered to the same process that performed the operation that caused the signal**, which is why they are called **synchronous**.
- **Asynchronous signals** are **generated by an event external to the running process**, e.g., **terminating a process with Ctrl-C**, a **timer expiring**, or another process calling `kill()`.
- **A signal may be received either synchronously or asynchronously, depending on the source and the reason.**

## [X4-39] ch4 | signal delivery in multithreaded process
Where should a signal be delivered in a multithreaded process? A process has threads T1–T3; T2 divides by zero, and later the user presses Ctrl-C. Where should each signal go? [4.30–4.31]

**Answer:**
**The delivery method depends on the type of signal.** There are four options:
1. **Deliver the signal to the thread to which the signal applies.**
2. **Deliver the signal to every thread in the process.**
3. **Deliver the signal to certain threads in the process.**
4. **Assign a specific thread to receive all signals for the process.**
- T2's division by zero is **synchronous, so it is delivered to the thread causing the signal (T2) and not to the other threads**.
- **Ctrl-C terminates the process, so this asynchronous signal should be sent to all threads** (T1–T3).
- UNIX **`kill(pid, signal)`** delivers a signal to a **process**; Pthreads **`pthread_kill(tid, signal)`** delivers it to a **specified thread**. Hence "all signals go to all threads" is **false**.

## [X4-40] ch4 | asynchronous vs deferred cancellation
What is thread cancellation? Compare asynchronous and deferred cancellation. Which is preferred, and why? [4.32]

**Answer:**
**Thread cancellation means terminating a thread before it has finished; the thread to be cancelled is the target thread.**
- **Asynchronous cancellation terminates the target thread immediately**, possibly **in the middle of a critical update** to shared data, which leaves the data inconsistent; **the OS may not be able to reclaim all resources** (memory, locks, files).
- **Deferred cancellation: the target thread periodically checks whether it should terminate, allowing it an opportunity to terminate itself in an orderly fashion**. It is cancelled only at a safe **cancellation point** (e.g., blocking calls such as `read()` or `close()`, or `pthread_testcancel()`).
- **Deferred is preferred** (and is the **Pthreads default type**) because the thread can finish its update and release its resources first.

## [X4-41] ch4 | pthread_cancel only requests cancellation
Thread A calls `pthread_cancel(tid)` and then `pthread_join(tid, NULL)`. Is the target terminated immediately? What if it is in a long computation loop with no function calls, or has cancellation disabled? [4.32–4.33]

**Answer:**
**No. Invoking `pthread_cancel()` only requests cancellation; the actual cancellation depends on the target thread's state and type.**
- **The default type is deferred**, so the request stays pending until the target reaches a **cancellation point**. A pure computation loop has none, so the thread is not cancelled until it calls, e.g., `pthread_testcancel()` or a blocking call that is a cancellation point.
- **If the thread has cancellation disabled, the cancellation remains pending until the thread enables it.**
- **`pthread_join()` makes A wait until the target has actually terminated.** Only a target whose type is set to **asynchronous** can be terminated immediately.

## [X4-42] ch4 | thread-local storage
What is thread-local storage (TLS)? How does it differ from local variables and from global data? Give an example. [4.36]

**Answer:**
**Thread-local storage is data that is unique to each thread**: every thread has its own copy.
- vs **global / static data**: globals are **shared by all threads** of the process, while TLS gives each thread a **private copy** that, like static data, persists across function calls.
- vs **local variables**: locals live on the stack and exist only **during a single function invocation**, while TLS is visible **across all function invocations** of that thread.
- Example: each thread's own **`errno`**, or a **unique transaction ID** when each transaction is serviced by a separate thread. (Windows keeps TLS in the thread's **TEB**.)

## [X4-43] ch4 | Windows thread components, ETHREAD KTHREAD TEB
List the components of a Windows thread and its primary data structures. Where does each data structure reside? [4.35–4.36]

**Answer:**
**Windows uses the one-to-one mapping: each user-level thread maps to an associated kernel thread.** A thread has:
- a **thread ID**, a **register set** (processor state), a **program counter**, **separate user and kernel stacks**, and a **private data storage area** used by run-time libraries and DLLs. **The register set, stacks and private storage area are known as the context of the thread.**
- **ETHREAD** (executive thread block): pointer to the **process** the thread belongs to and to its **KTHREAD**; in **kernel space**.
- **KTHREAD** (kernel thread block): **scheduling and synchronization info, kernel-mode stack, pointer to the TEB**; in **kernel space**.
- **TEB** (thread environment block): **thread ID, user-mode stack, thread-local storage**; in **user space**.

## [X4-44] ch4 | Linux tasks, task_struct vs Windows
How does Linux represent threads? Contrast Linux with Windows for a process that has two threads. [4.37]

**Answer:**
**Linux does not differentiate between threads and processes: each is a task.** **A thread is a process that may share certain resources (e.g., the address space) with other tasks**; **each thread has its own unique `task_struct`** and appears as a normal process.
- **Windows** (explicit kernel support for threads): **one PCB** describes the shared resources (address space, open files) and **points to the two threads' TCBs**, each describing the resources that thread alone possesses.
- **Linux:** simply **two tasks with normal `task_struct` structures, set up to share resources**.

## [X4-45] ch4 | clone() flags vs fork()
How does Linux create a thread with `clone()`? Explain the flags and how `clone()` differs from `fork()`. [4.38]

**Answer:**
**Threads are created like normal tasks, except that `clone()` is passed flags naming the resources the child task shares with its parent:**
`clone(CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND, 0);`
- **CLONE_VM**: share the **address space**; **CLONE_FS**: share **file-system information** (e.g., current directory); **CLONE_FILES**: share the **open files (file descriptors)**; **CLONE_SIGHAND**: share the **signal handlers**. With these flags, the child task behaves like a **thread**.
- **Instead of copying all data structures like `fork()`, the new task points to the data structures of the parent task, depending on the set of flags.**
- With no sharing flags, it behaves like a separate process: **a normal `fork()` can be implemented as `clone(SIGCHLD, 0)`** (SIGCHLD is the signal sent to the parent when the child terminates).

## [X4-TF] ch4 | True / False quick verdicts
| Statement | T/F | Why (≤ 12 words) |
|---|---|---|
| Threads of a process share the heap, but each thread has its own stack. | T | Heap and globals shared; stack, PC, registers private. |
| Each thread has its own set of open file descriptors. | F | Open files are shared by all threads of the process. |
| The process identifier (PID) is stored in each thread's TCB. | F | PID is in the PCB; TCB points to the PCB. |
| Each thread has its own state (ready/running/waiting) kept in its TCB. | T | TCBs are organized into queues by state. |
| Most operating-system kernels are multithreaded. | T | E.g., Linux boot creates kernel threads for devices, memory. |
| Context switching between threads of one process is cheaper than between processes. | T | Address space stays the same; only registers saved and restored. |
| Multithreading can shorten run time on one core if the threads do I/O. | T | One thread computes while another waits for I/O. |
| Parallelism is possible on a single core through time multiplexing. | F | Time multiplexing gives concurrency only; parallelism needs multiple cores. |
| A multicore chip uses more power than several single-core chips. | F | Uses less power; on-chip communication is also faster. |
| Two threads summing the two halves of an array is task parallelism. | F | Same operation on different data subsets: data parallelism. |
| By Amdahl's Law, a 50%-parallel program can never exceed 2× speedup. | T | Limit is 1/S = 1/0.5 = 2. |
| A 90%-parallel program gets at most about 5.26× speedup on 10 cores. | T | 1/(0.1 + 0.9/10) = 1/0.19 ≈ 5.26. |
| With enough cores, the Amdahl speedup can exceed 1/S. | F | Speedup approaches 1/S as N → ∞, never exceeds it. |
| The OS schedules user-level threads directly onto CPUs. | F | OS only manages and schedules kernel threads. |
| A many-to-one process on 8 cores uses at most one core at a time. | T | Only one kernel thread, so only one core at a time. |
| In the one-to-one model, the number of threads per process may be restricted. | T | Every user thread needs a kernel thread, which consumes resources. |
| In many-to-many, there must be as many kernel threads as user threads. | F | Smaller or equal number of kernel threads. |
| The two-level model allows a user thread to be bound to a kernel thread. | T | Many-to-many plus optional binding. |
| Pthreads is a specification, not an implementation. | T | POSIX standard API; each OS implements it differently. |
| `pthread_join()` terminates the specified thread. | F | It waits for that thread to terminate. |
| Returning from `main()` terminates all threads of the process. | T | Returning from main calls exit(), ending the whole process. |
| If exec() follows fork() immediately, duplicating all threads is unnecessary. | T | exec() replaces the entire process, including all threads. |
| A segmentation fault (illegal memory access) is an asynchronous signal. | F | Caused by the process's own operation: synchronous. |
| A signal sent by `kill()` from another process is asynchronous. | T | Generated by an event external to the running process. |
| `pthread_kill()` delivers a signal to a specific thread. | T | `kill()` targets a process; `pthread_kill()` a thread. |
| Asynchronous cancellation lets the target thread clean up before it terminates. | F | That is deferred; asynchronous terminates immediately. |
| A cancellation request to a thread with cancellation disabled is discarded. | F | It remains pending until the thread enables cancellation. |
| Thread-local storage is shared by all threads of a process. | F | TLS is unique to each thread. |
| Linux keeps separate PCB and TCB structures for a multithreaded process. | F | Each thread is a task with its own task_struct. |
| In Windows, the TEB resides in kernel space. | F | TEB is in user space; ETHREAD and KTHREAD in kernel. |
