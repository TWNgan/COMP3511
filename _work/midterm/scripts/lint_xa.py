"""Lint the answer-bank files (Midterm_Notes/xa_*.md): entry format, IDs, answers, math pitfalls."""
import glob
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HEAD = re.compile(r"^## \[([^\]]+)\] (ch\d) \| (.+)$", re.M)
ids = {}
for path in sorted(glob.glob(r"C:\Code\UST\COMP3511\Midterm_Notes\xa_*.md")):
    name = os.path.basename(path)
    if name == "xa_intro.md":
        continue
    md = io.open(path, encoding="utf-8").read()
    heads = list(HEAD.finditer(md))
    loose = [l for l in md.splitlines() if l.startswith("## ") and not HEAD.match(l)]
    n_tf = n_qa = 0
    problems = []
    for k, m in enumerate(heads):
        end = heads[k + 1].start() if k + 1 < len(heads) else len(md)
        body = md[m.end():end]
        eid = m.group(1)
        if eid in ids:
            problems.append("duplicate id %s (also in %s)" % (eid, ids[eid]))
        ids[eid] = name
        n_ans = len(re.findall(r"^\*\*Answer:\*\*\s*$", body, re.M))
        if eid.endswith("-TF"):
            n_tf += 1
            if n_ans:
                problems.append("%s: TF block has an Answer line" % eid)
            rows = [l for l in body.splitlines() if l.startswith("|")]
            if len(rows) < 5:
                problems.append("%s: TF table has only %d rows" % (eid, len(rows)))
        else:
            n_qa += 1
            if n_ans != 1:
                problems.append("%s: %d '**Answer:**' lines" % (eid, n_ans))
        text = re.sub(r"```[\s\S]*?```", "", body)
        text = re.sub(r"`[^`\n]*`", "", text)
        if text.count("$") % 2:
            problems.append("%s: odd number of $ (unbalanced math)" % eid)
        for f in re.findall(r"\$[^$]*\\frac[^$]*\\frac[^$]*\$", text):
            if re.search(r"\\frac\{[^{}]*\\frac", f):
                problems.append("%s: nested fraction %s" % (eid, f[:60]))
        if re.search(r"\\tfrac", text):
            problems.append("%s: \\tfrac (prints tiny)" % eid)
    print("%-16s Q&A %3d | TF blocks %d | loose '## ' lines %d" % (name, n_qa, n_tf, len(loose)))
    for p in problems + ["loose heading: " + l[:70] for l in loose]:
        print("   !", p)
print("total entries:", len(ids))
