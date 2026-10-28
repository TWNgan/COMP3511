"""Convert plain-text/Unicode formulas in the notes to LaTeX ($...$ inline, $$...$$ display).
Each (old, new) must match exactly once unless marked with count=None (replace all)."""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
N = r"C:\Code\UST\COMP3511\Midterm_Notes"

R = {}
R["ch1_introduction.md"] = [
    ("- **KB = 1,024 bytes；MB = 1,024² bytes；GB = 1,024³；TB = 1,024⁴；PB = 1,024⁵**。",
     r"- **KB = $2^{10}$ = 1,024 bytes；MB = $1024^{2}$ bytes；GB = $1024^{3}$；TB = $1024^{4}$；PB = $1024^{5}$**。"),
    ("""> 🧮 **Average Access Time = (Hit Ratio × Hit Time) + (Miss Ratio × Miss Time)**
- Miss Ratio = 1 − Hit Ratio。
- **HW1 例**：hit ratio 90%、hit time 2 ns、miss time 50 ns → 0.9×2 + 0.1×50 = 1.8 + 5 = **6.8 ns**。
- 如果題目畀 **miss penalty**（額外時間）而唔係 miss time：Miss Time = Hit Time + Miss Penalty → AMAT = Hit Time + Miss Ratio × Miss Penalty（兩條公式結果一樣）。""",
     r"""> 🧮 **Average Access Time（AMAT）**
>
> $$
> \text{AMAT} = (\text{Hit Ratio} \times \text{Hit Time}) + (\text{Miss Ratio} \times \text{Miss Time})
> $$

- $\text{Miss Ratio} = 1 - \text{Hit Ratio}$。
- **HW1 例**：hit ratio 90%、hit time 2 ns、miss time 50 ns → $0.9 \times 2 + 0.1 \times 50 = 1.8 + 5 =$ **6.8 ns**。
- 如果題目畀 **miss penalty**（額外時間）而唔係 miss time：$T_{\text{miss}} = T_{\text{hit}} + \text{penalty}$ → $\text{AMAT} = T_{\text{hit}} + (1-h) \times \text{penalty}$（兩條公式結果一樣）。"""),
]

R["ch4_threads.md"] = [
    ("""> 🧮 **speedup ≤ 1 / ( S + (1 − S) / N )**
- **S = serial portion，1 − S = parallel portion，N = number of processing cores**。
- **As N → ∞, speedup → 1/S.**""",
     r"""> 🧮 **Amdahl's Law**
>
> $$
> \text{speedup} \le \frac{1}{S + \dfrac{1-S}{N}}, \qquad \lim_{N \to \infty} \text{speedup} = \frac{1}{S}
> $$

- **S = serial portion，$1 - S$ = parallel portion，N = number of processing cores**。
- **As $N \to \infty$, speedup → $1/S$.**"""),
    ("| 1/(0.25 + 0.75/2) = 1/0.625 |", r"| $\frac{1}{0.25 + 0.75/2} = \frac{1}{0.625}$ |"),
    ("| 1/(0.3 + 0.7/7) = 1/0.4 |", r"| $\frac{1}{0.3 + 0.7/7} = \frac{1}{0.4}$ |"),
    ("| 1/(0.2 + 0.8/4) = 1/0.4 |", r"| $\frac{1}{0.2 + 0.8/4} = \frac{1}{0.4}$ |"),
    ("| HW2 Q3.1(b) | 0.2 | ∞ | 1/S = 1/0.2 |", r"| HW2 Q3.1(b) | 0.2 | $\infty$ | $\frac{1}{S} = \frac{1}{0.2}$ |"),
    ("| 1/(0.19 + 0.27) = 1/0.46 |", r"| $\frac{1}{0.19 + 0.81/3} = \frac{1}{0.46}$ |"),
    ("| 1/(0.19 + 0.162) = 1/0.352 |", r"| $\frac{1}{0.19 + 0.81/5} = \frac{1}{0.352}$ |"),
    ("| 1/(0.39 + 0.2033) = 1/0.5933 |", r"| $\frac{1}{0.39 + 0.61/3} = \frac{1}{0.5933}$ |"),
    ("| 1/(0.39 + 0.122) = 1/0.512 |", r"| $\frac{1}{0.39 + 0.61/5} = \frac{1}{0.512}$ |"),
    ("""- 反向題：要 speedup = X with N cores → 解 S：**S = (1/X − 1/N) / (1 − 1/N)**。
- 例：想 4 cores 有 3× speedup → S = (1/3 − 1/4)/(1 − 1/4) = (1/12)/(3/4) = **1/9 ≈ 11.1% serial**。
- Speedup 上限永遠 **≤ N** 同 **≤ 1/S**。""",
     r"""- 反向題：要 speedup = X with N cores → 解 S：$S = \dfrac{1/X - 1/N}{1 - 1/N}$。
- 例：想 4 cores 有 3× speedup → $S = \dfrac{1/3 - 1/4}{1 - 1/4} = \dfrac{1/12}{3/4} = \dfrac{1}{9}$ ≈ **11.1% serial**。
- Speedup 上限永遠 **$\le N$** 同 **$\le 1/S$**。"""),
    ("| As N→∞, Amdahl speedup → 1/S | ✅ |", r"| As $N \to \infty$, Amdahl speedup → $1/S$ | ✅ |"),
    ("（1/(0.5+0.125) = **1.6**）；無限 cores？（**2**）", r"（$\frac{1}{0.5 + 0.5/4} = \frac{1}{0.625}$ = **1.6**）；無限 cores？（$1/S$ = **2**）"),
]

