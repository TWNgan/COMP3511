# X3 Answer Bank — Chapter 3: Processes, Interrupts, IPC

> Anticipated questions beyond the past papers, in slide order. Copy the Answer directly; **bold** = grader keywords. Conventions: `fork()` returns 0 to the child, the child's PID to the parent, −1 on failure; assume every fork succeeds and `printf` flushes immediately unless stated. Every "Output" program was compiled and run.

## [X3-01] ch3 | Program vs process; loading a program
What is the difference between a program and a process? When does a program become a process, and can one program be associated with several processes?

**Answer:**
- A **program is a passive entity** — an **executable file stored on disk**. A **process is an active entity** — a **program in execution**, with a **program counter** specifying the next instruction to fetch and execute and a set of **associated resources** (address space, registers, open files).
- A program **becomes a process when its executable file is loaded into main memory** (double-click an icon or enter a command in the shell): the OS (1) loads the **code and static data**, (2) allocates the **run-time stack** and fills in `argc`/`argv`, (3) allocates the **heap**, (4) sets up I/O — **three open file descriptors: stdin (0), stdout (1), stderr (2)**.
- **Yes — one program can be executed by multiple processes** (e.g., several copies of a web browser): the **text section is the same, but each has its own data, heap, stack and PC**, so they are **separate execution sequences**. A process can itself be an execution environment for other programs (e.g., the **JVM**).

## [X3-02] ch3 | Memory layout: text, data, heap, stack
Describe the sections of a process in memory. In the program below, where are `x`, `y`, `values`, `i`, the five `int`s from `malloc()`, `argc`/`argv` and the code of `main` stored?
```c
int x;
int y = 15;
int main(int argc, char *argv[]) {
    int *values;
    int i;
    values = (int *)malloc(sizeof(int) * 5);
    for (i = 0; i < 5; i++)
        values[i] = i;
    return 0;
}
```

**Answer:**
| Section | Contents |
|---|---|
| **Text** | the **program code** |
| **Data** | **global variables**, divided into **initialized data** and **uninitialized data** |
| **Heap** | **memory dynamically allocated during run time** (`malloc()` / `free()`) |
| **Stack** | **temporary data for function calls: function parameters, return addresses, local variables** |
- A **separate section holds `argc` and `argv`** for `main()`. The **stack and heap grow toward each other**, and the OS must keep them from overlapping. The PC and registers form the **current activity**, not a memory section.
- `x` → **uninitialized data**; `y` → **initialized data**; `values`, `i` (locals) → **stack**; the five `int`s → **heap**; `argc`/`argv` → **argc/argv section**; code of `main` → **text**.

## [X3-03] ch3 | Process states and transition events
Name the five process states. Give the transition caused by each event: (a) admitted, (b) selected by the CPU scheduler, (c) timer interrupt, (d) a disk read is issued, (e) it calls `wait()` for its child, (f) the disk read completes, (g) it calls `exit()`.

**Answer:**
**New** (being created — allocating resources), **ready** (waiting to be assigned to a CPU core), **running** (instructions are being executed), **waiting** (waiting for some event to occur), **terminated** (finished — deallocating resources).
| Event | Transition |
|---|---|
| (a) admitted | **new → ready** |
| (b) scheduler dispatch (CPU scheduling) | **ready → running** |
| (c) timer interrupt | **running → ready** (interrupt) |
| (d) I/O request | **running → waiting** (I/O or event wait) |
| (e) `wait()` for a child | **running → waiting** (event wait) |
| (f) I/O completion | **waiting → ready** (I/O or event completion) |
| (g) `exit()` | **running → terminated** |
- **There is no waiting → running and no ready → waiting**: a process whose event completes **re-enters the ready queue** and must be dispatched; a ready process is not executing, so it cannot request I/O.
- On one core **at most one process is running**; any number can be ready or waiting.

## [X3-04] ch3 | PCB contents; process table; Linux task_struct
What is a Process Control Block (PCB) and what does it contain? How does the OS keep track of all PCBs, e.g., in Linux?

**Answer:**
The **PCB (task control block)** is a **kernel data structure** holding **all information associated with a process**:
1. **Process state** — new, ready, running, waiting, …
2. **Program counter** — location of the next instruction to execute
3. **CPU registers** — accumulators, index registers, **stack pointers**, general-purpose registers, condition codes
4. **CPU-scheduling information** — **priority, pointers to scheduling queues**, scheduling parameters
5. **Memory-management information** — memory allocated (page / segment tables)
6. **Accounting information** — CPU time used, clock time elapsed, time limits
7. **I/O status information** — I/O devices allocated, **list of open files**
- Each process has a unique **PID** (positive integer; **PID 1 = init / systemd**). The **process table (process list)**, indexed by PID, points to every PCB. **Linux** keeps a **circular doubly linked list (task list) of `struct task_struct`** (pid, state, time_slice, parent, children, files, mm).
- The PCB is what is **saved and restored in a context switch**.

## [X3-05] ch3 | Threads within a process
How is a thread represented, and what do the threads of one process share? Why use several threads in a process?

**Answer:**
- A **thread** is a **single unique execution context**: its own **program counter, registers, execution flags and stack**. It is executing when this context is **resident in the CPU registers**.
- Threads of a process **run within the same address space — they share code, data and open files**, while each keeps **its own thread state**.
- So a process can **perform more than one task at a time** (e.g., a **web browser** with one thread displaying images or text and another **retrieving data from the network**), and on **multicore systems its threads run in parallel**. A traditional single-threaded process is a **heavy-weight process**.

## [X3-06] ch3 | I/O-bound vs CPU-bound; good process mix
Define I/O-bound and CPU-bound processes. Why should the long-term scheduler select a good process mix?

**Answer:**
- **I/O-bound** — spends **more time doing I/O than computation**; **many short CPU bursts**. **CPU-bound** — **generates I/O requests infrequently**, mostly computing; **few very long CPU bursts**.
- A **good mix keeps both the CPU and the I/O devices busy**. If all processes are I/O-bound, the **ready queue is almost always empty** and the CPU idles; if all are CPU-bound, the **I/O wait queues are almost always empty** and the devices sit unused.
- Hence the long-term scheduler (mainframes) **strives for a good process mix** to maximize **CPU utilization**.

## [X3-07] ch3 | Scheduling queues and the queueing diagram
Which scheduling queues does the OS maintain, and how does a process migrate among them during its lifetime?

**Answer:**
- **Ready queue** — processes **in main memory, ready and waiting to execute**. **Wait queues** — processes **waiting for an event** such as I/O completion (one per device or event). The queues link **PCBs** (the PCB holds **pointers to scheduling queues**).
- A new process joins the ready queue until it is **dispatched**. While running, it leaves the CPU when it:
  1. **issues an I/O request** → I/O wait queue → back to ready when the I/O completes;
  2. **uses up its time slice** → straight back to the ready queue;
  3. **creates a child and waits for its termination** → wait queue until the child ends;
  4. **waits for an interrupt** → wait queue until the interrupt occurs.
