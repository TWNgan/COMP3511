import sys, os, site
sys.path.append(site.getusersitepackages())
import fitz
out_dir = sys.argv[1]
for path in sys.argv[2:]:
    doc = fitz.open(path)
    name = os.path.splitext(os.path.basename(path))[0]
    chars = 0
    with open(os.path.join(out_dir, name + ".txt"), "w", encoding="utf-8") as f:
        for i, page in enumerate(doc):
            t = page.get_text()
            chars += len(t)
            f.write(f"\n===== PAGE {i+1} =====\n")
            f.write(t)
    print(f"{name}: {doc.page_count} pages, {chars} chars")