R["ch5_cpu_scheduling.md"] = [
    ("""> 🧮 **Turnaround = Completion − Arrival**
>
> 🧮 **Waiting = Turnaround − CPU burst**
>
> 🧮 **Response = (completion of the FIRST run) − Arrival**
""",
     r"""> 🧮 **Metrics（本科 convention）**
>
> $$
> \begin{aligned}
> \text{Turnaround} &= \text{Completion} - \text{Arrival} \\
> \text{Waiting} &= \text{Turnaround} - \text{CPU burst} \\
> \text{Response} &= (\text{end of the FIRST run}) - \text{Arrival}
> \end{aligned}
> $$

"""),
    ("**WT = 0, 24, 27 → avg 17；TAT avg = (24+27+30)/3 = 27**",
     r"**WT = 0, 24, 27 → avg 17；TAT avg** $= \frac{24+27+30}{3} = 27$"),
    ("**WT：P1 = 6, P2 = 4, P3 = 7 → avg 5.67；TAT avg = (30+7+10)/3 = 15.67；RT = 4, 7, 10 → avg 7**",
     r"**WT：P1 = 6, P2 = 4, P3 = 7 → avg 5.67；TAT avg** $= \frac{30+7+10}{3} = 15.67$**；RT = 4, 7, 10 → avg 7**"),
    ("**avg WT = (3 + 16 + 9 + 0)/4 = 7**（slide 答案）", r"**avg WT** $= \frac{3 + 16 + 9 + 0}{4} = 7$（slide 答案）"),
    ("**avg WT = [(10−1) + (1−1) + (17−2) + (5−3)]/4 = 26/4 = 6.5**",
     r"**avg WT** $= \frac{(10-1) + (1-1) + (17-2) + (5-3)}{4} = \frac{26}{4} = 6.5$"),
    ("""> 🧮 **τ(n+1) = α · t(n) + (1 − α) · τ(n)**，0 ≤ α ≤ 1
- **tₙ = actual length of the n-th CPU burst；τₙ₊₁ = predicted value for the next burst**；通常 **α = ½**。
- **α = 0 → τₙ₊₁ = τₙ（recent history does not count）；α = 1 → τₙ₊₁ = tₙ（only the last burst counts）。**
- 展開：**τₙ₊₁ = α tₙ + (1−α) α tₙ₋₁ + … + (1−α)ʲ α tₙ₋ⱼ + … + (1−α)ⁿ⁺¹ τ₀** → **all past values count but recent ones weigh more；past effect diminishes exponentially**（α=0.5，10 rounds 後 (1/2)¹⁰ = 1/1024 可忽略）。
- 預測取決於 **(1) all previous actual bursts with different weights, (2) the initial estimate τ₀**。
- Slide 5.20 例（α = ½, τ₀ = 10）：""",
     r"""> 🧮 **Exponential averaging**
>
> $$
> \tau_{n+1} = \alpha\, t_n + (1-\alpha)\,\tau_n, \qquad 0 \le \alpha \le 1
> $$

- **$t_n$ = actual length of the n-th CPU burst；$\tau_{n+1}$ = predicted value for the next burst**；通常 **$\alpha = \tfrac{1}{2}$**。
- **$\alpha = 0 \Rightarrow \tau_{n+1} = \tau_n$（recent history does not count）；$\alpha = 1 \Rightarrow \tau_{n+1} = t_n$（only the last burst counts）。**
- 展開 → **all past values count but recent ones weigh more；past effect diminishes exponentially**：

$$
\tau_{n+1} = \alpha t_n + (1-\alpha)\alpha\, t_{n-1} + \cdots + (1-\alpha)^{j}\alpha\, t_{n-j} + \cdots + (1-\alpha)^{n+1}\tau_0
$$

- 例：$\alpha = 0.5$，10 rounds 後 $(1/2)^{10} = 1/1024$ → 可忽略。
- 預測取決於 **(1) all previous actual bursts with different weights, (2) the initial estimate $\tau_0$**。
- Slide 5.20 例（$\alpha = \tfrac{1}{2}$, $\tau_0 = 10$）："""),
    ("| CPU burst tᵢ |", r"| CPU burst $t_i$ |"),
    ("| guess τᵢ |", r"| guess $\tau_i$ |"),
    ("- **HW2 MC9**：τ = 10, t = 6, α = 0.25 → 0.25×6 + 0.75×10 = 1.5 + 7.5 = **9 ms**。",
     r"- **HW2 MC9**：$\tau_n = 10,\ t_n = 6,\ \alpha = 0.25 \Rightarrow \tau_{n+1} = 0.25 \times 6 + 0.75 \times 10 = 1.5 + 7.5 =$ **9 ms**。"),
    ("**avg WT = (6+0+16+18+1)/5 = 8.2**", r"**avg WT** $= \frac{6+0+16+18+1}{5} = 8.2$"),
    ("- **Gets q₀ in Q0；if not finished → moved to Q1.** **In Q1 gets q₁ additional；if still not complete → preempted and moved to Q2.**",
     r"- **Gets $q_0$ in Q0；if not finished → moved to Q1.** **In Q1 gets $q_1$ additional；if still not complete → preempted and moved to Q2.**"),
    ("- **Burst ≤ q₀ + q₁（e.g. 4 + 8 = 12）嘅 job 永遠唔會落 Q2。**", r"- **Burst $\le q_0 + q_1$（e.g. 4 + 8 = 12）嘅 job 永遠唔會落 Q2。**"),
    ("**WT：P1 = 14, P2 = 28, P3 = 3, P4 = 21, P5 = 18 → avg = 84/5 = 16.8** ✅",
     r"**WT：P1 = 14, P2 = 28, P3 = 3, P4 = 21, P5 = 18 → avg** $= \frac{84}{5} = 16.8$ ✅"),
    ("- 參數：**processing time t, deadline d, period p，0 ≤ t ≤ d ≤ p**；**rate = 1/p**。",
     r"- 參數：**processing time $t$, deadline $d$, period $p$，$0 \le t \le d \le p$**；**rate = $1/p$**。"),
    ("- **CPU utilization of task i = tᵢ / pᵢ；total U = Σ tᵢ/pᵢ**（U > 1 → 一定有 miss）。",
     r"""- **CPU utilization of task $i$ = $t_i / p_i$**；total（$U > 1$ → 一定有 miss）：

$$
U = \sum_{i} \frac{t_i}{p_i}
$$
"""),
    ("**RM guaranteed if U ≤ N(2^{1/N} − 1)**：N=1 → 1；**N=2 → 0.828**；N=3 → 0.780；N=4 → 0.757；N→∞ → ln 2 ≈ 0.693。",
     r"**RM guaranteed if** $U \le N\left(2^{1/N} - 1\right)$：N=1 → 1；**N=2 → 0.828**；N=3 → 0.780；N=4 → 0.757；$N \to \infty \Rightarrow \ln 2 \approx 0.693$。"),
    ("6. 先計 U = Σt/p 做 sanity check。", r"6. 先計 $U = \sum_i t_i/p_i$ 做 sanity check。"),
    ("- ⭐ **Little's Formula：n = λ × W**（**n = average queue length, λ = average arrival rate, W = average waiting time in queue**）",
     r"- ⭐ **Little's Formula：$n = \lambda \times W$**（**$n$ = average queue length, $\lambda$ = average arrival rate, $W$ = average waiting time in queue**）"),
    ("  - 例：λ = 7/s，n = 14 → **W = 2 s**；**HW2 MC10**：λ = 3/s，n = 12 → **W = 4 s**。",
     r"  - 例：$\lambda = 7/\text{s},\ n = 14 \Rightarrow W = n/\lambda =$ **2 s**；**HW2 MC10**：$\lambda = 3/\text{s},\ n = 12 \Rightarrow W = 12/3 =$ **4 s**。"),
    ("7. **Average**：寫出 **(a+b+…)/n = x**（S26：140/6 = 23.33）。", r"7. **Average**：寫出 $\dfrac{a+b+\cdots}{n} = x$（S26：$\frac{140}{6} = 23.33$）。"),
    ("→ **avg = 140/6 = 23.33**", r"→ **avg** $= \frac{140}{6} = 23.33$"),
    ("→ **avg = 28/6 = 4.67**", r"→ **avg** $= \frac{28}{6} = 4.67$"),
    ("→ **avg = 23/6 = 3.83**", r"→ **avg** $= \frac{23}{6} = 3.83$"),
    ("- (a) α = 0, β = 3（", r"- (a) $\alpha = 0,\ \beta = 3$（"),
    ("- (b) α = 1, β = 0，", r"- (b) $\alpha = 1,\ \beta = 0$，"),
    ("- (c) α = 1, β = −2，", r"- (c) $\alpha = 1,\ \beta = -2$，"),
    ("### 14.3 S26 Q2.3 自訂 policy（fᵢ = 1/(a·cᵢ + b)，揀 fᵢ 最大）\n",
     "### 14.3 S26 Q2.3 自訂 policy（揀 fᵢ 最大）\n\n$$\nf_i = \\frac{1}{a\\,c_i + b} \\qquad (a, b > 0)\n$$\n\n"),
    ("small average CPU bursts cᵢ → larger fᵢ → higher priority.", r"small average CPU bursts $c_i$ → larger $f_i$ → higher priority."),
    ("(large cᵢ, low fᵢ)", r"(large $c_i$, low $f_i$)"),
    ("| Little's formula n = λW only for FCFS |", r"| Little's formula $n = \lambda W$ only for FCFS |"),
    ("3. α = 0.5，τ₀ = 10，bursts 6, 4 → τ₂？（τ₁ = 8；τ₂ = 6）", r"3. $\alpha = 0.5,\ \tau_0 = 10$，bursts 6, 4 → $\tau_2$？（$\tau_1 = 8$；$\tau_2 = 6$）"),
]

