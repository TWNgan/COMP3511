# Chapter 2 — Operating-System Structures（作業系統結構）

> 📌 **考試範圍提示**：Ch2 每年都有 **3–5 題 MC** + **1–2 題 short question**。必考：**API vs system call（點解要分開）**、**printf() → write()**、**parameter passing 三種方法**、**linker vs loader**、**monolithic / layered / microkernel / LKM / hybrid 比較**（優缺點）、**policy vs mechanism**、**OS services**。
> ⚠️ **Dual-mode / interrupt / trap** 今個 term 放咗喺 **Ch3 slides（3.x）**，見 Ch3 notes §0。

---

## 1. Operating System Services（OS 服務）[2.4–2.7]

OS provides an environment for **execution of programs** and **other services to programs and users**。分兩組：

### 1.1 對 user 有用嘅服務（helpful to the user）
| Service | 解釋 |
|---|---|
| **User interface (UI)** | **CLI (command-line)**, **GUI**, **touch-screen** |
| **Program execution** | load a program into memory and run it; end execution **normally or abnormally (indicating error)** |
| **I/O operations** | running program may require I/O（file 或 I/O device） |
| **File-system manipulation** | read/write/create/delete/search files & directories, list info, **permission management** |
| **Communications** | processes exchange information（同一部機或 network）via **shared memory** or **message passing (packets moved by the OS)** |
| **Error detection** | errors **may occur in CPU and memory, in I/O devices, in user programs**；OS takes appropriate actions；**debugging facilities** |

### 1.2 確保系統本身有效運作（efficient operation via resource sharing）
| Service | 解釋 |
|---|---|
| **Resource allocation** | 多 user/job 同時跑 → 分配 **CPU cycles, memory, file storage, I/O devices** |
| **Logging (accounting)** | **keep track of which users use how much and what kinds of computer resources** |
| **Protection and security** | **Protection**: ensure all access to system resources is controlled；**Security**: defend from outsiders → **user authentication**, defend external I/O devices from invalid access |

> ⚠️ **S26 MC5 陷阱**：「**Errors only occur in memory and I/O devices**」→ **False**（CPU、memory、I/O devices、user programs 都可以出錯）。
> ✅「Logging service should keep track of computer resources that each user uses」→ True。

- Summary 補充：OS services 兩大類 —（1）**enforce protection among concurrent processes**（process 只可以存取自己 address space；唔可以直接存取 hardware）；（2）**provide functionalities not directly supported by hardware**（memory management、file systems）。
- [2.7/2.13 圖] user & system programs → user interfaces (GUI/touch/CLI) → **system calls** → services (program execution, I/O, file systems, communication, resource allocation, accounting, error detection, protection & security) → OS → hardware。

![OS services and the system-call layer [2.13]](img/ch2_p13.png)


---

## 2. User Interfaces [2.8–2.12]

- **CLI / command interpreter** — allows **direct command entry**。
  - **Sometimes implemented in kernel, sometimes by system programs.**
  - 有多個 flavor → **shells**（C shell, **Bourne-Again shell (bash)**, Korn shell）。
  - **Shell 嘅主要功能：(1) fetches a command from user, (2) interprets it, (3) executes it.** ⭐（PA1 myshell 就係做呢樣）
- **GUI** — user-friendly **desktop metaphor**；icons；mouse；**invented at Xerox PARC (early 1970s)**，first widely used in **Apple Macintosh (1984)**。Windows = GUI + CLI "command" shell；Mac OS X = **"Aqua" GUI** + UNIX kernel；Unix/Linux = CLI + optional GUI（KDE, GNOME）。
- **Touchscreen** — gestures, virtual keyboard, voice command（Siri）。

---

## 3. System Calls ⭐⭐ [2.13–2.26]

### 3.1 定義
- **System calls provide the programming interface to the services provided by the OS.**（Sp21 MC：「___ provide an interface to the services provided by an OS」→ **System calls**）
- 通常以 **high-level language (C/C++) functions** 提供；**certain low-level tasks written in assembly** for accessing hardware。
- 例：`cp in.txt out.txt` 涉及**一連串 system calls**（acquire input file name、open input file、create output file、loop read/write、close、write completion message、terminate normally）。

