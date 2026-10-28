# Chapter 0 — 考試攻略（Exam Strategy）

> 🗓️ **COMP3511 Midterm：29-Oct-2026（Thu）8:00 PM – 10:00 PM（2 小時）**
> 📍 **L1 → LTD｜L2 → LSKG012｜L3 → LTB**（唔好同 lab section LAx 搞亂！唔記得 → Canvas > People）
> 📚 **Coverage：Chapters 1–6（up to Synchronization Tools）**
> 📖 **Open-book, open-notes（printed materials）**；**calculator OK（唔准手機/平板）**；**自備 rough work sheets**（booklet 雙面）；答案寫喺 booklet 指定位置。
> 💻 可能有 **PA / lab API coding 題**（fork, exec, wait, pipe, dup, open/read/write/close, pthread, semaphore）→ 印埋 lab notes / 本 cheat book 嘅 API 章。

---

## 1. 試卷結構預測（根據 4 份 past papers）

| Section | S26（今個 instructor 出） | F20 | F19 | Sp21 | 預測 F26 |
|---|---|---|---|---|---|
| **MC** | **25 × 1 = 25** | 15 × 1 | — | 30 × 1.5 = 45 | **~25 分** |
| **Short questions** | **16**（race condition、caching、custom policy、swap spinlock） | 20（microkernel、linker/loader、heavyweight、SMP queues、MLFQ） | 10 + 部分 | — | **~15 分** |
| **Process & thread（fork）** | **24**（fork tree、fork+exec cases、pipe/dup 填空） | 23（output orderings、count “a”） | 25 | 18 | **~24 分** |
| **CPU scheduling** | **27**（MLFQ、RM/EDF、dynamic priority） | 27（FCFS/SJF/SRTF、2-level FQ aging、priority+RR） | 40 | 26 | **~27 分** |
| **Synchronization** | **8**（semaphore ordering 填空） | 15（race values） | 25 | 11 | **~8–15 分** |

> 🎯 **S26（Spring 2026）係最近一份、由 lecturer 直接提供，格式同今次 announcement 一致（open-book、calculator、rough sheets）→ 最有參考價值** → 預期題型：**25 MC + 4 short + 3 fork 題 + MLFQ + RM/EDF + custom priority + semaphore 填空**。F19/F20 係 closed-book 年代，題目偏背誦；Sp21 MC 多。

---

## 2. 時間分配（120 分鐘）
| 部分 | 建議時間 | 策略 |
|---|---|---|
| 掃一次全卷 | 3 min | 圈出 calculation 題，估分 |
| MC（25 題） | **25 min** | 每題 ≤ 1 min；唔肯定 → 用 **MC 陷阱表**（每章 §「常見陷阱」）；做唔到先跳 |
| Short questions | 15 min | 抄 **Model answer**（英文），寫 2–3 句 + 例子 |
| fork 題 | 20 min | 用 **Ch3 §9 解題大法**；畫 process tree |
| Scheduling | **35 min** | 用 **Ch5 §13 流程**；寫晒每個 boundary time；每個 avg 寫 working |
| Synchronization | 12 min | 用 **Ch6 §6** |
| Check | 10 min | 檢查 Gantt 總時間、WT ≥ 0、MC 答案格 |

---