R["ch3_processes.md"] = [
    ("3. **n 句連續 fork()（無條件）→ 2ⁿ processes。**", r"3. **n 句連續 fork()（無條件）→ $2^n$ processes。**"),
    ("| `fork();` | 2 | **2ⁿ** |", r"| `fork();` | 2 | **$2^n$** |"),
    ("| 4 | **4ⁿ**（slide：10 次 → 4¹⁰） |", r"| 4 | **$4^n$**（slide：10 次 → $4^{10}$） |"),
    ("| 3（parent 再 fork 一次） | **3ⁿ**（slide：3¹⁰） |", r"| 3（parent 再 fork 一次） | **$3^n$**（slide：$3^{10}$） |"),
    ("| 3（child 再 fork） | **3ⁿ**（n=3 → **27**） |", r"| 3（child 再 fork） | **$3^n$**（n=3 → **27**） |"),
    ("`fork() \\|\\| fork()` | 3 | 3ⁿ |", "`fork() \\|\\| fork()` | 3 | $3^n$ |"),
    ("""- **A_k = 2^k**（iteration k 開始前 active 數）；每 iteration 新增 2^k 個 break。
- **Total processes = 2ⁿ (active) + (2ⁿ − 1) (stopped) = 2ⁿ⁺¹ − 1**；**break 次數 = 2ⁿ − 1**。""",
     r"""- **$A_k = 2^k$**（iteration k 開始前 active 數）；每 iteration 新增 $2^k$ 個 break。
- **Total processes** $= \underbrace{2^n}_{\text{active}} + \underbrace{(2^n - 1)}_{\text{stopped}} = 2^{n+1} - 1$；**break 次數** $= 2^n - 1$。"""),
    ("→ **3⁵ = 243**（包括 child 自己）。", r"→ **$3^5 = 243$**（包括 child 自己）。"),
    ("→ **(3⁵ + 1) × 2 = 488** ✅", r"→ **$(3^5 + 1) \times 2 = 488$** ✅"),
    ("- 同上：child branch 變 3ⁿ，加 parent → 3ⁿ + 1，最後 fork ×2 → **\"a\" 數 = 2(3ⁿ + 1)** ✅",
     r"- 同上：child branch 變 $3^n$，加 parent → $3^n + 1$，最後 fork ×2 → **\"a\" 數** $= 2(3^n + 1)$ ✅"),
    ("- 第 i 次 iteration（由 1 數）有 2^i 個 process 各印一行 → **2 + 4 + … + 2ⁿ = 2ⁿ⁺¹ − 2** ✅",
     r"- 第 i 次 iteration（由 1 數）有 $2^i$ 個 process 各印一行 → $2 + 4 + \cdots + 2^n = \sum_{i=1}^{n} 2^i = 2^{n+1} - 2$ ✅"),
    ("Q3.1 fork tree（7 / 3 / 2ⁿ⁺¹−1）", r"Q3.1 fork tree（7 / 3 / $2^{n+1}-1$）"),
    ("Q2.6（2ⁿ⁺¹−2）", r"Q2.6（$2^{n+1}-2$）"),
    ("Q3.2（2(3ⁿ+1)）", r"Q3.2（$2(3^n+1)$）"),
]

