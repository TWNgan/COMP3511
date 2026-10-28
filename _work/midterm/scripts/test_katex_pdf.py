"""Render a few formulas with KaTeX, print to PDF with Chrome, and report which fonts got embedded."""
import io
import json
import os
import site
import subprocess
import sys

sys.path.append(site.getusersitepackages())
sys.stdout.reconfigure(encoding="utf-8")
import fitz  # noqa: E402

W = r"C:\Code\UST\COMP3511\_work\midterm\cb"
S = r"C:\Code\UST\COMP3511\_work\midterm\scripts"
items = [{"tex": r"\text{speedup} \le \dfrac{1}{S + \dfrac{1-S}{N}}", "display": True},
         {"tex": r"\tau_{n+1} = \alpha\, t_n + (1-\alpha)\,\tau_n", "display": False},
         {"tex": r"2^{n+1}-1", "display": False}]
io.open(os.path.join(W, "km_in.json"), "w", encoding="utf-8").write(json.dumps(items))
subprocess.run(["node", os.path.join(S, "katex_render.js"), os.path.join(W, "km_in.json"), os.path.join(W, "km_out.json")], check=True)
html = json.loads(io.open(os.path.join(W, "km_out.json"), encoding="utf-8").read())
css = "file:///C:/Code/UST/COMP3511/_work/midterm/katex_pkg/node_modules/katex/dist/katex.min.css"
page = ('<!DOCTYPE html><html><head><meta charset="utf-8"><link rel="stylesheet" href="%s"></head>'
        '<body style="font-family:Segoe UI">Display:%s<p>Inline %s and %s.</p></body></html>' % (css, html[0], html[1], html[2]))
hp = os.path.join(W, "km_test.html")
io.open(hp, "w", encoding="utf-8").write(page)
pdf = os.path.join(W, "km_test.pdf")
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-first-run", "--user-data-dir=" + os.path.join(W, "prof"),
                "--no-pdf-header-footer", "--print-to-pdf=" + pdf, "file:///" + hp.replace("\\", "/")],
               capture_output=True, timeout=120)
d = fitz.open(pdf)
print("fonts embedded:", sorted(set(f[3] for f in d[0].get_fonts())))
d[0].get_pixmap(matrix=fitz.Matrix(2, 2), clip=fitz.Rect(0, 0, 400, 200)).save(os.path.join(W, "km_test.png"))