- This repeats until it terminates. **The state of a process is determined by the queue it is in** (the running process is the exception), and **each queue can have its own scheduling policy**.

## [X3-08] ch3 | Long-, short- and medium-term schedulers compared
Compare the long-term, short-term and medium-term schedulers. What is the degree of multiprogramming, and why must the short-term scheduler be fast?

**Answer:**
| | **Long-term (job) scheduler** | **Short-term (CPU) scheduler** | **Medium-term scheduler** |
|---|---|---|---|
| Role | **selects which processes are brought into memory** from the job queue (allocates memory) | **selects a process from the ready queue and allocates a CPU core** | **swaps a process out to disk and back in later** |
| Frequency | **very infrequent** (seconds, minutes) — may be slow | **very frequent** (milliseconds) — **must be fast** | when the workload is too heavy |
| Degree of multiprogramming | **dictates it** | no direct effect | **reduces it** |
| Where used | **mainframes / minicomputers, not PCs** | all systems | mainframes / minicomputers |
- **Degree of multiprogramming = the number of processes currently residing in memory.**
- The short-term scheduler runs every few milliseconds: if choosing takes 1 ms and the process then runs 10 ms, **1/(10 + 1) ≈ 9 % of the CPU is wasted on scheduling**.

## [X3-09] ch3 | Swapping and the medium-term scheduler
What is swapping? When and why does the medium-term scheduler swap a process out?

**Answer:**
- **Swapping**: the **medium-term scheduler removes a partially executed process from memory, stores it temporarily on secondary storage (swap space)**, and later **brings it back into memory to continue execution** where it left off.
- **When**: the **degree of multiprogramming must be reduced** — **memory is over-committed / the workload is heavy** and execution becomes slow (or to improve the process mix).
- **Why**: it **frees memory and other resources for the remaining processes**, so they run faster; the swapped-out process resumes when resources become available.

## [X3-10] ch3 | Context switch: saved state and kernel actions
What is a context switch? Describe the actions the kernel takes, and name events that cause one.

**Answer:**
- A **context switch** occurs when the **CPU switches from one process (or thread) to another**: the OS must **save the state of the old process and load the saved state of the new process**. The **context is represented in the PCB** — **CPU registers, program counter, stack pointer**, process state, memory-management information.
- Kernel actions: (1) an **interrupt or system call** enters the kernel; (2) **save the running process's context in its PCB**, set its state (ready / waiting) and queue it; (3) the **short-term scheduler selects** the next process; (4) **restore that process's context from its PCB** and resume it in user mode. Architecture-specific work such as **flushing data and instruction caches** may also be needed.
- Causes: **timer interrupt (time slice expired)**; a **system call** that blocks (I/O request, `wait()`) or lets the scheduler pick another process (e.g., `fork()`); an **interrupt that readies a higher-priority process**; **process termination**.

## [X3-11] ch3 | Context-switch overhead; multiple register sets
Why is context-switch time overhead, and what does it depend on? Some CPUs have multiple register sets: what happens if the new context is already in a register set, and if it is not?

**Answer:**
- **Context-switch time is pure overhead — the system does no useful work while switching**; **the more complex the OS and the PCB, the longer the switch**.
- It is **highly dependent on the hardware**: **memory speed, the number of registers to copy, and special instructions** (e.g., a single instruction to load or store all registers).
- **Multiple register sets** (e.g., **SUN UltraSPARC**): if the new context is already loaded, the switch **only changes the pointer to the current register set** — very fast. If it is in memory and **all register sets are in use**, one set must be **saved to memory** and the new context **loaded from memory** into it — slower, like an ordinary switch.

## [X3-12] ch3 | Context switch vs mode switch
Is a context switch the same as switching from user mode to kernel mode? Explain.

**Answer:**
**No.**
- A **mode switch** flips the **mode bit** (user ↔ kernel) on a **system call, interrupt or trap**; the CPU saves the running process's state, runs kernel code and may **return to the same process** — e.g., `getpid()` returns at once and **no other process runs**.
- A **context switch** changes **which process runs**: the kernel **saves the old process's state in its PCB and loads another process's saved state**. It is **performed by the kernel (in kernel mode)**, typically after a **timer interrupt or a blocking system call**.
- So every context switch requires entering the kernel, but **a mode switch does not always lead to a context switch**.

## [X3-13] ch3 | Interrupt-driven I/O and device controllers
Explain how the CPU and a device controller cooperate to perform interrupt-driven I/O.

**Answer:**
- **I/O devices and the CPU execute concurrently and asynchronously.** **Each device controller is in charge of a particular device and has a local buffer.**
- The **device driver** starts the operation by loading the controller's registers; the **controller moves data between the device and its local buffer** while the **CPU continues other work**.
- When finished, the **device controller informs the CPU by causing an interrupt** (signal on the **interrupt-request line**): for input, **data is available in the local buffer**; for output, the **I/O operation is completed**.
- The CPU **handles the interrupt** — for slow devices (keyboard, mouse) the **CPU moves the data between the local buffer and main memory** — and then **returns to the interrupted instruction**.

## [X3-14] ch3 | Interrupt handling and the interrupt vector
What is an interrupt? Describe how the CPU handles one, and explain why an interrupt vector is used.

**Answer:**
- An **interrupt** is a **signal from hardware to the CPU, through an interrupt-request line, that an event requires CPU attention** (e.g., **I/O completion**). It **transfers control to an interrupt service routine (interrupt handler)**, which is **part of the kernel**.
- Handling: the CPU **senses the interrupt-request line after executing every instruction**; on a signal it **saves the state of the interrupted process** (PC, registers), **reads the interrupt number**, **uses it as an index into the interrupt vector** and **jumps to the handler** in kernel mode; afterwards it **restores the state and returns to the interrupted instruction**.
- **Interrupt vector** = a **table (array) holding the addresses of the interrupt handlers**, indexed by each interrupt's **unique number** → **fast dispatch to the proper handler**, with no generic routine needed to find the source first.
- **All modern operating systems are interrupt-driven** (hundreds of interrupts per second).

## [X3-15] ch3 | Maskable vs nonmaskable interrupts; priority levels
Distinguish maskable and nonmaskable interrupts. What are interrupt priority levels for?

**Answer:**
- Most CPUs have **two interrupt-request lines**:
  - **Nonmaskable** — **cannot be turned off**; reserved for events such as **unrecoverable memory errors and power failure**.
  - **Maskable** — **can be turned off by the CPU before executing critical instruction sequences that must not be interrupted**; used by **device controllers to request service**, which can be delayed.
- **Interrupt priority levels** let the CPU **defer low-priority interrupts without masking all interrupts**, and let a **high-priority interrupt preempt the execution of a low-priority interrupt** — interrupts are not all serviced the same way. A **trap (software interrupt) gets a relatively low priority** compared with device interrupts.

## [X3-16] ch3 | Programmed I/O vs DMA; DMA transfer steps
Why is DMA used instead of programmed I/O? Describe how a DMA transfer is set up and completed.

