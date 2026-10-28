import sys, os, site
sys.path.append(site.getusersitepackages())
import fitz
# usage: render.py pdf out_dir zoom page1 [page2 ...]  (1-based pages)
pdf, out_dir, zoom = sys.argv[1], sys.argv[2], float(sys.argv[3])
doc = fitz.open(pdf)
name = os.path.splitext(os.path.basename(pdf))[0]
for p in sys.argv[4:]:
    page = doc[int(p) - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    out = os.path.join(out_dir, f"{name}_p{p}.png")
    pix.save(out)
    print(out)
