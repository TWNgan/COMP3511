# Answer Bank — Ch1 Introduction & Ch2 OS Structures

## [X1-01] ch1 | OS definition, intermediary, four components
What is an operating system? Explain its role among the four components of a computer system. [1.20–1.21]

**Answer:**
An OS is **system software that acts as an intermediary between users / application programs and the computer hardware**; it **controls and coordinates the use of computing resources among various applications and users**.
- **Four components**: **hardware** (CPU, memory, I/O devices) → **operating system** → **application programs** (define how resources are used to solve problems, e.g., editors, browsers, games) → **users** (people, machines, other computers).
- **Abstraction**: the OS **hides the complicated details of the hardware** and provides a **simple, easy-to-use interface**, so users deal with files, photos and web pages instead of bytes and blocks on devices.
- **Resource allocation**: it gives an **orderly and controlled allocation** of processors, memory, disks and I/O devices among programs.

## [X1-02] ch1 | OS goals in different computing environments
How do OS design goals differ for shared computers, workstations, mobile devices, embedded systems and real-time systems? [1.22]

**Answer:**
The OS design **first and foremost depends on the target device**:

| Environment | Main OS goal / feature |
|---|---|
| **Shared computers** (mainframe, minicomputer) | keep all users satisfied: balance **performance vs. fairness** |
| **Individual systems** (workstations) | dedicated resources: **performance rather than fairness**; may use shared resources from servers |
| **Mobile devices** (smartphones, handhelds) | **resource constrained**; sensors; **touch screen and voice control** (e.g., Siri); optimized for **usability and battery life** |
| **Embedded systems** (air conditioners, cars, ships, spacecraft) | **little or no user interface**; OS **pre-installed in ROM** |
| **Real-time systems** | **strict time constraints** |

## [X1-03] ch1 | OS goals, resource allocator, control program
What are the main goals of an OS? Explain the views of the OS as a resource allocator and as a control program. [1.23]

**Answer:**
Two main goals: **user convenience** (an environment to execute programs in a **convenient, safe, protected and efficient** manner) and **resource allocation** (allocate resources **fairly and efficiently**).
- **Resource allocator**: the OS **manages all resources**, hardware (CPU, memory, I/O) and software (e.g., signals, locks), and **decides between conflicting requests for efficient and fair resource use**.
- **Control program**: the OS **controls the execution of programs to prevent errors and improper use of the computer** (stops users misusing resources; handles I/O).
- In a nutshell, the OS **manages and controls the hardware and helps programs run on the computer**.

## [X1-04] ch1 | Scenario: which OS role
Which OS role does each case show? (a) Two programs request the only printer at the same time. (b) A program writing into another program's memory is stopped. (c) A user opens a photo by file name, not by disk block numbers. [1.21, 1.23]

**Answer:**
- (a) **Resource allocator**: the OS **decides between conflicting requests** (one job gets the printer, the other waits), so the device is shared **fairly and efficiently**.
- (b) **Control program**: the OS **controls program execution to prevent errors and improper use**; each program may access only its own memory.
- (c) **Abstraction / user convenience**: the OS **hides hardware details** (bytes and blocks) behind a simple interface (files).

## [X1-05] ch1 | Kernel, middleware, system and application programs
Distinguish the kernel, middleware, system programs and application programs. Which of them are part of the OS? [1.23–1.24]

**Answer:**
There is **no universally accepted definition** of an OS ("everything a vendor ships" is only an approximation); commonly, **OS = always-running kernel + middleware frameworks + system programs**.

| Term | Meaning | Part of OS? | Example |
|---|---|---|---|
| **Kernel** | **"the one program running at all times on the computer"**; the essential functions | yes | process and memory management |
| **Middleware** | **software frameworks that provide additional services to application developers** | yes (popular in iOS, Android) | databases, multimedia, graphics |
| **System programs** | **ship with the OS but are not part of the kernel**; help manage the system while it runs | yes | shells, compilers, `ls`, `cp` |
| **Application programs** | **not associated with the OS** | no | apps from app stores, games |

## [X1-06] ch1 | Computer-system organization: bus, controllers, drivers
Describe the organization of a modern computer system. Why do the CPUs and devices compete for memory? [1.25, 1.27]

**Answer:**
A computer has **one or more CPU cores and device controllers connected through a common bus that provides access to shared memory**.
- **CPUs and devices execute concurrently**, so they **compete for memory cycles through the shared bus** (a memory controller keeps the access orderly).
- Each **device controller** is in charge of a particular device; the OS controls it through a **device driver** (the kernel module that controls a device).
- Basic I/O hardware elements: **buses, device controllers and the devices themselves**.

## [X1-07] ch1 | von Neumann architecture, stored-program concept
Describe the main components of the von Neumann architecture. What does "stored-program" mean? [1.26]

**Answer:**
- **Processing unit (CPU)**: an **arithmetic logic unit (ALU)** and **processor registers**: PC (program counter), AC (accumulator), MAR (memory address register), MDR (memory data register).
- **Control unit**: an **instruction register (IR)** and the **program counter (PC)**.
- **Memory** that stores **both data and instructions** (with caches), **external mass storage** (secondary storage), and **input and output mechanisms**.

**Stored-program**: **instructions and data are stored in the same memory and accessed by address**, so **programs and data must be brought into memory before execution**.

## [X1-08] ch1 | Instruction-execution cycle steps
Describe the steps of the instruction-execution cycle on a von Neumann machine. [1.26]

**Answer:**
1. **Fetch instruction**: the instruction at the address in the **PC** is fetched from memory (or cache) into the **instruction register (IR)**.
2. **Decode instruction**.
3. **Fetch data**: the operands are fetched from memory (or cache) into **data registers**.
4. **Execute instruction**: the ALU operates on the operands.
5. **Write back (if any)**: the result **may be stored back in memory or cache**.

The cycle then repeats for the next instruction.

## [X1-09] ch1 | Why programs must be in memory; MMU
Why must a program be loaded into main memory before it can run? What does the memory management unit (MMU) "see"? [1.26, 1.30]

**Answer:**
Because **main memory is the only large storage the CPU can access directly**; the CPU accesses **secondary storage only indirectly**, so code and data on disk must first be **brought into memory**.
- In the von Neumann (stored-program) model, the CPU **fetches every instruction and operand from memory** (or cache / registers).
- The **MMU sees only a stream of memory addresses**; it **does not know how they are generated, or whether they are instructions or data**.

## [X1-10] ch1 | I/O subsystem: buffering, caching, spooling, drivers
What services does the kernel I/O subsystem provide? Distinguish buffering, caching and spooling, and state what a device driver does. (Ch1 summary, Lab 2)

**Answer:**
The kernel I/O subsystem provides **I/O scheduling, buffering, caching, spooling, device reservation and error handling**.
- **Buffering**: **stores data temporarily while it is being transferred** (e.g., between a device and an application).
- **Caching**: keeps a **copy of data on faster storage**. Difference: **a buffer may hold the only existing copy of a data item, whereas a cache only holds a copy of an item that resides elsewhere**.
- **Spooling**: **holds output for a device that cannot accept interleaved data** (e.g., a **printer**), coordinating concurrent output.
- **Device driver**: the **kernel module that controls a device**; it **hides device details behind a uniform device-access interface** for the I/O subsystem.

## [X1-11] ch1 | Storage units: bits, bytes, words, KB–PB
(Calculation) A computer has 64-bit registers and addressing. (a) Bytes per word? (b) Words in 1 KB? (c) Bytes in 4 GB? (d) Time to send a 1 GB file over a 1 Gb/s link? [1.28]

**Answer:**
Use **1 byte = 8 bits**; **KB = $2^{10}$ = 1,024 bytes, MB = $1024^{2}$, GB = $1024^{3}$, TB = $1024^{4}$, PB = $1024^{5}$ bytes**; a **word** is the architecture's **native unit of data**; **networks are measured in bits per second** (Mb/s, Gb/s).
- (a) 64 bits / 8 = **8 bytes per word**.
- (b) 1,024 / 8 = **128 words**.
- (c) $4 \times 2^{30} = 2^{32}$ = **4,294,967,296 bytes** (manufacturers round this to about 4 billion).
- (d) $2^{30} \times 8$ = 8,589,934,592 bits; at $10^{9}$ bits/s this takes about **8.6 s** (about 8 s if 1 GB is rounded to $10^{9}$ bytes). Always **multiply bytes by 8** before dividing by a network rate.

