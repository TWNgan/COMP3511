"""Build the COMP3511 midterm study website from Midterm_Notes/*.md.

Run:  python -I build_site.py
Writes HTML pages + generated data scripts into Midterm_Site/ (never deletes other files there).
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
import mistune  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Code\UST\COMP3511"
NOTES = os.path.join(ROOT, "Midterm_Notes")
SITE = os.path.join(ROOT, "Midterm_Site")

# (slug, source file or None, nav title, group, short label)
PAGES = [
    ("index", None, "首頁 Home", "Start", "Home"),
    ("ch0", "ch0_exam_strategy.md", "考試攻略 Exam Strategy", "Start", "Strategy"),
    ("essentials", "cb_essentials.md", "考場一頁通 Essentials", "Start", "Essentials"),
    ("playbooks", "cb_playbooks.md", "解題 Playbooks", "Start", "Playbooks"),
    ("ch1", "ch1_introduction.md", "Ch1 Introduction", "Notes", "Ch1"),
    ("ch2", "ch2_os_structures.md", "Ch2 OS Structures", "Notes", "Ch2"),
    ("ch3", "ch3_processes.md", "Ch3 Processes", "Notes", "Ch3"),
    ("ch4", "ch4_threads.md", "Ch4 Threads", "Notes", "Ch4"),
    ("ch5", "ch5_cpu_scheduling.md", "Ch5 CPU Scheduling", "Notes", "Ch5"),
    ("ch6", "ch6_synchronization.md", "Ch6 Synchronization", "Notes", "Ch6"),
    ("labs", "lab_notes.md", "Labs & PA1/PA2", "Notes", "Labs"),
    ("api", "api_reference.md", "API 速查 (C / Pthreads)", "Reference", "API"),
    ("glossary", "glossary.md", "Glossary A–Z", "Reference", "Glossary"),
    ("bank", None, "歷屆試題 Past Papers", "Practice", "Past papers"),
    ("quiz", None, "MC 練習 Quiz", "Practice", "Quiz"),
    ("tools", None, "工具 Scheduler & Calculators", "Practice", "Tools"),
]
NAV_ICON = {"index": "🏠", "ch0": "🎯", "essentials": "⚡", "playbooks": "🧭", "ch1": "1️⃣", "ch2": "2️⃣",
            "ch3": "3️⃣", "ch4": "4️⃣", "ch5": "5️⃣", "ch6": "6️⃣", "labs": "🧪", "api": "🧰", "glossary": "🔤",
            "bank": "📜", "quiz": "✅", "tools": "🛠️"}
MD_PLUGINS = ["table", "strikethrough", "math", "mistune.plugins.math.math_in_quote",
              "mistune.plugins.math.math_in_list"]


# ---------------------------------------------------------------- LaTeX math (KaTeX, pre-rendered at build time)
KATEX_PKG = os.path.join(ROOT, "_work", "midterm", "katex_pkg", "node_modules", "katex")
KATEX_JS = os.path.join(ROOT, "_work", "midterm", "scripts", "katex_render.js")
KATEX_CACHE = os.path.join(ROOT, "_work", "midterm", "katex_cache.json")
_KCACHE = {}


def _kc():
    if not _KCACHE:
        try:
            _KCACHE.update(json.load(io.open(KATEX_CACHE, encoding="utf-8")))
        except (OSError, ValueError):
            pass
    return _KCACHE


def katex_prerender(items):
    """items: iterable of (tex, display). Render all uncached formulas with one node call."""
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


def collect_math(md_texts):
    """Parse sources once just to collect every formula, so they can be rendered in one batch."""
    found = []
    r = mistune.HTMLRenderer(escape=False)
    m = mistune.create_markdown(renderer=r, plugins=MD_PLUGINS)
    r.register("block_math", lambda _r, t: found.append((t.strip(), True)) or "")
    r.register("inline_math", lambda _r, t: found.append((t.strip(), False)) or "")
    for s in md_texts:
        m(preprocess(s))
    return found


def ensure_katex_assets():
    """Copy KaTeX CSS + woff2 fonts (+ MIT licence) into Midterm_Site/assets/katex/."""
    dst = os.path.join(SITE, "assets", "katex")
    os.makedirs(os.path.join(dst, "fonts"), exist_ok=True)
    shutil.copyfile(os.path.join(KATEX_PKG, "dist", "katex.min.css"), os.path.join(dst, "katex.min.css"))
    shutil.copyfile(os.path.join(KATEX_PKG, "LICENSE"), os.path.join(dst, "LICENSE"))
    for f in glob.glob(os.path.join(KATEX_PKG, "dist", "fonts", "*.woff2")):
        shutil.copyfile(f, os.path.join(dst, "fonts", os.path.basename(f)))


# ---------------------------------------------------------------- generated tables (playbooks)
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
        row = ["**%.2f**（par %.0f%%）" % (S, (1 - S) * 100)]
        row += ["%.2f" % (1 / (S + (1 - S) / N)) for N in Ns]
        rows.append(row + ["**%.2f**" % (1 / S)])
    return md_table([r"$S \backslash N$"] + [str(n) for n in Ns] + [r"$\infty$"], rows)


def pow_table():
    rows = [[n, 2 ** n, 3 ** n, 4 ** n, 6 ** n, 2 ** (n + 1) - 1, 2 ** n - 1, 2 ** (n + 1) - 2, 2 * (3 ** n + 1),
             (4 ** n - 1) // 3] for n in range(1, 11)]
    return md_table([r"$n$", r"$2^n$", r"$3^n$", r"$4^n$", r"$6^n$", r"$2^{n+1}-1$", r"$2^n-1$", r"$2^{n+1}-2$",
                     r"$2(3^n+1)$", r"$(4^n-1)/3$"], rows)


def rm_table():
    rows = [[n, "%.3f" % (n * (2 ** (1.0 / n) - 1))] for n in range(1, 11)] + [[r"$\infty$", r"0.693（$\ln 2$）"]]
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
    """Markdown source of a page (playbooks get their generated tables)."""
    md = read(name)
    return inject(md) if name == "cb_playbooks.md" else md


# ---------------------------------------------------------------- markdown helpers
def read(name):
    with io.open(os.path.join(NOTES, name), encoding="utf-8") as f:
        return f.read()


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
    """Make every table a top-level block surrounded by blank lines; protect pipes inside cells."""
    lines = md.split("\n")
    out, in_code = [], False
    i = 0
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


def make_id(text, used):
    t = strip_tags(text).strip()
    m = re.match(r"^(\d+(?:\.\d+)*)\.?\s", t + " ")
    if m:
        base = "s" + m.group(1).replace(".", "-")
    else:
        words = re.findall(r"[A-Za-z0-9]+", t)
        base = "-".join(words[:6]).lower() or "sec"
    hid, k = base, 2
    while hid in used:
        hid = "%s-%d" % (base, k)
        k += 1
    used.add(hid)
    return hid


def callout_class(text):
    t = strip_tags(text).lstrip()
    if t.startswith("⚠"):
        return "warn"
    if t.startswith("📝"):
        return "answer"
    if t.startswith("🧮"):
        return "formula"
    if t.startswith("🎯"):
        return "tip"
    return "info"


class Renderer(mistune.HTMLRenderer):
    def __init__(self):
        super().__init__(escape=False)
        self.toc, self.used = [], set()

    def reset(self):
        self.toc, self.used = [], set()

    def heading(self, text, level, **attrs):
        hid = make_id(text, self.used)
        if level in (2, 3):
            self.toc.append((level, hid, strip_tags(text)))
        if level == 1:
            return '<h1 id="%s">%s</h1>\n' % (hid, text)
        return '<h%d id="%s"><a class="anchor" href="#%s">#</a>%s</h%d>\n' % (level, hid, hid, text, level)

    def block_quote(self, text):
        return '<blockquote class="callout %s">\n%s</blockquote>\n' % (callout_class(text), text)

    def block_code(self, code, info=None):
        lang = (info or "").strip().split(" ")[0]
        return '<pre class="code" data-lang="%s"><code>%s</code></pre>\n' % (html.escape(lang), html.escape(code))


RENDERER = Renderer()
MD = mistune.create_markdown(renderer=RENDERER, plugins=MD_PLUGINS)
RENDERER.register("block_math", lambda r, t: '<div class="math-display">%s</div>\n' % katex_html(t.strip(), True))
RENDERER.register("inline_math", lambda r, t: katex_html(t.strip(), False))

SREF = re.compile(r"\[(\d\.\d{1,2}(?:\s*[–\-]\s*\d?\.?\d{1,2})?(?:\s*,\s*\d\.\d{1,2}(?:\s*[–\-]\s*\d?\.?\d{1,2})?)*)\]")


FIG = re.compile(r'<p><img src="img/([^"]+)" alt="([^"]*)"\s*/?></p>')


def figures(htm, base):
    """Turn a lone markdown image into a captioned figure; keep slide refs out of the alt attribute."""
    return FIG.sub(lambda m: '<figure class="fig"><img src="%s%s" alt="%s" loading="lazy"><figcaption>%s</figcaption></figure>'
                   % (base, m.group(1), re.sub(r"\s*\[[^\]]*\]", "", m.group(2)), m.group(2)), htm)


def post(htm):
    """Wrap tables, mark slide refs and ticks — outside <pre> blocks only."""
    htm = figures(htm, "assets/img/")
    parts = re.split(r"(<pre[\s\S]*?</pre>)", htm)
    for k in range(0, len(parts), 2):
        p = parts[k]
        p = p.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
        p = SREF.sub(lambda m: '<span class="sref">[%s]</span>' % m.group(1), p)
        p = p.replace("✅", '<span class="ok">✅</span>').replace("❌", '<span class="no">❌</span>')
        p = re.sub(r"(?<![\w>])✔(?![\w<])", '<span class="ok">✔</span>', p)
        parts[k] = p
    return "".join(parts).replace(PIPE_PH, "|")


def render_md(md):
    RENDERER.reset()
    out = post(MD(preprocess(md)))
    return out, list(RENDERER.toc)


def render_inline(md):
    """Render a short markdown fragment; drop the outer <p> if it is a single paragraph."""
    RENDERER.reset()
    h = post(MD(preprocess(md))).strip()
    if h.startswith("<p>") and h.endswith("</p>") and h.count("<p>") == 1:
        h = h[3:-4]
    return h


# ---------------------------------------------------------------- page template
def nav_html(active):
    out, group = [], None
    for slug, _src, title, grp, _short in PAGES:
        if grp != group:
            out.append('<div class="nav-group">%s</div>' % grp)
            group = grp
        cls = ' class="active"' if slug == active else ""
        out.append('<a href="%s.html" data-page="%s"%s><span>%s</span><span>%s</span><span class="done-dot"></span></a>'
                   % (slug, slug, cls, NAV_ICON.get(slug, "•"), html.escape(title)))
    out.append('<div class="nav-group">Print</div>')
    out.append('<a href="../COMP3511_Midterm_CheatBook.pdf"><span>🖨️</span><span>Cheat Book (PDF)</span></a>')
    out.append('<a href="../COMP3511_Midterm_CheatBook.html"><span>📖</span><span>Cheat Book (HTML)</span></a>')
    return "\n".join(out)


def toc_html(toc):
    if not toc:
        return ""
    items = ['<div class="toc-title">本頁內容 On this page</div>']
    for level, hid, text in toc:
        items.append('<a class="l%d" href="#%s">%s</a>' % (level, hid, html.escape(text)))
    return '<aside class="toc">%s</aside>' % "\n".join(items)


def pager_html(slug):
    slugs = [p[0] for p in PAGES]
    i = slugs.index(slug)
    prev = PAGES[i - 1] if i > 0 else None
    nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
    a = ('<a href="%s.html"><small>← 上一頁</small>%s</a>' % (prev[0], html.escape(prev[2]))) if prev else "<span></span>"
    b = ('<a class="next" href="%s.html"><small>下一頁 →</small>%s</a>' % (nxt[0], html.escape(nxt[2]))) if nxt else "<span></span>"
    return '<nav class="pager">%s%s</nav>' % (a, b)


def page(slug, title, body, toc=None, extra_head="", extra_js="", mark=True, show_toc=True):
    toc = toc or []
    mark_btn = '<button class="btn mark-done" id="mark-done"></button>' if mark else ""
    return """<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · COMP3511 Midterm</title>
