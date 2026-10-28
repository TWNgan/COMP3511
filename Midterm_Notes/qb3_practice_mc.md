# Question Bank 3 — 新練習 MC（針對 Fall 2026 slides，舊 paper 未考過嘅位）

> 每題都根據 Fall 2026 slide 原文出，括號 [x.xx] 係 slide 編號。

---

## [P-ch1-1] ch1 | Storage managed by
According to the storage characteristics table, which level of storage is managed by the **compiler**?
- A. Registers
- B. Cache
- C. Main memory
- D. Solid-state disk

**Answer: A**

解：registers – compiler；cache – hardware；main memory / SSD / disk – OS [1.34]。

## [P-ch1-2] ch1 | Bootstrap
Where is the bootstrap program (the first program run at power-on) typically stored?
- A. DRAM
- B. Cache
- C. EEPROM
- D. Hard disk

**Answer: C**

解：[1.30] bootstrap program stored on EEPROM（firmware）。

## [P-ch1-3] ch1 | Multiprocessor speedup
Why is the speed-up ratio with N processors less than N?
- A. Each processor runs a different instruction set
- B. Overhead, e.g., contention for shared resources such as the bus or memory
- C. Only one processor can execute user processes
- D. Processors must share a single register set

**Answer: B**

解：[1.37]。

## [P-ch1-4] ch1 | Multiprocessor advantages
Which is **NOT** an advantage of multiprocessor systems listed in the lecture?
- A. Increased throughput
- B. Economy of scale
- C. Increased reliability (graceful degradation)
- D. Simpler parallel programming

**Answer: D**

解：multiprocessor 令 parallel programming **更複雜** [1.37, summary]。

## [P-ch1-5] ch1 | NUMA drawback
What is the potential drawback of a NUMA system?
- A. All CPUs must share a single slow bus
- B. Increased latency when a CPU must access remote memory across the system interconnect
- C. CPUs cannot share one physical address space
- D. It consumes more power than multicore chips

**Answer: B**

解：[1.40]。

## [P-ch1-6] ch1 | Cloud models
A database server provided as a ready-to-use software stack over the Internet is an example of:
- A. SaaS
- B. PaaS
- C. IaaS
- D. MaaS

**Answer: B**

解：SaaS = applications；**PaaS = software stack (e.g. database server)**；IaaS = servers/storage [1.48]。

## [P-ch1-7] ch1 | VMM
Which statement about virtualization components is correct?
- A. The guest OS creates and manages the virtual machine manager
- B. The VMM (hypervisor) creates and manages VMs, providing an interface identical to the host
- C. The host is the virtual copy given to each guest
- D. Programs in a VM usually run several times faster than natively

**Answer: B**

解：[1.44]。

## [P-ch1-8] ch1 | Timesharing
Which statement is correct?
- A. Multiprogramming is an extension of timesharing
- B. Timesharing switches jobs so frequently that users can interact with each job while it runs
- C. Timesharing requires that only one program be in memory
- D. Multiprogramming is not used in modern systems

**Answer: B**

解：timesharing = logical extension of multiprogramming [1.42]。

## [P-ch1-9] ch1 | Mechanical vs electrical storage
Compared with mechanical storage (e.g., HDD), electrical storage (NVM) is generally:
- A. Larger and cheaper per byte
- B. More costly, smaller, more reliable and faster
- C. Slower but more reliable
- D. Volatile

**Answer: B**

解：[1.31]。

## [P-ch1-10] ch1 | AMAT
A cache has hit ratio 95%, hit time 1 ns and miss time 100 ns. The average access time is:
- A. 1.0 ns
- B. 5.0 ns
- C. 5.95 ns
- D. 100 ns

**Answer: C**

解：$0.95 \times 1 + 0.05 \times 100 = 0.95 + 5 =$ **5.95 ns**。

---

## [P-ch2-1] ch2 | ioctl
In UNIX, `ioctl()` belongs to which category of system calls?
- A. Process control
- B. File management
- C. Device management
- D. Protection

**Answer: C**

解：[2.25] device management：ioctl()、read()、write()。

## [P-ch2-2] ch2 | chmod
`chmod()`, `umask()` and `chown()` are examples of which category of system calls?
- A. Information maintenance
- B. Communications
- C. Protection
- D. File management

**Answer: C**

解：[2.25]。

