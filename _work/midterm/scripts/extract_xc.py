"""Extract every ```c block of Midterm_Notes/xa_code.md into _work/midterm/c/xc/XC-nn.c (for compile tests)."""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"C:\Code\UST\COMP3511\Midterm_Notes\xa_code.md"
OUT = r"C:\Code\UST\COMP3511\_work\midterm\c\xc"
os.makedirs(OUT, exist_ok=True)
md = io.open(SRC, encoding="utf-8").read()
for m in re.finditer(r"^## \[(XC-\d+)\][^\n]*\n(.*?)(?=^## \[|\Z)", md, re.M | re.S):
    blocks = re.findall(r"```c\n(.*?)```", m.group(2), re.S)
    for k, b in enumerate(blocks):
        name = m.group(1) + ("" if k == 0 else "_%d" % k) + ".c"
        io.open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n").write(b)
        print(name, len(b.splitlines()), "lines")
