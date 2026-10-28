"""Insert slide-figure references into the chapter notes after given anchor lines (idempotent)."""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
NOTES = r"C:\Code\UST\COMP3511\Midterm_Notes"

# file -> list of (line prefix to find, image file, caption)
PLAN = {
    "ch1_introduction.md": [
        ("- 越近 CPU → **越快、越細、每 byte 越貴**", "ch1_p29.png", "Storage hierarchy [1.29]"),
        ("- [1.45] 圖：(a) processes → kernel → hardware", "ch1_p45.png", "Virtualization system models [1.45]"),
    ],
    "ch2_os_structures.md": [
        ("- [2.7/2.13 圖] user & system programs", "ch2_p13.png", "OS services and the system-call layer [2.13]"),
        ("- **The caller knows nothing about how a system call is implemented.**", "ch2_p19.png", "API – system call – OS relationship [2.19]"),
        ("- Object files / executables 有 **standard formats**", "ch2_p32.png", "Role of the linker and loader [2.32]"),
        ("- **Traditional UNIX kernel = everything below the system-call interface", "ch2_p40.png", "Original UNIX: monolithic structure [2.40]"),
        ("- **Main function：provide communication between client programs", "ch2_p47.png", "Microkernel: services in user mode talk via message passing [2.47]"),
    ],
    "ch3_processes.md": [
        ("6. **When C = 0, DMA interrupts CPU to signal transfer completion**", "ch3_p26.png", "Six-step DMA transfer [3.26]"),
        ("- Running → Terminated：**exit**", "ch3_p9.png", "Process state diagram [3.9]"),
        ("- **Queueing diagram** [3.16]", "ch3_p16.png", "Queueing diagram [3.16]"),
    ],
    "ch4_threads.md": [
        ("> ⚠️ **F20 MC11**：NOT shared by threads in the same process → **Stack**。", "ch4_p6.png", "Single- vs multithreaded process [4.6]"),
        ("- **Concurrency without parallelism 係可以嘅；parallelism 一定 concurrent。**", "ch4_p10.png", "Concurrency vs parallelism [4.10]"),
    ],
    "ch5_cpu_scheduling.md": [
        ("  - P4（priority 1）先跑完；P2、P3（priority 2）RR", "ch5_p27.png", "Priority scheduling with round-robin, q = 2 [5.27]"),
        ("- 例 [5.50]：P1 (50, 25), P2 (80, 35)", "ch5_p50.png", "RM: P2 misses its deadline at 80 [5.50]"),
        ("- 例 [5.51]（P1 50/25, P2 80/35）", "ch5_p51.png", "EDF: same tasks, no deadline missed [5.51]"),
    ],
}

for fname, items in PLAN.items():
    path = os.path.join(NOTES, fname)
    lines = io.open(path, encoding="utf-8").read().split("\n")
    for prefix, img, cap in items:
        tag = "![%s](img/%s)" % (cap, img)
        if any(tag in l for l in lines):
            continue
        idx = next((i for i, l in enumerate(lines) if l.startswith(prefix)), None)
        if idx is None:
            print("NOT FOUND:", fname, prefix[:50])
            continue
        # insert after the end of this list item / paragraph block (next blank line or next bullet at same level)
        j = idx + 1
        while j < len(lines) and lines[j].strip() and lines[j].startswith(("  ", "    ")) and not lines[j].lstrip().startswith(("- ", "|")):
            j += 1
        lines[j:j] = ["", tag, ""]
        print("inserted", img, "into", fname, "at line", j + 1)
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
