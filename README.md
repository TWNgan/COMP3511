# COMP3511 Midterm OP Notes (HKUST, Fall 2026)

Personal revision pack for HKUST COMP3511 Operating Systems — midterm on 29 Oct 2026, Chapters 1–6
(up to Synchronization Tools). Explanations in Traditional Chinese (Hong Kong); keywords and
exam-ready model answers in English.

**Live site: https://twngan.github.io/COMP3511/**

| What | Where |
|---|---|
| Study website — chapter notes, Labs & PA1/PA2 notes, answer bank, search, MC quiz, past-paper bank, CPU-scheduling simulator, calculators | [`Midterm_Site/`](Midterm_Site/index.html) |
| Printable cheat book — 176 pages (part H = how-to guide), A4, LaTeX-rendered formulas, print double-sided (flip on long edge); part X = 313 predicted questions with copy-ready answers, True/False verdicts and 19 compile-tested C programs | [`COMP3511_Midterm_CheatBook.pdf`](COMP3511_Midterm_CheatBook.pdf) |
| Source notes (Markdown) | [`Midterm_Notes/`](Midterm_Notes/) |
| Build and verification scripts | [`_work/midterm/scripts/`](_work/midterm/scripts/) |

Every fork() count, Gantt chart and synchronization answer from the past papers was checked by running
real C programs or the scheduling simulator against the official solutions.

## Rebuild

Needs Python 3.9+ with `mistune` 3 and `PyMuPDF`, Node.js with KaTeX (formulas are pre-rendered at
build time), plus Google Chrome for the PDF. The scripts use absolute paths for the author's machine
(`C:\Code\UST\COMP3511`).

```bash
npm install --prefix _work/midterm/katex_pkg katex@0.16          # once
python -I _work/midterm/scripts/build_site.py        # Midterm_Notes/*.md -> Midterm_Site/
python -I _work/midterm/scripts/build_cheatbook.py   # -> COMP3511_Midterm_CheatBook.pdf / .html
node _work/midterm/scripts/test_sched.js             # scheduling simulator tests
```

## Publish an update

GitHub Pages serves the `gh-pages` branch, so push both branches:

```bash
git add -A && git commit -m "Update notes" && git push origin main main:gh-pages
```

---
Unofficial student notes. Slide figures and quoted past-paper questions belong to their authors
(HKUST COMP3511 teaching team; Silberschatz, Galvin & Gagne, *Operating System Concepts*, 10th ed.).