### 3.2 API (Application Programming Interface) [2.15]
- **API specifies a set of functions available to application programmers, including the parameters passed to each function and the return values it may expect.**
- **The functions that make up an API invoke the actual system calls on behalf of the programmer.**
  - 例：Windows `CreateProcess()` invokes `NTCreateProcess()` system call。
- Programmer 經 OS 提供嘅 **library** 用 API；UNIX/Linux C → **libc**。
- **三大 API**：**Win32 API**（Windows）、**POSIX API**（UNIX, Linux, Mac OS X）、**Java API**（JVM）。
- [2.16] `ssize_t read(int fd, void *buf, size_t count)` — `fd` file descriptor；`buf` buffer；`count` max bytes；**return 0 = end of file；−1 = error**。

### 3.3 點解用 API 而唔直接 call system call？⭐（F19 Q1.3、S26 MC6）[2.17]
> 📝 **Model answer**：*(1) **Program portability** — a program using an API can compile and run on any system that supports the same API, even though the implementation of system calls varies from machine to machine. (2) **Hide the complex details of system calls** — actual system calls are often more detailed and difficult to work with; the caller only needs to obey the API and understand what the OS will do, not how the system call is implemented.*

- S26 MC6 答案：**APIs provide a more convenient programming interface**。
- ❌「APIs always execute faster than system calls」、❌「APIs can bypass kernel protection」、❌「APIs eliminate the need for linkers and loaders」。
- F20 MC4：「Programmers interface with ___ to obtain services from the OS」→ **APIs**（best answer）。

### 3.4 System Call Implementation [2.18–2.19]
- 大部分語言嘅 **run-time environment (RTE)**（a set of functions built into libraries）提供 **system-call interface**，作為連接 OS system calls 嘅 **link**。
- **Each system call is associated with an identity number**；system-call interface **maintains a table indexed by these numbers**。
- System-call interface 做三件事：**intercepts function calls in the API → invokes the necessary system call within the OS → returns the status of the system call and return value(s)**。
- **The caller knows nothing about how a system call is implemented.**（只需要 obey API）

![API – system call – OS relationship [2.19]](img/ch2_p19.png)

- [2.19 圖]：user application 呼叫 `open()` → (user mode) **system call interface** → (kernel mode) 用 index *i* 查 table → implementation of `open()` → return。

> 📝 **HW1 Q2.4：user program call read() 點樣 user→kernel→user？（三步）**
> 1. *The program calls the `read()` API in libc (user mode); the library/system-call interface puts the system-call number and parameters in registers (or a block/stack) and executes a **trap (system-call) instruction**.*
> 2. *The trap switches the CPU to **kernel mode** (mode bit 1→0); the kernel uses the system-call number to index the **system-call table** and runs the `read()` service routine (which may block waiting for the device).*
> 3. *When finished, the kernel puts the return value/status in a register, executes a **return-from-trap** which resets the mode to **user mode**, and control returns to the instruction after the call.*
> - HW1 MC6 答案：**The API and run-time environment use the system-call interface to invoke the corresponding kernel service, and control later returns to the application.**

### 3.5 System Call Parameter Passing ⭐ [2.20–2.21]
三種方法（F20 MC5：**All of the above**）：
1. **Registers** — simplest；但可能 parameters 多過 registers。
2. **Block (table) method** — parameters stored in a **block/table in memory**, **address of the block passed in a register**（Linux & Solaris 用）。
3. **Stack method** — parameters **pushed onto the stack by the program and popped off by the OS**。
- **Block and stack methods do not limit the number or length of parameters.**