R["ch6_synchronization.md"] = [("Pᵢ", "$P_i$", None), ("Pⱼ", "$P_j$", None)]

R["cb_essentials.md"] = [
    ("| **AMAT = h × T_hit + (1 − h) × T_miss**（若畀 penalty：T_miss = T_hit + penalty） | 0.9×2 + 0.1×50 = **6.8 ns** |",
     r"| $\text{AMAT} = h\,T_{\text{hit}} + (1-h)\,T_{\text{miss}}$（若畀 penalty：$T_{\text{miss}} = T_{\text{hit}} + \text{penalty}$） | $0.9 \times 2 + 0.1 \times 50 =$ **6.8 ns** |"),
    ("| **speedup ≤ 1 / (S + (1 − S)/N)**；N→∞：**1/S**；S = **serial** | S=0.25, N=2 → **1.6** |",
     r"| $\text{speedup} \le \dfrac{1}{S + \frac{1-S}{N}}$；$N \to \infty$：$\dfrac{1}{S}$；$S$ = **serial** | $S = 0.25,\ N = 2 \Rightarrow$ **1.6** |"),
    ("| **S = (1/X − 1/N) / (1 − 1/N)** | X=3, N=4 → S = 1/9 |", r"| $S = \dfrac{1/X - 1/N}{1 - 1/N}$ | $X = 3,\ N = 4 \Rightarrow S = \tfrac{1}{9}$ |"),
    ("| **TAT = completion − arrival** |", r"| $\text{TAT} = C - A$（completion − arrival） |"),
    ("| **WT = TAT − burst**（= Gantt 上嘅 gaps 總和） |", r"| $\text{WT} = \text{TAT} - \text{burst}$（= Gantt 上嘅 gaps 總和） |"),
    ("| **RT = end of FIRST run − arrival**（", r"| $\text{RT} = (\text{end of FIRST run}) - A$（"),
    ("| **τ(n+1) = α·t(n) + (1 − α)·τ(n)** | α=.25, t=6, τ=10 → **9** |",
     r"| $\tau_{n+1} = \alpha\, t_n + (1-\alpha)\,\tau_n$ | $\alpha = .25,\ t_n = 6,\ \tau_n = 10 \Rightarrow$ **9** |"),
    ("| **n = λ × W** | λ=3/s, n=12 → **W=4 s** |", r"| $n = \lambda \times W$ | $\lambda = 3/\text{s},\ n = 12 \Rightarrow W =$ **4 s** |"),
    ("| 冇 process 等多過 **(n − 1)·q** |", r"| 冇 process 等多過 $(n-1)\,q$ |"),
    ("| **U = Σ tᵢ / pᵢ**；**U > 1 ⇒ 一定 miss** | 25/50 + 35/80 = 0.94 |",
     r"| $U = \sum_i \dfrac{t_i}{p_i}$；**$U > 1 \Rightarrow$ 一定 miss** | $\frac{25}{50} + \frac{35}{80} = 0.94$ |"),
    ("| 保證可排：**U ≤ N(2^{1/N} − 1)**：N=1 1.000、2 0.828、3 0.780、4 0.757、5 0.743、∞ 0.693 |",
     r"| 保證可排：$U \le N\left(2^{1/N} - 1\right)$：N=1 1.000、2 0.828、3 0.780、4 0.757、5 0.743、$\infty$ 0.693 |"),
    ("| U ≤ 1（D = T 時）理論上可排 |", r"| $U \le 1$（$D = T$ 時）理論上可排 |"),
    ("| n 個無條件 fork → **2ⁿ**；`if(fork()) fork();` 每輪 ×3 |", r"| n 個無條件 fork → $2^n$；`if(fork()) fork();` 每輪 ×3 → $3^n$ |"),
    ("| value < 0 ⇒ **\\|value\\| = 等緊嘅 processes 數** |", r"| $\text{value} < 0 \Rightarrow \lvert \text{value} \rvert$ = 等緊嘅 processes 數 |"),
    ("| KB = 1024 B；MB = 1024²；GB = 1024³；networks 用 **bits** |", r"| KB $= 2^{10}$ B；MB $= 2^{20}$；GB $= 2^{30}$；networks 用 **bits** |"),
]