**Answer:**
- **Programmed I/O**: the **CPU runs special I/O instructions to move one byte at a time** between memory and a device — acceptable for **slow devices** (keyboard, mouse), but for **fast devices and large transfers** (disk) it **wastes CPU time** on data movement.
- **DMA**: the **DMA controller bypasses the CPU and transfers a whole block directly between the I/O device and memory**; the CPU/OS only **initializes** it, which **relieves the CPU** to run other work concurrently.
- Set-up: the OS **writes a DMA command block into memory** (**source and destination addresses, read or write mode, number of bytes**) and **writes its location to the DMA controller**; the controller uses **bus mastering** (grabs the bus, momentarily keeping the CPU out of main memory) and **interrupts the CPU once, when the transfer is complete** — not after every byte.
- Six steps (disk → buffer X): (1) the driver is told to transfer disk data to buffer X; (2) the driver tells the disk controller to transfer C bytes to X; (3) the disk controller initiates the DMA transfer; (4) it sends each byte to the DMA controller; (5) the DMA controller writes the bytes to X, **increasing the address and decreasing C until C = 0**; (6) **when C = 0, DMA interrupts the CPU** to signal completion.

## [X3-17] ch3 | Dual-mode operation, mode bit, privileged instructions
What is dual-mode operation and why is it needed? How does the hardware support it, and what happens when a user program executes a privileged instruction?

**Answer:**
- **Dual-mode operation** separates **user mode** (user code) from **kernel mode** (OS code); it **allows the OS to protect itself and other system components** — the **OS from errant users, and errant users from one another**.
- A **mode bit provided by hardware** shows the current mode: **user = 1, kernel = 0**. Some instructions are **privileged — executable only in kernel mode** (e.g., **I/O control, timer management, interrupt management**), and devices are accessed only in kernel mode, so user programs must request OS services through **system calls**.
- A **privileged instruction attempted in user mode is treated by the hardware as illegal and trapped to the OS**; it is not executed.
- **Control starts in kernel mode**; the mode is **set to user mode before control passes to a user application** and returns to kernel mode **via an interrupt, a trap or a system call**; **return from a system call resets user mode**.

## [X3-18] ch3 | Which operations must be privileged
Which of these must be privileged, and why? (a) set the value of the timer (b) read the clock (c) clear memory (d) issue a trap instruction (e) disable interrupts (f) modify entries in the device-status table (g) access an I/O device.

**Answer:**
- **Privileged: (a), (c), (e), (f), (g)** — set the timer, clear memory, disable interrupts, modify the device-status table, access I/O devices. A user program doing these could **monopolize the CPU** (timer, interrupts), **wipe out the OS or other processes** (clear memory), or **bypass the OS's control of devices**.
- **Not privileged: (b) read the clock** (harmless, read-only) and **(d) issue a trap instruction** — a trap is exactly **how a user program requests an OS service (system call)**, so it must work in user mode.

## [X3-19] ch3 | Timer: OS always regains control
How does the OS ensure that a user program cannot keep the CPU forever (e.g., one stuck in an infinite loop)?

**Answer:**
- With a **timer**: before giving control to a user program, the OS **sets the timer to interrupt after a specified period** (a counter decremented by the clock; an **interrupt occurs when it reaches 0**).
- The **timer interrupt transfers control back to the OS in kernel mode**, which may **treat it as a fatal error, give the program more time, or schedule another process** (time slice expired).
- **Instructions that modify the timer are privileged**, so a user program cannot turn it off — hence **a user program always returns control to the OS**.

## [X3-20] ch3 | Three types of mode transfer
Compare the three ways control passes from user mode to kernel mode: system call, interrupt, and trap/exception.

**Answer:**
| Type | Nature | Examples |
|---|---|---|
| **System call** | **a user process requests a service from the OS** — like a function call, but **outside** the user process | `read()`, `write()`, `exit()`, `fork()` |
| **Interrupt** | **external, asynchronous event**, **independent of the user process** | **timer**, **I/O completion** |
| **Trap / exception** | **internal, synchronous event** caused by the running process | **protection violation (segmentation fault)**, **divide by zero**, privileged instruction in user mode |
- All three **set the mode bit to kernel mode**, save the running process's state and run kernel code; the return resets user mode. A **trap is a software-generated interrupt**, and a **system call is carried out by executing a trap**.

## [X3-21] ch3 | System-call path: printf() to write()
In terms of user mode and kernel mode, explain what happens when a program calls `printf("hi\n")`.

**Answer:**
1. **`printf()` is a C library (API) function running in user mode**; it formats the text into a buffer and **invokes the `write()` system call** on fd 1 (buffering may delay this until a newline or flush).
2. The `write()` wrapper puts the **system-call number and parameters in registers** and executes a **trap** → the hardware sets the **mode bit to kernel mode (0)** and jumps to the kernel's system-call handler.
3. The kernel **indexes the system-call table** with the number, runs the **write service routine** (device driver) and stores the **return value** (bytes written, or −1).
4. **Return from the system call resets the mode bit to user mode (1)** and execution continues after the call. If the device is busy, the process may **block (running → waiting)** while another process runs.

## [X3-22] ch3 | Beyond two modes: rings, VMM, machine switch
How can dual-mode operation be extended beyond two modes? What is a machine switch?

**Answer:**
- **Intel processors have four protection rings: ring 0 = kernel mode, ring 3 = user mode**; rings 1 and 2 could run OS services but are **rarely used**. **ARMv8 systems have seven modes.**
- **CPUs that support virtualization have a separate mode for the virtual machine manager (VMM)**, with **more privileges than user processes but fewer than the kernel**.
- A **machine switch** is the VMM's counterpart of a context switch: it **saves the entire machine state of one guest OS — registers, PC and, unlike a context switch, any privileged hardware state** — **restores the new VM's machine state and jumps to its PC** (inside its kernel or in a user application).

## [X3-23] ch3 | Process creation options; tree of processes
When a parent creates a child, what are the options for (a) sharing resources, (b) execution, and (c) the child's address space? Give UNIX examples.

**Answer:**
- Processes form a **tree of processes**: a **parent creates children, which create their own children**; on Linux the root is **systemd (PID 1)**, and each process has a unique **pid**. The child needs CPU time, memory, files and I/O devices, and the parent may pass it **initialization data**.
- (a) **Resource sharing**: **parent and children share almost all resources — `fork()`** (the child gets copies of everything); **children share a subset of the parent's resources — `clone()`**; or **they share no resources**.
- (b) **Execution**: the **parent continues to execute concurrently with its children** (shell runs `a.out &`), or the **parent waits until some or all children have terminated** (shell runs `a.out` and waits).
- (c) **Address space**: the **child is a duplicate of the parent (same program and data)** — UNIX `fork()`; or the **child has a new program loaded into it** — `exec()` after `fork()`.

## [X3-24] ch3 | fork() return values and why two
What does `fork()` return, and why must the parent and the child receive different values?

