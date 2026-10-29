# 攻略：fork / pipe 題點用 cheat book 攞分

> 🎯 **呢頁唔係教原理，係教你點「查書 → 照做 → 照寫」**。所有頁數 = 印出嚟嗰本 cheat book（{{pages}} 頁版）。見到 fork / pipe 題：**先認類型（§1）→ 翻指定頁 → 跟步驟 → 用「答卷寫法」寫**。

## 0. 入場前：貼 5 張 sticky notes

| 貼喺 | 頁 | 用嚟 |
|---|---|---|
| **P1 fork Playbook**（pattern 表 + 已驗證答案） | **{{p:P-p1-fork-playbook}}** | 數 process / 數 print 次數 |
| **P2 pipe / dup 填空表** | **{{p:P-p2-pipe-dup-exec-playbook}}** | pipe / dup2 / open 填空 |
| **P5 Powers 表**（$2^n$、$3^n$、$4^n$、$6^n$…） | **{{p:P-p5-pre-computed-tables}}** | 唔使計次方，直接查 |
| **Ch3 §9 fork 解題大法** | **{{p:3-s9}}** | break / 短路 / 輸出次序 / exec |
| **XC 完整 C programs** | **{{p:X-xc}}** | 「寫 program」題直接抄改 |

## 1. 先認類型（睇題目字眼，10 秒）

| 題目字眼 | 類型 | 跳去 |
|---|---|---|
| "How many processes are created / in total (including the parent)?"、"How many times is … printed?" | **A 數目** | §2 |
| "Draw the process tree" | **B Process tree** | §3 |
| "List all possible outputs"、"Which output is (not) possible?" | **C 輸出次序** | §4 |
| "If `exec()` succeeds / fails…"、"if `fork()` fails…" | **D exec / fail 情況** | §5 |
| Code 有 BLANK，周圍有 `pipe` / `dup` / `open` / `read` / `write` | **E pipe 填空** | §6 |
| "Write a program…"、"Complete the code so that…" | **F 寫 code** | §7 |
| fork 同 `pthread_create` 一齊出現 | **G fork + threads** | §8 |

## 2. 類型 A — 數 process / 數 print（最常見）

**步驟（全部係查表，唔使理解）**
1. 抄低 loop 入面嗰段 code（`for (i = 0; i < n; i++) { 呢度 }`）同 **n**。
2. 翻 **P1 Step 2 pattern 表（{{p:P-p1-fork-playbook}}）**：喺「每 iteration」一欄搵**一模一樣**嘅 code → 讀「n 次後」formula → 代 n。
3. 次方數唔使計：翻 **P5 Powers 表（{{p:P-p5-pre-computed-tables}}）**，行 = n，欄 = formula（$2^n$、$3^n$、$4^n$、$6^n$、$2^{n+1}-1$、$2(3^n+1)$、$(4^n-1)/3$ 都有）。
4. 表冇 → 翻 **P1 Step 3「其他已驗證答案」（{{p:P-p1-fork-playbook}}）** 同 **Ch3 §9.8（{{p:3-s9-8}}）**：好多係歷屆原題（S26、F19、F20、Sp21、F22、F24、S25、Lab），**一樣就直接抄答案**。
5. 仍然冇 → 用「**一輪法**」（純機械）：
   - 喺 rough paper 由 **1 個 process** 開始，**只做一個 iteration**：照 **Ch3 §9.1 規則（{{p:3-s9-1}}）** 逐句行（child 拎到 0；`A && B`：A 係 0 就唔做 B；`A || B`：A 非 0 就唔做 B）。
   - 數 **k = 做完一輪仲會繼續 loop 嘅 process 數**，同 **s = 停咗嘅**（`break` / `return` / `exit` / exec 成功）。
   - **s = 0**：答案 $= k^n$（查 P5）。
   - **s > 0**：翻 **Ch3 §9.3（{{p:3-s9-3}}）** 嗰個「active 追蹤表」，逐輪填 *iteration · active · 新增 · total*。
6. 問 **print 幾多次**：
   - `printf` 喺 **loop 之後** → 次數 = 行到嗰句嘅 process 數（通常 = total；`return` / `exit` 咗嘅唔計）。
   - `printf` 喺 **loop 入面** → 每輪「執行嗰句嘅 process 數」加埋（P1 Step 3 有 F19 Q2.6 嘅 $2^{n+1}-2$ 例）。