<link rel="stylesheet" href="assets/katex/katex.min.css">
<link rel="stylesheet" href="assets/site.css">
{extra_head}
<script src="assets/site.js"></script>
<script src="assets/search-index.js"></script>
</head>
<body data-page="{slug}">
<header class="topbar">
  <button class="btn menu-btn" id="menu-btn" aria-label="menu">☰</button>
  <a class="brand" href="index.html">COMP3511 <span>Midterm</span><span class="hide-sm"> OP Notes</span></a>
  <div class="search-wrap">
    <input id="search" type="search" placeholder="搜尋 Search（按 / 或 Ctrl+K）: fork, MLFQ, zombie, Amdahl…" autocomplete="off">
    <div class="search-results" id="search-results"></div>
  </div>
  <span class="spacer"></span>
  <a class="btn hide-sm" href="../COMP3511_Midterm_CheatBook.pdf" title="Printable cheat book">🖨️ Cheat Book</a>
  <a class="btn show-sm" href="../COMP3511_Midterm_CheatBook.pdf" title="Printable cheat book">🖨️</a>
  <button class="btn" id="theme-btn" aria-label="theme">🌙</button>
</header>
<div class="layout">
<nav class="sidebar">
{nav}
</nav>
<main>
<div class="content">
<div class="page-head"><span class="tag">{tag}</span>{mark_btn}</div>
{body}
{pager}
</div>
<footer class="site">COMP3511 Fall 2026 · Midterm 29-Oct-2026 (Thu) 8–10 PM · L1 LTD · L2 LSKG012 · L3 LTB · notes generated from lecture slides 1–6</footer>
</main>
{toc}
</div>
{extra_js}
</body>
</html>
""".format(title=html.escape(title), extra_head=extra_head, slug=slug, nav=nav_html(slug),
           tag=html.escape(dict((p[0], p[3]) for p in PAGES).get(slug, "")), mark_btn=mark_btn, body=body,
           pager=pager_html(slug), toc=toc_html(toc) if show_toc else "", extra_js=extra_js)


BUILD = str(int(__import__("time").time()))


def write(name, text):
    if name.endswith(".html"):  # cache-bust local assets so a rebuilt site is always picked up
        text = re.sub(r'((?:src|href)="assets/[^"?]+\.(?:js|css))"', r'\1?v=' + BUILD + '"', text)
    with io.open(os.path.join(SITE, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------- search index
SEARCH = []


def index_sections(slug, title, htm, weight=0):
    """Split rendered HTML at h2/h3 and add each section to the search index."""
    chunks = re.split(r'(<h[23] id="[^"]+">[\s\S]*?</h[23]>)', htm)
    head_title, head_id = title, ""
    body = chunks[0]
    entries = []
    for k in range(1, len(chunks), 2):
        entries.append((head_title, head_id, body))
        m = re.match(r'<h[23] id="([^"]+)">([\s\S]*?)</h[23]>', chunks[k])
        head_id = m.group(1)
        head_title = strip_tags(m.group(2)).lstrip("#").strip()
        body = chunks[k + 1] if k + 1 < len(chunks) else ""
    entries.append((head_title, head_id, body))
    short = dict((p[0], p[4]) for p in PAGES).get(slug, slug)
    for t, hid, b in entries:
        text = re.sub(r"\s+", " ", strip_tags(b)).strip()
        if not text and not hid:
            continue
        SEARCH.append({"t": t, "u": "%s.html%s" % (slug, "#" + hid if hid else ""), "p": short,
                       "x": text[:700], "w": weight})


# ---------------------------------------------------------------- question banks
HEAD = re.compile(r"^## \[([^\]]+)\] (ch\d) \| (.+)$", re.M)


def parse_bank(md):
    items = []
    heads = list(HEAD.finditer(md))
    for k, m in enumerate(heads):
        end = heads[k + 1].start() if k + 1 < len(heads) else len(md)
        body = md[m.end():end].strip()
        body = re.sub(r"\n---\s*$", "", body).strip()
        items.append({"id": m.group(1), "ch": m.group(2), "topic": m.group(3).strip(), "body": body})
    return items


def mc_item(it, kind):
    body = it["body"]
    am = re.search(r"^\*\*Answer: ([A-D])\*\*(.*)$", body, re.M)
    if not am:
        raise ValueError("no answer in " + it["id"])
    before, after = body[:am.start()], body[am.end():].strip()
    alt = None
    altm = re.search(r"([A-D]) 亦接受", am.group(2))
    if altm:
        alt = altm.group(1)
    opt_lines = re.findall(r"^- ([A-D])\. (.+)$", before, re.M)
    stem = re.split(r"^- A\. ", before, flags=re.M)[0].strip()
    return {
        "id": it["id"], "ch": it["ch"], "topic": it["topic"], "kind": kind,
        "src": it["id"].split("-")[0],
        "stem": render_md(stem)[0],
        "opts": [render_inline(o) for _l, o in opt_lines],
        "ans": am.group(1), "alt": alt,
        "exp": render_md(after)[0] if after else "",
    }


def build_quiz():
    data = []
    for it in parse_bank(read("qb1_mc_bank.md")):
        data.append(mc_item(it, "past"))
    for it in parse_bank(read("qb3_practice_mc.md")):
        data.append(mc_item(it, "new"))
    for q in data:
        SEARCH.append({"t": "%s %s" % (q["id"], q["topic"]), "u": "quiz.html#" + q["id"], "p": "Quiz",
                       "x": re.sub(r"\s+", " ", strip_tags(q["stem"] + " " + " ".join(q["opts"]) + " " + q["exp"]))[:500],
                       "w": -2})
    write("assets/quiz-data.js", "window.QUIZ = " + json.dumps(data, ensure_ascii=False) + ";\n")
    body = ("<h1>MC 練習 Quiz</h1>"
            "<p>%d 題：歷屆 MC（S26 / F20 / Sp21 / HW1 / HW2）+ 新練習題（針對 Fall 2026 slides）。撳選項即時對答案；"
            "紀錄會保存喺瀏覽器（localStorage），可以揀「錯題 Wrong only」溫返錯嘅題目。</p>"
            '<div id="quiz-app"></div>' % len(data))
    write("quiz.html", page("quiz", "MC Quiz", body, mark=False, show_toc=False,
                            extra_js='<script src="assets/quiz-data.js"></script><script src="assets/quiz.js"></script>'))
    return len(data)


def build_bank():
    items = parse_bank(read("qb2_long_bank.md"))
    papers = []
    for it in items:
        p = it["id"].split("-")[0]
        if p not in papers:
            papers.append(p)
    out = ['<h1>歷屆試題 Past-paper Long Questions</h1>',
           '<p>全部 short / long questions 連標準答案（fork 數目、Gantt chart、synchronization 值都用程式驗證過 ✅）。'
           '先自己做，再撳「顯示答案」。MC 喺 <a href="quiz.html">Quiz</a> 頁。</p>',
           '<div class="filters" id="bank-f-paper"><b>Paper：</b>']
    for p in papers:
        out.append('<span class="chip on" data-paper="%s">%s</span>' % (p, p))
    out.append('</div><div class="filters" id="bank-f-ch"><b>Chapter：</b>')
    for c in ["ch1", "ch2", "ch3", "ch4", "ch5", "ch6"]:
        out.append('<span class="chip on" data-ch="%s">%s</span>' % (c, c.replace("ch", "Ch")))
    out.append('</div><div class="filters"><button class="btn" id="bank-open">全部展開答案</button>'
               '<button class="btn" id="bank-close">全部收起</button></div>')
    for it in items:
        body = it["body"]
        parts = re.split(r"^\*\*Answer:\*\*\s*$", body, flags=re.M)
        q_md = parts[0].strip()
        a_md = parts[1].strip() if len(parts) > 1 else ""
        q_html = render_md(q_md)[0]
        a_html = render_md(a_md)[0]
        paper = it["id"].split("-")[0]
        out.append('<div class="qitem" id="%s" data-paper="%s" data-ch="%s"><div class="qhead"><span class="qid">%s</span>'
                   '<span class="qtopic">%s</span><span class="qch">%s</span></div>%s'
                   '<details><summary>顯示答案 Show answer</summary><div class="ans">%s</div></details></div>'
                   % (it["id"], paper, it["ch"], it["id"], html.escape(it["topic"]), it["ch"].upper(), q_html, a_html))
        SEARCH.append({"t": "%s %s" % (it["id"], it["topic"]), "u": "bank.html#" + it["id"], "p": "Past papers",
                       "x": re.sub(r"\s+", " ", strip_tags(q_html + " " + a_html))[:600], "w": 1})
    js = """<script>