## [X1-12] ch1 | Storage hierarchy: speed, cost, capacity, volatility
Describe the storage hierarchy. How do speed, cost, capacity and volatility change as we move down it? [1.29]

**Answer:**
Storage is organized in a hierarchy by **speed, cost per byte, capacity and volatility**: **registers → cache → main memory → nonvolatile memory (e.g., SSD) → hard-disk drives → optical disk → magnetic tapes**.
- **Higher levels (closer to the CPU)** are **faster, smaller and more expensive per byte**.
- **Moving down**, **cost per byte decreases, access time increases (slower) and capacity increases**.
- **Registers, cache and main memory are volatile** (primary storage); **NVM and HDDs are nonvolatile** (secondary storage); optical disks and tapes are tertiary storage.

## [X1-13] ch1 | Why secondary storage is needed
Why can't all programs and data be kept permanently in main memory? What is secondary storage for? [1.30–1.31]

**Answer:**
Because **main memory is volatile** (it **loses its contents when power is turned off**) and is **too small and too costly per byte** to hold all programs and data.
- **Secondary storage** is an **extension of main memory that provides large nonvolatile storage capacity**, holding **large quantities of data permanently**.
- The most common devices are **hard-disk drives (HDDs)** and **nonvolatile memory (NVM) devices** such as SSDs; programs are loaded from them into memory when they run.

## [X1-14] ch1 | Main memory properties, bootstrap in EEPROM
Describe main memory. Where is the bootstrap program stored, and why not in main memory? [1.30]

**Answer:**
- **Main memory** is the **only large storage the CPU can access directly**; it is **volatile**, typically **DRAM**, accessed by **load and store instructions** to specific addresses, and **byte addressable (each address refers to one byte)**.
- The **bootstrap program**, the **first program run at power-on**, is stored in **EEPROM** (electrically erasable programmable read-only memory, i.e., firmware).
- Reason: **DRAM is volatile and empty at power-on**, so start-up code must be in **nonvolatile** memory; the bootstrap program **initializes the system and loads the OS kernel into memory**.

## [X1-15] ch1 | Mechanical vs electrical (NVM) storage
Compare mechanical and electrical secondary storage. [1.31]

**Answer:**
**Mechanical storage is larger and cheaper per byte; electrical storage (NVM) is more costly, smaller, more reliable and faster.**

| | **Mechanical** | **Electrical (NVM)** |
|---|---|---|
| Examples | HDDs, optical disks, holographic storage, magnetic tape | flash memory, SSD, FRAM, NRAM |
| Capacity | **larger** | smaller |
| Cost per byte | **less expensive** | **more costly** |
| Speed | slower | **faster** |
| Reliability | lower (moving parts) | **more reliable** |

Both are **nonvolatile** and hold programs and data permanently.

## [X1-16] ch1 | Cache hit, miss, cache management
Explain what happens on a cache hit and on a cache miss. What are the main cache-management issues? [1.32]

**Answer:**
Caching **temporarily copies a subset of information from a slower, larger storage into a faster, smaller storage**, making the **frequently used case faster**. Every access **first checks whether the information is in the cache**:
- **Hit**: it is in the cache, so it is **used directly from the cache (fast)**.
- **Miss**: it is not, so the **data is copied from the slower storage into the cache and used there**.
- **Cache management**: the **cache is much smaller than the storage being cached**, so the key issues are the **cache size** and the **replacement policy** (what to evict); the **major criterion is the cache hit ratio** (percentage of accesses found in the cache).

## [X1-17] ch1 | Where caching is used in systems
Caching is "performed at many levels". Give examples of caching in a computer system or OS. [1.32]

**Answer:**
Caching is used **whenever a subset of content can be kept on a faster device**:
- **Hardware caches** keep recently used parts of **main memory** close to the CPU.
- Recent **address translations** are cached for fast lookup.
- **File blocks, file names and file directories**: e.g., part of the **file directory** (a kernel data structure stored on disk) is **cached in main memory**, so main memory acts as a cache for the disk.
- Frequently used **network routes** are cached.

## [X1-18] ch1 | Average access time; miss time vs penalty
(Calculation) Hit ratio 98%, hit time 1 ns, miss time 60 ns: find the average access time. What if 60 ns is the miss penalty instead? [1.32]

**Answer:**
**Average access time = (hit ratio × hit time) + (miss ratio × miss time)**, where miss ratio = 1 − hit ratio:
$T_{avg} = h \times T_{hit} + (1-h) \times T_{miss}$
- Miss time 60 ns: $T_{avg} = 0.98 \times 1 + 0.02 \times 60 = 0.98 + 1.2 =$ **2.18 ns**.
- If 60 ns is the **miss penalty** (extra time on top of the hit time), then $T_{miss} = 1 + 60 = 61$ ns and $T_{avg} = 0.98 \times 1 + 0.02 \times 61 = 0.98 + 1.22 =$ **2.20 ns** (same as $T_{hit} + (1-h) \times \text{penalty} = 1 + 0.02 \times 60$).

State which interpretation you use.

## [X1-19] ch1 | Higher hit ratio is not always better
(Calculation) Cache A: hit ratio 95%, hit time 4 ns, miss time 100 ns. Cache B: hit ratio 90%, hit time 1 ns, miss time 60 ns. Which is better, and what does this show? [1.32]

**Answer:**
**Cache B is better, even though its hit ratio is lower.**
- Formula: $T_{avg} = h \times T_{hit} + (1-h) \times T_{miss}$.
- A: $0.95 \times 4 + 0.05 \times 100 = 3.8 + 5 =$ **8.8 ns**.
- B: $0.90 \times 1 + 0.10 \times 60 = 0.9 + 6 =$ **6.9 ns**.
- This shows that **hit ratio alone does not determine cache performance**: the **average access time** also depends on the **hit time** and the **miss time (miss penalty)**.

## [X1-20] ch1 | Required hit ratio and caching speedup
(Calculation) Hit time 2 ns, miss time 82 ns, and an access without the cache takes 80 ns. What hit ratio gives an average access time of at most 6 ns? What is the speedup over no cache? [1.32]

**Answer:**
**A hit ratio of at least 95% is needed, giving a speedup of about 13.3 times.**
- $h \times 2 + (1-h) \times 82 \le 6 \Rightarrow 82 - 80h \le 6 \Rightarrow 80h \ge 76 \Rightarrow h \ge 0.95$.
- General form: $h = (T_{miss} - T_{target}) / (T_{miss} - T_{hit})$ = (82 − 6) / (82 − 2) = 76 / 80 = 0.95.
- Check: $0.95 \times 2 + 0.05 \times 82 = 1.9 + 4.1 = 6$ ns; **speedup = 80 / 6 ≈ 13.3** compared with accessing memory directly.

## [X1-21] ch1 | Locality: temporal, spatial, when caching fails
Why does caching work? Identify the temporal and spatial locality in a loop that sums an array. When would a cache not help? [1.33]

**Answer:**
Caching works because programs show **locality of reference**:

```c
for (i = 0; i < n; i++)
    sum += a[i];
```

- **Temporal locality** (locality in time): **recently accessed items are likely to be accessed again soon**; here `sum`, `i` and the **loop instructions** are reused in every iteration.
- **Spatial locality** (locality in space): **items near recently accessed items are likely to be accessed shortly**; `a[0]`, `a[1]`, `a[2]`, ... are **contiguous** and accessed in order (instructions are also sequential), so one block brought into the cache serves the next accesses.
- **Without locality**, e.g., if **all items are accessed with equal probability**, **the cache would never work**: the hit ratio stays low and most accesses pay the miss time.

## [X1-22] ch1 | Who manages each storage level
Which component manages each level of the storage hierarchy? Is movement between levels explicit or implicit? [1.34]

**Answer:**
**Registers are managed by the compiler, the cache by hardware, and main memory, SSD and disk by the OS.**

| Level | Access time (ns) | Managed by | Backed by |
|---|---|---|---|
| Registers | 0.25–0.5 | **compiler** | cache |
| Cache | 0.5–25 | **hardware** | main memory |
| Main memory | 80–250 | **operating system** | disk |
| Solid-state disk | 25,000–50,000 | **operating system** | disk |
| Magnetic disk | 5,000,000 | **operating system** | disk or tape |

**Movement between levels can be explicit or implicit**: cache ↔ memory transfers are **implicit (done by hardware)**, while memory ↔ disk transfers (e.g., loading a program, swapping) are **explicitly controlled by the OS**.