## [P-ch2-3] ch2 | Parameter passing limit
Which parameter-passing methods do **not** limit the number or length of parameters?
- A. Registers only
- B. Block (table) and stack methods
- C. Registers and stack
- D. None of them

**Answer: B**

解：[2.20]。

## [P-ch2-4] ch2 | Policy vs mechanism
Deciding how long the timer should be set for a particular user is an example of:
- A. A mechanism
- B. A policy
- C. A system call
- D. A system program

**Answer: B**

解：timer 本身 = mechanism；設幾耐 = policy [2.34]。

## [P-ch2-5] ch2 | Shell
What is the primary functionality of a shell?
- A. Schedule kernel threads
- B. Fetch a command from the user, interpret it and execute it
- C. Manage virtual memory
- D. Load device drivers

**Answer: B**

解：[2.8]。

## [P-ch2-6] ch2 | DLL
What is a benefit of dynamically linked libraries (DLLs)?
- A. They are linked statically into every executable
- B. They are loaded when needed and shared by all programs using the same version
- C. They remove the need for a loader
- D. They make executables larger

**Answer: B**

解：[2.31]。

## [P-ch2-7] ch2 | MS-DOS
Which statement about MS-DOS is correct?
- A. It is a multitasking system with dual mode
- B. Application programs could access I/O directly, and it had no dual mode or hardware protection
- C. It is a microkernel design
- D. It creates a new process for every program

**Answer: B**

解：[2.36, 2.39]。

## [P-ch2-8] ch2 | Microkernel services
A microkernel typically provides:
- A. File systems and device drivers only
- B. Minimal process and memory management, plus a communication facility
- C. The GUI and shells
- D. All OS services in kernel mode

**Answer: B**

解：[2.46]。

## [P-ch2-9] ch2 | Darwin
Darwin, the kernel environment of macOS/iOS, consists of:
- A. Linux kernel and glibc
- B. Mach microkernel and BSD UNIX kernel
- C. Windows NT kernel and personalities
- D. ART and JNI

**Answer: B**

解：[2.54, 2.57]（hybrid，XNU kernel）。

## [P-ch2-10] ch2 | Android
Which statement about Android is **false**?
- A. Java applications execute on the Android RunTime (ART)
- B. Programs written using JNI are generally portable across hardware
- C. Android uses the Bionic C library instead of glibc
- D. The HAL abstracts hardware to provide a consistent view

**Answer: B**

解：JNI programs **generally not portable** [2.58]。

## [P-ch2-11] ch2 | Windows structure
Windows is described as:
- A. Pure microkernel
- B. Largely monolithic with microkernel-like subsystems (personalities) and loadable modules
- C. Pure layered
- D. Simple structure like MS-DOS

**Answer: B**

解：[2.52]。

## [P-ch2-12] ch2 | High-level language
Which is a main advantage of implementing an OS in a high-level language?
- A. Always faster than assembly
- B. Easier to port to other hardware
- C. Less storage needed
- D. No compiler needed

**Answer: B**

解：[2.35]；缺點 = reduced speed、more storage。

---

## [P-ch3-1] ch3 | Default file descriptors
On UNIX, each process by default has three open file descriptors. Which are they?
- A. stdin (0), stdout (1), stderr (2)
- B. stdin (1), stdout (2), stderr (3)
- C. pipe read end, pipe write end, stderr
- D. stdin, stdout, swap

**Answer: A**

解：[3.7]。

## [P-ch3-2] ch3 | Linux PCB
In Linux, the PCB is represented by:
- A. struct pcb in a hash table
- B. struct task_struct elements in a circular doubly linked list (task list)
- C. TCB in a binary tree
- D. ETHREAD

**Answer: B**

解：[3.13]。

## [P-ch3-3] ch3 | Long-term scheduler
Which statement about the long-term scheduler is correct?
- A. It is invoked every few milliseconds
- B. It controls the degree of multiprogramming and is mainly used in mainframes, not PCs
- C. It swaps processes out to disk
- D. It selects the next process from the ready queue

**Answer: B**

解：[3.17]。C = medium-term；D = short-term。

## [P-ch3-4] ch3 | Register sets
Some processors (e.g., SUN UltraSPARC) provide multiple register sets. What is the effect on context switch?
- A. Context switch becomes impossible
- B. A context switch may just change the pointer to a different register set
- C. The PCB is no longer needed
- D. Context switch time increases