R["cb_playbooks.md"] = [
    ("| **2ⁿ⁺¹ − 1** processes, **2ⁿ − 1** breaks（n=2：7, 3） |", r"| **$2^{n+1} - 1$** processes, **$2^n - 1$** breaks（n=2：7, 3） |"),
    ("| **2(3ⁿ + 1)** |", r"| **$2(3^n + 1)$** |"),
    ("| **(3⁵ + 1)×2 = 488** |", r"| **$(3^5 + 1) \times 2 = 488$** |"),
    ("| **2ⁿ⁺¹ − 2** lines |", r"| **$2^{n+1} - 2$** lines |"),
    ("| **4¹⁰ = 1,048,576** |", r"| **$4^{10} = 1{,}048{,}576$** |"),
    ("| **3¹⁰ = 59,049** |", r"| **$3^{10} = 59{,}049$** |"),
    ("(8) 檢查：最後完成時間 = Σburst + idle。", r"(8) 檢查：最後完成時間 $= \sum \text{burst} + \text{idle}$。"),
    ("| 計 init + α·waited + β·ran |", r"| 計 $\text{init} + \alpha \cdot \text{waited} + \beta \cdot \text{ran}$ |"),
    ("task i 喺 0, pᵢ, 2pᵢ… release；deadline = release + dᵢ。", r"task $i$ 喺 $0, p_i, 2p_i, \ldots$ release；deadline $=$ release $+\ d_i$。"),
    ("**Amdahl speedup = 1/(S + (1−S)/N)**（S = serial fraction；parallel = 1 − S）",
     r"**Amdahl speedup** $= \dfrac{1}{S + (1-S)/N}$（$S$ = serial fraction；parallel $= 1 - S$）"),
    ("**RM utilization bound N(2^{1/N} − 1)**", r"**RM utilization bound** $N\left(2^{1/N} - 1\right)$"),
    ("**Exponential averaging（α = ½）權重**：tₙ ½、tₙ₋₁ ¼、tₙ₋₂ ⅛、tₙ₋₃ 1/16、… τ₀ (½)ⁿ⁺¹。α = 0.25：tₙ 0.25、tₙ₋₁ 0.1875、tₙ₋₂ 0.1406、… τ 權重 0.75ⁿ⁺¹。",
     r"**Exponential averaging（$\alpha = \tfrac{1}{2}$）權重**：$t_n$ ½、$t_{n-1}$ ¼、$t_{n-2}$ ⅛、$t_{n-3}$ 1/16、… $\tau_0$ 權重 $(\tfrac{1}{2})^{n+1}$。$\alpha = 0.25$：$t_n$ 0.25、$t_{n-1}$ 0.1875、$t_{n-2}$ 0.1406、… $\tau_0$ 權重 $0.75^{n+1}$。"),
]