## [X1-23] ch1 | Timescales: why switch jobs during disk I/O
Using typical latencies, explain why the OS should run another job while one job waits for a disk access. [1.35, 1.42]

**Answer:**
**A disk access is about 100,000 times slower than a memory access**, so a waiting CPU would waste millions of instruction times.
- **Main memory reference ≈ 100 ns**; **disk seek ≈ 10 ms** = $10^{7}$ ns, so $10^{7} / 10^{2} = 10^{5}$ times slower (an L1 cache reference is only ≈ 0.5 ns).
- Therefore, under **multiprogramming**, when the running job waits for I/O the OS **switches the CPU to another job**, so the **CPU always has a job to execute**.

## [X1-24] ch1 | Single-processor system, special-purpose processors
A PC has one single-core CPU plus a disk controller and a GPU that contain their own processors. Is it a multiprocessor system? Explain. [1.36]

**Answer:**
**No, it is still a single-processor system.** It has **one general-purpose CPU with a single processing core**, which executes a **general-purpose instruction set**, including user processes.
- The disk controller and GPU are **special-purpose (device-specific) processors**: they **run a specific and limited instruction set** and **usually do not execute instructions from user processes**.

## [X1-25] ch1 | Multiprocessor advantages; speed-up below N
Give three advantages of multiprocessor systems. Why is the speed-up with N processors less than N? What is the main disadvantage? [1.37]

**Answer:**
- **Increased throughput**: more computing capability, so more work is done in less time.
- **Economy of scale**: processors **share I/O devices, power supplies, housings and peripherals**, so it costs less than several single-processor systems.
- **Increased reliability**: **graceful degradation** (service continues in proportion to the surviving hardware) or **fault tolerance** (operation continues despite a component failure).

**Speed-up is less than N** because of **overhead**, e.g., **contention for shared resources (bus or memory)** and coordination among processors. **Disadvantage**: **far more complex hardware design and software (parallel programming)**.

## [X1-26] ch1 | SMP vs AMP comparison
Compare symmetric multiprocessing (SMP) and asymmetric multiprocessing (AMP). [1.37–1.38]

**Answer:**
**In AMP a master processor assigns tasks to slaves and handles I/O; in SMP all processors are equal and each performs all tasks.**

| | **Asymmetric (AMP)** | **Symmetric (SMP)** |
|---|---|---|
| Relationship | **master–slave**: the master assigns specific tasks to the slaves | **all processors treated equally** |
| OS functions and user processes | run as the master assigns | **each processor performs all tasks, including OS functions and user processes** |
| I/O | **handled by the master only** | **handled by any processor** |
| Weakness | the **master can become a bottleneck** | adding CPUs may not scale: **contention for the system bus** |

In SMP, **each CPU has its own set of registers and a private (local) cache, but all processors share physical memory through the system bus**.

## [X1-27] ch1 | Cache coherency with private caches
In an SMP system each CPU has its own private cache. What problem does this create, and who usually solves it? [1.38]

**Answer:**
**Cache coherency**: **the same data item can be copied in several CPUs' private caches**, so after one CPU updates its copy, the **other caches may hold stale values**.
- The system must ensure that **an update in one cache is immediately reflected in all other caches** holding that item, so every CPU reads the **most recent value**.
- This is **usually handled by hardware**, below the OS level.

## [X1-28] ch1 | Multicore benefits for laptops and mobile devices
Why is one multicore chip preferred to several single-core chips, especially in laptops and mobile devices? [1.39]

**Answer:**
- **Faster communication**: cores on one chip communicate **on-chip, which is faster than between-chip communication**.
- **Lower power**: **one chip with multiple cores uses significantly less power than multiple single-core chips**, which matters for **battery-powered devices** such as mobile devices and laptops.

## [X1-29] ch1 | NUMA: motivation, structure, drawback
Why was NUMA introduced? Describe its structure, its drawback and its implication for the OS. [1.40]

**Answer:**
- **Motivation**: adding more CPUs to an SMP system **may not scale**, because **contention for the system bus becomes a bottleneck**.
- **Structure**: **each CPU (or group of CPUs) has its own local memory accessed via a small, fast local bus**; the CPUs are connected by a **shared system interconnect**, and **all CPUs share one physical memory address space**. Local memory is fast, remote memory is slower (**non-uniform** access time).
- **Drawback**: **increased latency when a CPU must access remote memory across the system interconnect**.
- **OS implication**: **scheduling and memory management** should keep a process on a CPU **close to the memory that holds its data**.

## [X1-30] ch1 | CPU, processor, core, multicore, multiprocessor
Define CPU, processor, core, multicore and multiprocessor. [1.41]

**Answer:**
A **processor** (chip) contains one or more **CPUs**, and the **core** is the unit that actually executes instructions:

| Term | Definition |
|---|---|
| **CPU** | the **hardware that executes instructions** |
| **Processor** | a **physical chip that contains one or more CPUs** |
| **Core** | the **basic computation unit of the CPU**; it **executes instructions and has registers for storing data locally** |
| **Multicore** | **multiple computing cores on a single physical processor chip** |
| **Multiprocessor** | a system **including multiple processors** |

## [X1-31] ch1 | Multiprogramming: why, how, OS support
Why is multiprogramming needed? What happens when the running job waits for I/O, and what OS support does it need? [1.42]

**Answer:**
**A single program cannot keep the CPU or I/O devices busy at all times**, so multiprogramming **keeps several jobs in memory at the same time and organizes them so the CPU always has one to execute**, raising **CPU utilization (efficiency)**.
- When the running job **waits for I/O**, the OS **switches the CPU to another job** in memory instead of leaving the CPU idle.
- OS support: **job scheduling** (choose queued jobs to load into memory), **CPU scheduling** (several jobs ready at the same time), memory management for several jobs, **swapping** (move processes in and out of memory when they do not fit) and **virtual memory** (run a process that is **not completely in memory**).

## [X1-32] ch1 | Multiprogramming vs time sharing compared
Compare multiprogramming (batch) and time sharing (multitasking). [1.42]

**Answer:**
**Time sharing is a logical extension of multiprogramming**: both keep several jobs in memory, but time sharing switches the CPU so often that users can interact with their programs.

| | **Multiprogramming (batch)** | **Time sharing (multitasking)** |
|---|---|---|
| Goal | **efficiency: keep the CPU busy** (CPU utilization) | **fast response time** for interactive users |
| When the CPU switches | when the running job **must wait (e.g., for I/O)** | **frequently**, even if the job is not waiting (short time slices, enforced by a timer) |
| User interaction | none while jobs run (jobs are submitted and queued) | users **interact with each job while it is running** (interactive computing) |
| Requirement | job scheduling, CPU scheduling | CPU scheduling; **response time under a certain threshold** |

## [X1-33] ch1 | Virtualization: host, VMM, guest OS
What is virtualization? Describe the roles of the host, the VMM (hypervisor) and the guest OS. [1.43–1.44]

**Answer:**
**Virtualization abstracts the hardware of a single computer into multiple different execution environments (virtual machines, VMs)**, creating the **illusion that each user or program runs on its own "private computer"**. It **allows an OS to run as an application within another OS**, so **one physical machine can run multiple operating systems concurrently**.
- **Host**: the **underlying hardware system**.
- **Virtual machine manager (VMM) or hypervisor**: **creates and manages virtual machines** by **providing an interface identical to the host**; it is **in complete control of system resources**.
- **Guest**: a process given a **virtual copy of the host**, usually an **operating system** (guest OS) running its own applications.

## [X1-34] ch1 | Virtualization motivations: consolidation, testing scenario
A company runs many lightly loaded servers, each needing a different OS or OS version, and its developers must test software on several OSes. How does virtualization help? [1.43]

**Answer:**
- **Server consolidation**: virtualization **consolidates multiple OSes onto fewer hardware platforms**; each service runs in its own VM with the OS / version it needs, on far fewer physical machines.
- **Testing and debugging**: **developers can run many OS types and versions on just one machine**, which makes **testing and debugging easier**.
- **Desktop use**: a user can run one OS (e.g., Linux) and **still use native applications of another platform, such as Windows**, inside a VM.

## [X1-35] ch1 | Virtualization vs emulation; VM performance
Distinguish virtualization from emulation. Does a program run faster inside a VM? [1.46]