**Answer: B**

解：[3.20]。

## [P-ch3-5] ch3 | Copy-on-write
In Linux, fork() uses copy-on-write. What does this achieve?
- A. Parent and child never share any pages
- B. Copying of the address space is delayed until a page is written, speeding up process creation
- C. The child always runs exec() first
- D. All pages are copied immediately

**Answer: B**

解：[3.46]。

## [P-ch3-6] ch3 | Mode bit
The hardware mode bit is ____ in user mode and ____ in kernel mode.
- A. 0, 1
- B. 1, 0
- C. 1, 1
- D. 0, 0

**Answer: B**

解：[3.28]。

## [P-ch3-7] ch3 | Protection rings
On Intel processors with four protection rings:
- A. Ring 3 is kernel mode and ring 0 is user mode
- B. Ring 0 is kernel mode and ring 3 is user mode
- C. All four rings are heavily used
- D. Ring 1 is for the VMM only

**Answer: B**

解：[3.29]；rings 1、2 rarely used。

## [P-ch3-8] ch3 | Trap
A segmentation fault (protection violation) causes which type of mode transfer?
- A. System call
- B. Interrupt
- C. Trap or exception
- D. Context switch only

**Answer: C**

解：trap/exception = **internal synchronous event** [3.31]。

## [P-ch3-9] ch3 | Bounded buffer
The shared-memory bounded-buffer solution with `in` and `out` and no counter can hold at most:
- A. BUFFER_SIZE items
- B. BUFFER_SIZE − 1 items
- C. BUFFER_SIZE + 1 items
- D. Unlimited items

**Answer: B**

解：[3.54]。

## [P-ch3-10] ch3 | Direct communication
Which is a property of direct communication in message passing?
- A. Messages go through mailboxes
- B. A link is associated with exactly one pair of processes
- C. A link may be associated with more than two processes
- D. It provides better modularity than indirect communication

**Answer: B**

解：[3.59]；缺點 = limited modularity。

## [P-ch3-11] ch3 | Zero capacity
With a zero-capacity message queue:
- A. The sender never waits
- B. The sender waits only if the queue is full
- C. The sender must wait for the receiver (rendezvous)
- D. Messages are lost

**Answer: C**

解：[3.64]。

## [P-ch3-12] ch3 | UNIX FIFO
Which statement about named pipes (FIFOs) in UNIX is correct?
- A. They support full-duplex transmission over networks
- B. They are created with mkfifo(), appear as files, support half-duplex, and processes must be on the same machine
- C. They disappear when the creating process exits
- D. They require a parent-child relationship

**Answer: B**

解：[3.69]；Windows named pipes 先係 full-duplex、可跨機。

## [P-ch3-13] ch3 | Ports
Which statement about client–server sockets is correct?
- A. Servers initiate the connection to clients
- B. All ports below 1024 are well known; clients pick a port above 1024
- C. HTTP uses port 22
- D. A socket is identified by the MAC address only

**Answer: B**

解：[3.71]；HTTP 80、SSH 22、FTP 21。

## [P-ch3-14] ch3 | Orphan
When a parent terminates without calling wait(), its child process:
- A. Is immediately deleted by the kernel in all OSes
- B. Becomes an orphan and is re-parented to init/systemd, which periodically calls wait()
- C. Becomes a zombie forever
- D. Takes over the parent's PID

**Answer: B**

解：[3.50]。

## [P-ch3-15] ch3 | exec
Which is true about a successful exec() call?
- A. It returns the PID of the new program
- B. It returns 0 to the child
- C. It does not return; the process image is replaced
- D. It creates a new process

**Answer: C**

解：exec **唔會建立新 process**，只係 replace 現有 process 嘅 image [3.41]。

## [P-ch3-16] ch3 | fork count
How many processes are there in total after: `fork(); fork() && fork(); fork();`
- A. 8
- B. 10
- C. 12
- D. 16

**Answer: C**

解：2 × 3 × 2 = **12**（`fork() && fork()` 令每個 process 變 3 個）。

## [P-ch3-17] ch3 | Interrupt vector
The interrupt vector is:
- A. A list of processes waiting for I/O
- B. A table of addresses of interrupt handlers, indexed by interrupt number
- C. The register that holds the next instruction address
- D. A queue of DMA requests