**Answer:**
- **`fork()` takes no parameters**; each process gets **exactly one return value**:
  - **> 0 in the parent** — the **PID of the newly created child**;
  - **0 in the child**;
  - **−1 in the original process if it fails — no child is created** (`errno` is set).
- The **child duplicates the parent's entire address space, including the program counter**, so **both continue at the instruction right after `fork()` with identical code**; the **return value is the only way to tell which process is running**, so the two can take different branches. The parent also learns the **child's PID**, needed later to **wait for or terminate** that child.
- Which process runs first is **decided by the CPU scheduler**; their execution may interleave.

## [X3-25] ch3 | fork() steps, copy-on-write, clone()
What steps does the kernel take to implement `fork()`? Why is this expensive, and how does Linux speed it up?

**Answer:**
- Steps: (1) **create and initialize the PCB** in the kernel (unique PID); (2) **create a new address space** (allocate memory); (3) **initialize it with a copy of the entire contents of the parent's address space** — **time consuming**; (4) **inherit the parent's execution context** (e.g., **open files**); (5) **inform the CPU scheduler that the child is ready to run**.
- The copy is wasted when the child **calls `exec()` immediately** and discards it.
- **Copy-on-write (COW)**: **parent and child share a single copy of the pages**, and a page is **copied only when either process writes to it**. If `exec()` follows `fork()`, the pages **never need to be copied** → **greatly speeds up process creation**, while each process still behaves as if it had its own copy.
- Linux implements `fork()` with the more general **`clone()`** system call, whose **flags specify which resources parent and child share**.

## [X3-26] ch3 | After fork(): copied, shared, different
After a successful `fork()`, what does the child get from the parent and what is different? Which of the stack, heap and shared-memory segments are shared?

**Answer:**
- **Duplicated (the child gets its own copy)**: the **address space — text, data, heap, stack**, hence **global and local variables**; the **program counter and registers**; **open file descriptors** (referring to the same files and pipes); **current and root directory**, process resources, **resource limits**; customized **signal handlers**.
- **Different**: the **PID** (and parent PID), the **return value of `fork()`**, **running time** and **running state**.
- **Stack and heap are copied, not shared** — a change by one process is **invisible to the other**; of the three, **only shared-memory segments are shared**.
- Because descriptors are inherited, a **pipe created before `fork()`** connects parent and child.

## [X3-27] ch3 | Output: child modifies a global array
What is printed at LINE X and LINE Y?
```c
#define SIZE 5
int nums[SIZE] = {0, 1, 2, 3, 4};
int main() {
    int i;
    pid_t pid = fork();
    if (pid == 0) {
        for (i = 0; i < SIZE; i++) {
            nums[i] *= -i;
            printf("CHILD: %d ", nums[i]);  /* X */
        }
    } else if (pid > 0) {
        wait(NULL);
        for (i = 0; i < SIZE; i++)
            printf("PARENT: %d ", nums[i]); /* Y */
    }
    return 0;
}
```

**Answer:**
- **LINE X (child): `CHILD: 0 CHILD: -1 CHILD: -4 CHILD: -9 CHILD: -16`**
- **LINE Y (parent): `PARENT: 0 PARENT: 1 PARENT: 2 PARENT: 3 PARENT: 4`**, printed **after** the child's output because of `wait(NULL)`.
- **`fork()` gives the child its own copy of the parent's data section**, so the child changes **only its own copy of `nums`**; the parent's array is unchanged. The same holds for the **heap**: after `int *h = malloc(...)`, both processes hold the **same address in `h`**, but `(*h)++` in the child does not change the parent's value.

## [X3-28] ch3 | Output: fork() return value vs getpid()
The actual PIDs of the parent and the child are 2600 and 2603. What values are printed at lines A, B, C and D?
```c
pid_t pid, pid1;
pid = fork();
if (pid == 0) {                         /* child */
    pid1 = getpid();
    printf("child: pid = %d", pid);     /* A */
    printf("child: pid1 = %d", pid1);   /* B */
} else if (pid > 0) {                   /* parent */
    pid1 = getpid();
    printf("parent: pid = %d", pid);    /* C */
    printf("parent: pid1 = %d", pid1);  /* D */
    wait(NULL);
}
```

**Answer:**
- **A = 0** (`fork()` returns 0 in the child); **B = 2603** (`getpid()` gives the child's own PID); **C = 2603** (`fork()` returns the child's PID to the parent); **D = 2600** (the parent's own PID).
- Key: **`getpid()` always returns the caller's own PID** (`getppid()` its parent's), whereas **`fork()`'s return value is the child's PID only in the parent**.

## [X3-29] ch3 | Output: unflushed printf buffer copied by fork()
What is printed (a) if every `printf` is flushed immediately, (b) if stdout is buffered? Why can `./a.out > out.txt` show `A` twice even with `printf("A\n")`?
```c
int main() {
    printf("A");
    fork();
    printf("B\n");
    return 0;
}
```

**Answer:**
- (a) **Flushed immediately: `A` once, `B` twice** → `AB` then `B`. `A` is printed before `fork()`, and **both processes execute `printf("B\n")`**.
- (b) **Buffered: `AB` is printed twice.** The unflushed `"A"` is still in the **stdio buffer inside the process's address space**, and **`fork()` copies the address space, buffer included**, so each process later flushes its own `"A"` followed by `"B\n"`.
- When stdout is a **file or pipe it is fully buffered**, so even `"A\n"` is still in the buffer at `fork()` and appears twice; a terminal is line-buffered and flushes at `\n`.
- Fix: **`fflush(stdout)` before `fork()`**.

## [X3-30] ch3 | exec(): success, failure, execlp vs execvp
What does a successful `exec()` do to the calling process? Does it create a new process or change the PID? When is the statement after `exec()` executed? Contrast `execlp()` and `execvp()`.