**答卷寫法（有 partial credit，S26 改法：tree 4 分 + 數目 1 分 + break 1 分）**
1. 一句規則：*"In each iteration every process becomes 3 processes: the parent, its child, and the child's child."*
2. 畫頭 1–2 個 iteration 嘅 tree（§3）。
3. 寫 formula（例如 $3^n$）再代數。
4. 最後答案寫清楚：*"Total = 27 processes (including the original parent); X is printed 27 times."*

> 📝 **示範**：`for (i = 0; i < 3; i++) if (fork() == 0) fork();` 之後 `printf("X\n");`，問 X 印幾多次。
> - 查 P1 表：row `if (fork() == 0) fork();` → 每 process ×3 → $3^n$。
> - 查 P5：$n = 3 \Rightarrow 3^3 = 27$。
> - `printf` 喺 loop 之後，每個 process 印一次 → **27**。
> - 寫：*"In each iteration, fork() returns 0 in the child, so only the child forks again: each process becomes 3. After 3 iterations: $3^3 = 27$ processes, so X is printed 27 times."* + 1 個 iteration 嘅 tree（P0 → C1 → C2）。

## 3. 類型 B — 畫 process tree

1. 翻 **P1 Step 4（{{t:Step 4 — Process tree}}）**：每個 node 寫名（P0、P1、P2…），旁邊寫 **佢喺第幾個 iteration（i 值）出世**；child 由 fork 下一句開始、**繼承 i 值**繼續 loop。
2. 由 P0 開始，一個 iteration 畫一層：每個仍然 active 嘅 node 照嗰輪 code 逐句行，**邊個 process 執行 `fork()`，就由佢拉一條箭咀去新 child**（child 再 fork 就由 child 再拉，所以會有孫）。
3. 有 `break` / `return` → 嗰個 node 之後**唔再生**。例子：**Ch3 §9.3（{{p:3-s9-3}}）**、原題 **S26 Q3.1（{{q:S26-Q3.1}}）**。
4. **自我檢查**：node 總數 = §2 計到嘅 total。

**答卷寫法**：箭咀 parent → child，每條線標 *i = 0 / 1 / 2*；最底寫 *"Total: N processes"*。

## 4. 類型 C — 所有可能輸出 / 次序

1. 翻 **P1 Step 5（{{t:Step 5 — Output ordering}}）** 同 **Ch3 §9.6（{{p:3-s9-6}}）**。
2. 喺 rough paper：**每個 process 一行**，寫低佢印嘅字（同一 process 嘅次序**固定**）。
3. 加約束（用箭咀連）：
   - parent 喺 `wait()` 之後印嘅 → 一定喺 child（同 child 嘅子孫）所有輸出**之後**；
   - fork 之前已印嘅 → 最先；
   - `read()` 一條 pipe → 要等對方 `write()` 之後（例：**X3-50（{{p:X3-50}}）**）。
4. 逐個位揀「而家可以印邊個」→ 列晒所有次序；數量可以用 Ch3 §9.6 嘅「插空位」方法計。
5. 同類原題：**F20 Q3.1（{{q:F20-Q3.1}}）**、**Sp21 Q1.3（{{q:Sp21-Q1.3}}）**；threads 版：**X4-24（{{p:X4-24}}）**。

**答卷寫法**：*"Assume each printf is flushed immediately."* 然後 (1)、(2)、(3)… 逐個 output 列出；問「幾多個」就寫總數 + 點數。

## 5. 類型 D — exec 成功 / 失敗、fork 失敗

1. 翻 **P1 Step 6（{{t:Step 6 — exec}}）** + **Ch3 §9.7（{{p:3-s9-7}}）**；原題 **S26 Q3.2（{{q:S26-Q3.2}}）**。
2. 照三個情況逐個寫：
   - **(I) fork ✓、exec ✓**：child 只印 exec **之前**嘅嘢（exec 之後嘅 code **永遠唔行**）+ parent 嘅輸出。
   - **(II) fork ✓、exec ✗**：exec 返回 −1，child **繼續行 exec 之後嘅 code**（loop 入面會繼續 fork！見 **X3-31（{{p:X3-31}}）**）。
   - **(III) fork ✗**：冇 child，只有 `pid < 0` 嗰個 branch 嘅輸出。

**答卷寫法**：三個 bullet，每個寫「印咩 + 一句原因」（*"exec replaces the process image, so the code after it never runs"*）。

## 6. 類型 E — pipe / dup / open 填空

1. 翻 **P2 表（{{p:P-p2-pipe-dup-exec-playbook}}）**，逐個 BLANK 對「要做」一欄：