## 3. 題型 → 去邊度搵方法（Index）
| 見到… | 去 |
|---|---|
| "interrupt / DMA / trap / dual mode / privileged" | **Ch3 §0** |
| "cache / hit ratio / locality / average access time" | **Ch1 §4** |
| "von Neumann / storage hierarchy / SMP / NUMA / multicore" | **Ch1 §2, §3, §5** |
| "API / system call / printf / parameter passing / linker / loader" | **Ch2 §3, §5** |
| "monolithic / layered / microkernel / LKM / hybrid" | **Ch2 §7（比較表）** |
| "process state / PCB / scheduler（long/short/medium）/ context switch" | **Ch3 §2–6** |
| "fork() … how many processes / lines / tree / outputs" | **Ch3 §9（公式表 + 例題）** |
| "exec 成功/失敗 scenarios" | **Ch3 §9.7** |
| "pipe / dup / open / read / write 填空" | **Ch3 §11 + API 章** |
| "zombie / orphan / IPC / message passing / socket" | **Ch3 §8, §10–12** |
| "thread shares / benefits / user vs kernel / models / signals / cancellation" | **Ch4** |
| "Amdahl" | **Ch4 §4（計算表）** |
| "Gantt chart / waiting time / turnaround / response" | **Ch5 §2, §13, §14** |
| "MLFQ" | **Ch5 §8（規則 + checklist）** |
| "RM / EDF / deadline / utilization" | **Ch5 §11** |
| "custom policy（LUF / dynamic priority / fᵢ）" | **Ch5 §14.2–14.4** |
| "exponential averaging / Little's formula" | **Ch5 §5.4, §12** |
| "PCS / SCS / affinity / load balancing / CMT" | **Ch5 §9–10** |
| "race condition / possible values of c" | **Ch6 §6.1** |
| "semaphore ordering / which output possible" | **Ch6 §6.2–6.3** |
| "test_and_set / CAS / swap / spinlock implementation" | **Ch6 §3** |
| "critical section requirements / binary semaphore vs mutex" | **Ch6 §2.3, §5.2** |

---

## 4. 答題技巧（拎分位）
1. **MC**：題目問 **NOT / false** 要特別留神；有 "always / only / never / exactly / all" 嘅選項通常係錯。
2. **Short questions**：**英文**作答；先一句定義（keywords 要出現），再一句解釋/例子。S26 race condition 4 分 = 定義 2.5 + 例子 1.5。
3. **fork 題**：寫 **process tree + 數式 + 最終答案**；有 partial credit（S26：tree 4 分、數目 1 分、break 1 分）。
4. **Gantt chart**：**由左至右評分，錯一格後面冇分**（F20 grading rule）→ 慢慢做、逐格 check；寫 **每段起止時間**；MLFQ 標 queue。
5. **Average**：寫 **(x1+x2+…)/n = 答案**（保留 2 位小數）；1 分 only if Gantt 啱。
6. **Ties / ambiguity**：寫低 **assumption**（e.g. "Assume: on tie, the running process continues; new arrivals enter the RR queue before the preempted process"）。
7. **Response time**：用 **course definition（end of first run − arrival）**；如有疑問可以寫一句說明。
8. **Synchronization values**：列出 **每個 case 嘅 interleaving + 值**；每個 distinct 值都有分。
9. **Semaphore 填空**：S26 要求冇用嘅 blank 寫 **`/* Nothing */`**，唔好留空！

---

## 5. 24 小時溫習計劃（Oct 28 晚 → Oct 29 8pm）
| 時間 | 做咩 |
|---|---|
| 今晚 2h | 讀 **Ch5 §8, §11, §13–14**；用網站 **Scheduler 工具**做 S26 MLFQ、RM/EDF 一次 |
| 今晚 1.5h | 讀 **Ch3 §9**；自己計 S26 Q3.1、F19 Q2.7、Sp21 Q1.2，對答案 |
| 今晚 1h | **Ch6 §6**：F19 Q4.3、F20 Q5、F19 Q4.4、S26 Q5 |
| 明早 2h | MC 練習（網站 Quiz 全部做一次；錯嘅睇解釋）|
| 明午 2h | Ch1、Ch2、Ch4 陷阱表 + short question model answers |
| 明日 5pm | **打印 cheat book**（雙面、加 tab / highlighter）；收拾 calculator、rough paper、Student ID |
| 7:30pm | 去對 venue（L1 LTD / L2 LSKG012 / L3 LTB） |

---

## 6. 考場必帶清單
- [ ] Student ID card
- [ ] **Cheat book（打印）** + lecture notes / lab notes（printed）
- [ ] **Calculator**（非手機）
- [ ] **Rough work sheets**（自備！）
- [ ] 筆（藍/黑 + 備用）、highlighter、尺（畫 Gantt chart）
- [ ] 手錶（唔可以用手機睇時間）
