"""Build the printable COMP3511 midterm cheat book (HTML -> PDF, two passes for page numbers).

Run:  python -I build_cheatbook.py
Outputs:
  C:\\Code\\UST\\COMP3511\\COMP3511_Midterm_CheatBook.pdf   (print this)
  C:\\Code\\UST\\COMP3511\\COMP3511_Midterm_CheatBook.html  (same content, on-screen)
"""
import glob
import html
import io
import json
import os
import re
import shutil
import site
import subprocess
import sys

sys.path.append(site.getusersitepackages())
import fitz  # noqa: E402
import mistune  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Code\UST\COMP3511"
NOTES = os.path.join(ROOT, "Midterm_Notes")
WORK = os.path.join(ROOT, "_work", "midterm", "cb")
OUT_PDF = os.path.join(ROOT, "COMP3511_Midterm_CheatBook.pdf")
OUT_HTML = os.path.join(ROOT, "COMP3511_Midterm_CheatBook.html")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# code, source, English title (footer/tab), Chinese subtitle, colour
PARTS = [
    ("H", None, "How-to Guide", "攻略・fork・sched・sync", "#b08900"),
    ("E", "cb_essentials.md", "Exam-Day Essentials", "考場一頁通：公式・慣例・陷阱", "#d63939"),
    ("P", "cb_playbooks.md", "Playbooks", "解題流程 + 預計表", "#e8590c"),
    ("X", None, "Answer Bank", "預測題 + 直接抄答案・C programs", "#111111"),
    ("1", "ch1_introduction.md", "Ch1 Introduction", "引言", "#1971c2"),
    ("2", "ch2_os_structures.md", "Ch2 OS Structures", "作業系統結構", "#0c8599"),
    ("3", "ch3_processes.md", "Ch3 Processes", "進程・fork・IPC・interrupt", "#2b8a3e"),
    ("4", "ch4_threads.md", "Ch4 Threads", "線程與並行", "#5c940d"),
    ("5", "ch5_cpu_scheduling.md", "Ch5 CPU Scheduling", "CPU 排程", "#7048e8"),
    ("6", "ch6_synchronization.md", "Ch6 Synchronization", "同步工具", "#ae3ec9"),
    ("L", "lab_notes.md", "Labs & PA1/PA2", "Lab 1–6・PA 考點・lab 例題", "#8f5b2e"),
    ("Q", "qb2_long_bank.md", "Past Papers Solved", "歷屆長題全解", "#c2255c"),
    ("M", None, "MC Answer Key", "MC 題庫 + 答案", "#495057"),
    ("A", "api_reference.md", "C / Pthreads API", "Lab / PA API 速查", "#087f5b"),
    ("G", "glossary.md", "Glossary A-Z", "術語表", "#e67700"),
    ("I", None, "Index", "索引", "#343a40"),
]
PART_BY_CODE = dict((p[0], p) for p in PARTS)
MD_PLUGINS = ["table", "strikethrough", "math", "mistune.plugins.math.math_in_quote",
              "mistune.plugins.math.math_in_list"]


