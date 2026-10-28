"""Report markdown table rows whose cell count differs from the header (pipes in code are protected)."""
import glob
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
PH = "\uE000"


def cells(line):
    s, out, inc, i = line.strip(), [], False, 0
    while i < len(s):
        ch = s[i]
        if ch == "`":
            inc = not inc
            out.append(ch)
        elif ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            out.append(PH)
            i += 1
        elif inc and ch == "|":
            out.append(PH)
        else:
            out.append(ch)
        i += 1
    return len("".join(out).strip().strip("|").split("|"))


bad = 0
for f in sorted(glob.glob(r"C:\Code\UST\COMP3511\Midterm_Notes\*.md")):
    L = io.open(f, encoding="utf-8").read().split("\n")
    incode = False
    for i, line in enumerate(L):
        if line.strip().startswith("```"):
            incode = not incode
        if incode:
            continue
        if line.lstrip().startswith("|") and i + 1 < len(L) and re.match(r"^\s*\|[\s:\-|]+\|\s*$", L[i + 1]):
            n, j = cells(line), i + 2
            while j < len(L) and L[j].lstrip().startswith("|"):
                if cells(L[j]) != n:
                    bad += 1
                    print(f.split("\\")[-1], j + 1, n, cells(L[j]), L[j][:100])
                j += 1
print("mismatched rows:", bad)