(function(){
  var chips=document.querySelectorAll('.chip[data-paper], .chip[data-ch]');
  function apply(){
    var on={}; for(var i=0;i<chips.length;i++){var c=chips[i]; on[c.getAttribute('data-paper')||c.getAttribute('data-ch')]=c.classList.contains('on');}
    var qs=document.querySelectorAll('.qitem');
    for(var j=0;j<qs.length;j++){var q=qs[j]; q.style.display=(on[q.getAttribute('data-paper')]&&on[q.getAttribute('data-ch')])?'':'none';}
  }
  for(var i=0;i<chips.length;i++) chips[i].addEventListener('click',function(){this.classList.toggle('on');apply();});
  document.getElementById('bank-open').onclick=function(){var d=document.querySelectorAll('.qitem details');for(var i=0;i<d.length;i++)d[i].open=true;};
  document.getElementById('bank-close').onclick=function(){var d=document.querySelectorAll('.qitem details');for(var i=0;i<d.length;i++)d[i].open=false;};
  if(location.hash){var el=document.getElementById(location.hash.slice(1)); if(el){var d=el.querySelector('details'); if(d) d.open=true;}}
})();
</script>"""
    write("bank.html", page("bank", "Past Papers", "\n".join(out), mark=False, show_toc=False, extra_js=js))
    return len(items)


# ---------------------------------------------------------------- notes pages
def build_notes():
    for slug, src, title, _grp, _short in PAGES:
        if not src:
            continue
        htm, toc = render_md(source(src))
        if slug == "glossary":
            # give each glossary row an id so search can deep-link to it
            def row_id(m):
                term = strip_tags(m.group(1)).strip()
                gid = "g-" + re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
                SEARCH.append({"t": term, "u": "glossary.html#" + gid, "p": "Glossary",
                               "x": re.sub(r"\s+", " ", strip_tags(m.group(2)))[:300], "w": 6})
                return '<tr id="%s"><td>%s</td>%s</tr>' % (gid, m.group(1), m.group(2))
            htm = re.sub(r"<tr>\s*<td>([\s\S]*?)</td>([\s\S]*?)</tr>", row_id, htm)
        else:
            index_sections(slug, title, htm, weight=3 if slug.startswith("ch") else 1)
        write(slug + ".html", page(slug, title, htm, toc))


# ---------------------------------------------------------------- home + tools
def build_home():
    cards = [
        ("ch0", "考試攻略 Strategy", "必讀", ["試卷結構預測 + 時間分配", "題型 → 方法 index", "24 小時溫習計劃 + 必帶清單"]),
        ("essentials", "考場一頁通 Essentials", "考前必睇", ["公式卡（LaTeX）", "本科 conventions", "Top traps 陷阱表"]),
        ("playbooks", "解題 Playbooks", "計數題", ["fork / pipe / scheduling / sync 步驟", "Amdahl / powers / RM 預計表", "歷屆 fork 答案總表"]),
        ("ch1", "Ch1 Introduction", "MC 2–4 題", ["Caching + AMAT + locality", "von Neumann / storage hierarchy", "SMP / multicore / NUMA / virtualization"]),
        ("ch2", "Ch2 OS Structures", "MC 3–5 + short", ["API vs system call / printf→write", "Linker vs loader", "Monolithic / layered / microkernel / LKM"]),
        ("ch3", "Ch3 Processes", "~24 分", ["fork() 解題大法（公式 + 例題）", "Interrupt / DMA / dual mode", "Pipe / dup / zombie / IPC"]),
        ("ch4", "Ch4 Threads", "MC 3–4", ["Shared vs private", "Amdahl 計算", "Models / signals / cancellation"]),
        ("ch5", "Ch5 CPU Scheduling", "~27 分（最重）", ["Gantt 流程 + response time 定義", "MLFQ 規則 + RM/EDF", "全部歷屆計算題答案"]),
        ("ch6", "Ch6 Synchronization", "8–15 分", ["Race condition 可能值", "Semaphore 次序 / 序列題", "TAS / CAS / swap spinlock"]),
        ("labs", "Labs & PA1/PA2", "PA 考點", ["Lab 3 system calls / dup / exec family", "PA2 MLFQ 規則 + Lab 4–6 exam examples", "F22 / F24 / S25 / S23 歷屆題"]),
        ("api", "API 速查", "Lab / PA", ["fork / exec / wait / pipe / dup2", "Pthreads mutex / semaphore", "Redirection & pipeline code"]),
        ("bank", "歷屆試題", "Practice", ["S26 / F20 / F19 / Sp21 / HW + Lab 例題", "連標準答案（已驗證）", "按 paper / chapter 篩選"]),
        ("quiz", "MC Quiz", "Practice", ["~150 題 MC（歷屆 + 新題）", "即時對答案 + 解釋", "錯題重溫"]),
        ("tools", "工具", "Practice", ["CPU scheduling 模擬器（Gantt + 步驟）", "RM / EDF / MLFQ / dynamic priority", "Amdahl / AMAT / Little 計算機"]),
    ]
    c = []
    for slug, t, w, pts in cards:
        c.append('<div class="card" data-page="%s"><span class="weight">%s</span><h3>%s</h3><ul>%s</ul>'
                 '<a class="go" href="%s.html">打開 →</a></div>'
                 % (slug, w, t, "".join("<li>%s</li>" % p for p in pts), slug))
    body = """