**Answer:**
- **Virtualization**: the **guest OS is natively compiled for the same CPU** as the host; most guest instructions run directly on the hardware under VMM control, so programs show **only minor performance decreases** (they pass through more layers of software).
- **Emulation**: **simulates a different CPU architecture in software** (source CPU differs from target CPU); every instruction must be translated, so it is **much slower**.
- So a program in a VM is **not faster** than on the physical machine; it is usually **slightly slower**. (History: virtualization began on **IBM mainframes (1972)**; in the late 1990s Intel CPUs became fast enough for **VMware and Xen** on PCs.)

## [X1-36] ch1 | Cloud computing; public, private, hybrid clouds
What is cloud computing, and why is it a "logical extension of virtualization"? Distinguish public, private and hybrid clouds. [1.47–1.48]

**Answer:**
**Cloud computing delivers computing, storage and applications as a service over a network**, on demand.
- It is a **logical extension of virtualization** because it **uses virtualization as the base for its functionality**; e.g., **Amazon EC2** has millions of servers running **tens of millions of VMs**, and users **pay based on usage**.
- **Public cloud**: available **via the Internet to anyone willing to pay**.
- **Private cloud**: **run by a company for the company's own use**.
- **Hybrid cloud**: **includes both public and private cloud components**.

## [X1-37] ch1 | SaaS, PaaS, IaaS classification
Explain SaaS, PaaS and IaaS, and classify: (a) an online word processor; (b) a ready-to-use database server for your application; (c) rented storage for backups or virtual servers. [1.48]

**Answer:**
**SaaS provides applications, PaaS a ready software stack, and IaaS servers or storage, all over the Internet.**

| Model | Provided over the Internet | Example |
|---|---|---|
| **SaaS** (Software as a Service) | **one or more applications** | (a) **online word processor** |
| **PaaS** (Platform as a Service) | **a software stack ready for application use** | (b) **a database server** |
| **IaaS** (Infrastructure as a Service) | **servers or storage** | (c) **storage for backup**, virtual servers (e.g., Amazon EC2) |

Clouds increasingly offer other services too, e.g., **MaaS (Machine learning as a Service)**.

## [X1-TF] ch1 | True / False quick verdicts

| Statement | T/F | Why (≤ 12 words) |
|---|---|---|
| The kernel is the one program running at all times on the computer. | T | Middleware and system programs are part of the OS, not kernel. |
| System programs ship with the OS and are part of the kernel. | F | They ship with the OS but are not part of the kernel. |
| There is a universally accepted definition of an operating system. | F | "Everything a vendor ships" is only an approximation. |
| Embedded systems usually have rich user interfaces. | F | Little or no UI; OS is pre-installed in ROM. |
| The MMU knows whether an address refers to an instruction or data. | F | The MMU sees only a stream of memory addresses. |
| The CPU can execute a program directly from the hard disk. | F | Programs must first be brought into main memory. |
| DRAM keeps its contents when the power is turned off. | F | Main memory (DRAM) is volatile. |
| The bootstrap program is stored in EEPROM. | T | Nonvolatile firmware; DRAM is empty at power-on. |
| Moving down the hierarchy, cost per byte and access time both decrease. | F | Cost per byte decreases, but access time increases. |
| NVM (flash, SSD) is larger and cheaper per byte than an HDD. | F | Mechanical storage is larger and cheaper; NVM is faster. |
| Cache memory is managed by the operating system. | F | Cache is managed by hardware; registers by the compiler. |
| Main memory, SSD and magnetic disk are managed by the OS. | T | Storage-characteristics table, levels 3 to 5. |
| A cache is usually larger than the storage being cached. | F | A cache is much smaller; it holds a subset. |
| A cache with a higher hit ratio always has a lower average access time. | F | Hit time and miss time also determine average access time. |
| Spatial locality: items near a recent access are likely accessed soon. | T | E.g., sequential array elements and sequential instructions. |
| Caching still works if all items are accessed with equal probability. | F | Without access locality, a cache would never work. |
| A buffer may hold the only existing copy of a data item. | T | A cache, by definition, only holds a copy. |
| Spooling holds output for a device that cannot accept interleaved data. | T | E.g., a printer shared by many processes. |
| A GPU in a single-CPU PC makes it a multiprocessor system. | F | Special-purpose processors do not execute user processes. |
| In AMP, any processor may handle I/O. | F | The master handles I/O; any processor only in SMP. |
| Multicore chips use more power than multiple single-core chips. | F | One multicore chip uses significantly less power. |
| In NUMA, each CPU has a separate physical address space. | F | All CPUs share one physical memory address space. |
| Cache coherency is usually handled by hardware. | T | It is handled below the operating-system level. |
| Multiprogramming lets users interact with each job while it runs. | F | That is time sharing (multitasking). |
| Emulation is used when guest and host have the same CPU type. | F | That is virtualization; emulation simulates a different CPU. |
| A private cloud is available to anyone willing to pay. | F | That is a public cloud; private is for one company. |
| Storage available over the Internet for backup is IaaS. | T | IaaS provides servers or storage over the Internet. |
| 1 KB is 1,000 bytes in the lecture's notation. | F | 1 KB = 1,024 bytes; manufacturers round off. |
| Network speeds are usually given in bytes per second. | F | Networks move data a bit at a time: bits/s. |

## [X2-01] ch2 | OS services: helpful to user, efficient operation
List the OS services that are helpful to the user, and those that ensure the efficient operation of the system itself. [2.4–2.6]

**Answer:**
**Helpful to the user:**
- **User interface**: CLI, GUI, touch screen.
- **Program execution**: load a program into memory, run it, and end execution **normally or abnormally (indicating error)**.
- **I/O operations**: a running program may require I/O on a file or an I/O device.
- **File-system manipulation**: read, write, create, delete and search files and directories; list file information; **permission management**.
- **Communications**: processes exchange information on the same computer or over a network, via **shared memory** or **message passing** (packets moved by the OS).
- **Error detection**: errors **may occur in the CPU and memory, in I/O devices and in user programs**; the OS takes appropriate action to ensure **correct and consistent computing** (plus **debugging facilities**).

**Efficient operation of the system (via resource sharing):** **resource allocation** (CPU cycles, memory, file storage, I/O devices), **logging** (keep track of **which users use how much and what kinds of resources**), and **protection and security**.

## [X2-02] ch2 | Scenario: identify the OS service
Which OS service is shown? (a) CPU time used by each user is recorded for billing. (b) A disk read fails; the OS retries and reports it. (c) Two processes exchange data through shared memory. (d) A program is loaded, runs, and exits with an error code. (e) A user must log in with a password. [2.4–2.6]

**Answer:**
- (a) **Logging (accounting)**: tracks which users use how much and what kinds of resources.
- (b) **Error detection**: the OS is constantly aware of possible errors (here in an I/O device) and takes appropriate action.
- (c) **Communications**, using the **shared-memory** model (the other model is message passing).
- (d) **Program execution**: load, run, and end execution normally or **abnormally (indicating error)**.
- (e) **Protection and security**: **security from outsiders requires user authentication**.

## [X2-03] ch2 | Protection vs security; access rights, domains
Distinguish protection and security. What are an access right and a domain? [2.6] (Ch2 summary)

**Answer:**
- **Protection**: **controlling the access of users or processes to the resources** (hardware and software) of the computer, **ensuring that all access to system resources is controlled**, so concurrent processes do not interfere with each other.
- **Security**: **defending the system against internal and external attacks** (e.g., **denial-of-service, worms, viruses**); **security from outsiders requires user authentication** and extends to defending external I/O devices from invalid access attempts.
- An **access right** is the **permission to perform certain operations on an object**; a **domain** is **a set of access rights for a set of objects**. A process executes in a domain and **cannot perform an operation on an object unless its domain allows it**.

## [X2-04] ch2 | Two categories: protection, functionality beyond hardware
According to the chapter summary, OS services fall into two general categories. What are they? Give an example of each. (Ch2 summary)

**Answer:**
1. **Enforcing protection among processes running concurrently**: e.g., **a process may access only the memory in its own address space**, and **may not access hardware devices directly without OS assistance and intervention**.
2. **Providing functionality not directly supported by the underlying hardware**: e.g., **memory management and file systems** (the disk only stores blocks; the OS builds files and directories on top of them).

## [X2-05] ch2 | CLI vs GUI vs touch-screen interfaces
Compare the three approaches for users to interact with an OS: CLI, GUI and touch screen. [2.8–2.12]

**Answer:**
**CLI = typed commands, GUI = desktop metaphor with mouse and icons, touch screen = gestures and voice.**