### 3.6 Types of System Calls（六類）⭐ [2.22–2.25]
| 類別 | 例子 | UNIX 例 | Windows 例 |
|---|---|---|---|
| **Process control** | create/terminate process, end/abort, load/execute, get/set attributes, wait for time, wait/signal event, allocate/free memory, dump memory, debugger, **locks** | `fork()`, `exit()`, `wait()` | `CreateProcess()`, `ExitProcess()`, `WaitForSingleObject()` |
| **File management** | create/delete, open/close, read/write/reposition, get/set attributes | `open()`, `read()`, `write()`, `close()` | `CreateFile()`, `ReadFile()`, `WriteFile()`, `CloseHandle()` |
| **Device management** | request/release device, read/write, get/set attributes, attach/detach | `ioctl()`, `read()`, `write()` | `SetConsoleMode()`, `ReadConsole()`, `WriteConsole()` |
| **Information maintenance** | get/set time/date, system data, attributes | `getpid()`, `alarm()`, `sleep()` | `GetCurrentProcessID()`, `SetTimer()`, `Sleep()` |
| **Communications** | create/delete connection, send/receive messages (**message passing**), **shared-memory** create/access regions | `pipe()`, `shm_open()`, `mmap()` | `CreatePipe()`, `CreateFileMapping()`, `MapViewOfFile()` |
| **Protection** | control access, get/set permissions, allow/deny user access | `chmod()`, `umask()`, `chown()` | `SetFileSecurity()`, ... |

### 3.7 Standard C Library Example ⭐（S26 MC8）[2.26]
- **C program invoking `printf()` library call, which calls the `write()` system call.**
- ✅ **"printf() invokes write() system call to get service from OS"**
- ❌ 「printf() and write() are both system calls」（printf 係 library function）
- ❌ 「program enters kernel mode immediately when printf() is called」（printf 喺 user mode 處理 formatting/buffering，到 write() 先 trap 入 kernel）
- ❌ 「write() invokes printf()」

---

## 4. System Programs（系統程式）[2.27–2.30]

- **System services / system programs / system utilities provide a convenient environment for program development and execution.**
- 有啲只係 **user interfaces to system calls**；有啲複雜得多。
- **The view of the OS seen by most users is defined by the application and system programs, not the actual system calls.**（GUI 同 CLI 用同一套 system calls，但 user 睇落好唔同）
- **類別**：
  - **File management** — create, delete, copy, rename, print, list files/directories
  - **Status information** — date, time, available memory, disk space, number of users；performance, logging, debugging info
  - **File modification** — text editors；search/transform file contents
  - **Programming-language support** — compilers, assemblers, debuggers, interpreters
  - **Program loading and execution** — absolute loaders, relocatable loaders, linkage editors, overlay loaders, debugging systems
  - **Communications** — virtual connections among processes/users/systems（message, web, email, remote login, file transfer）
  - **Background services** — launch at boot；有啲跑到系統關機 → **services, subsystems, daemons**（disk checking, process scheduling, error logging）
- **Application programs** — **not part of the OS**（browsers, word processors, spreadsheets, databases, games）。

---

## 5. Linkers and Loaders ⭐⭐（F19 Q1.1、F20 Q2.2 都考過）[2.31–2.32]

```
main.c --(compiler: gcc -c main.c)--> main.o (relocatable object file)
main.o + other object files + libraries --(linker: gcc -o main main.o -lm)--> main (executable file)
main --(loader: ./main)--> program in memory  (+ dynamically linked libraries)
```
- **Source code is compiled into relocatable object files**（designed to be loaded into any physical memory location）。
- **Linker combines these relocatable object files into a single binary executable file**（along with libraries if needed, e.g. `-lm` math library）。
- **Programs reside on secondary storage as binary executables, which must be brought into memory by the loader to be executed.**
- **Relocation** assigns final addresses to program parts and adjusts code & data to match those addresses。
- Modern OS **don't link libraries statically**；而係用 **dynamically linked libraries (DLLs in Windows)** — **loaded when needed, shared by all programs using the same version (loaded only once)** → 慳 memory，避免 link 用唔到嘅 library。
- Object files / executables 有 **standard formats**（machine code + symbol table；Linux = **ELF**）→ OS 知點 load 同 start。

![Role of the linker and loader [2.32]](img/ch2_p32.png)