<div class="hero">
  <h1>COMP3511 Midterm OP Notes 🚀</h1>
  <div class="meta">📅 29-Oct-2026（Thu）8:00–10:00 PM · 📍 L1 → <b>LTD</b> · L2 → <b>LSKG012</b> · L3 → <b>LTB</b>（唔好同 LAx 搞亂）<br>
  📚 Chapters 1–6（up to Synchronization Tools）· 📖 Open-book / open-notes（printed）· 🧮 Calculator OK · 📝 自備 rough work sheets</div>
  <div class="countdown" id="countdown"></div>
</div>
<blockquote class="callout tip"><p>🎯 <b>點用呢個網站：</b>(1) 先睇 <a href="ch0.html">考試攻略</a>；(2) 按章讀 notes（中文解釋 + 英文 keywords / model answers）；
(3) 用 <a href="tools.html">Scheduler 工具</a> 做 Gantt chart 對答案；(4) 做晒 <a href="quiz.html">MC Quiz</a> 同 <a href="bank.html">歷屆長題</a>；
(5) 考試帶打印咗嘅 <a href="../COMP3511_Midterm_CheatBook.pdf">Cheat Book</a>。按 <code>/</code> 隨時搜尋。</p></blockquote>
<div class="grid">@@CARDS@@</div>
<h2 id="key-facts">⚡ 最易失分嘅 10 件事</h2>
<ol>
<li><b>Response time（本科）= 第一次運行「完結」− arrival</b>（slide 5.12），唔係第一次開始。</li>
<li><b>MLFQ：被 preempt 嘅 Q1/Q2 job 返 queue HEAD，保留剩餘 quantum</b>；只有用晒 quantum 先降級。</li>
<li><b>fork() 返回值：child = 0、parent = child PID、失敗 = −1</b>；<code>&&</code> / <code>||</code> 短路。</li>
<li><b>exec() 成功唔會 return</b>（之後嘅 printf 唔會印）。</li>
<li><b>Mode bit：1 = user，0 = kernel</b>；privileged instruction 喺 user mode → trap。</li>
<li><b>DMA 完成一個 block 先 interrupt 一次</b>（唔係每個 byte）。</li>
<li><b>Named pipe 要 explicitly delete</b>；ordinary pipe 要 parent–child、單向。</li>
<li><b>Amdahl：S = serial portion</b>（題目畀 parallel % 要轉換）；N→∞ speedup → 1/S。</li>
<li><b>RM = static（period 短 = 高）；EDF = dynamic（deadline 早 = 高）</b>；soft RT miss 咗都繼續跑。</li>
<li><b>Semaphore 填空題冇用嘅 blank 要寫 <code>/* Nothing */</code></b>；test_and_set / CAS 返回 <b>old value</b>。</li>
</ol>
""".replace("@@CARDS@@", "\n".join(c))
    write("index.html", page("index", "Home", body, mark=False, show_toc=False))


def build_tools():
    body = """