| | **CLI (command interpreter)** | **GUI** | **Touch screen** |
|---|---|---|---|
| Interaction | user **enters commands directly**; the shell fetches, interprets and executes them | **user-friendly desktop metaphor**: mouse, keyboard, monitor; **icons** for files, programs, directories | **gestures**, **virtual keyboard**, **voice commands** (e.g., Siri) |
| Best for | experienced users; fast and scriptable | ease of learning and use | devices where a mouse is not feasible (phones, tablets) |
| Examples | UNIX/Linux shells: Bourne-Again (bash), C shell, Korn shell | Mac OS X **Aqua**, Windows, KDE / GNOME | iPhone, iPad, Android |

The GUI was **invented at Xerox PARC (early 1970s)** and first widely used on the **Apple Macintosh (1984)**; **many systems now provide both CLI and GUI** (e.g., Windows GUI with a CLI "command" shell).

## [X2-06] ch2 | Shell: functions; kernel or system program
What is the primary function of a shell? Why is it better to implement the command interpreter as a system program than inside the kernel? [2.8, 2.37]

**Answer:**
A shell **(1) fetches a command from the user, (2) interprets it and (3) executes it**; in UNIX it runs a program by calling **`fork()`** to create a new process and **`exec()`** to load the program into it, then **waits** for it (or continues, for a background job).

The command interpreter is **sometimes implemented in the kernel, sometimes by system programs**. As a system program:
- **Several shells can coexist** (C shell, Bourne-Again shell, Korn shell), and users can choose or replace one **without changing the kernel**.
- Most commands are **separate system programs**: the shell just **uses the command name to find a file to load and execute**, so **new commands can be added without modifying the shell**.
- A bug in the shell **affects only the shell process, not the kernel**.

## [X2-07] ch2 | cp command: sequence of system calls
Describe the sequence of system calls needed by `cp in.txt out.txt` to copy one file to another. [2.14]

**Answer:**
Even this simple command needs **a sequence of system calls**:
1. **Acquire the input and output file names** (from the command line, or by writing a prompt to the screen and reading the keyboard).
2. **Open the input file**; if it does not exist, print an error and **abort**.
3. **Create the output file**; if it already exists, abort (or overwrite).
4. **Loop: read from the input file and write to the output file**, until the read reaches end of file (or an error occurs).
5. **Close the files**, write a completion message to the screen, and **terminate normally**.

## [X2-08] ch2 | API definition, common APIs, read() example
What is an API? Name the three most common APIs, and explain the parameters and return value of `ssize_t read(int fd, void *buf, size_t count)`. [2.15–2.16]

**Answer:**
An **Application Programming Interface (API)** **specifies a set of functions available to application programmers, including the parameters passed to each function and the return values it may expect**. The API functions **invoke the actual system calls on behalf of the programmer** (e.g., Windows **`CreateProcess()`** invokes the **`NTCreateProcess()`** system call). Programmers use an API through a **library provided by the OS**: **libc** for C programs on UNIX/Linux.
- Most common APIs: **Win32 API** (Windows), **POSIX API** (virtually all versions of UNIX, Linux and Mac OS X), **Java API** (Java virtual machine).
- `read()`: `fd` = the **file descriptor** to be read; `buf` = the **buffer** the data is read into; `count` = the **maximum number of bytes** to read. It returns the **number of bytes read**, **0 at end of file**, and **−1 if an error occurred**.

## [X2-09] ch2 | Why use APIs; API call vs system call
Explain why programmers use an API rather than invoking system calls directly. Does every API call result in a system call? [2.17]

**Answer:**
- **Program portability**: a program written to an API **can compile and run on any system that supports the same API**, although **the implementation of system calls varies from machine to machine**.
- **Hiding complex details**: actual system calls are **more detailed and difficult to work with**; the caller **need know nothing about how the system call is implemented**, only **obey the API and understand what the OS will do** as a result. E.g., `printf()` handles formatting and buffering, then calls the `write()` system call.
- **No**: an API function may **invoke one or more system calls, or none**; e.g., `strlen()` runs entirely in user mode.

## [X2-10] ch2 | System-call interface, RTE, system-call table
How does the system-call interface link an API call to the kernel? Explain the roles of the run-time environment, the system-call number and the system-call table. [2.18–2.19]

**Answer:**
**The system-call interface, part of the run-time environment, maps each API call to a numbered system call and invokes it in the kernel.**
- The **run-time environment (RTE)**, the full suite of software needed to run programs in a language (compilers or interpreters, **libraries**, loaders), provides a **system-call interface that serves as the link to the system calls** of the OS.
- **An identity number is associated with each system call**, and the system-call interface **maintains a table indexed by these numbers**.
- The interface **intercepts function calls in the API, invokes the necessary system call within the OS** (the call traps into kernel mode; the kernel uses the number to index the table and run the service routine), and **returns the status of the system call and any return values**.
- **The caller knows nothing about how the system call is implemented.**

## [X2-11] ch2 | printf() vs write(); when kernel mode starts
Explain the relationship between `printf()` and `write()`. At what point does the program enter kernel mode? [2.26]

**Answer:**
**`printf()` is a standard C library (API) function; `write()` is a system call.** The program **invokes the `printf()` library call, which calls the `write()` system call** to get the service from the OS.
- `printf()` runs in **user mode** (formatting the string and buffering the output).
- Only when the library **invokes `write()`** does the program **trap into kernel mode**; the kernel writes the data to the file or device and then **returns to user mode** with the result.
- The standard C library (**libc**) thus provides the **system-call interface** for UNIX and Linux.

## [X2-12] ch2 | Parameter passing: registers, block, stack
Describe the three methods to pass system-call parameters to the OS. A call needs 7 parameters but only 4 registers are available: which method would you use? [2.20–2.21]

**Answer:**
**Use the block (or stack) method**, because registers limit the number of parameters:

| Method | How | Limit |
|---|---|---|
| **Registers** | parameters are placed **directly in CPU registers** (**simplest**) | **limited**: there may be more parameters than registers |
| **Block (table)** | parameters are **stored in a block, or table, in memory**, and **the address of the block is passed in a register** | **no limit** on number or length |
| **Stack** | parameters are **pushed onto the stack by the program and popped off by the OS** | **no limit** on number or length |

E.g., store all 7 parameters in a memory block and pass its address in one register.

## [X2-13] ch2 | Six types of system calls, classification
Name the six categories of system calls, and classify `fork()`, `wait()`, `open()`, `ioctl()`, `getpid()`, `sleep()`, `pipe()`, `mmap()`, `chmod()` and `umask()`. [2.22–2.25]

**Answer:**
**Process control, file management, device management, information maintenance, communications and protection.**

| Category | Typical operations | UNIX | Windows |
|---|---|---|---|
| **Process control** | create/terminate, load/execute, wait for time or event, allocate/free memory, dump memory, debugger, **locks** | **`fork()`**, `exit()`, **`wait()`** | `CreateProcess()`, `ExitProcess()`, `WaitForSingleObject()` |
| **File management** | create/delete, open/close, read/write/reposition, get/set file attributes | **`open()`**, `read()`, `write()`, `close()` | `CreateFile()`, `ReadFile()`, `WriteFile()`, `CloseHandle()` |
| **Device management** | request/release device, read/write, get/set device attributes, attach/detach | **`ioctl()`**, `read()`, `write()` | `SetConsoleMode()`, `ReadConsole()`, `WriteConsole()` |
| **Information maintenance** | get/set time or date, system data, process/file/device attributes | **`getpid()`**, `alarm()`, **`sleep()`** | `GetCurrentProcessID()`, `SetTimer()`, `Sleep()` |
| **Communications** | create/delete connection, send/receive messages, **shared-memory** regions | **`pipe()`**, `shm_open()`, **`mmap()`** | `CreatePipe()`, `CreateFileMapping()`, `MapViewOfFile()` |
| **Protection** | control access, get/set permissions, allow/deny user access | **`chmod()`**, **`umask()`**, `chown()` | `SetFileSecurity()`, `InitializeSecurityDescriptor()` |

## [X2-14] ch2 | System programs: categories and user view
What are system programs? List their main categories with examples. Why is the user's view of the OS defined by them? [2.27–2.30]

**Answer:**
**System programs (system services, system utilities) provide a convenient environment for program development and execution**; some are simply **user interfaces to system calls**, others are considerably more complex.
- **File management**: create, delete, copy, rename, print, list files and directories.
- **Status information**: date, time, available memory or disk space, number of users; performance, logging and debugging information.
- **File modification**: text editors; commands to search file contents or transform text.
- **Programming-language support**: compilers, assemblers, debuggers, interpreters.
- **Program loading and execution**: absolute and relocatable loaders, linkage editors, overlay loaders, debugging systems.
- **Communications**: messages between users, web browsing, e-mail, remote login, file transfer.
- **Background services**: launched at boot; those running until the system halts are **services, subsystems or daemons** (disk checking, process scheduling, error logging).