> 📝 **Model answer**：*The **linker** combines several relocatable object files (generated by the compiler), together with any needed libraries, into a single binary executable file stored on disk. The **loader** loads the binary executable file into memory (possibly together with dynamically linked libraries) so that it can be run on a CPU.*

---

## 6. OS Design and Implementation [2.33–2.37]

### 6.1 Design goals [2.33]
- Design 受 **choice of hardware, type of system**（desktop, mobile, distributed, real-time）影響；先定 **goals and specifications**。
- **User goals**：convenient to use, easy to learn and use, reliable, safe, fast。
- **System goals**：easy to design, implement, maintain; flexible, reliable, error-free, efficient。

### 6.2 Policy vs Mechanism ⭐ [2.34]
- **Policy: What will be done?　Mechanism: How to do it?**
- 例：**A timer is a mechanism for ensuring CPU protection, but deciding how long the timer is set for a particular user is a policy decision.**
- **Separation of policy from mechanism allows flexibility if policy decisions are changed later**（同一個 mechanism 可以支持「I/O-intensive 優先」或者相反嘅 policy）。
- 總結：**goals → determine policies → implemented through mechanisms**。

### 6.3 Implementation [2.35]
- 早期用 **assembly**；而家多數用 **C/C++**；最底層 kernel 可能仍用 assembly。Android：system libraries C/C++，frameworks Java。
- **Advantages of high-level languages**：**easier to port to other hardware**；code written faster, more compact, easier to understand and debug；compiler 進步 → recompile 就變好。
- **Disadvantages**：reduced speed、increased storage requirements（今日唔係大問題）。

### 6.4 Examples [2.36–2.37]
- **MS-DOS**：**single-tasking**；開機 invoke shell；**no process created**；single memory space；load program overwriting all but the kernel；program exit → shell reloaded。
- **FreeBSD**（Unix variant）：**multitasking**；user login → shell；**shell executes `fork()` to create a new process, `exec()` to load a new program into the process**；shell **waits for the process to terminate** or continues with user commands（background）；需要 CPU scheduling、process coordination、memory management。

---

## 7. Operating System Structure ⭐⭐⭐（必考比較題）[2.38–2.53]

### 7.0 一覽表
| Structure | 核心概念 | 優點 | 缺點 | 例子 |
|---|---|---|---|---|
| **Simple structure** | 無 well-defined structure | most functionality in least space | interfaces/levels 唔分明；**app 可直接 access I/O**；no dual mode/no hardware protection | **MS-DOS** |
| **Monolithic** | **all kernel functionality in a single, static binary file running in a single address space** | **performance**：system-call interface overhead 好少，kernel 內部溝通快 | **difficult to implement, debug, maintain/modify**；**tightly coupled** | **Original UNIX**, Linux, Windows（largely） |
| **Layered** | layer 0 = hardware … layer N = user interface；每層只用下層服務 | **simplicity of construction and debugging**；**information hiding** | **難定義 layers**；**performance overhead**（traverse 多層） | TCP/IP networks；(pure layered OS 好少) |
| **Microkernel** | **remove nonessential components from kernel, implement them as user-level programs in separate address spaces**；靠 **message passing** | **easier to extend**、**easier to port**、**more secure and reliable**（less code in kernel mode） | **performance suffers** due to **increased system-function overhead / user–kernel communication / message copying** | **Mach**, Darwin（macOS/iOS 部分）, Windows NT（layered microkernel） |
| **Loadable kernel modules (LKMs)** | core kernel + **dynamically loaded modules（boot time or run time）** | 唔使 recompile/reboot；**any module can call any other module**；**no message passing → more efficient than microkernel** | （仍喺 kernel mode，module 出錯可影響 kernel） | **Linux**（device drivers, file systems）, Solaris |
| **Hybrid** | 混合多種結構 | performance + security + usability | 複雜 | **Linux**（monolithic + modular）, **Windows**（monolithic + microkernel-like **personalities** + LKMs）, **macOS/iOS**（Darwin = Mach + BSD） |

### 7.1 Simple Structure — MS-DOS [2.39]
- **Written to provide the most functionality in the least space**；not carefully divided into modules。
- **Application programs can access I/O directly**（interfaces/levels 唔分開）。
- Written for **Intel 8088 — no dual mode and no hardware protection**。

