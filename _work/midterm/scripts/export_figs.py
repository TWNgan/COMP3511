"""Render selected lecture slides to PNG for the notes (site + cheat book)."""
import os
import site
import sys

sys.path.append(site.getusersitepackages())
import fitz  # noqa: E402

ROOT = r"C:\Code\UST\COMP3511"
OUT = os.path.join(ROOT, "Midterm_Site", "assets", "img")
os.makedirs(OUT, exist_ok=True)
FIGS = {
    "Chapter1.pdf": [29, 45],
    "Chapter2.pdf": [13, 19, 32, 40, 47],
    "Chapter3.pdf": [9, 16, 26],
    "Chapter4.pdf": [6, 10],
    "Chapter5.pdf": [27, 50, 51],
}
for pdf, pages in FIGS.items():
    doc = fitz.open(os.path.join(ROOT, "Lecture_notes", pdf))
    for p in pages:
        page = doc[p - 1]
        r = page.rect
        # trim the dark sidebar/footer chrome a little: keep the slide body
        clip = fitz.Rect(r.x0 + r.width * 0.04, r.y0 + r.height * 0.02, r.x1, r.y1 - r.height * 0.045)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), clip=clip)
        name = "%s_p%d.png" % (pdf.replace("Chapter", "ch").replace(".pdf", ""), p)
        pix.save(os.path.join(OUT, name))
        print(name, pix.width, pix.height)