**Most users see the OS through application and system programs, not the actual system calls**: a GUI and a UNIX shell **use the same set of system calls** but look and act very differently.

## [X2-15] ch2 | System calls vs system programs vs applications
Compare system calls, system programs and application programs. [2.27–2.30]

**Answer:**
**System calls are the low-level programming interface; system programs are higher-level utilities built on them; application programs are not part of the OS.**

| | **System calls** | **System programs** | **Application programs** |
|---|---|---|---|
| Level | **low-level programming interface to OS services** | higher-level utilities shipped with the OS | user programs that solve problems |
| Used by | running programs, usually **through an API** | users, **without writing programs** (e.g., shell commands to create or delete a file) | end users |
| Requests | **basic functions: process control, file and device manipulation** | one request may be **translated into a sequence of system calls** with richer functions | use system calls through libraries |
| Part of the OS? | yes (kernel interface) | yes (ship with the OS, not part of the kernel) | **no** |
| Examples | `fork()`, `read()`, `write()` | `ls`, `cp`, compilers, text editors | games, spreadsheets |

## [X2-16] ch2 | Compiler, linker, loader roles; relocation
What does each of the compiler, linker and loader do? What is a relocatable object file, and what is relocation? [2.31–2.32]

**Answer:**
**The compiler produces relocatable object files, the linker combines them into one executable on disk, and the loader brings that executable into memory to run.**

```
gcc -c main.c            # compiler -> main.o (relocatable object file)
gcc -o main main.o -lm   # linker   -> main (executable; -lm links the math library)
./main                   # loader   -> program loaded into memory (+ DLLs if needed)
```

- A **relocatable object file** is compiled code **designed to be loaded into any physical memory location**.
- **Linker**: **combines the relocatable object files, along with libraries if needed, into a single binary executable file** stored on secondary storage.
- **Loader**: **brings the binary executable into memory**, possibly with **dynamically linked libraries**, where it **becomes eligible to run on an available CPU**.
- **Relocation** **assigns final addresses to the program parts and adjusts the code and data to match those addresses**. Object and executable files have **standard formats** (machine code + symbol table, e.g., ELF on Linux), so the OS knows how to load and start them.

## [X2-17] ch2 | Static linking vs dynamically linked libraries
Compare static linking with dynamically linked libraries (DLLs). Why do modern OSes use DLLs? [2.31]

**Answer:**
**Modern general-purpose OSes do not link libraries statically; DLLs are loaded when needed and shared, which saves memory.**

| | **Static linking** | **Dynamic linking (DLLs)** |
|---|---|---|
| When linked | at link time; library code is **copied into every executable** | **loaded when needed**, at load or run time |
| Executable size | larger | smaller |
| Memory use | every program has its own copy | **loaded only once and shared by all programs using the same version of the library** |
| Unused code | libraries may be linked in even if never used | **avoids linking and loading libraries that end up not being used** |

Trade-off: the program **depends on the right library version being present** at run time, and loading it costs a little time.

## [X2-18] ch2 | Why applications are OS-specific; ABI
Why can an executable built for one OS usually not run on another OS? How can programs be made portable? [2.15, 2.31, 2.56]

**Answer:**
**Because each OS has its own system calls, executable format and binary conventions.**
- **Different system calls / APIs**: **each OS provides its own set of system calls** (different numbers, parameters, meanings and results), e.g., Win32 vs POSIX.
- **Different executable formats**: each OS uses its **own standard binary format** so it knows how to load and start the program (e.g., **ELF** on Linux, **PE** on Windows).
- **Different CPUs have different instruction sets**: e.g., **iOS runs on ARM and does not run Mac OS X (Intel) applications natively**. The rules for how binary code interfaces with a given OS on a given architecture are called the **ABI (application binary interface)**.

**Portability**: write to a **standard API** (e.g., POSIX) and **recompile** on each system, or use an **interpreted or virtual-machine language** such as **Java (JVM)**.

## [X2-19] ch2 | OS design goals: user vs system
What are user goals and system goals in OS design? What affects the design at the highest level? [2.33]

**Answer:**
- At the highest level, the design is **affected by the choice of hardware and the type of system** (desktop/laptop, mobile, distributed or real-time); it starts by **defining goals and specifications**.
- **User goals**: the OS should be **convenient to use, easy to learn and use, reliable, safe and fast**.
- **System goals** (for designers and maintainers): it should be **easy to design, implement and maintain**, and **flexible, reliable, error-free and efficient**.
- OS design is **not "solvable"**; it is a **highly creative software-engineering task**, though some approaches have proven successful.

## [X2-20] ch2 | Policy vs mechanism: definition, separation
Distinguish policy and mechanism with an example. Why should they be separated? [2.34]

**Answer:**
**Policy: what will be done. Mechanism: how to do it.**
- Example: a **timer** is a **mechanism** for ensuring CPU protection, but **deciding how long the timer is set for a particular user** is a **policy** decision.
- **Why separate**: policies change over time; if policy and mechanism are properly separated, **a policy change needs minimal change to the mechanism**, which gives **flexibility**. The same mechanism can support **"I/O-intensive programs have priority over CPU-intensive ones"** or **the opposite policy**.
- In a nutshell, **design goals determine the policies, and the OS implements these policies through specific mechanisms**.

## [X2-21] ch2 | Scenario: classify policy or mechanism
Policy or mechanism? (a) code that saves and restores registers to switch processes; (b) "interactive jobs get higher priority than batch jobs"; (c) a hardware timer; (d) "each user may run at most 10 ms at a time"; (e) checking permission bits on every `open()`; (f) "only the owner may write a file". [2.34]

**Answer:**
- (a) **Mechanism**: how the CPU is switched between processes.
- (b) **Policy**: decides which jobs get priority.
- (c) **Mechanism**: a tool for ensuring CPU protection.
- (d) **Policy**: how long the timer is set for a user.
- (e) **Mechanism**: how access control is enforced.
- (f) **Policy**: what access is allowed.

Rule: **"what should be done / who gets what" = policy; "how it is done" = mechanism**.

## [X2-22] ch2 | OS in a high-level language: pros, cons
What are the advantages and disadvantages of implementing an OS in a high-level language (C/C++) rather than assembly? [2.35]

