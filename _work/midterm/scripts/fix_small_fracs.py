"""Replace nested / \\tfrac fractions that print too small with slash forms (idempotent)."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
N = "C:\\Code\\UST\\COMP3511\\Midterm_Notes\\"
EDITS = {
    "cb_essentials.md": [(r"S + \frac{1-S}{N}}", r"S + (1-S)/N}"),
                         (r"S = \tfrac{1}{9}", r"S = 1/9"),
                         (r"\frac{25}{50} + \frac{35}{80}", r"25/50 + 35/80")],
    "cb_playbooks.md": [(r"\tfrac{1}{2}", r"1/2")],
    "ch5_cpu_scheduling.md": [(r"\tfrac{1}{2}", r"1/2")],
}
for name, pairs in EDITS.items():
    path = N + name
    s = io.open(path, encoding="utf-8").read()
    for old, new in pairs:
        print(name, repr(old), s.count(old))
        s = s.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