### 7.2 Monolithic Structure — Original UNIX ⭐ [2.40–2.42]
- **Traditional UNIX kernel = everything below the system-call interface and above the physical hardware.**

![Original UNIX: monolithic structure [2.40]](img/ch2_p40.png)

- **Place all functionality of the kernel into a single, static binary file that runs in a single address space.**
- **UNIX = two separable parts: kernel + system programs**；kernel 再分成 interfaces 同 device drivers。
- **Drawback**：enormous functionalities combined into one level → **difficult to implement, debug, and maintain**。
- **Advantage**：**distinct performance advantage — very little overhead in the system-call interface, and communication within the kernel is fast.** → 所以 UNIX、Linux、Windows 仍然用。
- Sp21 MC：Original UNIX 採用 → **Monolithic structure**。
- **Linux** [2.42]：based on UNIX；**monolithic — runs entirely in kernel mode in a single address space**；apps 用 **glibc** 同 system call interface 溝通；**modular design 可以 run time 改 kernel（LKM）**。

### 7.3 Modular Design [2.43]
- Monolithic = **tightly coupled system**（改一部分影響其他部分）。
- **Loosely coupled system**：分成細 components，每個有 specific/limited 功能 → **changes in one component affect only that component** → 更自由靈活。
- **Layered approach 係 modular design 嘅其中一種。**

### 7.4 Layered Approach ⭐ [2.44–2.45]
- **OS divided into layers, each built on top of lower layers. Bottom layer (layer 0) = hardware; highest (layer N) = user interface.**
- 每層有 data structures + functions，可被上層調用、可調用下層。
- **Information hiding**：上層唔需要知下層點 implement，只需知 **what** these operations do（interface）；每層隱藏自己嘅 data structures、operations、hardware。
- **Main advantage：simplicity of construction and debugging**（由最底層開始逐層 debug）。
- 成功例子：**computer networks（TCP/IP）**、web applications。
- **Few OSes use a pure layered approach because**：
  1. **Significant challenges in appropriately defining layers and their functionalities**
  2. **Overall performance affected by the overhead of traversing multiple layers to obtain a service**
- Trend：**fewer layers with more functionality**，modularized code。
- S26 MC9 ✅：**The interfaces between adjacent layers are usually well defined**。❌ any layer may directly access any other layer；❌ eliminates all performance overhead；❌ pure layered is dominant。

### 7.5 Microkernel ⭐⭐ [2.46–2.48]
- Kernel 變大難管理 → **removing all nonessential components from the kernel and implementing them as system or user-level programs in separate address spaces** → **much smaller kernel**。
- **Mach**（CMU, mid-1980s）；best-known：**Darwin**（Mac OS X/iOS，包含 Mach microkernel）。
- 微核心通常提供：**minimal process and memory management + communication facility (IPC)**。
- **Main function：provide communication between client programs and services running in user space through message passing.** 例：app 要讀 file → 同 **file server** 經 microkernel **exchange messages**，兩者**唔直接 interact**。

![Microkernel: services in user mode talk via message passing [2.47]](img/ch2_p47.png)

- **Advantages**：
  - **Easier to extend** — new services added to **user space without modifying the kernel**
  - Kernel 要改時改動較少（kernel 細）
  - **Easier to port to new architectures**
  - **More secure and reliable** — less code in kernel mode；**if a service fails, the rest of the OS remains untouched**
- **Drawbacks**：
  - **Performance can suffer due to increased system-function overhead (user space ↔ kernel space communication)**
  - Two user-level services communicate → **messages must be copied between services in separate address spaces**
  - Windows NT（layered microkernel）比 Windows 95 慢 → Windows XP 變返 more monolithic。

> 📝 **F20 Q2.1 Model answer**：*Main idea: a microkernel removes all nonessential components from the kernel and implements them as system or user-level programs in separate address spaces; the kernel keeps only minimal process/memory management and IPC (message passing). Advantage: easier to extend/port, more secure and reliable since less code runs in kernel mode. Disadvantage: performance suffers due to increased system-function overhead — message passing / copying between user space and kernel space.*

