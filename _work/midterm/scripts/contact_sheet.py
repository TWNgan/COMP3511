"""Make contact sheets (grid of page thumbnails) for a PDF: contact_sheet.py in.pdf out_prefix cols rows"""
import site
import sys

sys.path.append(site.getusersitepackages())
import fitz  # noqa: E402

src, prefix = sys.argv[1], sys.argv[2]
cols, rows = int(sys.argv[3]), int(sys.argv[4])
doc = fitz.open(src)
W, H = doc[0].rect.width, doc[0].rect.height
per = cols * rows
for s in range(0, doc.page_count, per):
    out = fitz.open()
    page = out.new_page(width=W * cols / 2, height=H * rows / 2)
    for k in range(per):
        i = s + k
        if i >= doc.page_count:
            break
        c, r = k % cols, k // cols
        rect = fitz.Rect(c * W / 2, r * H / 2, (c + 1) * W / 2, (r + 1) * H / 2)
        page.show_pdf_page(rect, doc, i)
        page.draw_rect(rect, color=(0.6, 0.6, 0.6), width=0.5)
        page.insert_text((rect.x0 + 4, rect.y0 + 10), str(i + 1), fontsize=9, color=(1, 0, 0))
    pix = page.get_pixmap(matrix=fitz.Matrix(0.9, 0.9))
    name = "%s_%03d.png" % (prefix, s + 1)
    pix.save(name)
    print(name)