**Answer: B**

解：Ch3 summary。

## [P-ch3-18] ch3 | Nonmaskable interrupt
A nonmaskable interrupt is reserved for events such as:
- A. Keyboard input
- B. Unrecoverable memory errors and power failure
- C. Timer expiry for RR
- D. Disk I/O completion

**Answer: B**

解：Ch3 summary；maskable 用於 device controllers。

---

## [P-ch4-1] ch4 | Multicore challenges
Which is **NOT** one of the multicore programming challenges listed in the lecture?
- A. Dividing tasks
- B. Data dependency
- C. Testing and debugging
- D. Reducing the number of system calls

**Answer: D**

解：五大：dividing tasks、balance、data splitting、data dependency、testing & debugging [4.9]。

## [P-ch4-2] ch4 | Windows TEB
In Windows, which thread data structure lives in **user space** and contains the thread id, user-mode stack and thread-local storage?
- A. ETHREAD
- B. KTHREAD
- C. TEB
- D. PCB

**Answer: C**

解：[4.36]。ETHREAD、KTHREAD 喺 kernel space。

## [P-ch4-3] ch4 | clone()
Which call creates a Linux task that behaves like a thread?
- A. clone(SIGCHLD, 0)
- B. clone(CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND, 0)
- C. fork() followed by exec()
- D. pthread_kill()

**Answer: B**

解：share address space、fs info、files、signal handlers [4.38]；A = normal fork。

## [P-ch4-4] ch4 | Linux threads
How does Linux treat threads?
- A. As lightweight processes with separate TCB and PCB structures
- B. As tasks — a thread is a process that shares certain resources with other tasks
- C. Only user-level threads are supported
- D. Through the many-to-one model

**Answer: B**

解：[4.37]。

## [P-ch4-5] ch4 | Signal delivery
A synchronous signal such as division by zero should be delivered to:
- A. Every thread in the process
- B. The thread that caused the signal
- C. A random thread
- D. The parent process

**Answer: B**

解：[4.31]。

## [P-ch4-6] ch4 | Pthread cancellation default
In Pthreads, the default cancellation type is:
- A. Asynchronous
- B. Deferred
- C. Disabled permanently
- D. Immediate

**Answer: B**

解：[4.32]。

## [P-ch4-7] ch4 | Amdahl limit
An application is 50% parallel. As the number of cores approaches infinity, the maximum speedup is:
- A. 1.5
- B. 2
- C. 4
- D. Infinite

**Answer: B**

解：$1/S = 1/0.5 =$ **2**。

## [P-ch4-8] ch4 | One-to-one drawback
What is the main drawback of the one-to-one model?
- A. One blocking call blocks the whole process
- B. Threads cannot run in parallel
- C. Creating a user thread requires creating a kernel thread, so the number of threads may be restricted
- D. It is difficult to implement

**Answer: C**

解：[4.23]。A、B 係 many-to-one；D 係 many-to-many。

## [P-ch4-9] ch4 | Thread context switch
Why is a context switch between two threads of the same process cheaper than between processes?
- A. Threads have no registers
- B. The address space stays the same
- C. Threads do not have stacks
- D. The OS does not save any state

**Answer: B**

解：[4.14]。

## [P-ch4-10] ch4 | fork in multithreaded process
If exec() is called immediately after fork() in a multithreaded process, which fork() version is appropriate?
- A. Duplicate all threads
- B. Duplicate only the calling thread
- C. Duplicate no threads
- D. It does not matter for correctness or efficiency

**Answer: B**

解：exec 會 replace 成個 process，複製所有 threads 係浪費 [4.28]。

---

## [P-ch5-1] ch5 | Dispatcher
Which is **NOT** a function of the dispatcher?
- A. Switching context
- B. Switching to user mode
- C. Jumping to the proper location in the user program
- D. Selecting the next process using the scheduling algorithm

**Answer: D**

解：揀 process 係 **CPU scheduler**；dispatcher 只負責交 CPU 畀佢 [5.7]。

## [P-ch5-2] ch5 | RR waiting bound
With n processes and quantum q under RR (ignoring context switches), no process waits more than:
- A. nq
- B. (n − 1)q
- C. q / n
- D. n + q

**Answer: B**

解：[5.11]。

