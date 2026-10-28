// Batch-render LaTeX with KaTeX: node katex_render.js in.json out.json
// in.json  = [{"tex": "...", "display": true|false}, ...]
// out.json = ["<span class=\"katex\">...</span>", ...]   (HTML only, no MathML copy)
const fs = require('fs');
const katex = require('C:/Code/UST/COMP3511/_work/midterm/katex_pkg/node_modules/katex');

const items = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const errors = [];
const out = items.map((it, i) => {
  try {
    return katex.renderToString(it.tex, {
      displayMode: !!it.display, output: 'html', throwOnError: true, strict: 'ignore',
    });
  } catch (e) {
    errors.push(`#${i}: ${e.message}  <<${it.tex}>>`);
    return katex.renderToString(it.tex, { displayMode: !!it.display, output: 'html', throwOnError: false });
  }
});
fs.writeFileSync(process.argv[3], JSON.stringify(out));
if (errors.length) { console.error('KaTeX errors:\n' + errors.join('\n')); process.exitCode = 2; }
console.log(`rendered ${items.length} formulas`);
