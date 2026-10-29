# 攻略：CPU scheduling 題點用 cheat book 攞分

> 🎯 **呢頁唔係教原理，係教你點「查書 → 照做 → 照寫」**。頁數 = 印出嚟嗰本 cheat book（{{pages}} 頁版）。Scheduling 係**最多分**嘅部分（歷屆約 27 分），而且 **Gantt chart 由左至右改，錯一格之後冇分**（F20 改卷規則），所以每一步都照書做、逐格對。

## 0. 入場前：貼 6 張 sticky notes

| 貼喺 | 頁 | 用嚟 |
|---|---|---|
| **E2 本科 Conventions** | **{{p:E-e2-conventions-assumption}}** | tie、RR 新 arrival、MLFQ 規則、response time 定義 |
| **E4 答題模板** | **{{p:E-e4-answer-templates}}** | Gantt + 表 + 平均數寫法 |
| **P3 Scheduling Playbook** | **{{p:P-p3-cpu-scheduling-playbook}}** | 每個 algorithm「揀邊個 / 幾時重揀」 |
| **P5 RM bound 表** | **{{p:P-p5-pre-computed-tables}}** | RM 可唔可以排 |
| **Ch5 §13 Gantt 萬用流程** | **{{p:5-s13}}** | 逐步 + tie-breaking |
| **Ch5 §14 歷屆計算全集** | **{{p:5-s14}}** | 同類已解題（對答案用） |

## 1. 先認類型

| 題目字眼 | 跳去 |
|---|---|
| FCFS / SJF / SRTF / RR / (non-)preemptive priority + "Gantt chart"、"average waiting / turnaround / response time" | **§2** |
| "priority scheduling … processes with the same priority are scheduled RR" | **§3** |
| "multilevel feedback queue"、Q0 / Q1 / Q2、"aging"、"two-level" | **§4** |
| "rate-monotonic"、"EDF"、"period"、"deadline"、"CPU utilization" | **§5** |
| "predict the next CPU burst"（α、τ）、Little's formula、context-switch overhead、RR bound | **§6** |
| 自訂 policy：dynamic priority（α、β）、"least used first"、公式 $f_i$ | **§7** |
| 冇數字：why / compare / which algorithm… | 題目搜尋表 **{{p:X-finder}}** → **X5（{{p:X-x5}}）** 直接抄 |

## 2. FCFS / SJF / SRTF / RR / Priority：Gantt + 平均數

**Step 0 — 先寫 assumptions（照抄 E2，{{p:E-e2-conventions-assumption}}）**，放喺答案最頂：
*"Assumptions: ties are broken by FCFS, then smaller process ID; in RR a newly arrived process enters the ready queue before the preempted process; response time = end of the first run − arrival time."*

**Step 1** — 喺 rough paper 抄個表：P、arrival、burst（、priority）。

**Step 2** — 翻 **P3 表（{{p:P-p3-cpu-scheduling-playbook}}）**，搵你個 algorithm 嗰行，抄低兩樣嘢：**「揀邊個」**同**「幾時重新揀」**：

| 你個 algorithm | 揀邊個 | 幾時重新揀 |
|---|---|---|
| FCFS | 最早到 | 有人完成 |
| SJF | **已經到咗**嘅最短 burst | 有人完成 |
| SRTF | 最短 **remaining** | 有人完成 + **每個 arrival**（平手唔 preempt） |
| RR q | queue 頭 | 完成 / 用完 q（用完 → 排 queue 尾） |
| Priority NP / P | 最細數字 | 完成 /（P：較高 priority 嘅 arrival） |

**Step 3** — 喺時間軸點出所有 **arrival 時間**；之後一路行一路加 **完成時間**同（RR）**quantum 用完時間**。

**Step 4** — 每個 event 時間，寫低 **ready queue（照次序）**，再照 Step 2 揀下一個。RR：用完 q 嘅排**尾**；同一時刻有新 arrival → **新 arrival 先入**。

**Step 5** — 寫 Gantt：`0 P1 3 P3 5 P1 8 …`（**每個 boundary 都寫**；CPU 冇嘢做都要寫 idle）。

**Step 6** — 填表（公式喺 **E1，{{p:E-e1-formula-card}}**）：

```
P  | Arr | Burst | Completion | TAT = C - A | WT = TAT - Burst | RT = end of 1st run - A
```

- **RT 用本科定義**：第一次上 CPU 嗰段**完結**嘅時間 − arrival（non-preemptive 時 RT = TAT）。