**Answer:**
- **`exec()` changes the program being run by the current process: it creates a new process image from an executable file, replacing the address space (text, data, heap, stack).** It **does not create a new process — the PID, PCB and open file descriptors stay the same** (so redirection set up before `exec()` still applies).
- **A successful `exec()` never returns**, so the code after it is **never executed**; **only if it fails** (e.g., program not found, no permission) does it **return −1**, and execution continues with the next statement.
- **`execlp("ls", "ls", "-l", NULL)`** passes the arguments as a **list** (count known at compile time); **`execvp(args[0], args)`** passes an **array (vector)** (count known only at run time, as for PA1's parsed commands). **p = search the PATH**. **`argv[0]` is the program name**, and the list/array **must end with `NULL`** because exec has no argument count and stops at the NULL — hence PA1's array of **9 entries for at most 8 arguments**.

## [X3-31] ch3 | Output: exec in a loop succeeds/fails
How many processes are created and what is printed if (a) `execlp()` succeeds, (b) `execlp()` fails? What should the child do after a failed exec?
```c
int main() {
    for (int i = 0; i < 3; i++) {
        pid_t pid = fork();
        if (pid == 0)
            execlp("echo", "echo", "hi", NULL);
    }
    while (wait(NULL) > 0)
        ;
    printf("done\n");
    return 0;
}
```

**Answer:**
- **(a) exec succeeds: 4 processes** (parent + 3 children). Each child **becomes `echo`**, prints **`hi`** and terminates — it **never returns to the loop**. The parent reaps all three and prints **`done` once, last**: `hi`, `hi`, `hi`, `done`.
- **(b) exec fails: `execlp()` returns −1 and the child continues the loop as a copy of the parent**, so every process forks in each remaining iteration → **$2^3 = 8$ processes**, **`done` printed 8 times**, no `hi`.
- So a child must **`exit()` after a failed exec** (e.g., `perror("exec"); exit(1);`). In PA1 a missing exit leaves an **extra shell process running** (redundant processes), so the **start and end PIDs no longer match**.

## [X3-32] ch3 | Why a shell uses fork, exec, wait
Why does a shell create a child with `fork()` and call `exec()` in the child, instead of calling `exec()` directly? Why is it useful that UNIX separates the two calls?

**Answer:**
- If the shell called `exec()` itself, **its own image would be replaced by the command**, and the **shell would be gone** when the command ended. So the shell **`fork()`s a child**, the **child `exec()`s the command** (overlays the new program), and the **parent `wait()`s for the child**, then reads the next command. For a **background command (`a.out &`) the shell does not wait**.
- **Most OSes create a process and load a program in one step; UNIX splits this into `fork()` and `exec()`.** The child can therefore **run code between the two calls to set up the new program's environment** — **I/O redirection with `dup2()`, connecting pipes, closing file descriptors** — without affecting the shell. **Copy-on-write** keeps the extra `fork()` cheap.

## [X3-33] ch3 | PA1: cd and exit as built-ins
In PA1, why can `cd` not be executed with `exec*()`, and how is it implemented? Why is `exit` also a built-in?

**Answer:**
- The **current working directory is a per-process attribute**. If the shell forked a child to change directory, **only the child's directory would change, and the change is lost when the child exits** — a child **cannot change its parent's directory**, so the shell would stay where it was.
- So `cd` is a **built-in command run inside the shell process itself, without `fork()`**, using **`chdir(path)`**: **0 on success, −1 on error** (print "Myshell cd command error"); it accepts absolute and relative paths, including `.` and `..`.
- **`exit` must terminate the shell process itself**, so it is likewise handled inside the shell, not in a child.

## [X3-34] ch3 | PA1: why system() and popen() are banned
Why are `system()` and `popen()` forbidden in PA1? Why must pipes be used with `open/read/write/close` rather than `fopen/fread/fwrite/fclose`?

**Answer:**
- **`system()` creates a system shell (e.g., bash) that runs the command, and the parent is blocked until it finishes**; **`popen()`** also **has a shell run the command** concurrently and returns a **`FILE*`** for one-way communication with it. Using them **hands all process creation, redirection and piping to another shell**, defeating the purpose of PA1 (**process management and IPC through system calls**); they are detected by pattern matching and score **0 marks**.
- PA1 must use **`fork`, `exec*`, `wait`, `pipe`, `dup/dup2`**. **`FILE*` is a high-level struct defined only in the C standard library and cannot be used in pipe operations**; the low-level **`open/read/write/close` work on file descriptors**, which is what `pipe()` returns and `dup2()` manipulates.

## [X3-35] ch3 | PA1: Ctrl-C (SIGINT) handling with signal()
How does PA1 customize Ctrl-C handling? What is a signal, and what does the handler receive?

**Answer:**
- A **signal is a software-generated interrupt** that **notifies a process that an event has occurred**. **Ctrl-C** makes the OS send **SIGINT (signal number 2)**, whose **default handler terminates** the process; SIGINT is **asynchronous** (caused by an event outside the process).
- PA1 **overrides the default with a user-defined handler** registered at start-up; the **signal number is passed to the handler as its parameter**:
```c
void handler(int sig) {          /* sig = 2 */
    printf("Myshell (pid=%d) terminates"
           " by Ctrl-C with signal: %d\n",
           getpid(), sig);
    exit(0);
}
/* in main(): */
signal(SIGINT, handler);
```
- **Child processes inherit the customized handler** through `fork()`. The PID printed must equal the start PID; otherwise redundant shell processes exist.

## [X3-36] ch3 | Termination: exit, wait, abort, cascading
Describe how a process terminates normally and how its parent obtains the exit status. Why might a parent terminate a child, and what is cascading termination?

**Answer:**
- After its last statement a process **asks the OS to delete it with `exit()`**, called **directly or indirectly** (the **C run-time library calls `exit()` when `main()` returns**). The OS **de-allocates and reclaims its resources: memory (program, data, heap, stack), open files, I/O buffers**.
- It may **return a status value (integer) to its waiting parent**: **`pid = wait(&status);`** returns the **PID of the terminated child** (so the parent knows which child ended) and stores its **exit status** (`exit(0)` = normal, non-zero = error); `wait()` returns −1 if there are no children.
- A parent may terminate a child (**`abort()`** on UNIX/Linux in the slides, **`TerminateProcess()`** on Windows; a process can also be killed with `kill()`) because the **child has exceeded its allocated resources**, the **task assigned to the child is no longer required**, or the **parent is exiting and the OS does not allow a child to continue**. The parent knows the **child's PID from `fork()`**.
- **Cascading termination**: some OSes **do not allow a child to exist if its parent has terminated — when a process terminates, all its children must also be terminated, initiated by the OS**. UNIX/Linux instead **re-parent orphans to init/systemd**.

## [X3-37] ch3 | Zombie vs orphan; role of init/systemd
Compare zombie and orphan processes, and explain the role of `init`/`systemd` in process termination.

**Answer:**
| | **Zombie** | **Orphan** |
|---|---|---|
| Definition | **has terminated, but its parent has not yet called `wait()`** | **its parent terminated without calling `wait()`** |
| What remains | only its **PID, process-table entry and PCB** (holding the **exit status**); all other resources released | everything — it **may still be running** |
| Runnable? | **no** — it has no address space | **yes** (if cascading termination is not used) |
| Cleaned up by | the **parent's `wait()`**, which releases the PID, entry and PCB | **init/systemd**, its new parent |
- **All processes pass through the zombie state, usually only briefly.** The entry is kept because the **process table holds the exit status** that the parent collects; if the child is already a zombie, `wait()` returns at once.
- **init/systemd (PID 1) is assigned as the new parent of orphans and periodically calls `wait()`**, collecting their exit status and releasing their PID and process-table entry; otherwise **parentless terminated processes would remain zombies forever, wasting system memory**.

## [X3-38] ch3 | Zombie or orphan? Two scenarios
What happens to the child in each case? (A) The child calls `exit(0)` at once; the parent calls `sleep(30)` and then `wait(NULL)`. (B) The child calls `sleep(30)` and then prints; the parent returns from `main()` at once without `wait()`.

**Answer:**
- **(A) The child is a zombie for about 30 seconds**: it has terminated, but its **PID, process-table entry and PCB (exit status) remain until the parent's `wait(NULL)`** reaps it; then they are released.
- **(B) The child becomes an orphan**: the parent ends first, so the **shell prompt reappears before the child's output**. The child **keeps running**, is **re-parented to init/systemd (PID 1)**, prints after the prompt, and when it exits **init/systemd's `wait()` reaps it**, so it does not remain a zombie.
- Correct practice: the parent calls **`wait()` for each child** before it exits.

## [X3-39] ch3 | Independent vs cooperating processes
Distinguish independent and cooperating processes. Give reasons for allowing processes to cooperate.

**Answer:**
- **Independent** processes cannot affect or be affected by other processes; **cooperating processes can affect or be affected by other processes** (e.g., they **share data**), so they need an **interprocess communication (IPC) mechanism** to exchange data.
- Reasons: **information sharing** — several applications need the same information (e.g., **copy and paste**); **computation speedup** — split a task into **parallel subtasks** (e.g., machine-learning jobs on multiple cores); **modularity** — divide system functions into separate processes or threads; **convenience** — a user can work on many tasks at once.

## [X3-40] ch3 | Shared memory vs message passing
Compare the two IPC models, shared memory and message passing, giving an advantage of each.

**Answer:**
| | **Shared memory** | **Message passing** |
|---|---|---|
| How | a **region of memory is shared**; processes **read and write the shared region** — **implicit** communication | **explicit messages** exchanged with **`send()` / `receive()`** |
| Kernel role | **system calls only to set up the region**, then ordinary memory accesses | **kernel intervention (system call) for every message** |
| Speed | **faster** | slower for large data |
| Synchronization | **the processes must coordinate themselves** (e.g., producer–consumer) | provided by the IPC facility (e.g., blocking send/receive) |
| Suits | large data on one machine | **small amounts of data; distributed environments** |
- Message passing lets processes **communicate and synchronize without sharing the address space** — **Mach** uses it as its primary IPC, and Windows provides a form of it. Both models are commonly used.

## [X3-41] ch3 | Bounded buffer: empty, full, BUFFER_SIZE − 1
In the shared-memory bounded-buffer solution with `in` and `out`, when is the buffer empty or full, and why can it hold only `BUFFER_SIZE - 1` items? With `BUFFER_SIZE = 10`, `in = 3`, `out = 7`, how many items are in the buffer?

**Answer:**
- **Unbounded buffer**: no practical limit on size (only the consumer may wait). **Bounded buffer**: fixed size — the consumer waits when it is empty, the **producer waits when it is full**.
- **Empty: `in == out`.** **Full: `(in + 1) % BUFFER_SIZE == out`.** The producer stores `buffer[in]` and advances `in = (in + 1) % BUFFER_SIZE`; the consumer takes `buffer[out]` and advances `out` the same way; each **busy-waits** ("do nothing") while the buffer is full or empty, which wastes CPU cycles.
- Since **`in == out` already means empty**, a completely full buffer would look identical, so **one slot is always left unused → at most `BUFFER_SIZE - 1` items**.
- Items = `(in - out + BUFFER_SIZE) % BUFFER_SIZE` = (3 − 7 + 10) % 10 = **6** (slots 7, 8, 9, 0, 1, 2).
- Using all slots needs a shared **`count`**, but then `count++` / `count--` in two processes must be **synchronized**, or a **race condition** occurs (Chapter 6).

## [X3-42] ch3 | Message passing: link and design choices
What must processes P and Q do to communicate by message passing? List the design choices for implementing the link, and compare fixed- and variable-size messages.

**Answer:**
- P and Q must **establish a communication link** between them, then **exchange messages with the primitives `send(message)` and `receive(message)`**.
- Design choices for the link: **direct or indirect communication** (naming); **synchronous (blocking) or asynchronous (non-blocking)** send/receive; **automatic or explicit buffering**.
- **Fixed-size messages** keep the **system-level implementation straightforward but make programming harder**; **variable-size messages need a more complex system implementation but make programming simpler**.

## [X3-43] ch3 | Direct vs indirect communication; mailbox sharing
Compare direct and indirect communication. If P1, P2 and P3 share mailbox A, P1 sends a message, and both P2 and P3 call `receive()`, who gets it?

**Answer:**
| | **Direct** | **Indirect (mailbox)** |
|---|---|---|
| Naming | **processes name each other explicitly**: `send(P, msg)`, `receive(Q, msg)` | **send to / receive from a mailbox**: `send(A, msg)`, `receive(A, msg)`; each mailbox has a **unique id** |
| Link set-up | **automatic**; each needs only the other's **identity** | **only if both processes share a mailbox** |
| Processes per link | **exactly one pair** | **may be more than two** |
| Links per pair | **exactly one** | **several**, one per shared mailbox |
| Drawback | **limited modularity**: changing a process's identifier means re-examining all other processes | the OS must provide **create, send/receive and destroy** for mailboxes |
- Who receives depends on the rule the system adopts: **(1) allow a link to be associated with at most two processes; (2) allow only one process at a time to execute `receive()`; or (3) let the system select the receiver arbitrarily and notify the sender who the receiver was.**

## [X3-44] ch3 | Blocking vs non-blocking send/receive; rendezvous
Explain blocking and non-blocking send and receive. What is a rendezvous, and how does it simplify producer–consumer?

**Answer:**
| | **Blocking (synchronous)** | **Non-blocking (asynchronous)** |
|---|---|---|
| `send()` | the **sender is blocked until the message is received** by the receiving process or mailbox | the **sender sends and resumes** its operation |
| `receive()` | the **receiver blocks until a message is available** | the **receiver retrieves either a valid message or null** |
- **When both `send()` and `receive()` are blocking, we have a rendezvous** between the sender and the receiver.
- Producer–consumer becomes **trivial**: the producer calls **`send(next_produced)`** and the consumer **`receive(next_consumed)`**; the blocking calls do the synchronization — **no shared buffer, `in`/`out` or busy waiting**.
- Blocking is simple but the sender may wait unnecessarily; non-blocking allows more concurrency — so systems usually offer both.

## [X3-45] ch3 | Buffering: zero, bounded, unbounded capacity
Describe the three ways to implement the queue of messages on a link. When must the sender wait?

**Answer:**
| Capacity | Queue | Sender waits? |
|---|---|---|
| **Zero capacity** | **no messages are queued** on the link | **always — it must wait for the receiver (rendezvous)** |
| **Bounded capacity** | **finite length of n messages** | **only if the link is full** |
| **Unbounded capacity** | **infinite length** | **never** |
- Messages reside in this **temporary queue whether communication is direct or indirect**. Zero capacity means **no buffering**; bounded and unbounded are **automatic buffering**.
- A **UNIX pipe behaves like bounded capacity**: it has a limited size, so a **writer blocks when the pipe is full**.

## [X3-46] ch3 | Pipe design issues; ordinary vs named pipes
List the four issues to consider when implementing a pipe, and answer them for ordinary pipes and UNIX named pipes (FIFOs).

**Answer:**
| Issue | **Ordinary pipe** | **Named pipe (UNIX FIFO)** |
|---|---|---|
| Unidirectional or bidirectional? | **unidirectional** (one-way, producer → consumer) | **bidirectional** |
| Half or full duplex? | one direction only | **half-duplex** — two FIFOs for both directions at once |
| Relationship needed? | **parent–child** | **none**; several processes, typically **several writers** |
| Over a network? | **no — same machine** | **no — same machine** |
| Creation | `pipe(int fd[2])`: **fd[0] = read end, fd[1] = write end** | **`mkfifo()`**; appears as a **typical file in the file system** |
| Lifetime | **ceases to exist when the processes finish communicating and terminate** | **continues to exist until explicitly deleted** |
- An ordinary pipe **cannot be accessed from outside the process that creates it**; the parent creates it and the **child inherits it through `fork()`**. UNIX treats a pipe as a **special type of file** accessed with `read()` / `write()`.
- Windows: ordinary pipes are **anonymous pipes** (`ReadFile()` / `WriteFile()`); **Windows named pipes are full-duplex and work between the same or different machines** (`CreateNamedPipe()`).

## [X3-47] ch3 | When to use ordinary vs named pipes
Give a situation in which an ordinary pipe is more suitable than a named pipe, and one in which a named pipe is more suitable.

**Answer:**
- **Ordinary pipe**: simple **one-way communication between a parent and its child** on one machine — e.g., a shell running **`ls | sort`**, or a parent writing a file's contents into a pipe while its child **counts the characters**. No name is needed, and the pipe **disappears automatically** when they terminate.
- **Named pipe**: **unrelated processes** (no parent–child relationship) or **many writers** — e.g., several processes **write log messages to a named pipe** and a **logger server reads it** and appends them to the log file. The processes can start independently, and the FIFO **persists** until it is deleted.

## [X3-48] ch3 | Why close unused pipe ends (EOF)
Why must every process close the pipe ends it does not use? In the lab's `ls | wc -l` program, what happens if the process that runs `wc` does not close `pfds[1]`?

**Answer:**
- **`read()` on a pipe returns 0 (end-of-file) only when every write end is closed in every process.** If any process — even the reader itself — **keeps a write end open**, the reader **blocks forever** once the data is used up, and the program hangs.
- In the lab the parent runs `close(0); dup(pfds[0]); close(pfds[1]); wait(0); execlp("wc", ...)`. Without **`close(pfds[1])`**, `wc` holds a write end itself, so **after `ls` exits, `wc` never sees EOF and never prints the count**.
- Rule from the slides: **if the parent writes and the child reads, the parent must close the read end and the child must close the write end**.
- Note: since that parent calls `wait(0)` before `wc` reads, an `ls` output larger than the **pipe capacity** would make `ls` **block on a full pipe**, and both would wait forever.

## [X3-49] ch3 | What happens: blocking pipe and FIFO calls
What happens when: (a) a process reads an empty pipe whose write end is still open; (b) it reads after all write ends are closed; (c) a process writes to a full pipe; (d) a process opens a FIFO for writing while no process has it open for reading; (e) two processes read the same FIFO?

**Answer:**
- (a) **`read()` blocks** until data is written — pipe **read/write are blocking I/O**.
- (b) **`read()` returns 0 = end-of-file** (after any remaining data has been read).
- (c) **`write()` blocks** until the reader removes data — a pipe has a **limited size** (lab: a 4 KB page; 64 KB on some systems).
- (d) **`open()` blocks until a reader opens the FIFO** — FIFOs block until **both ends are opened** (`O_NONBLOCK` makes FIFO access non-blocking).
- (e) **Data read from a FIFO is discarded**, so each byte goes to **only one reader** — a FIFO **cannot broadcast** a message. Writes of **at most `PIPE_BUF` bytes are atomic**; larger writes from several writers may interleave.

## [X3-50] ch3 | Output: parent-to-child pipe program
List all possible outputs (assume each `printf` is flushed immediately).
```c
int pfds[2]; char buf[30];
pipe(pfds);
pid_t pid = fork();
if (pid != 0) {
    printf("PARENT: writing to pipe\n");
    close(pfds[0]);
    write(pfds[1], "test", 5);
    wait(NULL);
    printf("PARENT: exiting\n");
} else {
    printf("CHILD: reading from pipe\n");
    close(pfds[1]);
    read(pfds[0], buf, 5);
    printf("CHILD: read \"%s\"\n", buf);
}
printf("world!\n");
```

**Answer:**
**Two outputs** — only the first two lines can swap:
1. `PARENT: writing to pipe` / `CHILD: reading from pipe` / `CHILD: read "test"` / `world!` / `PARENT: exiting` / `world!`
2. `CHILD: reading from pipe` / `PARENT: writing to pipe` / `CHILD: read "test"` / `world!` / `PARENT: exiting` / `world!`
- The child's **`read()` blocks until the parent writes**, and the parent prints its line **before** `write()`, so `CHILD: read "test"` follows both first lines, then comes the child's `world!`.
- **`wait(NULL)`** puts `PARENT: exiting` and the parent's `world!` **after all of the child's output**. (5 bytes = `"test"` plus `'\0'`.)

## [X3-51] ch3 | Two-way communication with ordinary pipes
How can a parent and child communicate in both directions using ordinary pipes? Why not use one pipe?

**Answer:**
- An ordinary pipe is **unidirectional**, so **create two pipes before `fork()`**: `p2c` (parent → child) and `c2p` (child → parent).
- **Parent**: `close(p2c[0]); close(c2p[1]);`, then **writes to `p2c[1]`** and **reads from `c2p[0]`**. **Child**: `close(p2c[1]); close(c2p[0]);`, then **reads from `p2c[0]`** and **writes to `c2p[1]`**.
- With one pipe, a process that writes and then reads **may read back its own message**. (A UNIX FIFO is likewise **half-duplex**; two FIFOs are used for simultaneous two-way traffic.)
- Order the calls so that **one side writes first**; if both begin with a blocking `read()`, both wait forever.

## [X3-52] ch3 | Shell pipelines and multi-level pipes
How does a shell implement `ls | grep x`? How is this extended to an n-segment pipeline such as PA1's `ls | sort -r | sort | ...`?

**Answer:**
- The shell calls **`pipe(fd)` before forking**, then forks two children: **child 1 does `dup2(fd[1], 1)`** (stdout → write end) and **execs `ls`**; **child 2 does `dup2(fd[0], 0)`** (stdin ← read end) and **execs `grep x`** (it prints only the lines of `ls` output containing x). **Every process closes the pipe ends it does not use**, and the **shell closes both ends and waits for both children**. Neither program knows about the pipe — **pipes let separate tools be combined without being designed to work together**.
- **n segments**: in a **for-loop**, use **n − 1 pipes** and **n children**. Child i does `dup2(pipe[i-1][0], 0)` **if i > 0** and `dup2(pipe[i][1], 1)` **if i < n − 1**, **closes all pipe fds**, and **`execvp()`s its segment**. The parent **closes all pipe fds and waits for all n children** (PA1: at most 8 segments).

## [X3-53] ch3 | dup vs dup2; I/O redirection
What do `dup()` and `dup2()` do? How is `wc -l < in.txt > out.txt` implemented, and why is the redirection done in the child after `fork()` and before `exec()`? What appears on the screen and in `log.txt` below?
```c
int fd = open("log.txt", O_CREAT | O_WRONLY,
              S_IRUSR | S_IWUSR);
printf("A\n");
int saved = dup(1);
dup2(fd, 1);
printf("B\n"); fflush(stdout);
dup2(saved, 1);
printf("C\n");
```

**Answer:**
- **`dup(oldfd)`** copies an open descriptor into the **lowest-numbered unused fd** (so `close(1); dup(fd);` makes fd 1 refer to the file). **`dup2(oldfd, newfd)`** copies it into **`newfd`, closing `newfd` first if it is open**. Both return the new fd (−1 on error); `dup2` is clearer when several fds are replaced.
- In the **child**: `in = open("in.txt", O_RDONLY); dup2(in, 0);` and `out = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644); dup2(out, 1);`, close `in` and `out`, then **`execvp("wc", args)`**. **File descriptors stay open across `exec()`**, so `wc` reads fd 0 and writes fd 1 without knowing they are files.
- Doing it **in the child** leaves the **shell's own stdin/stdout unchanged** (its prompts still reach the terminal).
- Program: **the screen shows `A` and `C`; `log.txt` contains `B`** — `dup(1)` saves the terminal, `dup2(fd, 1)` sends stdout to the file, `dup2(saved, 1)` restores it.

## [X3-54] ch3 | Sockets, ports and the 4-tuple
What is a socket? How does client–server communication work, and how are two connections from the same client host to the same web server told apart?

**Answer:**
- A **socket is an endpoint for communication**; two processes communicating over a network use **a pair of sockets**, one at each end. A socket is **identified by an IP address (host) and a port number (process or application)**.
- The **server is always running with a well-known address and port, listening** for requests; **only clients can initiate communication**. **Ports below 1024 are well known**, reserved for standard services (**SSH 22, FTP 21, HTTP 80**); a client picks an **unused port number above 1024**.
- **The 4-tuple (source IP address, source port, destination IP address, destination port) uniquely identifies a connection.** Two connections from host 146.86.5.20 to web server 161.25.19.8 port 80 use **different client ports** (e.g., 1625 and 1626), so their 4-tuples differ.

## [X3-55] ch3 | Remote procedure calls (RPC)
What is a remote procedure call (RPC), and what is it commonly used for? How does it differ from using sockets directly?

**Answer:**
- **RPC abstracts the procedure-call mechanism for use between systems with network connections**: a client calls a procedure on a remote host **as if it were a local call**. It is a **message-based communication scheme to provide remote services**.
- A **client-side stub** packs the procedure name and parameters into a **message** and sends it to an **RPC daemon** on the server, which executes the procedure and **sends the result back in a message**.
- Common use: **distributed file systems**, implemented as a **set of RPC daemons and clients**.
- **Sockets are low-level**: they exchange an **unstructured stream of bytes**, and the application must impose structure; RPC hides the networking behind a procedure call.

## [X3-TF] ch3 | True / False quick verdicts
| Statement | T/F | Why (≤ 12 words) |
|---|---|---|
| A program is an active entity and a process is a passive one. | F | Reversed: a program is passive; a process is active. |
| Function parameters, return addresses and local variables are on the stack. | T | Heap holds `malloc()` memory; data section holds globals. |
| A process can move directly from waiting to running. | F | It goes waiting → ready, then is dispatched. |
| Issuing an I/O request moves a process from running to waiting. | T | It sits in a wait queue until the I/O completes. |
| On a single-core CPU, two processes can be running at the same instant. | F | At most one runs; the others interleave (concurrency). |
| The short-term scheduler runs infrequently, so it may be slow. | F | Invoked every few milliseconds; it must be fast. |
| The medium-term scheduler swaps processes out to disk. | T | Swapping reduces the degree of multiprogramming. |
| Context-switch time is useful work for the system. | F | Pure overhead: no useful work is done while switching. |
| A context switch means switching from user mode to kernel mode. | F | That is a mode switch; a context switch changes process. |
| Interrupts can only be generated by I/O devices. | F | Traps/exceptions are software-generated interrupts. |
| A trap is given higher priority than device interrupts. | F | Traps get relatively low priority versus device interrupts. |
| Device controllers request service on the nonmaskable interrupt line. | F | They use the maskable line; nonmaskable is for power/memory failure. |
| DMA needs one interrupt per byte transferred. | F | One interrupt when the whole block is done. |
| The mode bit is 1 in user mode and 0 in kernel mode. | T | Hardware-provided mode bit: user = 1, kernel = 0. |
| Reading the system clock must be a privileged instruction. | F | Harmless read; setting the timer is privileged. |
| A privileged instruction executed in user mode traps to the OS. | T | The hardware treats it as illegal. |
| A divide-by-zero error causes an asynchronous interrupt. | F | It is a synchronous trap (exception). |
| `fork()` returns 0 to the parent and the child's PID to the child. | F | Reversed: the child gets 0, the parent the child's PID. |
| A failed `fork()` returns −1 and creates no child. | T | The error is returned to the original process. |
| After `fork()`, the parent automatically waits for the child. | F | The parent must call `wait()` explicitly. |
| With copy-on-write, a child's writes become visible to the parent. | F | The written page is copied; the processes stay separate. |
| `exec()` creates a new process with a new PID. | F | It replaces the program image; the PID is unchanged. |
| Code after a successful `exec()` call is never executed. | T | `exec()` returns (−1) only on failure. |
| Open file descriptors stay open across `exec()`. | T | So redirection set up before `exec()` still applies. |
| A zombie keeps its PID and process-table entry until `wait()`. | T | The entry holds the exit status for the parent. |
| UNIX/Linux use cascading termination by default. | F | Orphans are re-parented to init/systemd instead. |
| Shared memory requires a system call for every access. | F | System calls are needed only to establish the region. |
| With zero-capacity buffering, the sender never waits. | F | It waits for the receiver; unbounded capacity never waits. |
| The `in`/`out` bounded buffer can hold `BUFFER_SIZE` items. | F | At most `BUFFER_SIZE - 1`, since `in == out` means empty. |
| An ordinary pipe can be used by any two processes. | F | Parent–child only; not accessible outside its creator. |
| A UNIX FIFO is full-duplex and works across machines. | F | Half-duplex, same machine only (unlike Windows named pipes). |
| Data read from a FIFO can be read again by another reader. | F | FIFO data is discarded once read; no broadcasting. |
| `read()` on a pipe returns 0 only after all write ends are closed. | T | Otherwise it blocks waiting for more data. |
| `cd` can be implemented by forking and calling `execvp("cd", ...)`. | F | It must be a built-in calling `chdir()` in the shell. |
| Only clients initiate client–server socket communication. | T | The server listens on a well-known port. |