def read(name):
    with io.open(os.path.join(NOTES, name), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- LaTeX math (KaTeX, pre-rendered at build time)
KATEX_JS = os.path.join(ROOT, "_work", "midterm", "scripts", "katex_render.js")
KATEX_CACHE = os.path.join(ROOT, "_work", "midterm", "katex_cache.json")
KATEX_CSS_ABS = "file:///C:/Code/UST/COMP3511/Midterm_Site/assets/katex/katex.min.css"   # copied by build_site.py
KATEX_CSS_REL = "Midterm_Site/assets/katex/katex.min.css"
_KCACHE = {}


def _kc():
    if not _KCACHE:
        try:
            _KCACHE.update(json.load(io.open(KATEX_CACHE, encoding="utf-8")))
        except (OSError, ValueError):
            pass
    return _KCACHE


def katex_prerender(items):
    cache = _kc()
    todo = [(t, d) for t, d in dict.fromkeys(items) if ("D|" if d else "I|") + t not in cache]
    if not todo:
        return
    tin, tout = KATEX_CACHE + ".in.json", KATEX_CACHE + ".out.json"
    io.open(tin, "w", encoding="utf-8").write(json.dumps([{"tex": t, "display": d} for t, d in todo]))
    r = subprocess.run(["node", KATEX_JS, tin, tout], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode not in (0, 2):
        raise RuntimeError("katex failed: " + r.stderr)
    if r.stderr.strip():
        print(r.stderr.strip())
    for (t, d), h in zip(todo, json.loads(io.open(tout, encoding="utf-8").read())):
        cache[("D|" if d else "I|") + t] = h
    io.open(KATEX_CACHE, "w", encoding="utf-8").write(json.dumps(cache, ensure_ascii=False))


def katex_html(tex, display):
    key = ("D|" if display else "I|") + tex
    if key not in _kc():
        katex_prerender([(tex, display)])
    return _kc()[key]


def print_tex(tex):
    """Inline fractions / binomials at full size on paper (\\frac -> \\dfrac); the website keeps standard sizes."""
    return re.sub(r"\\(frac|binom)(?![a-zA-Z])", r"\\d\1", tex)


def collect_math(md_texts):
    found = []
    r = mistune.HTMLRenderer(escape=False)
    m = mistune.create_markdown(renderer=r, plugins=MD_PLUGINS)
    r.register("block_math", lambda _r, t: found.append((t.strip(), True)) or "")
    r.register("inline_math", lambda _r, t: found.append((print_tex(t.strip()), False)) or "")
    for s in md_texts:
        m(preprocess(s))
    return found


def ensure_katex_assets():
    """KaTeX CSS + fonts live in Midterm_Site/assets/katex/ (shared with the website)."""
    pkg = os.path.join(ROOT, "_work", "midterm", "katex_pkg", "node_modules", "katex")
    dst = os.path.join(ROOT, "Midterm_Site", "assets", "katex")
    os.makedirs(os.path.join(dst, "fonts"), exist_ok=True)
    shutil.copyfile(os.path.join(pkg, "dist", "katex.min.css"), os.path.join(dst, "katex.min.css"))
    shutil.copyfile(os.path.join(pkg, "LICENSE"), os.path.join(dst, "LICENSE"))
    for f in glob.glob(os.path.join(pkg, "dist", "fonts", "*.woff2")):
        shutil.copyfile(f, os.path.join(dst, "fonts", os.path.basename(f)))


# ---------------------------------------------------------------- markdown rendering
PIPE_PH = "\uE000"


def _fix_row(line, ncols=None):
    """Protect pipes inside code spans (and escaped pipes) in a table row; normalise the cell count."""
    s = line.strip()
    out, in_code, i = [], False, 0
    while i < len(s):
        ch = s[i]
        if ch == "`":
            in_code = not in_code
            out.append(ch)
        elif ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            out.append(PIPE_PH)
            i += 1
        elif in_code and ch == "|":
            out.append(PIPE_PH)
        else:
            out.append(ch)
        i += 1
    cells = "".join(out).strip().strip("|").split("|")
    if ncols:
        if len(cells) < ncols:
            cells += [" "] * (ncols - len(cells))
        elif len(cells) > ncols:
            cells = cells[:ncols - 1] + [PIPE_PH.join(cells[ncols - 1:])]
    return "| " + " | ".join(c.strip() or " " for c in cells) + " |", len(cells)


def preprocess(md):
    lines = md.split("\n")
    out, in_code, i = [], False, 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append(line)
            i += 1
            continue
        if (not in_code and line.lstrip().startswith("|") and i + 1 < len(lines)
                and re.match(r"^\s*\|[\s:\-|]+\|\s*$", lines[i + 1])):
            if out and out[-1].strip():
                out.append("")
            head, ncols = _fix_row(line)
            out.append(head)
            out.append("|" + "---|" * ncols)
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                out.append(_fix_row(lines[i], ncols)[0])
                i += 1
            out.append("")
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def callout_class(text):
    t = strip_tags(text).lstrip()
    for mark, cls in (("⚠", "warn"), ("📝", "answer"), ("🧮", "formula"), ("🎯", "tip")):
        if t.startswith(mark):
            return cls
    return "info"


class Renderer(mistune.HTMLRenderer):
    def __init__(self):
        super().__init__(escape=False)
        self.prefix, self.heads, self.used = "x", [], set()

    def start(self, prefix):
        self.prefix, self.heads, self.used = prefix, [], set()

    def heading(self, text, level, **attrs):
        t = strip_tags(text).strip()
        m = re.match(r"^(\d+(?:\.\d+)*)\.?\s", t + " ")
        base = self.prefix + "-" + (("s" + m.group(1).replace(".", "-")) if m else
                                    ("-".join(re.findall(r"[A-Za-z0-9]+", t)[:5]).lower() or "h"))
        hid, k = base, 2
        while hid in self.used:
            hid = "%s-%d" % (base, k)
            k += 1
        self.used.add(hid)
        self.heads.append((level, hid, t))
        return '<h%d id="%s">%s</h%d>\n' % (level, hid, text, level)

    def block_quote(self, text):
        return '<blockquote class="co %s">%s</blockquote>\n' % (callout_class(text), text)

    def block_code(self, code, info=None):
        lang = (info or "").strip().split(" ")[0]
        return '<pre class="code %s"><code>%s</code></pre>\n' % (html.escape(lang), html.escape(code.rstrip("\n")))


R = Renderer()
MD = mistune.create_markdown(renderer=R, plugins=MD_PLUGINS)
# the math plugin installs its own renderers; replace them with pre-rendered KaTeX HTML
R.register("block_math", lambda r, t: '<div class="math-display">%s</div>\n' % katex_html(t.strip(), True))
R.register("inline_math", lambda r, t: katex_html(print_tex(t.strip()), False))
SREF = re.compile(r"\[(\d\.\d{1,2}(?:\s*[–\-]\s*\d?\.?\d{1,2})?(?:\s*,\s*\d\.\d{1,2}(?:\s*[–\-]\s*\d?\.?\d{1,2})?)*)\]")


FIG = re.compile(r'<p><img src="img/([^"]+)" alt="([^"]*)"\s*/?></p>')
IMG_ABS = "file:///C:/Code/UST/COMP3511/Midterm_Site/assets/img/"   # pass HTML lives in _work, so use absolute paths


def figures(h, base):
    return FIG.sub(lambda m: '<figure class="fig"><img src="%s%s" alt="%s"><figcaption>%s</figcaption></figure>'
                   % (base, m.group(1), re.sub(r"\s*\[[^\]]*\]", "", m.group(2)), m.group(2)), h)


def post(h):
    h = figures(h, IMG_ABS)
    parts = re.split(r"(<pre[\s\S]*?</pre>)", h)
    for k in range(0, len(parts), 2):
        p = parts[k]
        p = SREF.sub(lambda m: '<span class="sref">[%s]</span>' % m.group(1), p)
        p = p.replace("✅", '<span class="ok">✔</span>').replace("❌", '<span class="no">✘</span>')
        parts[k] = p
    return "".join(parts).replace(PIPE_PH, "|")


def render(md, prefix):
    R.start(prefix)
    h = post(MD(preprocess(md)))
    return h, list(R.heads)


def render_inline(md, prefix="z"):
    R.start(prefix)
    h = post(MD(preprocess(md))).strip()
    if h.startswith("<p>") and h.endswith("</p>") and h.count("<p>") == 1:
        h = h[3:-4]
    return h


# ---------------------------------------------------------------- generated tables
def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def amdahl_table():
    Ns = [2, 3, 4, 5, 6, 7, 8, 10, 16, 32]
    Ss = [0.05, 0.10, 0.15, 0.19, 0.20, 0.25, 0.30, 0.35, 0.39, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80]
    rows = []
    for S in Ss:
        row = ["**%.2f** (par %.0f%%)" % (S, (1 - S) * 100)]
        row += ["%.2f" % (1 / (S + (1 - S) / N)) for N in Ns]
        rows.append(row + ["**%.2f**" % (1 / S)])
    return md_table([r"$S \backslash N$"] + [str(n) for n in Ns] + [r"$\infty$"], rows)


def pow_table():
    rows = [[n, 2 ** n, 3 ** n, 4 ** n, 6 ** n, 2 ** (n + 1) - 1, 2 ** n - 1, 2 ** (n + 1) - 2, 2 * (3 ** n + 1),
             (4 ** n - 1) // 3] for n in range(1, 11)]
    return md_table([r"$n$", r"$2^n$", r"$3^n$", r"$4^n$", r"$6^n$", r"$2^{n+1}-1$", r"$2^n-1$", r"$2^{n+1}-2$",
                     r"$2(3^n+1)$", r"$(4^n-1)/3$"], rows)


def rm_table():
    rows = [[n, "%.3f" % (n * (2 ** (1.0 / n) - 1))] for n in range(1, 11)] + [[r"$\infty$", r"0.693 ($\ln 2$)"]]
    half = (len(rows) + 1) // 2
    merged = [rows[i] + (rows[i + half] if i + half < len(rows) else ["", ""]) for i in range(half)]
    return md_table([r"$N$", "bound", r"$N$", "bound"], merged)


def fork_table():
    rows = [
        ["`fork();`", "×2", r"$2^n$", "n=3 → 8；n=10 → 1024"],
        ["`fork(); fork();`", "×4", r"$4^n$", "n=3 → 64"],
        ["`if (fork()) fork();`", "×3", r"$3^n$", "n=3 → 27"],
        ["`if (fork() == 0) fork();`", "×3", r"$3^n$", "n=3 → 27（Sp21 MC8）"],
        ["`fork() && fork();`", "×3", r"$3^n$", "parent 做兩次"],
        ["`fork() || fork();`", "×3", r"$3^n$", "child 做第二次"],
        ["`if (fork() == fork()) printf`", "×4", r"$4^n$；lines $(4^n-1)/3$", "F22 Q3"],
        ["`if (fork()) {fork(); fork();} else fork();`", "×6", r"$6^n$", "Lab 3 Ex3"],
        ["`if (fork()) fork(); else break;`", "active ×2", r"$2^{n+1}-1$ total", r"breaks $2^n-1$（S26 Q3.1）"],
        ["`if (fork()) printf; else printf;`", r"lines $2^i$ per iter", r"$2^{n+1}-2$ lines", "F19 Q2.6"],
        ["`pid = fork(); if (!pid) for (j<N) fork();`（M 輪）", r"×$(2^N+1)$", r"$(2^N+1)^M$", "F24 P3.1"],
        ["`if (fork() == 0) break;`（fan）", "+1 child", r"$n+1$", "只 parent 繼續"],
        ["`if (fork() > 0) break;`（chain）", "+1 child", r"$n+1$", "只 child 繼續"],
    ]
    return md_table(["每 iteration", "每 process 變", "n 次後", "例"], rows)


def inject(md):
    return (md.replace("{{AMDAHL_TABLE}}", amdahl_table()).replace("{{POW_TABLE}}", pow_table())
              .replace("{{RM_TABLE}}", rm_table()).replace("{{FORK_TABLE}}", fork_table()))


def source(name):
    """Markdown source of a part (playbooks get their generated tables)."""
    md = read(name)
    return inject(md) if name == "cb_playbooks.md" else md


# ---------------------------------------------------------------- banks
HEAD = re.compile(r"^## \[([^\]]+)\] (ch\d) \| (.+)$", re.M)


def parse_bank(md):
    items, heads = [], list(HEAD.finditer(md))
    for k, m in enumerate(heads):
        end = heads[k + 1].start() if k + 1 < len(heads) else len(md)
        body = re.sub(r"\n---\s*$", "", md[m.end():end].strip()).strip()
        items.append({"id": m.group(1), "ch": m.group(2), "topic": m.group(3).strip(), "body": body})
    return items


def mc_key_html():
    groups = []
    for fname, label in (("qb1_mc_bank.md", "歷屆 MC（S26 / F20 / Sp21 / HW1 / HW2 / Lab 4）"),
                         ("qb3_practice_mc.md", "新練習 MC（針對 Fall 2026 slides）")):
        items = parse_bank(read(fname))
        out = ['<h2 id="M-%s">%s</h2>' % ("past" if fname.startswith("qb1") else "new", label), '<div class="mc-cols">']
        for it in items:
            body = it["body"]
            am = re.search(r"^\*\*Answer: ([A-D])\*\*(.*)$", body, re.M)
            before, after = body[:am.start()], body[am.end():].strip()
            opts = re.findall(r"^- ([A-D])\. (.+)$", before, re.M)
            stem = re.split(r"^- A\. ", before, flags=re.M)[0].strip()
            ans = am.group(1)
            o_html = []
            for L, o in opts:
                cls = ' class="right"' if L == ans or (am.group(2) and L in am.group(2)) else ""
                o_html.append("<span%s><b>%s.</b> %s</span>" % (cls, L, render_inline(o)))
            exp = after.replace("解：", "").strip()
            out.append('<div class="mc"><div class="mch"><b class="mcid">%s</b> <span class="mct">%s</span> '
                       '<span class="mcans">→ %s%s</span></div>%s<div class="mco">%s</div>%s</div>'
                       % (it["id"], html.escape(it["topic"]), ans, html.escape(am.group(2).strip()),
                          render(stem, "mcs")[0], " ".join(o_html),
                          ('<div class="mce">%s</div>' % render_inline(exp)) if exp else ""))
        out.append("</div>")
        groups.append("\n".join(out))
    return "\n".join(groups), [(2, "M-past", "歷屆 MC"), (2, "M-new", "新練習 MC")]


def bank_html():
    items = parse_bank(read("qb2_long_bank.md"))
    out, heads, paper = [], [], None
    names = {"S26": "Spring 2026 Midterm（lecturer 提供）", "F19": "Fall 2019 Midterm", "F20": "Fall 2020 Midterm",
             "Sp21": "Spring 2021 Midterm", "HW1": "Homework 1（Fall 2026）", "HW2": "Homework 2（Fall 2026）",
             "F22": "Fall 2022 Midterm（lab slides 引用）", "F24": "Fall 2024 Midterm（lab slides 引用）",
             "S25": "Spring 2025 Midterm（lab slides 引用）", "S23": "Spring 2023 Midterm（lab slides 引用）",
             "Lab2": "Lab 2 Exercises", "Lab4": "Lab 4 Exam Example", "Lab6": "Lab 6 Sample Questions（官方答案）"}
    for it in items:
        p = it["id"].split("-")[0]
        if p != paper:
            paper = p
            hid = "Q-" + p
            out.append('<h2 id="%s">%s</h2>' % (hid, names.get(p, p)))
            heads.append((2, hid, names.get(p, p)))
        parts = re.split(r"^\*\*Answer:\*\*\s*$", it["body"], flags=re.M)
        q = render(parts[0].strip(), "qq")[0]
        a = render(parts[1].strip(), "qa")[0] if len(parts) > 1 else ""
        out.append('<div class="lq" id="Q-%s"><div class="lqh"><b>%s</b> %s <span class="lqch">%s</span></div>%s'
                   '<div class="lqa"><b>Answer.</b> %s</div></div>'
                   % (it["id"], it["id"], html.escape(it["topic"]), it["ch"].upper(), q, a))
    return "\n".join(out), heads


# ---------------------------------------------------------------- answer bank (part X)
XA_FILES = ["xa_ch1_ch2.md", "xa_ch3.md", "xa_ch4.md", "xa_ch5.md", "xa_ch6.md", "xa_cross.md", "xa_code.md"]
XA_NAMES = {"X1": "Ch1 Introduction", "X2": "Ch2 OS Structures", "X3": "Ch3 Processes · IPC · Interrupts",
            "X4": "Ch4 Threads", "X5": "Ch5 CPU Scheduling", "X6": "Ch6 Synchronization",
            "XI": "Cross-chapter traces（綜合「發生咩事」題）",
            "XC": "Copy-ready C programs（Lab / PA coding，已編譯測試）"}


def xa_sources():
    return [read(f) for f in XA_FILES if os.path.exists(os.path.join(NOTES, f))]


def xa_html(pages=None):
    out, heads, buf, sec = [], [], [], None
    items = [it for src in xa_sources() for it in parse_bank(src)]
    if os.path.exists(os.path.join(NOTES, "xa_intro.md")):
        out.append(render(read("xa_intro.md"), "Xi")[0])
    # question finder: every entry with its page number (filled in on pass 2)
    finder, cur = [], None
    for it in items:
        p = it["id"].split("-")[0]
        if p != cur:
            cur = p
            finder.append('<div class="xf-h">%s · %s</div>' % (p, html.escape(XA_NAMES.get(p, p))))
        finder.append('<div class="toc-line"><a class="t" href="#%s"><b>%s</b> %s</a>%s</div>'
                      % (it["id"], it["id"].split("-", 1)[1], render_inline(it["topic"], "xh"), pg(it["id"], pages)))
    out.append('<h2 id="X-finder">題目搜尋表 Question finder（按章節 → 題目關鍵字 → 頁數）</h2>'
               '<div class="xf-cols">%s</div>' % "".join(finder))
    heads.append((2, "X-finder", "題目搜尋表 Question finder"))

    def flush():
        if buf:
            out.append('<div class="xa-cols">%s</div>' % "".join(buf))
            del buf[:]
    for it in items:
        p = it["id"].split("-")[0]
        if p != sec:
            flush()
            sec = p
            hid, title = "X-" + p.lower(), "%s · %s" % (p, XA_NAMES.get(p, p))
            out.append('<h2 id="%s">%s</h2>' % (hid, html.escape(title)))
            heads.append((2, hid, title))
        head = ('<div class="xah"><b class="xid">%s</b> <span class="xt">%s</span></div>'
                % (it["id"], render_inline(it["topic"], "xh")))
        parts = re.split(r"^\*\*Answer:\*\*\s*$", it["body"], flags=re.M)
        if len(parts) == 1:                      # True/False table or note: full width
            flush()
            out.append('<div class="xtf" id="%s">%s%s</div>' % (it["id"], head, render(it["body"], "xt")[0]))
            continue
        q, a = render(parts[0].strip(), "xq")[0], render(parts[1].strip(), "xa")[0]
        code_lines = max([c.count("\n") for c in re.findall(r"<pre[\s\S]*?</pre>", a)] or [0])
        wide = code_lines > 14 or a.count("<th>") > 3
        entry = ('<div class="xa%s" id="%s">%s<div class="xq">%s</div><div class="xans">%s</div></div>'
                 % (" wide" if wide else "", it["id"], head, q, a))
        if wide:
            flush()
            out.append(entry)
        else:
            buf.append(entry)
    flush()
    return "\n".join(out), heads


# ---------------------------------------------------------------- index terms
INDEX_EXTRA = [
    "fork()", "exec()", "execlp", "execvp", "wait()", "waitpid", "exit()", "pipe()", "dup2", "dup(", "mkfifo", "open(", "read()",
    "write()", "close(", "signal()", "kill(", "chdir", "pthread_create", "pthread_join", "pthread_cancel", "pthread_mutex",
    "sem_wait", "sem_post", "sem_init", "pthread_cond_wait", "test_and_set", "compare_and_swap", "compare_and_reset", "swap(",
    "printf", "clone()", "task_struct", "getpid", "SIGINT", "Ctrl-C", "LUF", "Least Used First", "dynamic priority",
    "MLFQ", "multilevel feedback queue", "RR", "round robin", "FCFS", "SJF", "SRTF", "EDF", "rate-monotonic", "RM",
    "Gantt", "response time", "waiting time", "turnaround", "throughput", "CPU utilization", "convoy effect", "aging",
    "starvation", "Little's formula", "exponential averaging", "Amdahl", "speedup", "deadline", "utilization",
    "time quantum", "dispatcher", "dispatch latency", "preemptive", "non-preemptive", "PCS", "SCS", "LWP",
    "processor affinity", "soft affinity", "hard affinity", "load balancing", "push migration", "pull migration",
    "memory stall", "hyperthreading", "CMT", "logical processor", "SMP", "AMP", "NUMA", "multicore", "multiprocessor",
    "zombie", "orphan", "cascading termination", "PCB", "TCB", "context switch", "process state", "ready queue",
    "wait queue", "long-term scheduler", "short-term scheduler", "medium-term scheduler", "swapping",
    "degree of multiprogramming", "I/O-bound", "CPU-bound", "copy-on-write", "interrupt", "interrupt vector",
    "maskable", "trap", "exception", "DMA", "programmed I/O", "dual mode", "mode bit", "privileged instruction",
    "protection ring", "system call", "API", "parameter passing", "linker", "loader", "DLL", "microkernel",
    "monolithic", "layered", "loadable kernel module", "LKM", "hybrid", "Darwin", "Mach", "Android", "ART", "JNI",
    "policy", "mechanism", "MS-DOS", "UNIX", "Linux", "Windows", "shell", "GUI", "CLI", "system program",
    "cache", "locality", "temporal locality", "spatial locality", "hit ratio", "average access time", "von Neumann",
    "storage hierarchy", "main memory", "byte addressable", "volatile", "NVM", "HDD", "EEPROM", "bootstrap",
    "virtualization", "VMM", "hypervisor", "guest", "cloud", "SaaS", "PaaS", "IaaS", "multiprogramming",
    "timesharing", "multitasking", "kernel", "middleware", "resource allocator", "control program",
    "thread", "user thread", "kernel thread", "many-to-one", "one-to-one", "many-to-many", "two-level",
    "thread library", "Pthreads", "concurrency", "parallelism", "data parallelism", "task parallelism",
    "responsiveness", "economy", "scalability", "resource sharing", "signal handler", "synchronous signal",
    "asynchronous signal", "thread cancellation", "deferred cancellation", "asynchronous cancellation",
    "thread-local storage", "heavyweight", "lightweight", "IPC", "shared memory", "message passing",
    "direct communication", "indirect communication", "mailbox", "rendezvous", "blocking", "non-blocking",
    "zero capacity", "bounded capacity", "unbounded capacity", "bounded buffer", "producer", "consumer",
    "ordinary pipe", "named pipe", "FIFO", "half-duplex", "full-duplex", "socket", "port", "RPC",
    "race condition", "critical section", "mutual exclusion", "progress", "bounded waiting", "entry section",
    "exit section", "atomic", "spinlock", "busy waiting", "mutex", "semaphore", "binary semaphore",
    "counting semaphore", "deadlock", "Peterson", "readers-writers", "condition variable", "atomic variable",
    "next_available_pid", "counter++", "possible values", "process tree", "short-circuit",
    # labs / PA
    "PA1", "PA2", "popen", "pclose", "spooling", "buffering", "cycle stealing", "device driver", "nonmaskable",
    "Makefile", "gcc", "execl", "execv", "execle", "execvpe", "getppid", "O_CREAT", "O_RDONLY", "O_WRONLY",
    "STDOUT_FILENO", "fflush", "fopen", "wc -l", "ps aux", "pthread_exit", "pthread_attr", "pthread_mutex_lock",
    "pthread_mutex_init", "sem_destroy", "read_count", "rw_mutex", "SIGCHLD", "usleep",
]


# ---------------------------------------------------------------- HTML assembly
CSS = r"""
@page { size: A4; margin: 11mm 15mm 13mm 15mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: "Segoe UI", "Noto Sans HK", "Microsoft JhengHei", sans-serif; font-size: 8.9pt;
       line-height: 1.36; color: #111; }
code, pre { font-family: Consolas, "Cascadia Mono", "Noto Sans HK", monospace; }
a { color: inherit; text-decoration: none; }
p { margin: 2.5pt 0; }
ul, ol { margin: 2pt 0; padding-left: 15pt; }
li { margin: 0.8pt 0; }
hr { border: none; border-top: 0.6pt dashed #bbb; margin: 6pt 0; }
h1 { font-size: 15pt; margin: 0 0 6pt; padding: 5pt 8pt; color: #fff; border-radius: 4pt; break-after: avoid; }
h1 .sub { font-size: 10pt; font-weight: 600; opacity: .95; margin-left: 6pt; }
h1 .code { display: inline-block; background: rgba(255,255,255,.25); border-radius: 3pt; padding: 0 5pt; margin-right: 6pt; }
h2 { font-size: 11.6pt; margin: 9pt 0 3pt; padding: 1.5pt 0 1.5pt 5pt; border-left: 4pt solid var(--pc); background: #f3f4f6;
     break-after: avoid; }
h3 { font-size: 10.2pt; margin: 6pt 0 2pt; color: var(--pc); break-after: avoid; }
h4 { font-size: 9.4pt; margin: 4pt 0 2pt; break-after: avoid; }
strong, b { font-weight: 700; }
code { font-size: 8.1pt; background: #f1f3f5; padding: 0 2pt; border-radius: 2pt; }
pre.code { background: #f6f7f9; border: 0.6pt solid #d0d4da; border-radius: 3pt; padding: 3pt 5pt; margin: 3pt 0;
           font-size: 7.9pt; line-height: 1.28; white-space: pre-wrap; word-break: break-word; break-inside: avoid; }
pre.code code { background: none; padding: 0; font-size: inherit; }
table { border-collapse: collapse; width: 100%; margin: 3pt 0; font-size: 8.1pt; break-inside: auto; }
th, td { border: 0.5pt solid #c4c9d1; padding: 1.4pt 3.5pt; vertical-align: top; text-align: left; }
th { background: #eceff3; font-weight: 700; }
tr { break-inside: avoid; }
blockquote.co { margin: 3pt 0; padding: 2.5pt 6pt; border-left: 3pt solid #4c6ef5; background: #eef2ff; border-radius: 2pt;
                break-inside: avoid; }
blockquote.co p { margin: 1pt 0; }
blockquote.warn { border-color: #f08c00; background: #fff4e6; }
blockquote.answer { border-color: #2b8a3e; background: #ebfbee; }
blockquote.formula { border-color: #7048e8; background: #f3f0ff; font-size: 10pt; }
blockquote.tip { border-color: #e8590c; background: #fff4e6; }
.sref { font-size: 7pt; color: #c92a2a; font-weight: 700; white-space: nowrap; }
figure.fig { width: 58%; margin: 3pt auto 4pt; break-inside: avoid; text-align: center; }
figure.fig img { width: 100%; border: 0.5pt solid #ced4da; border-radius: 2pt; }
figure.fig figcaption { font-size: 7.4pt; color: #495057; margin-top: 1pt; }
.ok { color: #2b8a3e; font-weight: 700; }
.no { color: #c92a2a; font-weight: 700; }
/* LaTeX (KaTeX, pre-rendered) */
.katex { font-size: 1.1em; }
.math-display { margin: 2.5pt 0; overflow: hidden; break-inside: avoid; }
.math-display .katex-display { margin: 0.25em 0; }
blockquote.co .math-display { margin: 1pt 0; }
td .katex, th .katex, .mc .katex { font-size: 1.04em; }
section.part { break-before: page; --pc: #333; }
/* cover */
.cover { break-after: page; }
.cover .title { background: linear-gradient(135deg, #1c3d8f, #7048e8); color: #fff; border-radius: 8pt; padding: 18pt 18pt 14pt; }
.cover .title h1 { background: none !important; font-size: 26pt; padding: 0; margin: 0 0 4pt; }
.cover .title .meta { font-size: 10.5pt; line-height: 1.5; }
.cover .legend { display: grid; grid-template-columns: 1fr 1fr; gap: 3pt 10pt; margin-top: 10pt; }
.cover .legend div { display: flex; align-items: center; gap: 6pt; font-size: 9.6pt; }
.cover .legend .lt { flex: 1; }
.cover .legend .sw { width: 16pt; height: 13pt; border-radius: 2pt; color: #fff; font-weight: 800; display: inline-flex;
                     align-items: center; justify-content: center; font-size: 8.5pt; }
.box { border: 0.8pt solid #ced4da; border-radius: 5pt; padding: 6pt 8pt; margin-top: 8pt; }
.box h3 { margin-top: 0; color: #1c3d8f; }
/* toc */
.toc-cols { columns: 2; column-gap: 8mm; }
.toc-part { break-inside: avoid; margin-bottom: 5pt; }
.toc-part .tp { font-weight: 800; font-size: 9.6pt; padding: 1pt 4pt; color: #fff; border-radius: 2pt; display: flex; }
.toc-line { display: flex; gap: 4pt; font-size: 8.3pt; line-height: 1.3; }
.toc-line .t { flex: 1; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.toc-line .dots { flex: 0 0 auto; }
.pg { display: inline-block; min-width: 18pt; text-align: right; font-weight: 700; font-variant-numeric: tabular-nums; }
.toc-part .tp .pg { color: #fff; margin-left: auto; }
.router { columns: 2; column-gap: 7mm; font-size: 8.2pt; }
.router .rr { display: flex; gap: 4pt; border-bottom: 0.5pt dotted #b8bec7; padding: 1pt 0; break-inside: avoid; }
.router .rr a { flex: 1; }
/* MC key */
.mc-cols { columns: 2; column-gap: 6mm; column-rule: 0.5pt solid #dee2e6; }
.mc { break-inside: avoid; border-bottom: 0.5pt dotted #adb5bd; padding: 2pt 0 3pt; font-size: 7.9pt; line-height: 1.27; }
.mc p { margin: 0.5pt 0; }
.mc pre.code { font-size: 7pt; }
.mch .mcid { color: #c2255c; }
.mch .mct { color: #495057; font-weight: 600; }
.mch .mcans { float: right; font-weight: 800; color: #fff; background: #2b8a3e; padding: 0 4pt; border-radius: 2pt; }
.mco span { display: inline; margin-right: 5pt; color: #555; }
.mco span.right { color: #111; font-weight: 700; text-decoration: underline; text-decoration-color: #2b8a3e; text-decoration-thickness: 1.2pt; }
.mce { color: #364fc7; font-size: 7.6pt; }
/* long questions */
.lq { break-inside: avoid; border: 0.5pt solid #dee2e6; border-radius: 3pt; padding: 3pt 6pt; margin: 4pt 0; }
.lqh { font-size: 9.2pt; } .lqh b { color: #c2255c; } .lqch { color: #868e96; font-size: 7.5pt; float: right; }
.lqa { background: #ebfbee; border-left: 2.5pt solid #2b8a3e; padding: 2pt 5pt; margin-top: 2pt; }
.lqa p { margin: 1pt 0; }
/* answer bank (part X) */
.xa-cols { columns: 2; column-gap: 6mm; column-rule: 0.5pt solid #dee2e6; }
.xa { break-inside: avoid; border-bottom: 0.5pt dotted #adb5bd; padding: 2pt 0 3pt; font-size: 8.2pt; line-height: 1.3; }
.xa.wide { border: 0.6pt solid #ced4da; border-radius: 3pt; padding: 3pt 6pt; margin: 5pt 0; break-inside: auto; }
.xa.wide .xah, .xa.wide .xq { break-after: avoid; }
.xa.wide pre.code { break-inside: auto; font-size: 7.3pt; line-height: 1.22; }
.xah { font-size: 7.4pt; color: #868e96; }
.xah .xid { color: #fff; background: #111; padding: 0 3pt; border-radius: 2pt; font-weight: 700; }
.xq { font-weight: 700; color: #1c3d8f; }
.xq p, .xans p { margin: 0.8pt 0; }
.xans ul, .xans ol { margin: 0.5pt 0; padding-left: 12pt; }
.xans table { font-size: 7.6pt; margin: 1.5pt 0; }
.xa pre.code { font-size: 7.4pt; margin: 2pt 0; }
/* how-to guides (part H) */
.pb { break-before: page; }
.pgi { font-weight: 800; }
.part-H a { text-decoration: underline; text-decoration-color: #b08900; }
.part-H h2 { background: #fff8db; }
.xf-cols { columns: 2; column-gap: 7mm; font-size: 7.6pt; }
.xf-cols .toc-line { font-size: 7.6pt; line-height: 1.25; }
.xf-h { break-after: avoid; font-weight: 800; color: #fff; background: #111; padding: 0.5pt 4pt; margin: 3pt 0 1pt;
        border-radius: 2pt; font-size: 8pt; }
.xtf { margin: 5pt 0; }
.xtf table { font-size: 7.7pt; }
.xtf td:nth-child(2) { font-weight: 800; text-align: center; white-space: nowrap; }
/* glossary + index */
.part-G table { font-size: 7.8pt; }
.idx-cols { columns: 3; column-gap: 6mm; font-size: 8pt; line-height: 1.32; }
.idx-cols .L { font-weight: 800; font-size: 10pt; color: #343a40; margin-top: 4pt; border-bottom: 0.6pt solid #343a40; break-after: avoid; }
.idx-cols .e { break-inside: avoid; }
.idx-cols .e b.main { color: #c92a2a; }
"""


def heads_toc_lines(heads, levels=(2,)):
    return [(lv, hid, t) for lv, hid, t in heads if lv in levels]


def pg(hid, pages):
    return '<span class="pg" data-id="%s">%s</span>' % (hid, (pages.get(hid, "000") if pages else "000"))


HOWTO_FILES = ["howto_fork.md", "howto_sched.md", "howto_sync.md"]


def howto_refs(md, pages):
    """Guide placeholders -> clickable page references, numbered on pass 2 like the TOC."""
    md = md.replace("（{{pages}} 頁版）", "")

    def rep(m):
        anchor = ("Q-" if m.group(1) == "q" else "") + m.group(2).strip()
        return '<a href="#%s">p.<span class="pgi" data-id="%s">%s</span></a>' % (
            anchor, anchor, (pages.get(anchor, "000") if pages else "000"))
    return re.sub(r"\{\{([pq]):([^}]+)\}\}", rep, md)


def howto_html(pages=None):
    """Part H: the three how-to guides (same sources as the website's how-to pages), one per page."""
    chunks = []
    for k, name in enumerate(HOWTO_FILES):
        md = howto_refs(read(name), pages)
        md = re.sub(r"^(#{1,5}) ", lambda m: "#" + m.group(1) + " ", md, flags=re.M)   # H1 -> H2, H2 -> H3
        chunks.append(('<div class="pb"></div>\n\n' if k else "") + md)
    return render("\n\n".join(chunks), "H")


def build_html(pages=None, index_html=None):
    sections, toc_data, all_links = [], [], []
    for code, src, title, sub, color in PARTS:
        pid = "part-" + code
        if code == "H":
            body, heads = howto_html(pages)
        elif code == "X":
            body, heads = xa_html(pages)
        elif code == "M":
            body, heads = mc_key_html()
        elif code == "Q":
            body, heads = bank_html()
        elif code == "I":
            body, heads = (index_html or '<div class="idx-cols">%s</div>' % "".join(
                '<div class="e">%s 000, 000</div>' % html.escape(t) for t in INDEX_EXTRA)), []
        else:
            md = re.sub(r"^# .*\n", "", source(src), count=1)  # drop the file's own H1; we print our own part header
            body, heads = render(md, code)
            if code == "P":   # anchors for the P1 steps (the how-to guides link to them)
                body = re.sub(r"<p><strong>Step (\d) — ", r'<p id="P-p1-step\1"><strong>Step \1 — ', body)
        h1 = ('<h1 id="%s" style="background:%s"><span class="code">%s</span>%s<span class="sub">%s</span></h1>'
              % (pid, color, code, html.escape(title), html.escape(sub)))
        sections.append('<section class="part part-%s" style="--pc:%s">%s\n%s</section>' % (code, color, h1, body))
        lv = (2, 3) if code in ("E", "P", "5", "3", "L") else (2,)
        toc_data.append((code, title, sub, color, pid, heads_toc_lines(heads, lv)))

    # ---- cover
    legend = "".join('<div><span class="sw" style="background:%s">%s</span><span class="lt">%s · %s</span>%s</div>'
                     % (c[4], c[0], html.escape(c[2]), html.escape(c[3]), pg("part-" + c[0], pages)) for c in PARTS)
    router = [
        ("Stuck on fork / scheduling / sync? → how-to guide", "part-H"),
        ("Formula card / course conventions / top traps", "E-e1-formula-card"),
        ("ANY short question → predicted Q + copy answer", "X-finder"),
        ("Write C code: fork / pipe / dup2 / exec / pthreads / sem", "X-xc"),
        ("Interrupt / DMA / trap / dual mode / privileged", "3-s0"),
        ("Cache, locality, average access time", "1-s4"),
        ("von Neumann, storage hierarchy, main memory", "1-s2-1"),
        ("SMP / multicore / NUMA / multiprocessor", "1-s5"),
        ("Multiprogramming vs timesharing; virtualization; cloud", "1-s6"),
        ("API vs system call, printf→write, parameters", "2-s3"),
        ("Linker vs loader, DLL", "2-s5"),
        ("Monolithic / layered / microkernel / LKM / hybrid", "2-s7"),
        ("Process states, PCB, schedulers, context switch", "3-s2"),
        ("fork() counting / tree / outputs / exec cases", "P-p1-fork-playbook"),
        ("pipe / dup / open / read / write fill-in", "P-p2-pipe-dup-exec-playbook"),
        ("Zombie / orphan / termination", "3-s8"),
        ("IPC, message passing, pipes, sockets", "3-s10"),
        ("Threads: shared vs private, benefits, models", "4-s1"),
        ("Amdahl's Law (pre-computed table)", "P-p5-pre-computed-tables"),
        ("Signals, cancellation, fork/exec semantics", "4-s8"),
        ("Gantt chart procedure + tie rules", "P-p3-cpu-scheduling-playbook"),
        ("Metrics: TAT / WT / response (course def)", "5-s2"),
        ("MLFQ rules + example", "5-s8"),
        ("RM / EDF / real-time", "5-s11"),
        ("PCS / SCS, affinity, load balancing, CMT", "5-s9"),
        ("Past scheduling answers (all papers)", "5-s14"),
        ("Race condition possible values", "6-s6"),
        ("Semaphores, spinlock with TAS / CAS / swap", "6-s3"),
        ("Critical-section requirements", "6-s2"),
        ("Lab 3 system calls, exec family, dup / dup2", "L-l3-lab-3-linux-process"),
        ("PA1 simplified shell (what the exam may ask)", "L-l3-8-pa1-simplified-linux"),
        ("Named pipe / FIFO, popen, Pthreads (Lab 4)", "L-l4-lab-4-named-pipes"),
        ("Priority + RR with arrivals; PA2 MLFQ spec", "L-l5-lab-5-scheduling-review"),
        ("Peterson + Lab 6 sync sample questions", "L-l6-lab-6-synchronization-review"),
    ]
    router_rows = "".join('<div class="rr"><a href="#%s">%s</a>%s</div>' % (t, html.escape(q), pg(t, pages))
                          for q, t in router)
    cover = """
<section class="cover">
 <div class="title"><h1>COMP3511 Midterm Cheat Book</h1>
  <div class="meta">Fall 2026 · Midterm 29-Oct-2026 (Thu) 8:00–10:00 PM · L1 <b>LTD</b> · L2 <b>LSKG012</b> · L3 <b>LTB</b><br>
  Coverage: Chapters 1–6 (to Synchronization Tools) · open-book · calculator allowed · bring rough sheets<br>
  中文解釋 + English keywords / model answers · 所有 fork / scheduling / sync 答案已用程式驗證</div></div>
 <div class="box"><h3>點用（How to use）</h3>
  <ol><li><b>唔記得點用？翻 H（攻略）</b>：fork / scheduling / sync 每類題「認題型 → 翻邊頁 → 照做 → 照寫」。</li>
  <li><b>先睇 E（考場一頁通）</b>：公式卡、本科 conventions、陷阱表 — MC 前掃一次。</li>
  <li><b>計數題用 P（Playbooks）</b>：fork / pipe / scheduling / sync 步驟 + 預計表（Amdahl、powers、RM bound）。</li>
  <li><b>概念題 / short question / T-F</b> → 先翻 <b>X（Answer Bank）</b>：按章節排嘅預測題，英文答案直接抄；每章尾有 True/False 快速判斷。冇再去章節（1–6）📝 Model answer。</li>
  <li><b>PA / lab API / coding 題</b> → X 最後嘅 <b>完整 C programs（已編譯測試）</b> + L（Labs &amp; PA1/PA2）+ A（API 速查）。</li>
  <li><b>見到似曾相識嘅題目</b> → Q（歷屆全解）/ M（MC key）。<b>搵字</b> → 最後嘅 Index（紅色 = 主要頁）。</li>
  </ol></div>
 <div class="box"><h3>Tab legend</h3><div class="legend">%s</div></div>
 <div class="box"><h3>題型 Router（見到 → 翻去）</h3>
  <div class="router">%s</div></div>
</section>""" % (legend, router_rows)

    # ---- TOC
    toc_parts = []
    for code, title, sub, color, pid, lines in toc_data:
        rows = "".join('<div class="toc-line"><a class="t" href="#%s">%s</a>%s</div>'
                       % (hid, html.escape(("· " if lv == 3 else "") + t), pg(hid, pages)) for lv, hid, t in lines)
        toc_parts.append('<div class="toc-part"><a class="tp" href="#%s" style="background:%s">%s · %s %s</a>%s</div>'
                         % (pid, color, code, html.escape(title), pg(pid, pages), rows))
        all_links.append(pid)
        all_links.extend(h for _l, h, _t in lines)
    toc = ('<section class="part" style="--pc:#1c3d8f"><h1 id="toc" style="background:#1c3d8f"><span class="code">≡</span>'
           'Contents<span class="sub">目錄</span></h1><div class="toc-cols">%s</div></section>' % "".join(toc_parts))

    doc = """<!DOCTYPE html><html lang="zh-HK"><head><meta charset="utf-8"><title>COMP3511 Midterm Cheat Book</title>
<link rel="stylesheet" href="%s">
<style>%s</style></head><body>%s%s%s</body></html>""" % (KATEX_CSS_ABS, CSS, cover, toc, "\n".join(sections))
    return doc, [t for _q, t in router]


# ---------------------------------------------------------------- PDF helpers
def chrome_pdf(html_path, pdf_path):
    prof = os.path.join(WORK, "prof")
    os.makedirs(prof, exist_ok=True)
    url = "file:///" + html_path.replace("\\", "/")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
           "--user-data-dir=" + prof, "--no-pdf-header-footer", "--print-to-pdf=" + pdf_path, url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF not produced: " + r.stderr[-500:])


def named_pages(pdf_path):
    d = fitz.open(pdf_path)
    names = d.resolve_names()
    d.close()
    return dict((k, v["page"] + 1) for k, v in names.items())


def part_ranges(pages, n_pages):
    starts = sorted((pages["part-" + c[0]], c[0]) for c in PARTS if ("part-" + c[0]) in pages)
    ranges = {}
    for i, (s, code) in enumerate(starts):
        e = starts[i + 1][0] - 1 if i + 1 < len(starts) else n_pages
        ranges[code] = (s, e)
    return ranges


def compute_index(pdf_path, ranges):
    d = fitz.open(pdf_path)
    skip = set()
    for code in ("I", "G", "H"):
        if code in ranges:
            skip.update(range(ranges[code][0], ranges[code][1] + 1))
    first_content = min(r[0] for r in ranges.values())
    texts, heads = {}, {}
    for i in range(d.page_count):
        pno = i + 1
        if pno < first_content or pno in skip:
            continue
        page = d[i]
        texts[pno] = page.get_text()
        big = []
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                for sp in ln["spans"]:
                    if sp["size"] >= 10.0:
                        big.append(sp["text"])
        heads[pno] = " ".join(big)
    d.close()
    # glossary spellings win over the extra list; dedupe case-insensitively
    def key(t):
        return re.sub(r"\(\)?$", "", t.strip().lower())
    by_key = {}
    for row in re.findall(r"^\| ([^|]+?) \|", read("glossary.md"), re.M):
        t = row.strip()
        if t not in ("Term",) and not t.startswith("---"):
            by_key.setdefault(key(t), t)
    for t in INDEX_EXTRA:
        if key(t) in ("amdahl",):
            continue
        by_key.setdefault(key(t), t)
    terms = list(by_key.values())
    entries = []
    for term in sorted(terms, key=lambda s: s.lower().lstrip("_")):
        core = re.sub(r"\s*\(.*?\)\s*$", "", term) if not term.endswith("()") else term
        variants = [v.strip() for v in core.split("/") if v.strip()]
        pats = []
        for v in variants:
            esc = re.escape(v)
            pats.append(re.compile(r"(?<![A-Za-z0-9_])" + esc + (r"(?![A-Za-z0-9_])" if v[-1].isalnum() else ""), re.I))
        hits, mains = [], []
        for pno, txt in texts.items():
            if any(p.search(txt) for p in pats):
                hits.append(pno)
                if any(p.search(heads[pno]) for p in pats):
                    mains.append(pno)
        if not hits:
            continue
        chosen = sorted(set(mains[:4] + hits[: max(0, 7 - len(mains[:4]))]))
        if len(hits) > len(chosen):
            # keep the pages with most occurrences instead of just the first ones
            counts = sorted(hits, key=lambda p: -sum(len(pt.findall(texts[p])) for pt in pats))
            chosen = sorted(set(mains[:4]) | set(counts[: max(0, 7 - len(mains[:4]))]))
        entries.append((term, chosen, set(mains)))
    # render, grouped by first letter
    out, letter = ['<div class="idx-cols">'], None
    for term, chosen, mains in entries:
        L = term.lstrip("_(").upper()[:1]
        L = L if L.isalpha() else "#"
        if L != letter:
            letter = L
            out.append('<div class="L">%s</div>' % L)
        pg_html = ", ".join(('<b class="main">%d</b>' % p) if p in mains else str(p) for p in chosen)
        shown = term + ")" if term.endswith("(") else term
        out.append('<div class="e">%s · %s</div>' % (html.escape(shown), pg_html))
    out.append("</div>")
    return "\n".join(out), len(entries)


def decorate(pdf_in, pdf_out, pages):
    d = fitz.open(pdf_in)
    n = d.page_count
    ranges = part_ranges(pages, n)
    W, H = d[0].rect.width, d[0].rect.height
    mm = 72 / 25.4
    slot_top, slot_h = 16 * mm, (H - 32 * mm) / len(PARTS)
    order = [c[0] for c in PARTS]
    for i in range(n):
        pno = i + 1
        page = d[i]
        code = None
        for c, (s, e) in ranges.items():
            if s <= pno <= e:
                code = c
        odd = pno % 2 == 1
        # footer
        label = "COMP3511 Midterm Cheat Book"
        if code:
            label += "  ·  " + PART_BY_CODE[code][2]
        y = H - 6.5 * mm
        if odd:
            page.insert_text((15 * mm, y), label, fontsize=7, fontname="helv", color=(0.35, 0.35, 0.35))
            page.insert_text((W - 15 * mm - 22, y), "p. %d" % pno, fontsize=8.5, fontname="hebo", color=(0, 0, 0))
        else:
            page.insert_text((15 * mm, y), "p. %d" % pno, fontsize=8.5, fontname="hebo", color=(0, 0, 0))
            tw = fitz.get_text_length(label, fontname="helv", fontsize=7)
            page.insert_text((W - 15 * mm - tw, y), label, fontsize=7, fontname="helv", color=(0.35, 0.35, 0.35))
        # thumb tab on the outer edge
        if code:
            k = order.index(code)
            col = tuple(int(PART_BY_CODE[code][4][j:j + 2], 16) / 255 for j in (1, 3, 5))
            y0 = slot_top + k * slot_h
            x0, x1 = (W - 8 * mm, W) if odd else (0, 8 * mm)
            rect = fitz.Rect(x0, y0 + 1, x1, y0 + slot_h - 1)
            page.draw_rect(rect, color=None, fill=col, overlay=True)
            tx = (W - 5.6 * mm) if odd else (2.0 * mm)
            page.insert_text((tx, y0 + slot_h / 2 + 4), code, fontsize=11, fontname="hebo", color=(1, 1, 1))
    # bookmarks
    toc = []
    for c in PARTS:
        pid = "part-" + c[0]
        if pid in pages:
            toc.append([1, "%s  %s" % (c[0], c[2]), pages[pid]])
    toc.insert(0, [1, "Contents", pages.get("toc", 2)])
    d.set_toc(toc)
    d.set_metadata({"title": "COMP3511 Midterm Cheat Book", "subject": "Fall 2026 midterm, chapters 1-6"})
    d.save(pdf_out, garbage=3, deflate=True)
    d.close()
    return ranges


def fill_numbers(doc_html, pages):
    def rep(m):
        cls, hid = m.group(1), m.group(2)
        return '<span class="%s" data-id="%s">%s</span>' % (cls, hid, pages.get(hid, "–"))
    return re.sub(r'<span class="(pg|pgi)" data-id="([^"]+)">[^<]*</span>', rep, doc_html)


def main():
    os.makedirs(WORK, exist_ok=True)
    ensure_katex_assets()
    sources = ([source(p[1]) for p in PARTS if p[1]] + [read("qb1_mc_bank.md"), read("qb3_practice_mc.md")]
               + xa_sources() + ([read("xa_intro.md")] if os.path.exists(os.path.join(NOTES, "xa_intro.md")) else [])
               + [read(f) for f in HOWTO_FILES])
    formulas = collect_math(sources)
    katex_prerender(formulas)
    print("formulas:", len(formulas))
    h1_path = os.path.join(WORK, "cheatbook_pass1.html")
    p1_path = os.path.join(WORK, "cheatbook_pass1.pdf")
    doc, router_ids = build_html()
    io.open(h1_path, "w", encoding="utf-8").write(doc)
    chrome_pdf(h1_path, p1_path)
    pages1 = named_pages(p1_path)
    n1 = fitz.open(p1_path).page_count
    ranges1 = part_ranges(pages1, n1)
    missing = [t for t in router_ids if t not in pages1]
    print("pass1 pages:", n1, "| named dests:", len(pages1), "| router ids missing:", missing)
    index_html, n_idx = compute_index(p1_path, ranges1)
    # pass 2 with real numbers + real index
    doc2, _ = build_html(pages=pages1, index_html=index_html)
    h2_path = os.path.join(WORK, "cheatbook_pass2.html")
    p2_path = os.path.join(WORK, "cheatbook_pass2.pdf")
    io.open(h2_path, "w", encoding="utf-8").write(doc2)
    chrome_pdf(h2_path, p2_path)
    pages2 = named_pages(p2_path)
    shifted = [k for k in pages1 if pages2.get(k) != pages1[k] and not k.startswith("part-I")]
    print("pass2 pages:", fitz.open(p2_path).page_count, "| shifted anchors:", shifted[:10])
    if shifted:
        doc2 = fill_numbers(doc2, pages2)
        io.open(h2_path, "w", encoding="utf-8").write(doc2)
        chrome_pdf(h2_path, p2_path)
        pages2 = named_pages(p2_path)
    ranges = decorate(p2_path, OUT_PDF, pages2)
    io.open(OUT_HTML, "w", encoding="utf-8").write(
        doc2.replace(IMG_ABS, "Midterm_Site/assets/img/").replace(KATEX_CSS_ABS, KATEX_CSS_REL))
    print("index entries:", n_idx)
    for c in PARTS:
        if c[0] in ranges:
            s, e = ranges[c[0]]
            print("  %s %-22s pages %3d-%3d (%d)" % (c[0], c[2], s, e, e - s + 1))
    print("wrote", OUT_PDF)


if __name__ == "__main__":
    main()
