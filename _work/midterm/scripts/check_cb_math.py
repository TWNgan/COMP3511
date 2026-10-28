"""Check the cheat book PDF: KaTeX fonts embedded, which pages carry math, cover/TOC fit; render sample pages."""
import io
import os
import re
import site
import sys

sys.path.append(site.getusersitepackages())
import fitz  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Code\UST\COMP3511"
PDF = os.path.join(ROOT, "COMP3511_Midterm_CheatBook.pdf")
HTML = os.path.join(ROOT, "COMP3511_Midterm_CheatBook.html")
OUT = os.path.join(ROOT, "_work", "midterm", "cb", "png")
os.makedirs(OUT, exist_ok=True)

h = io.open(HTML, encoding="utf-8").read()
print("html: katex spans", h.count('class="katex"'), "| display", h.count('class="math-display"'),
      "| katex-error", h.count("katex-error"), "| css link", "Midterm_Site/assets/katex/katex.min.css" in h,
      "| leftover $", len(re.findall(r"(?<![\\\w])\$[^$\s][^$]*\$", re.sub(r"<[^>]+>", " ", h))))

d = fitz.open(PDF)
names = d.resolve_names()
print("pages", d.page_count, "| toc on page", names.get("toc", {}).get("page", -2) + 1, "| part-E on", names["part-E"]["page"] + 1)
fonts, math_pages = set(), []
for i in range(d.page_count):
    fs = [f[3] for f in d[i].get_fonts()]
    k = [f for f in fs if "KaTeX" in f]
    fonts.update(k)
    if k:
        math_pages.append(i + 1)
print("KaTeX fonts:", sorted(set(re.sub(r"^[A-Z]{6}\+", "", f) for f in fonts)))
print("pages with math (%d):" % len(math_pages), math_pages)
want = [int(a) for a in sys.argv[1:]] or [1, 2, 4, 5, 8]
for p in want:
    pix = d[p - 1].get_pixmap(dpi=110)
    pix.save(os.path.join(OUT, "p%03d.png" % p))
print("rendered", want, "->", OUT)