<h1>工具 Tools</h1>
<p>CPU scheduling 模擬器（跟本科 convention：response time = end of first run − arrival；MLFQ preempted → head of queue + 剩餘 quantum），
同埋考試常用計算機。考試唔可以用電腦，所以用嚟<b>練習同對答案</b>。</p>
<h2 id="scheduler">🗓️ CPU Scheduling Simulator</h2>
<div id="sched-app"><p class="muted">（載入中… 如果冇顯示，請確認 assets/sched.js 存在）</p></div>
<h2 id="calculators">🧮 Calculators</h2>
<div class="calc" id="calc-amdahl"><h3>Amdahl's Law</h3>
 <label>輸入係 <select id="am-mode"><option value="serial">serial 比例 S</option><option value="parallel">parallel 比例</option></select></label>
 <label>比例 (0–1) <input id="am-s" type="number" step="0.01" value="0.25"></label>
 <label>cores N <input id="am-n" type="number" value="2"></label>
 <div class="out" id="am-out"></div>
 <h4>反向：想要 speedup X（N cores）需要幾多 serial？</h4>
 <label>X <input id="amr-x" type="number" step="0.1" value="3"></label><label>N <input id="amr-n" type="number" value="4"></label>
 <div class="out" id="amr-out"></div>
</div>
<div class="calc"><h3>Average Memory Access Time</h3>
 <label>hit ratio (0–1 或 %) <input id="am-h" type="number" step="0.01" value="0.9"></label>
 <label>hit time <input id="am-ht" type="number" value="2"></label>
 <label><select id="am-mtype"><option value="time">miss time</option><option value="penalty">miss penalty</option></select> <input id="am-mt" type="number" value="50"></label>
 <div class="out" id="amat-out"></div>
