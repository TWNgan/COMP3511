# Cross-chapter "trace what happens" questions

## [XI-01] ch3 | read() system call: user → kernel → DMA → interrupt → return
Describe what happens, step by step, from the moment a process calls `read(fd, buf, n)` on a disk file until it gets the data.

**Answer:**
1. The program calls the **C library wrapper `read()`** (API). The wrapper puts the **system-call number and parameters in registers** and executes a **trap** (software interrupt) → **mode bit set to kernel mode**.
2. The kernel's system-call handler looks up the **system-call table**, checks the parameters and calls the file system / **device driver**. If the block is not already in memory, the driver programs the **disk controller for a DMA transfer** (source, destination address in memory, count).
3. The process **cannot continue** → state **running → waiting**, placed on the device's **wait queue**; the **CPU scheduler** picks another ready process (**context switch**: save the caller's state in its **PCB**, load the next one).
4. The **DMA controller transfers the whole block directly into memory** without the CPU (CPU only sets up the transfer), then raises **one interrupt** when the block is done.
5. The CPU saves the current context and jumps (via the **interrupt vector**) to the **interrupt service routine**, which marks the I/O complete and moves the process **waiting → ready**.
6. When the scheduler **dispatches** the process again, the kernel copies the data into `buf`, sets the **return value = number of bytes read** (0 = EOF, −1 = error) and **returns to user mode** (mode bit = user).

## [XI-02] ch5 | Timer interrupt ends a time quantum (RR)
What happens when the time quantum of the running process expires under round-robin scheduling?

**Answer:**
1. The **timer** (loaded by the OS with a **privileged instruction**) counts down and raises a **timer interrupt** at the end of the quantum.
2. The CPU switches to **kernel mode** and jumps to the timer **interrupt handler**.
3. The OS **saves the running process's context (PC, registers, state) in its PCB**, changes its state **running → ready** and puts it at the **tail of the ready queue**.
4. The **short-term (CPU) scheduler** selects the next process (RR: the **head** of the ready queue).
5. The **dispatcher** restores that process's context from its PCB, **switches to user mode** and **jumps to the saved PC**. The time for steps 3–5 is **dispatch latency / context-switch overhead**: no useful work is done, which is why q must be large relative to the switch time.

## [XI-03] ch3 | How a shell runs `ls -l > out.txt` and `ls | wc -l`
Explain which system calls a shell uses to execute `ls -l > out.txt` and `ls | wc -l`.

**Answer:**
- **`ls -l > out.txt`**: the shell parses the line → **`fork()`** → in the **child**: `fd = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644)`, **`dup2(fd, 1)`** (stdout now refers to the file), `close(fd)`, **`execvp("ls", argv)`** (the redirection survives exec) → the **parent (shell)** calls **`waitpid()`** and then prints the next prompt. The shell's own stdout is untouched because only the child redirected.
- **`ls | wc -l`**: the shell calls **`pipe(fd)` before forking**; child 1 does `dup2(fd[1], 1)` and execs `ls`; child 2 does `dup2(fd[0], 0)` and execs `wc -l`. **Every process closes the pipe ends it does not use**. The shell closes **both** ends (otherwise `wc` never gets EOF) and **waits for both** children.
- **Built-ins** (`cd`, `exit`) run **inside the shell process itself** without fork: `cd` uses **`chdir()`**, because a child's directory change would be lost when the child exits.

## [XI-04] ch3 | Life cycle of a process through all states
Describe the life cycle of a process using the process states, naming the event that causes each transition.

**Answer:**
- **new**: created by `fork()`; the OS allocates a **PCB** and memory.
- **new → ready**: **admitted** (long-term scheduler), placed in the **ready queue**.
- **ready → running**: **dispatched** by the short-term scheduler.
- **running → ready**: **interrupt** / **time quantum expires** / preempted by a higher-priority process.
- **running → waiting**: requests **I/O** or waits for an **event** (e.g. `wait()`, `read()` on an empty pipe).
- **waiting → ready**: **I/O completion** (interrupt) or the event occurs. A process never goes waiting → running directly.
- **running → terminated**: calls **`exit()`** (or is killed). It stays a **zombie** (PCB + exit status kept) until the parent calls **`wait()`**, then its PCB is removed. Only **one process is running per core** at any instant.

## [XI-05] ch2 | From source file to running process (compiler, linker, loader, exec)
Explain how a C source file `prog.c` becomes a running process.

**Answer:**
1. **Compiler**: `gcc -c prog.c` → **relocatable object file** `prog.o` (machine code with unresolved addresses/symbols).
2. **Linker**: combines object files and **libraries** into one **executable** (e.g. ELF); static libraries are copied in, **dynamically linked libraries (DLLs / shared libraries)** are only referenced and linked at **load or run time** (saves memory and disk; one shared copy).
3. **Launch**: typing `./prog` makes the shell **`fork()`** a child that calls **`exec()`**. The **loader** brings the executable into memory (text, data, heap, stack), **relocates** addresses and loads needed DLLs.
4. The OS sets up the **PCB**, puts the process in the **ready queue**, and the scheduler dispatches it; execution starts at the program's **entry point**, which calls `main()`.

## [XI-06] ch3 | What happens when you press Ctrl-C
What happens when the user presses Ctrl-C while a program runs in the shell, and how can a program change this?

**Answer:**
- The terminal driver sends the signal **SIGINT (signal number 2)** to the **foreground process**. A signal is a software notification of an event; it is **asynchronous** (generated outside the receiving process).
- **Default action** for SIGINT: **terminate** the process.
- A program can install its own **signal handler** with **`signal(SIGINT, handler)`** (PA1 prints a message and exits), or ignore it with `signal(SIGINT, SIG_IGN)`. **SIGKILL (9) and SIGSTOP cannot be caught or ignored.**
- In a multithreaded process the signal is delivered to one thread (or as the OS chooses: to the thread it applies to, every thread, certain threads, or a designated thread).