**Step 7** — 平均數連 working：*avg WT = (2 + 10 + 0 + 3) / 4 = 3.75*。

**Step 8 — 自我檢查**（P3 第 8 步）：最後完成時間 = 全部 burst 加埋 + idle；每個 process 喺 Gantt 上各段加埋 = 佢嘅 burst。

> 📝 **示範（SRTF）**：P1 (0, 6)、P2 (2, 5)、P3 (3, 2)、P4 (5, 4)。
> - P3 表 SRTF：揀最短 remaining；每個 arrival 都重新揀；平手唔 preempt。
> - t = 0：得 P1 → 行 P1。t = 2：P2 (5) vs P1 剩 4 → 繼續 P1。t = 3：P3 (2) vs P1 剩 3 → **轉 P3**。
> - t = 5：P3 完；ready = P1 (3)、P2 (5)、P4 (4) → P1。t = 8：P1 完 → P4 (4) < P2 (5) → P4。t = 12 → P2 → 17。
> - Gantt `0 P1 3 P3 5 P1 8 P4 12 P2 17`；WT = 2, 10, 0, 3 → **avg 3.75**。
> - 書入面 **X5-22（{{p:X5-22}}）** 有同一組數嘅 FCFS / SJF / SRTF / RR 全部答案 → **考前用佢練一次，對答案**。

**同類已解題（考試時見到似嘅就對住做）**：**X5-22（{{p:X5-22}}）**、**X5-25 priority（{{p:X5-25}}）**、**F19 Q3.6（{{q:F19-Q3.6}}）**、**F20 Q4.1（{{q:F20-Q4.1}}）**、**Sp21 Q2.1（{{q:Sp21-Q2.1}}）**、**HW2 Q3.2（{{q:HW2-Q3.2}}）**、**Lab 5 review（{{p:L-l5-1-review-p1-7}}）**。

## 3. Priority + RR（同 priority 輪流）

1. 照 §2 步驟，但**每個 priority level 一條 queue**（細數字 = 高，**E2 第 4 點**）。
2. 規則（**X5-26，{{p:X5-26}}** 有完整示範）：
   - 被**更高 priority** 嘅 arrival preempt → 返**自己 level 嘅 queue 頭**，**保留剩餘 quantum**；
   - 用完 quantum → 排自己 level 嘅 **queue 尾**；
   - 同一 level 得一個 process → 佢繼續行。
3. 同類原題：**S23（{{q:S23-PRR}}）**、**F20 Q4.3（{{q:F20-Q4.3}}）**、**Lab 5 L5.2（{{p:L-l5-2-priority-rr-arrival}}）**。
4. 最常錯：preempt 完重新畀返成個 quantum（**錯**，書入面有標）。

## 4. MLFQ（每年必考）

1. 抄低題目規則（幾多條 queue、每條 quantum、最後一條 FCFS、有冇 aging）。題目冇講嘅 → 用 **E2 第 3 點（{{p:E-e2-conventions-assumption}}）**，**寫做 assumption**。
2. Rough paper 畫 **P3 嘅 MLFQ 追蹤表（{{p:P-p3-cpu-scheduling-playbook}}）**：

```
t | event | Q0 | Q1 (rem q) | Q2 | running (queue, q left, burst left)
```

3. 每個 event 照呢幾條（E2 第 3 點）：
   - 新 job → **Q0 尾**；
   - 用完 quantum 仲未完 → **降一級，排尾**；
   - 被**高層 queue 新 arrival** preempt → 返**自己 queue 頭**，**保留剩餘 quantum**，**唔降級**；
   - 只係最高非空 queue 先可以行；Q0 job 唔會被新 arrival preempt。
4. Gantt 標 queue：`0 P1@Q0 4 P2@Q0 8 P1@Q1 …`（E2 第 8 點）。
5. 表 + 平均數同 §2 一樣。
6. 對答案用：**X5-34（{{p:X5-34}}）** 完整示範（連 queue 狀態）、**Ch5 §8.2 lecture example（{{p:5-s8-2}}）**、**§8.4 checklist（{{p:5-s8-4}}）**；原題 **S26 Q4.1（{{q:S26-Q4.1}}）**、**Sp21 Q2.2（{{q:Sp21-Q2.2}}）**、**HW2 Q3.3（{{q:HW2-Q3.3}}）**；two-level + aging：**F20 Q4.2（{{q:F20-Q4.2}}）**。
7. 純文字題（"why MLFQ"、"parameters of MLFQ"、"advantages"）→ **X5-31 至 X5-33（{{p:X5-31}}）** 直接抄。