## [P-ch5-3] ch5 | Quantum rule of thumb
A common rule of thumb for choosing the RR quantum is:
- A. q should be smaller than the context-switch time
- B. 80% of CPU bursts should be shorter than q
- C. q should equal the longest CPU burst
- D. q should be 1 ms

**Answer: B**

解：[5.16]。

## [P-ch5-4] ch5 | Exponential averaging α = 0
With exponential averaging, if $\alpha = 0$ then:
- A. Only the last CPU burst counts
- B. Recent history does not count; the prediction never changes
- C. All bursts are weighted equally
- D. The prediction is always 0

**Answer: B**

解：$\tau_{n+1} = \tau_n$ [5.22]。

## [P-ch5-5] ch5 | SJF as priority
SJF is a special case of priority scheduling where the priority is:
- A. The arrival time
- B. The inverse of the predicted next CPU burst
- C. The process ID
- D. The period of the task

**Answer: B**

解：[5.25]。

## [P-ch5-6] ch5 | MLFQ preemption rule
In the lecture's MLFQ, when a job running from Q1 is preempted by a new arrival in Q0, it:
- A. Is demoted to Q2
- B. Joins the tail of Q1 with a fresh quantum
- C. Joins the head of Q1 with its remaining quantum
- D. Is moved to Q0

**Answer: C**

解：[5.31]。

## [P-ch5-7] ch5 | Logical CPUs
A quad-core processor with 2 hardware threads per core appears to the OS as how many logical processors?
- A. 2
- B. 4
- C. 6
- D. 8

**Answer: D**

解：4 × 2 = 8 [5.42]。

## [P-ch5-8] ch5 | Push migration
Push migration means:
- A. An idle processor pulls a waiting task from a busy processor
- B. A specific task periodically checks loads and moves tasks from overloaded to idle/less-busy CPUs
- C. A process specifies the CPUs it may run on
- D. A thread is pinned to one core forever

**Answer: B**

解：A = pull migration [5.46]；C = hard affinity [5.45]。

## [P-ch5-9] ch5 | Affinity system call
In Linux, which system call supports hard affinity?
- A. sched_setaffinity()
- B. setpriority()
- C. clone()
- D. nice()

**Answer: A**

解：[5.45]。

## [P-ch5-10] ch5 | RM optimality
Rate-monotonic scheduling is optimal in the sense that:
- A. It always achieves 100% CPU utilization
- B. If a task set cannot be scheduled by RM, it cannot be scheduled by any other static-priority algorithm
- C. It never misses deadlines
- D. It handles aperiodic tasks best

**Answer: B**

解：[5.52]。

## [P-ch5-11] ch5 | EDF requirement
What is the only requirement EDF places on a process?
- A. It must be periodic
- B. It must have a constant CPU burst
- C. It must announce its deadline to the scheduler when it becomes runnable
- D. Its period must be a power of 2

**Answer: C**

解：[5.52]。

## [P-ch5-12] ch5 | RM utilization
Two periodic tasks: P1 (period 50, burst 25), P2 (period 80, burst 35). Under RM:
- A. Total utilization is 75% and no deadline is missed
- B. Total utilization ≈ 94% and P2 misses its deadline at 80 (finishes at 85)
- C. P1 misses its deadline
- D. EDF would also miss a deadline

**Answer: B**

解：[5.50–5.51]；EDF 可以全部 meet。

## [P-ch5-13] ch5 | Deterministic modeling
Which statement about deterministic modeling is correct?
- A. It uses probability distributions of CPU bursts
- B. It takes a predetermined workload and gives exact numbers, but results apply only to that workload
- C. It requires running the real system
- D. It is the most accurate method

**Answer: B**

解：[5.54]。

## [P-ch5-14] ch5 | Response time (course definition)
RR with q = 4; P1 (24), P2 (3), P3 (3) all arrive at 0 in that order. Using the course definition, the average response time is:
- A. 3.67
- B. 5.67
- C. 7
- D. 15.67

**Answer: C**

解：end of first run − arrival = 4, 7, 10 → avg **7** [5.13]。（3.67 係課本「first start」定義；5.67 係 avg WT；15.67 係 avg TAT）

## [P-ch5-15] ch5 | Non-preemptive kernel / scheduling
Scheduling that happens only when a process switches from running to waiting or terminates is called:
- A. Preemptive
- B. Non-preemptive (cooperative)
- C. Real-time
- D. Multilevel