</div>
<div class="calc"><h3>Exponential Averaging τ(n+1) = α·t(n) + (1−α)·τ(n)</h3>
 <label>α <input id="ea-a" type="number" step="0.05" value="0.5"></label>
 <label>τ0 <input id="ea-t0" type="number" value="10"></label>
 <label>actual bursts <input id="ea-ts" value="6 4 6 4 13 13 13" style="width:220px"></label>
 <div class="out" id="ea-out"></div>
</div>
<div class="calc"><h3>Little's Formula n = λ × W（留空要計嗰格）</h3>
 <label>n <input id="li-n" type="number" value="12"></label>
 <label>λ <input id="li-l" type="number" value="3"></label>
 <label>W <input id="li-w" type="number"></label>
 <div class="out" id="li-out"></div>
</div>
<div class="calc"><h3>Real-time utilization & RM bound</h3>
 <label>每行一個 task：<code>processing_time period</code></label><br>
 <textarea id="rt-tasks" rows="4" cols="30">25 50
35 80</textarea>
 <div class="out" id="rt-out"></div>
</div>
<div class="calc"><h3>fork() pattern counter</h3>
 <label>pattern <select id="fk-pat">
  <option value="f1">loop n: fork();</option>
  <option value="f2">loop n: fork(); fork();</option>
  <option value="f3">loop n: if (fork()) fork();</option>
  <option value="f4">loop n: if (fork()==0) fork();</option>
  <option value="f5">loop n: if (fork()) fork(); else break;</option>
  <option value="f6">loop n: if (fork()) printf else printf (lines)</option>
  <option value="f7">if(!fork()){loop n: if(fork()) fork();} fork(); printf</option>
 </select></label>
 <label>n <input id="fk-n" type="number" value="3"></label>
 <div class="out" id="fk-out"></div>
