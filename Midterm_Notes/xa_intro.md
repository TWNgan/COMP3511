> 🎯 **用法**：搵題目關鍵字 → 去對應 X1–X6 → 直接抄 **Answer**（英文，已按評分重點寫好，粗體 = 評分關鍵字）。計數題用 **P（Playbooks）**；歷屆原題用 **Q / M**；寫 code 用 **XC**（全部已編譯 + 跑過）。

**任何 short question 都套得落嘅滿分寫法**
1. **Explain / Why**：一句 direct answer → mechanism（點做）→ consequence / example。
2. **Compare A vs B**：3–4 行表（purpose・mechanism・advantage・disadvantage/overhead），每格一句。
3. **Advantages / disadvantages**：每點 = point + 一句 reason；分數幾多就寫幾多點（2 marks → 2 points）。
4. **Calculation**：formula → substitution → answer（連 unit）；Gantt 寫 `0 P1 5 P2 8 …`；唔清楚就寫 assumption（e.g. "Assume ties are broken by FCFS, then smaller process ID"）。
5. **Code**：close 唔用嘅 pipe ends；parent `wait()`；exec 之後加 `perror(...); exit(1);`；threads 要 `pthread_join`；shared data 用 mutex / semaphore 保護。
6. **True / False**：先答 T/F，再加一句 reason（用關鍵字）。