**Answer: B**

解：[5.6]。

## [P-ch5-16] ch5 | SMP common queue issue
With a single common ready queue in SMP, what must the system guard against?
- A. Two processors choosing to schedule the same thread (race condition)
- B. Processor affinity being too strong
- C. Too many push migrations
- D. Memory stalls

**Answer: A**

解：[5.39]。

---

## [P-ch6-1] ch6 | Disabling interrupts
Why is disabling interrupts not a good critical-section solution on multiprocessors?
- A. It is not allowed in kernel mode
- B. It is inefficient — interrupts must be disabled on all processors
- C. It causes race conditions on uniprocessors
- D. It requires semaphores

**Answer: B**

解：[6.13]。

## [P-ch6-2] ch6 | CAS return value
compare_and_swap(&value, expected, new_value) returns:
- A. new_value
- B. expected
- C. The original value of *value
- D. TRUE if the swap happened

**Answer: C**

解：[6.17]。

## [P-ch6-3] ch6 | Negative semaphore
In the blocking (no busy waiting) semaphore implementation, a value of −3 means:
- A. The semaphore is broken
- B. Three processes are waiting on the semaphore
- C. Three resources are available
- D. Three signals were lost

**Answer: B**

解：[6.26]。

## [P-ch6-4] ch6 | Spinlock usage
Spinlocks are most appropriate when:
- A. Locks are held for a long time on a uniprocessor
- B. Locks are held for short times on multiprocessor systems
- C. Processes must sleep while waiting
- D. Context switches are free

**Answer: B**

解：[6.22]。

## [P-ch6-5] ch6 | Preemptive kernel
Which statement is correct?
- A. A preemptive kernel is free from race conditions
- B. A non-preemptive kernel is essentially free from race conditions in kernel mode (on a single processor)
- C. Non-preemptive kernels are harder to make correct on SMP than preemptive ones
- D. Kernel code never has race conditions

**Answer: B**

解：[6.12]。

## [P-ch6-6] ch6 | Kernel race example
The lecture's kernel race-condition example involves two processes calling fork() concurrently. Which variable is at risk?
- A. counter
- B. next_available_pid
- C. lock
- D. turn

**Answer: B**

解：same PID could be assigned to two processes [6.8]。

## [P-ch6-7] ch6 | P and V
In Dijkstra's notation, P() and V() correspond to:
- A. signal() and wait()
- B. wait() and signal()
- C. acquire() and test_and_set()
- D. lock() and fork()

**Answer: B**

解：P = proberen (test)，V = verhogen (increment) [6.24]。

## [P-ch6-8] ch6 | Semaphore deadlock
P0: wait(S); wait(Q); … P1: wait(Q); wait(S); … with S = Q = 1. What can happen?
- A. Starvation only
- B. Deadlock
- C. Race condition on S only
- D. Nothing; this is always safe

**Answer: B**

解：[6.28]。

## [P-ch6-9] ch6 | Starvation in semaphore queue
Starvation (indefinite blocking) can occur with semaphores when:
- A. Processes are removed from the waiting queue in LIFO order
- B. The semaphore is initialized to 1
- C. signal() is atomic
- D. The waiting queue is FIFO

**Answer: A**

解：[6.28]。

## [P-ch6-10] ch6 | Atomic increment
In `do { temp = *v; } while (temp != compare_and_swap(v, temp, temp + 1));`, why might the loop repeat?
- A. Because CAS always fails the first time
- B. Because another thread changed *v between reading temp and the CAS, so the CAS returned a different value
- C. Because temp + 1 overflows
- D. It never repeats

**Answer: B**

解：[6.21]。

## [P-ch6-11] ch6 | Counting semaphore initial value
A counting semaphore controlling access to 5 identical printers should be initialized to:
- A. 0
- B. 1
- C. 5
- D. −5

**Answer: C**

解：initialized to the number of resources available [6.25]。

## [P-ch6-12] ch6 | Simple TAS lock
The simple lock `while (test_and_set(&lock)); /*CS*/ lock = false;` satisfies:
- A. Mutual exclusion and bounded waiting
- B. Mutual exclusion but not bounded waiting
- C. Bounded waiting but not mutual exclusion
- D. None of the requirements

**Answer: B**

解：要用 waiting[] 版本 [6.19] 先有 bounded waiting。