## 5. RM / EDF（real-time）

1. **計 U**：$U = \sum_i t_i / p_i$（**E1，{{p:E-e1-formula-card}}**），寫晒條式。
2. **判斷**：
   - **RM**：查 **P5 RM bound 表（{{p:P-p5-pre-computed-tables}}）**（N = 2 → 0.828、N = 3 → 0.780…）。$U \le$ bound → *"schedulable by RM (guaranteed)"*；$U >$ bound → *"not guaranteed — draw the timeline"*。
   - **EDF**：$U \le 1$（deadline = period）→ *"schedulable by EDF"*。
   - $U > 1$ → *"overloaded: no algorithm can meet all deadlines"*。
3. **要畫 timeline**：照 **P3「RM / EDF 追蹤」（{{p:P-p3-cpu-scheduling-playbook}}）**：
   - 每個 task 列 **release 時間** $0, p, 2p, \ldots$ 同 **deadline = release + d**（題目 d < p 就用 d！見 **S26 Q4.2，{{q:S26-Q4.2}}**）；
   - 逐個時間單位揀：**RM = period 最短**（固定）；**EDF = absolute deadline 最早**；平手 → 唔 preempt（E2 第 5 點）。
4. **Deadline miss**：完成時間 > deadline 就係 miss；soft real-time → **嗰個 job 繼續行完**，計一次 miss（E2 第 6 點）。
5. **答卷寫法**：U 條式 → 同 bound 比較一句 → Gantt → 逐個 miss 寫「P2 misses its deadline at t = 7」。
6. 對答案用：**X5-53（{{p:X5-53}}）**（同一組 task 嘅 RM vs EDF timeline）、**X5-52（{{p:X5-52}}）**（四組 U 判斷）、**Ch5 §11.5 做題方法（{{p:5-s11-5}}）**、**Lab 5 L5.3（{{p:L-l5-3-rm-edf-deadline}}）**；原題 **Sp21 Q2.3（{{q:Sp21-Q2.3}}）**、**F19 Q3.4（{{q:F19-Q3.4}}）**、**HW2 Q2.5（{{q:HW2-Q2.5}}）**。

## 6. 公式題（直接代入）

| 題目 | 公式頁 | 已解示範（照格式抄） |
|---|---|---|
| Exponential averaging（α、τ） | E1 **{{p:E-e1-formula-card}}**、P5 權重表 **{{p:P-p5-pre-computed-tables}}** | **X5-19（{{p:X5-19}}）**、**X5-20（{{p:X5-20}}）** |
| Little's formula $n = \lambda W$ | E1 | **X5-55（{{p:X5-55}}）**（記得先轉單位） |
| RR + context switch：efficiency / utilization | — | **X5-13（{{p:X5-13}}）**、**X5-14（{{p:X5-14}}）** |
| RR 等待上限 $(n-1)q$ | E1 | **X5-11（{{p:X5-11}}）** |
| Response time 定義 | E2 第 1 點 | **X5-07（{{p:X5-07}}）** |

**答卷寫法**：formula → 代數 → 答案（連 unit）。逐步寫，錯數都有 method 分。

## 7. 自訂 policy（dynamic priority、LUF、$f_i$ 公式）

1. P3 表有「Dynamic priority」同「LUF」兩行（{{p:P-p3-cpu-scheduling-playbook}}）。
2. 每個決策時間點**列一個表**：每個 process 嘅 priority / 用咗幾多 CPU / $f_i$ 值 → 照題目規則揀 → 平手照**題目**講（例如 S26：larger ID）。
3. 對答案用：**Ch5 §14.2 至 §14.4（{{p:5-s14-2}}）**；原題 **S26 Q4.3（{{q:S26-Q4.3}}）**、**S26 Q2.3（{{q:S26-Q2.3}}）**、**F19 Q3.5（{{q:F19-Q3.5}}）**。

## 8. 交卷前 30 秒 checklist

- 有冇寫 **assumptions**（tie、RR 新 arrival、response time 定義）？
- Gantt **每個 boundary** 有冇寫？有冇漏 idle？
- 每個 process 嘅段數加埋 = burst？最後完成時間 = 總 burst + idle？
- RT 係「**第一段完結** − arrival」（唔係開始）？
- MLFQ：preempt 之後有冇**錯降級 / 錯 reset quantum**？
