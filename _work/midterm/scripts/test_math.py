"""Check mistune's math plugins on the syntax the notes will use."""
import site
import sys

sys.path.append(site.getusersitepackages())
sys.stdout.reconfigure(encoding="utf-8")
import mistune  # noqa: E402

R = mistune.HTMLRenderer(escape=False)
md = mistune.create_markdown(renderer=R, plugins=["table", "strikethrough", "math",
                                                  "mistune.plugins.math.math_in_quote",
                                                  "mistune.plugins.math.math_in_list"])
R.register("block_math", lambda r, text: "<DISPLAY[%s]>\n" % text)
R.register("inline_math", lambda r, text: "<INLINE[%s]>" % text)
sample = r"""
Inline $T_{\text{hit}}$ and **bold $2^{n+1}-1$** text, cost $5 no-math.

> 🧮 **AMAT**
>
> $$
> \text{AMAT} = h \cdot T_{\text{hit}} + (1-h)\,T_{\text{miss}}
> $$

- item with $\tau_{n+1} = \alpha t_n + (1-\alpha)\tau_n$
  - nested $\frac{1}{S+\frac{1-S}{N}}$

| A | B |
|---|---|
| speedup | $\dfrac{1}{S + \frac{1-S}{N}}$ |

$$
U = \sum_i \frac{t_i}{p_i}
$$
"""
print(md(sample))
