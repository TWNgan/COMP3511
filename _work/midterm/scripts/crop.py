import sys, os, site
sys.path.append(site.getusersitepackages())
import fitz
# usage: crop.py pdf page(1-based) zoom x0 y0 x1 y1 (fractions of page) out.png
pdf, p, zoom = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
fx0, fy0, fx1, fy1 = map(float, sys.argv[4:8])
out = sys.argv[8]
doc = fitz.open(pdf)
page = doc[p - 1]
r = page.rect
clip = fitz.Rect(r.x0 + fx0 * r.width, r.y0 + fy0 * r.height, r.x0 + fx1 * r.width, r.y0 + fy1 * r.height)
pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip)
pix.save(out)
print(out, pix.width, pix.height)