R["glossary.md"] = [
    ("| speedup ≤ 1 / (S + (1−S)/N); as N→∞, speedup → 1/S |", r"| $\text{speedup} \le \frac{1}{S + (1-S)/N}$; as $N \to \infty$, speedup $\to 1/S$ |"),
    ("| τ(n+1) = α t(n) + (1−α) τ(n): predicts the next CPU burst |", r"| $\tau_{n+1} = \alpha t_n + (1-\alpha)\tau_n$: predicts the next CPU burst |"),
    ("| n = λ × W (queue length = arrival rate × waiting time) |", r"| $n = \lambda \times W$ (queue length = arrival rate × waiting time) |"),
]

R["qb1_mc_bank.md"] = [
    ("解：speedup = 1/(S + (1−S)/N)。A：1/(0.19+0.27) = 2.17；B：2.84；**C：1/(0.39+0.2033) = 1.69**；D：1.95。",
     r"解：$\text{speedup} = \frac{1}{S + (1-S)/N}$。A：$\frac{1}{0.19 + 0.27} = 2.17$；B：2.84；**C：$\frac{1}{0.39 + 0.2033} = 1.69$**；D：1.95。"),
    ("解：1/(0.3 + 0.7/7) = 1/0.4 = **2.5**。", r"解：$\frac{1}{0.3 + 0.7/7} = \frac{1}{0.4} =$ **2.5**。"),
    ("→ **3³ = 27** ✅", r"→ **$3^3 = 27$** ✅"),
    ("the actual burst is 6 ms, α = 0.25.", r"the actual burst is 6 ms, $\alpha = 0.25$."),
    ("解：0.25 × 6 + 0.75 × 10 = **9**。", r"解：$\tau_{n+1} = 0.25 \times 6 + 0.75 \times 10 =$ **9**。"),
    ("解：W = n / λ = 12 / 3 = **4 s** [5.57]。", r"解：$W = n/\lambda = 12/3 =$ **4 s** [5.57]。"),
]

