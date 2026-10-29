# 攻略：Synchronization 題點用 cheat book 攞分

> 🎯 **呢頁唔係教原理，係教你點「查書 → 照做 → 照寫」**。頁數 = 印出嚟嗰本 cheat book（{{pages}} 頁版）。Sync 題（歷屆約 8–15 分）幾乎全部係固定套路：**可能值、semaphore 次序、輸出序列、用 atomic instruction 寫 lock、三個 requirement 判斷**。

## 0. 入場前：貼 4 張 sticky notes

| 貼喺 | 頁 | 用嚟 |
|---|---|---|
| **P4 Synchronization Playbook** | **{{p:P-p4-synchronization-playbook}}** | 可能值方法、semaphore 次序規則、spinlock 表 |
| **Ch6 §6 做題方法** | **{{p:6-s6}}** | 歷屆題型逐步示範 |
| **X6 答案庫（判斷表、填空、例題）** | **{{p:X-x6}}** | 直接抄答案 / 對答案 |
| **XC mutex / semaphore programs** | **{{p:XC-15}}** | 寫 code 題 |

## 1. 先認類型

| 題目字眼 | 跳去 |
|---|---|
| "What are all the possible values of c / x / counter?" | **§2 可能值** |
| "Initialize the semaphores / fill in wait() and signal() so that S1 runs before S2…"、precedence graph | **§3 semaphore 次序** |
| "Which outputs are possible?"、"Is the sequence … possible?"（有 semaphores） | **§4 輸出序列** |
| "Implement a lock using `test_and_set` / `compare_and_swap` / `swap` / 新 instruction"、填空 | **§5 spinlock** |
| "Does this solution satisfy mutual exclusion / progress / bounded waiting?" | **§6 三個 requirements** |
| "Write a program with a mutex / semaphores"、producer–consumer、readers–writers | **§7 code** |
| 定義 / 解釋：race condition、critical section、spinlock pros/cons、semaphore vs mutex | 題目搜尋表 **{{p:X-finder}}** → **X6（{{p:X-x6}}）** 直接抄 |

## 2. 所有可能值（race condition）

照 **P4「Race 可能值」（{{p:P-p4-synchronization-playbook}}）** 四步，全部機械式：
1. **拆 T1 做 atomic steps**：`if (a > 0)` = 讀 a；`c = a + b` = 讀 a → 讀 b → 寫 c（**由左至右讀**）；`c = b - a` = 讀 b → 讀 a → 寫 c。寫成 *R1, R2, R3, W*。
2. **T2 嘅 writes 次序固定**（例如 `a = -1;` 先，`b = 10;` 後）；佢哋可以插入 T1 每個空位（R1 之前、R1–R2 之間…）。
3. **逐個插法計**：每個 read 見到新值定舊值 → 行邊個 branch → 計結果。如果 T2 都寫同一個變數（例如兩邊都寫 c），**最後寫嗰個贏**，記得加埋呢啲 case。
4. 收集所有**唔同**嘅值。

**答卷寫法**（**E4 模板，{{p:E-e4-answer-templates}}**）：逐個 case 列：*"Case 1: T1 reads a = 3, then T2 runs a = −1; b = 10; T1 reads b = 10 → c = 13."* → 最後 *"Possible values: {4, 6, 8, 9, 11, 13}"*。**每個 distinct 值都有分**，所以寧願多列 case。

> 📝 **完整示範**：**X6-41（{{p:X6-41}}）**（6 個值，連表）。同類原題：**F19 Q4.3（{{q:F19-Q4.3}}）**、**F20 Q5（{{q:F20-Q5}}）**、**Lab 6 Q7（{{q:Lab6-Q7}}）**、**HW1 Q3.1（{{q:HW1-Q3.1}}）**；`counter++ / counter--` 版：**X6-02（{{p:X6-02}}）**。

## 3. Semaphore 次序 / precedence graph 填空

照 **P4「Semaphore 次序」（{{p:P-p4-synchronization-playbook}}）**：
1. 畫出要求嘅次序：每個「X 要喺 Y 之前」畫一條箭咀 X → Y。
2. **每條箭咀 = 一個 semaphore，初始值 0**：**X 做完之後 `signal(s)`；Y 開始之前 `wait(s)`**。
3. 一個 statement 有兩個前置 → **兩個 `wait`**（例：**X6-37，{{p:X6-37}}**）。
4. **輪流**（T1 → T2 → T3 → T1 …）→ 第一個 semaphore **= 1**，其餘 **= 0**；每個 thread `wait(自己)` … `signal(下一個)`（**X6-38，{{p:X6-38}}**；**Lab 6 Q1，{{q:Lab6-Q1}}**）。
5. 「最多 k 個同時」→ 一個 semaphore = **k**；mutual exclusion → **1**（**X6-24 / X6-26，{{p:X6-24}}**）。
6. 唔使填嘢嘅 BLANK → 寫 `/* Nothing */`。

**答卷寫法**：每個 semaphore 寫「名 = 初始值」，再逐個 BLANK 填；加一句 *"S1 signals s after it finishes; S2 waits on s before it starts, so S2 always follows S1."*
同類原題：**S26 Q5（{{q:S26-Q5}}）**、**Lab 6 Q2（{{q:Lab6-Q2}}）**；示範 **X6-25（{{p:X6-25}}）**。