> ⚠️ **S26 MC7**：「microkernel typically has better performance than monolithic」→ **False**。（「runs memory management in user space」亦被接受為 false，因為 minimal memory management 喺 kernel 入面。）HW1 MC5 ✅「microkernel keeps only essential functions in the kernel and provides other services outside the kernel through message passing」。

### 7.6 Loadable Kernel Modules (LKMs) — Modular Approach ⭐⭐ [2.49–2.51]
- **Best current methodology for OS design.**
- **Kernel has a set of core components and links in additional services via modules, either at boot time or during run time.**
- 好處：**dynamic linking is preferable to adding features directly to the kernel, which would require recompiling the entire kernel every time**。例：kernel 內有 CPU scheduling + memory management，**file systems 經 loadable modules 加入**。
- **Similar to layered**：each kernel section has **well-defined, protected interfaces**；**but more flexible — any module can call any other module**（無上下層限制）。
- **Similar to microkernel**：primary module 只有 core functions + 知點 load/communicate 其他 modules；**but more efficient — modules do not need message passing to communicate**。
- **Linux uses LKMs primarily for device drivers and file systems**；可以 boot/run time **insert** 或 **remove**。例：插 USB，kernel 冇 driver → dynamic load。
- → **dynamic and modular kernel while keeping the performance benefits of a monolithic system**。
- [2.51] Solaris：core kernel + scheduling classes, file systems, loadable system calls, executable formats, STREAMS modules, misc modules, device & bus drivers。
- F20 MC6：「core components in kernel + adds services via modules during run time」→ **LKMs**。

> 📝 **F19 Q1.4 Model answer（LKM vs layered）**：*Similarity: like a layered design, OS functionality is divided into modules, each with a well-defined (protected) interface. Difference: LKM is much more flexible — any module can call any other module directly, with no higher/lower layer restriction (and modules can be loaded/removed at run time).*

### 7.7 Hybrid Systems [2.52–2.59]
- **Very few OSes adopt a single strictly defined structure → hybrid systems** combine approaches for **performance, security, usability**。
- **Linux**：**monolithic**（single address space → efficient）+ **modular**（LKM）。
- **Windows**：**largely monolithic**，但保留 microkernel 特色 — **separate subsystems (personalities) running as user-mode processes**；亦支援 dynamically loadable kernel modules。
- **macOS / iOS** [2.54–2.57]：kernel environment **Darwin = Mach microkernel + BSD UNIX kernel**（**XNU kernel**，hybrid）。
  - **Two system-call interfaces**：**Mach system calls (traps)** + **BSD system calls (POSIX)**。
  - **Mach** → memory management, CPU scheduling, IPC；**BSD** → POSIX API, networking, file system, security。
  - **I/O kit** for device drivers；dynamically loadable modules = **kernel extensions (kexts)**。
  - Mac：**Aqua** UI（mouse/trackpad）、**Cocoa**（Objective-C API）、Core frameworks（QuickTime, OpenGL）。
  - iOS：**Springboard** UI（touch）、**Cocoa Touch**、Media services、Core services（cloud, databases）；**ARM**（vs Intel）；不能原生跑 Mac apps。
- **Android** [2.58–2.59]：Open Handset Alliance（Google）；**open-source**（iOS closed-source）；layered；**Android API for Java** → 跑喺 **Android RunTime (ART)**（VM optimized for mobile）；**JNI (Java Native Interface)** bypass VM 存取 hardware（**not portable**）；libraries：webkit, SQLite, SSL；**HAL (hardware abstraction layer)** → consistent view；**Bionic** C library（唔係 glibc）；modified Linux kernel（power management）。
- **iOS vs Android**（summary）：相同 — 都基於現有 kernel、software stack、developer frameworks；唔同 — iOS closed / Android open；Objective-C vs Java；**Android uses a VM, iOS executes natively**。