</div>
"""
    head = '<link rel="stylesheet" href="assets/sched.css">'
    js = ('<script src="assets/sched.js"></script><script src="assets/sched-ui.js"></script>'
          '<script src="assets/tools.js"></script>')
    write("tools.html", page("tools", "Tools", body, toc=[(2, "scheduler", "CPU Scheduling Simulator"),
                                                        (2, "calculators", "Calculators")],
                             extra_head=head, extra_js=js, mark=False))
    SEARCH.append({"t": "CPU Scheduling Simulator (Gantt chart tool)", "u": "tools.html#scheduler", "p": "Tools",
                   "x": "FCFS SJF SRTF RR priority MLFQ RM EDF dynamic priority Gantt chart simulator waiting turnaround response",
                   "w": 4})
    SEARCH.append({"t": "Calculators: Amdahl, AMAT, exponential averaging, Little, RM bound, fork", "u": "tools.html#calculators",
                   "p": "Tools", "x": "Amdahl speedup average access time exponential averaging Little's formula utilization rate monotonic bound fork count", "w": 4})


def main():
    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
    ensure_katex_assets()
    sources = [source(p[1]) for p in PAGES if p[1]] + [read("qb1_mc_bank.md"), read("qb2_long_bank.md"),
                                                      read("qb3_practice_mc.md")]
    formulas = collect_math(sources)
    katex_prerender(formulas)
    print("formulas:", len(set(formulas)))
    build_notes()
    nq = build_quiz()
    nb = build_bank()
    build_home()
    build_tools()
    write("assets/search-index.js", "window.SEARCH_INDEX = " + json.dumps(SEARCH, ensure_ascii=False) + ";\n")
    print("pages:", len(PAGES), "quiz:", nq, "bank:", nb, "search entries:", len(SEARCH))


if __name__ == "__main__":
    main()