## 4. 有 semaphores 嘅輸出序列

**「呢個序列可唔可能？」** → 照 **P4「Semaphore 序列可行性」**：
1. 寫低每個 semaphore 嘅**初始值**。
2. 跟住個序列逐個字：搵出邊個 process 印 → 行到嗰度之前要經過嘅 `wait`，**當時個值一定要 > 0**（否則嗰個 process 要等，序列就唔得）；`signal` 就 +1。
3. 全部行得通 → possible；卡住 → impossible，寫低**卡喺邊個 `wait`、個值係幾多**。

**「列出所有可能輸出」** → **X6-43（{{p:X6-43}}）** 方法：
1. 每個 process 自己嘅次序固定；
2. 每對 `signal(s)` → `wait(s)` 加一條「之前」約束；
3. 列晒符合約束嘅次序；
4. 檢查會唔會 deadlock（**X6-44，{{p:X6-44}}**：數 permits，追到全部人卡住為止）。

同類原題：**F19 Q4.4（{{q:F19-Q4.4}}）**、**Lab 6 Q4（{{q:Lab6-Q4}}）**、**Lab 6 Q5（{{q:Lab6-Q5}}）**。

## 5. 用 atomic instruction 寫 spinlock / 填空

1. 讀題目畀嘅 instruction 定義，問自己：**「返回咩值代表我攞到 lock？」**
2. 套 **P4 spinlock 表（{{p:P-p4-synchronization-playbook}}）** 嘅格式：

```c
while (instr(...) 返回「攞唔到」嘅值)
    ;                     /* spin */
/* critical section */
lock = 「free」嘅值;       /* release */
```

3. 表入面已經有四隻：`test_and_set`、`compare_and_swap`、`swap`、`compare_and_reset`；新 instruction（例如 `fetch_and_add`）→ **X6-40（{{p:X6-40}}）**。
4. 填空版 → **X6-39（{{p:X6-39}}）**；bounded-waiting TAS 填空 / 改錯 → **P4「Bounded-waiting TAS 檢查點」** + **X6-15 至 X6-17（{{p:X6-15}}）**。
5. 同類原題：**S26 Q2.4 swap（{{q:S26-Q2.4}}）**、**Sp21 Q3.1 compare_and_reset（{{q:Sp21-Q3.1}}）**、**Sp21 Q3.2（{{q:Sp21-Q3.2}}）**。

**答卷寫法**：code + 一句 *"The lock is acquired only when the instruction returns the old value 'free'; the release stores the free value back."*

## 6. 「滿唔滿足 ME / progress / bounded waiting？」

1. 先翻 **X6-32 判斷表（{{p:X6-32}}）**：九種常見 protocol（只用 `turn`、flag 先 check 後 set、flag 先 set 後 check、Peterson、Peterson 調轉、TAS、CAS、bounded-waiting TAS、非 atomic acquire）。**搵到一樣嘅就抄嗰行 Yes/No + reason**。
2. 搵唔到 → 用 **X6-33 至 X6-36（{{p:X6-33}}）** 嘅「反例」寫法逐個試：
   - **ME**：試搵一個 interleaving 令**兩個都入到 CS**（兩邊都過咗 check 先改變數）→ 搵到 = violated。
   - **Progress**：試一個 process 留喺 **remainder section**（唔想入），另一個入唔入到？入唔到 = violated；或者兩個互相等（deadlock）= violated。
   - **Bounded waiting**：一個 process 等緊，另一個可唔可以**無限次**再入？可以 = violated。
3. 定義原文：**X6-06（{{p:X6-06}}）**（三個 requirements + 點樣會違反）。

**答卷寫法**：每個 requirement 一行：*"Mutual exclusion: satisfied, because … / violated: P0 … then P1 …, both enter."* 有反例就寫出 interleaving（攞分關鍵）。

## 7. 寫 code（mutex / semaphores / classic problems）

| 題目要求 | 抄 |
|---|---|
| 兩個 thread 加同一個 counter，要保證正確 | **XC-15（{{p:XC-15}}）** |
| 用 semaphores 保證 T1 → T2 → T3 | **XC-16（{{p:XC-16}}）** |
| Producer–consumer（bounded buffer） | **XC-17（{{p:XC-17}}）**、pseudo-code **X6-47（{{p:X6-47}}）** |
| Readers–writers | **XC-18（{{p:XC-18}}）**、**X6-48（{{p:X6-48}}）**、Lab 6 版 **Lab 6 Q6（{{q:Lab6-Q6}}）** |
| Mutex 填空（`pthread_mutex_lock` …） | **Lab 6 Q3（{{q:Lab6-Q3}}）** |
| Condition variable | **X6-50（{{p:X6-50}}）** |

## 8. 交卷前 30 秒 checklist

- 可能值：有冇**由左至右**讀 operands？有冇漏「T2 全部喺前 / 全部喺後」兩個極端？
- Semaphore 次序：所有「之前」關係都用 **init 0** 嘅 semaphore？輪流嗰個係咪得**第一個 = 1**？
- Spinlock：`test_and_set` / `compare_and_swap` 返回 **old value**（**E3 traps，{{p:E-e3-top-traps-mc}}**）。
- `wait` / `signal` 調轉或者漏咗：**X6-45（{{p:X6-45}}）** 有晒每種後果。