### 7.8 Summary in OS Design [2.53]（原句，MC 用）
- **Monolithic**: no structure; all functionality in a single static binary in a single address space; difficult to modify; **primary benefit is efficiency**.
- **Layered**: discrete layers (bottom = hardware interface, top = user interface); **not ideal for OS due to performance problems and difficulty in defining layers**.
- **Microkernel**: minimal kernel; most services run as user-level applications; **communication via message passing**.
- **LKM**: services through modules **loaded and removed during runtime**.
- **Many contemporary OSes are hybrid: monolithic kernel + modules.**

---

## 8. History of OS [2.60]
- 硬件貴、人平：**Hand programmed (1945–55)** → **Batch processing (1955–65)** → **Multiprogramming (1965–80)**
- 硬件平、人貴：**Time sharing** → **Personal computer** → **Distributed OS** → **Real-time OS**

---

## 9. 補充：Protection & Security（Chapter 2 summary）
- **Protection** — controlling access of users/processes to resources。**Access right** = permission to perform operations on an object；**Domain** = a set of access rights；process 喺 domain 入面執行。
- **Security** — defend system against internal/external attacks（DoS, worms, viruses）。

---

## 10. 常見陷阱 & MC 速查

| 敘述 | 真/假 |
|---|---|
| printf() is a system call | ❌（library function，calls write()） |
| API always faster than system calls | ❌ |
| API can bypass kernel protection | ❌ |
| Parameters can be passed by registers, block/table, stack | ✅（all of the above） |
| Block & stack methods limit number of parameters | ❌（**do not** limit） |
| Shell may be implemented in kernel or as system program | ✅ |
| Linker loads program into memory | ❌（loader 做） |
| DLLs are loaded once and shared | ✅ |
| Microkernel has better performance than monolithic | ❌ |
| Microkernel: services communicate by message passing | ✅ |
| Microkernel easier to port and extend | ✅ |
| Layered: any layer may call any other layer | ❌（LKM 先可以 any module calls any module） |
| Layered: main advantage = simplicity of construction & debugging | ✅ |
| LKM requires recompiling entire kernel | ❌ |
| LKM more efficient than microkernel (no message passing) | ✅ |
| Monolithic: fast but hard to maintain | ✅ |
| Original UNIX = monolithic | ✅ |
| Linux = monolithic + modular (hybrid) | ✅ |
| Windows NT = layered microkernel | ✅ |
| Policy = how; mechanism = what | ❌（**policy = what，mechanism = how**） |
| Darwin = Mach + BSD | ✅ |
| Android apps run on ART VM; iOS runs natively | ✅ |

---

## 11. Past-paper 題目（Ch2）
1. **S26 MC5** false about OS services → **"Errors only occur in memory and I/O devices"**
2. **S26 MC6** advantage of API → **more convenient programming interface**
3. **S26 MC7** false about microkernel → **better performance than monolithic**（C 亦接受）
4. **S26 MC8** printf/write → **printf() invokes write() system call**
5. **S26 MC9** layered → **interfaces between adjacent layers are well defined**
6. **F19 Q1.1 / F20 Q2.2** linker vs loader（§5）
7. **F19 Q1.3** 點解分開 API 同 system call（§3.3）
8. **F19 Q1.4** LKM vs layered（§7.6）
9. **F20 MC4** APIs；**MC5** all of the above；**MC6** LKMs；**Q2.1** microkernel（§7.5）
10. **Sp21 MC**：two modes → **user mode and kernel mode**；interface to OS services → **system calls**；original UNIX → **monolithic**
11. **HW1 MC5** microkernel true statement；**MC6** read() path；**MC7** privileged instruction in user mode → **trap to OS**；**Q2.4** read() user→kernel→user

---

## 12. 自我測驗
1. 寫出 system call 六大類別。
2. 點解 block/stack parameter passing 優於 registers？（no limit on number/length）
3. LKM 同 microkernel 有咩相似同唔同？（both: core kernel small; LKM no message passing → efficient）
4. 舉例說明 policy vs mechanism。（timer = mechanism; how long = policy）
5. FreeBSD shell 點樣 run 一個 program？（fork → exec → wait）
