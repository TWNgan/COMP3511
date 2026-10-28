"""Check internal links (page.html#anchor) across the generated site and the search index."""
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
SITE = r"C:\Code\UST\COMP3511\Midterm_Site"
ids, bad = {}, []
for f in glob.glob(os.path.join(SITE, "*.html")):
    h = io.open(f, encoding="utf-8").read()
    ids[os.path.basename(f)] = set(re.findall(r'\sid="([^"]+)"', h))
quiz = json.loads(re.sub(r"^window\.QUIZ = |;\s*$", "", io.open(os.path.join(SITE, "assets", "quiz-data.js"), encoding="utf-8").read()))
ids["quiz.html"] |= set(q["id"] for q in quiz)          # quiz items are rendered client-side
links = []
for f in glob.glob(os.path.join(SITE, "*.html")):
    h = io.open(f, encoding="utf-8").read()
    for href in re.findall(r'href="([^"]+)"', h):
        links.append((os.path.basename(f), href))
idx = json.loads(re.sub(r"^window\.SEARCH_INDEX = |;\s*$", "", io.open(os.path.join(SITE, "assets", "search-index.js"), encoding="utf-8").read()))
links += [("search-index", e["u"]) for e in idx]
for src, href in links:
    if href.startswith(("http", "mailto:", "#")) or href.startswith("../"):
        if href.startswith("../") and not os.path.exists(os.path.normpath(os.path.join(SITE, href.split("#")[0]))):
            bad.append((src, href, "missing file"))
        continue
    page, _, anchor = href.partition("#")
    page = page.split("?")[0]
    if page and page not in ids and not os.path.exists(os.path.join(SITE, page)):
        bad.append((src, href, "missing page"))
    elif anchor and anchor not in ids.get(page or src, set()):
        bad.append((src, href, "missing anchor"))
print("links checked:", len(links), "| broken:", len(bad))
for b in bad[:30]:
    print("  ", b)