**Answer:**
**The advantages outweigh the small costs**, so most OSes are now written in **C or C++** (the **lowest levels of the kernel may still be in assembly**; e.g., Android's system libraries are in C/C++ and its application frameworks mostly in Java).
- **Advantages**: the code **can be written faster, is more compact, and is easier to understand and debug**; **advances in compiler technology improve the generated code for the entire OS by simple recompilation**; and the OS is **far easier to port** to other hardware.
- **Disadvantages**: possibly **reduced speed and increased storage requirements**, which are **not a major issue in today's computer systems**.

## [X2-23] ch2 | MS-DOS vs FreeBSD: running a program
Compare how MS-DOS and FreeBSD run a user program. [2.36–2.37]

**Answer:**
**MS-DOS is single-tasking and runs a program without creating a process; FreeBSD is multitasking and runs each program in a new process (`fork()` + `exec()`).**

| | **MS-DOS** | **FreeBSD (UNIX variant)** |
|---|---|---|
| Tasking | **single-tasking** | **multitasking** |
| Running a program | the shell (invoked at boot) **loads the program into memory, overwriting all but the kernel**; **no process is created** | the shell **calls `fork()` to create a new process**, then **`exec()` to load the program** into it |
| Memory | **single memory space** | each process has its own address space |
| While it runs | only that program runs | the shell **waits for the process to terminate** or **continues with user commands** |
| When it exits | **the shell is reloaded** | the process terminates; the shell continues |
| OS support | simple | **CPU scheduling, process coordination, memory management** |

## [X2-24] ch2 | Simple structure: why MS-DOS was vulnerable
Why was MS-DOS vulnerable to buggy or malicious programs? [2.39]

**Answer:**
**Because nothing protected the OS and hardware from application programs.**
- MS-DOS has a **simple structure**: it was **written to provide the most functionality in the least space**, was **not carefully divided into modules**, and its **interfaces and levels of functionality are not well separated**.
- **Application programs can access I/O directly**, bypassing the OS.
- It was written for the **Intel 8088, which had no dual mode (kernel vs. user mode) and no hardware protection**, so **one faulty program could crash the whole system**.

## [X2-25] ch2 | Monolithic kernel: pros, cons, Linux
What is a monolithic kernel? Why do UNIX, Linux and Windows still use this structure despite its drawbacks? [2.40–2.42]

**Answer:**
A **monolithic structure places all the functionality of the kernel into a single, static binary file that runs in a single address space**; in traditional UNIX, **the kernel is everything below the system-call interface and above the physical hardware** (UNIX = **kernel + system programs**).
- **Why still used**: a **distinct performance advantage**, since there is **very little overhead in the system-call interface, and communication within the kernel is fast**.
- **Drawback**: an enormous amount of functionality is **combined into one level**, making it **difficult to implement, debug and maintain**; it is **tightly coupled**.
- **Linux** is monolithic (it **runs entirely in kernel mode in a single address space**; applications use **glibc** to reach the system-call interface) but also **modular**: **loadable kernel modules** let the kernel be modified at run time.

## [X2-26] ch2 | Tightly vs loosely coupled; modular design
Distinguish a tightly coupled system from a loosely coupled (modular) one. What is the advantage of modularity? [2.43]

**Answer:**
- **Tightly coupled** (monolithic): essentially **one big program running in one address space**, where **changes to one part of the system affect other parts**.
- **Loosely coupled (modular)**: the system is **divided into separate, smaller components, each with specific and limited functionality**, with specified interactions between them.
- **Advantage**: **changes in one component affect only that component**, giving **more freedom and flexibility in creating and modifying each component** and **simplifying debugging and verification**. The **layered approach** is one way to make a system modular.

## [X2-27] ch2 | Layered approach: information hiding, debugging
Describe the layered approach. What is information hiding, and why is a layered OS easy to construct and debug? [2.44–2.45]

**Answer:**
The OS is **divided into layers, each built on top of lower layers**: **layer 0 (bottom) is the hardware; layer N (top) is the user interface**. Each layer has **data structures and a set of functions**, **uses the services of the layer below** and **offers services to the layer above**.
- **Information hiding**: a layer **needs to know only what the lower-layer operations do (their interface), not how they are implemented**; each layer **hides its own data structures, operations and hardware** from higher layers.
- **Main advantage, simplicity of construction and debugging**: layers are **debugged one at a time, starting from the lowest layer**; when a layer is tested, the layers below are already verified, so **an error found must be in the layer being tested**.
- Layering is used successfully in other systems such as **computer networks (TCP/IP)** and web applications.

## [X2-28] ch2 | Why few OSes are purely layered
Why do few operating systems use a pure layered approach? What is the trend instead? [2.45, 2.53]

**Answer:**
1. **Difficulty of defining the layers**: there are **significant challenges in appropriately defining the layers and their functionalities**, since each layer may use only lower layers.
2. **Performance**: the **overhead of requiring a program to traverse multiple layers to obtain a service**.

**Trend**: **fewer layers with more functionality** and **modularized code**, avoiding the problems of complex layer definition and interaction.

## [X2-29] ch2 | Microkernel: file access by message passing
In a microkernel OS, describe how an application reads a file. Why does this hurt performance? [2.46–2.47]

**Answer:**
**The application and the file server never interact directly; they exchange messages through the microkernel.**
- The microkernel keeps only **minimal process and memory management plus a communication facility (IPC)**; services such as the **file server** and device drivers run as **user-level programs in separate address spaces**.
- To read a file, the **application sends a request message to the microkernel, which passes it to the file server; the file server does the work and replies by message through the microkernel**.
- **Performance cost**: each request needs **several user-to-kernel transitions and message copies between separate address spaces** (**increased system-function overhead**), instead of one function call inside a monolithic kernel.

## [X2-30] ch2 | Microkernel: advantages, drawback, Windows NT
Why is a microkernel OS easier to extend and port, and more secure and reliable? What is its main drawback? Give an example. [2.48]

**Answer:**
- **Easier to extend**: **new services are added in user space without modifying the kernel**; when the kernel must change, **the changes are fewer because the kernel is much smaller**.
- **Easier to port**: the **much smaller kernel can be more easily ported from one hardware platform to another**.
- **More secure and reliable**: **less code runs in kernel mode**; most services run as **user processes**, so **if a service fails, the rest of the OS remains untouched**; a simpler kernel is also more reliable.
- **Main drawback**: **performance suffers** from **increased system-function overhead**: user-space to kernel-space communication and **copying messages between services in separate address spaces**. Example: **Windows NT** (a layered microkernel) performed worse than Windows 95, so **Windows XP became more monolithic**.

## [X2-31] ch2 | LKM approach; USB device scenario
What is the loadable kernel module (LKM) approach? What happens when a USB device is plugged into a running Linux machine whose kernel lacks its driver? [2.49–2.51]

**Answer:**
**The kernel has a set of core components and links in additional services via modules, either at boot time or during run time**; this is the **best current methodology** in OS design.
- **USB case**: the needed **driver module is loaded dynamically into the running kernel** (and can be **removed** later), with **no need to recompile the kernel or reboot**.
- **Why better**: linking services dynamically is **preferable to adding features directly to the kernel, which would require recompiling the entire kernel every time a change is made**; since it is hard to predict every needed feature, functionality can be **added and removed while the kernel is running**.
- Linux uses LKMs **mainly for device drivers and file systems** (Solaris also loads scheduling classes, loadable system calls, executable formats and STREAMS modules); the result is a **dynamic, modular kernel with the performance benefits of a monolithic system**.

## [X2-32] ch2 | LKM vs microkernel; LKM vs layered
Compare the LKM approach with the microkernel approach (one similarity, one difference). How does LKM also resemble a layered design? [2.50]

**Answer:**
- **Similarity with a microkernel**: **the primary module has only core functions and knowledge of how to load and communicate with other modules**; other services are added separately.
- **Difference**: LKM is **more efficient, because modules do not need to invoke message passing to communicate**; they run inside the kernel and call each other directly, whereas microkernel services run in **user space** and talk through **message passing**.
- **Versus layered**: like a layered design, **each kernel section has a well-defined, protected interface**, but LKM is **more flexible, since any module can call any other module**.

## [X2-33] ch2 | Hybrid systems: Linux, Windows, macOS
Why are most modern OSes hybrid systems? Explain how Linux, Windows and macOS combine structures. [2.52–2.53]

**Answer:**
**Very few OSes adopt a single, strictly defined structure**; they **combine different structures to address performance, security and usability needs**.
- **Linux**: **monolithic** (OS in a single address space, so **efficient performance**) and **modular** (new functionality is **dynamically added** via LKMs).
- **Windows**: **largely monolithic**, but keeps microkernel-like behaviour with **separate subsystems (personalities) running as user-mode processes**, and supports **dynamically loadable kernel modules**.
- **macOS / iOS**: **layered** (user interface, application environments, kernel environment) with the kernel **Darwin = Mach microkernel + BSD UNIX kernel**, plus **dynamically loadable kernel extensions (kexts)**.

## [X2-34] ch2 | Compare monolithic, layered, microkernel, LKM
Compare the monolithic, layered, microkernel and loadable-kernel-module structures. [2.38–2.53]

**Answer:**
**Monolithic is fastest but hardest to maintain; microkernel is the most extensible and reliable but slowest; LKM combines modularity with near-monolithic speed.**

| | **Monolithic** | **Layered** | **Microkernel** | **LKM (modular)** |
|---|---|---|---|---|
| Idea | all kernel functions in **one static binary, one address space** | **layer 0 = hardware ... layer N = UI**; each layer uses only lower layers | **minimal kernel** (process and memory management, IPC); other services in **user space** | **core kernel + modules loaded or removed at boot or run time** |
| Communication | direct calls inside the kernel | calls to lower layers | **message passing** via the kernel | direct calls; **any module can call any other** |
| Performance | **best: little system-call overhead** | overhead of **traversing layers** | **worst: message-passing overhead** | **close to monolithic** |
| Main advantage | **efficiency** | **simple construction and debugging** | **easy to extend and port; more secure and reliable** | **flexible; no recompile or reboot** |
| Main drawback | **hard to implement, debug, maintain** (tightly coupled) | **hard to define the layers** | **performance suffers** | modules run in kernel mode, so a faulty module can still crash the kernel |
| Examples | **original UNIX**, Linux, Windows (largely) | TCP/IP networking; few pure OSes | **Mach**, Darwin, Windows NT | **Linux, Solaris** |

## [X2-35] ch2 | Scenario: choose an OS structure
Which structure would you choose, and why, for: (a) a server where speed matters most; (b) a safety-critical system where a failed service must not bring down the OS; (c) a desktop OS that must add drivers and file systems without rebooting; (d) an OS to be ported to many hardware platforms? [2.41–2.53]

**Answer:**
- (a) **Monolithic** (possibly with LKMs): **very little overhead in the system-call interface and fast communication within the kernel**.
- (b) **Microkernel**: services run as **user processes in separate address spaces**, so **if a service fails, the rest of the OS remains untouched**; less code in kernel mode makes it **more secure and reliable**.
- (c) **Loadable kernel modules (modular / hybrid)**: drivers and file systems are **loaded or removed at run time without recompiling or rebooting**, while keeping monolithic performance.
- (d) **Microkernel**: the **small kernel is more easily ported** to new hardware (writing the OS in a **high-level language** also helps).

## [X2-36] ch2 | Mac OS X structure: Darwin, Mach, BSD
Describe the structure of Mac OS X. What is Darwin, and what do Mach and BSD each provide? [2.54–2.57]

**Answer:**
Mac OS X is **hybrid and layered**: **Aqua GUI** (for mouse or trackpad) → **application environments and services** (**Cocoa** programming environment with an **Objective-C API**; **Core frameworks** for graphics and media, e.g., QuickTime, OpenGL) → **kernel environment, Darwin**.
- **Darwin** = **Mach microkernel + BSD UNIX kernel** (the hybrid **XNU kernel**), with **two system-call interfaces: Mach system calls (known as traps) and BSD system calls (POSIX functionality)**, plus rich libraries (standard C library, networking, security, programming-language support).
- **Mach** provides **fundamental OS services: memory management, CPU scheduling and IPC facilities**.
- **BSD** provides the **POSIX API, networking, file system and security**.
- The kernel environment also has an **I/O Kit for device drivers** and **dynamically loadable modules called kernel extensions (kexts)**.

## [X2-37] ch2 | macOS vs iOS: similarities, differences
Compare macOS and iOS. [2.54–2.56]

**Answer:**
**Similar**: both share the same architecture of **user interface, programming (language) support, graphics and media services, and the kernel environment Darwin (Mach microkernel + BSD UNIX kernel)**; iOS is **structured on Mac OS X with added functionality**.

| | **macOS** | **iOS** |
|---|---|---|
| User interface | **Aqua** (mouse or trackpad) | **Springboard** (touch devices) |
| Programming API | **Cocoa** (Objective-C API) | **Cocoa Touch** (Objective-C API for touch-screen devices) |
| Graphics and services | **Core frameworks** (QuickTime, OpenGL) | **Media services** (graphics, audio, video) and **Core services** (cloud computing, databases) |
| CPU | Intel | **ARM**; iOS **does not run Mac OS X applications natively** |

## [X2-38] ch2 | iOS vs Android: similarities, differences
Compare iOS and Android. [2.58]

**Answer:**
**Similarities**: (1) both are **based on existing kernels** (Android on **Linux**, iOS on the **Mac OS X kernel**); (2) both use a **layered software-stack architecture**; (3) both provide **rich frameworks for developers** (graphics, audio, hardware features).

| | **iOS** | **Android** |
|---|---|---|
| Source | **closed-source**; runs only on Apple mobile devices | **open-source**; runs on a variety of mobile platforms (Open Handset Alliance, led by Google) |
| App language | **Objective-C** | **Java**, using a separate **Android API** |
| Execution | **executes code natively** | apps run on a **virtual machine, the Android RunTime (ART)** |

## [X2-39] ch2 | Android architecture: ART, JNI, HAL, Bionic
Explain the roles of ART, JNI, HAL and Bionic in the Android architecture. [2.58–2.59]

**Answer:**
- **ART (Android RunTime)**: the **virtual machine on which Java applications execute**, **optimized for mobile devices with limited memory and CPU processing capabilities**.
- **JNI (Java Native Interface)**: lets developers **bypass the virtual machine** and write Java programs that **access specific hardware features**; such programs are **generally not portable** from one hardware to another.
- **HAL (hardware abstraction layer)**: **abstracts all hardware** (camera, GPS chip, other sensors) and gives applications a **consistent view independent of specific hardware**.
- **Bionic**: Google's **standard C library for Android**, used **instead of glibc**. Underneath is a **modified Linux kernel** for mobile systems (e.g., **power management**); libraries include **WebKit**, **SQLite** and **SSL**.

## [X2-40] ch2 | History: from batch to time sharing
Briefly describe how operating systems evolved, and why the focus moved from hardware utilization to user convenience. [2.60]

**Answer:**
**Early on, hardware was expensive and humans relatively cheap, so OSes maximized hardware utilization; later hardware became cheap and humans expensive, so OSes focused on users.**
- **Hand-programmed machines (1945–1955)** had low hardware utilization, followed by **batch processing (1955–1965)** and **multiprogramming (1965–1980)**: multiple jobs in memory, **multiplexed over the CPU(s)**.
- **Time sharing**: users share servers through cheap terminals. **Personal computers**: utilization is not a major concern; the focus is on **user interfaces and APIs**. **Distributed OSes**: consistency, performance, reliability and resource management. **Real-time OSes**: guarantee or prioritize jobs.

## [X2-TF] ch2 | True / False quick verdicts

| Statement | T/F | Why (≤ 12 words) |
|---|---|---|
| `printf()` is a system call provided by the kernel. | F | It is a library function that calls `write()`. |
| Every C library (API) function makes a system call. | F | Some, e.g., `strlen()`, run entirely in user mode. |
| Windows `CreateProcess()` invokes the `NTCreateProcess()` system call. | T | API functions invoke system calls for the programmer. |
| `read()` returns 0 at end of file and −1 on error. | T | Otherwise it returns the number of bytes read. |
| Using an API lets a program bypass kernel protection. | F | APIs only wrap system calls; protection still applies. |
| An API caller must know how the system call is implemented. | F | The caller only obeys the API and knows the result. |
| Each system call has a number that indexes a table. | T | The system-call interface maintains the table. |
| Block and stack methods limit the number of parameters. | F | Only registers are limited; block and stack are not. |
| With the stack method, the OS pushes and the program pops. | F | The program pushes parameters; the OS pops them. |
| The command interpreter is always part of the kernel. | F | Sometimes in the kernel, sometimes a system program. |
| Most users' view of the OS is defined by system calls. | F | It is defined by application and system programs. |
| Daemons are background services that run until the system halts. | T | Launched at boot, e.g., for error logging. |
| The loader combines object files into an executable. | F | The linker combines; the loader loads into memory. |
| A DLL is loaded once and shared by programs using it. | T | Same library version; saves memory. |
| Policy specifies how something is done. | F | Policy = what; mechanism = how. |
| A timer is a mechanism; its length for a user is a policy. | T | The slides' standard policy-versus-mechanism example. |
| Writing an OS in a high-level language makes it easier to port. | T | Recompile for new hardware; code is also easier to debug. |
| MS-DOS creates a new process for every program it runs. | F | Single-tasking: program overwrites all memory but the kernel. |
| MS-DOS on the Intel 8088 had dual mode and hardware protection. | F | Neither; applications could access I/O directly. |
| Monolithic kernels have very little system-call overhead. | T | Single address space; fast communication within the kernel. |
| In a layered OS, layer 0 is the user interface. | F | Layer 0 is the hardware; layer N is the UI. |
| In a microkernel, an app and the file server interact directly. | F | They exchange messages through the microkernel. |
| Windows XP was more microkernel-like than Windows NT. | F | XP became more monolithic for performance. |
| Loadable kernel modules communicate by message passing. | F | Modules call each other directly, so they are more efficient. |
| LKMs can be loaded and removed while the kernel runs. | T | No recompiling or rebooting is needed. |
| Windows personalities run as user-mode processes. | T | A microkernel-like feature of largely monolithic Windows. |
| In Darwin, Mach provides networking and the file system. | F | Mach: memory, CPU scheduling, IPC; BSD: networking, files. |
| iOS runs Mac OS X applications natively. | F | Different CPU architecture (ARM vs. Intel). |
| Android programs written with JNI are portable across hardware. | F | JNI accesses specific hardware; generally not portable. |
| Android uses glibc as its standard C library. | F | Android uses Google's Bionic C library. |