R["qb2_long_bank.md"] = [
    ("The OS keeps cᵢ = average past CPU burst of Pᵢ and picks the process with the highest fᵢ = 1/(a·cᵢ + b) (a, b > 0),",
     r"The OS keeps $c_i$ = average past CPU burst of $P_i$ and picks the process with the highest $f_i = \dfrac{1}{a\,c_i + b}$ ($a, b > 0$),"),
    ("small CPU bursts cᵢ, hence a larger fᵢ and higher priority.", r"small CPU bursts $c_i$, hence a larger $f_i$ and higher priority."),
    ("(large cᵢ, low fᵢ)", r"(large $c_i$, low $f_i$)"),
    ("active count doubles: Aₖ = 2ᵏ. After n iterations: active = 2ⁿ, stopped = 1 + 2 + … + 2ⁿ⁻¹ = 2ⁿ − 1. **Total = 2ⁿ⁺¹ − 1** (breaks = 2ⁿ − 1).",
     r"active count doubles: $A_k = 2^k$. After $n$ iterations: active $= 2^n$, stopped $= 1 + 2 + \cdots + 2^{n-1} = 2^n - 1$. **Total** $= 2^{n+1} - 1$ (breaks $= 2^n - 1$)."),
    ("waiting changes priority at rate α, running at rate β;", r"waiting changes priority at rate $\alpha$, running at rate $\beta$;"),
    ("- (a) α = 0, β = 3, initial 0:", r"- (a) $\alpha = 0,\ \beta = 3$, initial 0:"),
    ("- (b) α = 1, β = 0, only P1, P2,", r"- (b) $\alpha = 1,\ \beta = 0$, only P1, P2,"),
    ("- (c) α = 1, β = −2, initial 30,", r"- (c) $\alpha = 1,\ \beta = -2$, initial 30,"),
    ("iteration i prints 2ⁱ lines → total **2 + 4 + … + 2ⁿ = 2ⁿ⁺¹ − 2** ✅", r"iteration $i$ prints $2^i$ lines → total $2 + 4 + \cdots + 2^n = 2^{n+1} - 2$ ✅"),
    ("every process becomes 3 → 3ⁿ processes from the child branch. Plus the original → 3ⁿ + 1. The final fork doubles → **2(3ⁿ + 1) \"a\"s** ✅",
     r"every process becomes 3 → $3^n$ processes from the child branch. Plus the original → $3^n + 1$. The final fork doubles → **$2(3^n + 1)$ \"a\"s** ✅"),
    ("**(3⁵ + 1) × 2 = 488** ✅", r"**$(3^5 + 1) \times 2 = 488$** ✅"),
    ("(a) 1/(0.2 + 0.8/4) = **2.5**. (b) N → ∞: 1/0.2 = **5**.", r"(a) $\dfrac{1}{0.2 + 0.8/4} =$ **2.5**. (b) $N \to \infty$: $\dfrac{1}{0.2} =$ **5**."),
    ("0.9 × 2 + 0.1 × 50 = **6.8 ns**.", r"$0.9 \times 2 + 0.1 \times 50 =$ **6.8 ns**."),
    ("→ **avg = 140/6 = 23.33**.", r"→ **avg** $= \frac{140}{6} = 23.33$."),
    ("→ **avg = 28/6 = 4.67**", r"→ **avg** $= \frac{28}{6} = 4.67$"),
]

R["qb3_practice_mc.md"] = [
    ("解：1/S = 1/0.5 = **2**。", r"解：$1/S = 1/0.5 =$ **2**。"),
    ("With exponential averaging, if α = 0 then:", r"With exponential averaging, if $\alpha = 0$ then:"),
    ("解：τ(n+1) = τ(n) [5.22]。", r"解：$\tau_{n+1} = \tau_n$ [5.22]。"),
    ("解：0.95 × 1 + 0.05 × 100 = 0.95 + 5 = **5.95 ns**。", r"解：$0.95 \times 1 + 0.05 \times 100 = 0.95 + 5 =$ **5.95 ns**。"),
]

errors = 0
for fname, pairs in R.items():
    path = os.path.join(N, fname)
    s = io.open(path, encoding="utf-8").read()
    for item in pairs:
        old, new = item[0], item[1]
        allow_many = len(item) > 2 and item[2] is None
        c = s.count(old)
        if c == 0:
            if new in s:
                continue  # already converted
            print("NOT FOUND:", fname, "::", old[:70])
            errors += 1
            continue
        if c > 1 and not allow_many:
            print("AMBIGUOUS (%d):" % c, fname, "::", old[:70])
            errors += 1
            continue
        s = s.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
print("done, problems:", errors)