| BLANK 喺邊 | 通常填 |
|---|---|
| `fork()` **之前** | `pipe(fd);` |
| 會 `write` 嘅 process | `close(fd[0]);` → `write(fd[1], &x, sizeof(x));` → `close(fd[1]);` |
| 會 `read` 嘅 process | `close(fd[1]);` → `read(fd[0], &x, sizeof(x));` → `close(fd[0]);` |
| 要 stdout 去 pipe / file | `dup2(fd[1], 1);` 或 `dup2(fo, 1);` |
| 要 stdin 由 pipe / file | `dup2(fd[0], 0);` 或 `close(0); dup(fin);` |
| 開檔 | `open(name, O_RDONLY)` / `open(name, O_WRONLY \| O_CREAT \| O_TRUNC, 0644)` |

2. **點知邊個係 writer / reader**：睇 BLANK 之後嗰句用 `read` 定 `write`、用邊個 fd。
3. 兩條 pipe（雙向）→ 抄 **XC-07（{{p:XC-07}}）** / 原題 **Lab 4 EX1（{{q:Lab4-EX1}}）**。
4. 交卷前 checklist：
   - 每個 process 都 **close 自己唔用嗰端**（否則 reader 收唔到 EOF、永遠 block）；
   - `read` / `write` 第二個參數係 **address**（`&x` / `buf`），第三個係 **size**（`sizeof(x)`）；
   - **fd[0] = read，fd[1] = write**；
   - 個 BLANK 唔使填嘢 → 寫 `/* Nothing */`（**E4 模板，{{p:E-e4-answer-templates}}**）。
5. 同類原題：**S26 Q3.3（{{q:S26-Q3.3}}）**、**HW1 Q3.3（{{q:HW1-Q3.3}}）**、**HW1 Q2.5（{{q:HW1-Q2.5}}）**；完整程式：**XC-05（{{p:XC-05}}）**、**XC-06（{{p:XC-06}}）**、**XC-08（{{p:XC-08}}）**、**XC-09（{{p:XC-09}}）**。

## 7. 類型 F — 叫你寫 program

翻 **XC（{{p:X-xc}}）**，搵最似嘅 program **成段抄**，再改字串 / 檔名 / 數目：

| 題目要求 | 抄 |
|---|---|
| parent 等 child、印 exit status | **XC-01（{{p:XC-01}}）** |
| 開 N 個 children / 一條 chain | **XC-02（{{p:XC-02}}）** / **XC-03（{{p:XC-03}}）** |
| 用 exec 行一個 command | **XC-04（{{p:XC-04}}）** |
| parent → child 傳字串 | **XC-05（{{p:XC-05}}）** |
| child 計完傳結果畀 parent | **XC-06（{{p:XC-06}}）** |
| 雙向溝通 | **XC-07（{{p:XC-07}}）** |
| `cmd < in > out` redirection | **XC-08（{{p:XC-08}}）** |
| `cmd1 \| cmd2`（例如 `ls \| wc -l`） | **XC-09（{{p:XC-09}}）** |
| PA1 多段 pipe | **XC-10（{{p:XC-10}}）** |
| 簡單 shell / `cd` / Ctrl-C | **XC-11（{{p:XC-11}}）** |
| named pipe (FIFO) | **XC-12（{{p:XC-12}}）** |
| zombie / orphan 示範 | **XC-19（{{p:XC-19}}）** |

**答卷寫法**：保留 comments（graders 睇得明 = 攞分）；記得 `wait()`、exec 之後 `perror(...); exit(1);`、close 唔用嘅 pipe ends。API 參數唔記得 → **A 部 API 速查（{{p:part-A}}）**。

## 8. 類型 G — fork + pthread_create 混合

直接翻 **X4-32 至 X4-36（{{p:X4-32}}–{{p:X4-36}}）**：已解好「幾多 process / thread / 印幾多次」嘅五種寫法。規則（抄落答卷）：*"fork() in a multithreaded process duplicates only the calling thread (Linux)."*；*"Threads share globals, processes get a copy."*（**X4-34（{{p:X4-34}}）**）。

## 9. 交卷前 30 秒 checklist

- child 拎 **0**、parent 拎 **child PID**、失敗 **−1**（**E3 traps，{{p:E-e3-top-traps-mc}}**）。
- `&&` / `||` 短路有冇計錯？
- `break` / `return` 只停**嗰個** process。
- exec 成功 → 之後唔行。
- 有冇寫 assumption：*"all fork() calls succeed; printf is flushed immediately."*
