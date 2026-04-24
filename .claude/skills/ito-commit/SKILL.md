---
name: ito-commit
description: 掃描 git 工作區所有改動，依語意邏輯分組，生成符合 Conventional Commits 規範的 commit 計畫並於使用者確認後依序執行。適用於整理工作區提交、自動撰寫 commit message、一次處理多個性質不同的改動。支援 --fast 標記將所有改動合併為單一 commit。不適用於需要 push、需要調整單一 commit、或尚未完成改動的情境。
---

# ito-commit

## 概覽

本 skill 讀取 git 工作區所有 staged 與 unstaged 改動，生成符合 Conventional Commits 規範的 commit 計畫，待使用者確認後依序執行。使用者全程不需手動撰寫 commit message。

## 使用時機

- 使用者輸入 `/ito-commit` 或要求「整理 commit」、「幫我 commit」、「生成 commit message」。
- 工作區累積多個性質不同的改動，需要拆成多個 commit。
- 小幅改動想快速提交，使用者指定 `--fast` 標記合併為單一 commit。

**不應使用的情況：** 使用者要求 push、要求只調整既有 commit 計畫中的某一則 message、尚有改動未完成而需繼續撰寫程式碼的情境。這些任務另行處理。

## 核心流程

### 步驟 1：掃描工作區

1. 執行 `git status` 以取得工作區清單，確認是否存在 untracked files。
2. 執行 `git diff HEAD` 以取得 staged 與 unstaged 完整 diff 內容。
3. 執行 `git log --oneline -10` 以取得近期 commit 歷史。
4. 若 `git status` 顯示 untracked files，執行 `git add <untracked files>` 將其納入本輪分析範圍；不得以 `git add -A` 或 `git add .` 批次加入，以避免誤納敏感檔案。

### 步驟 2：偵測 commit message 語言

1. 解析步驟 1 中 `git log` 的輸出，判別近期 commit message 使用的自然語言。
2. 若近 10 則 commit 皆使用同一語言，後續生成的 commit message 一律沿用該語言。
3. 若近 10 則 commit 混用多種語言，於對話中輸出以下訊息並等待使用者明確回覆再繼續：

   > 「偵測到近期 commit message 使用了多種語言（如：中文、英文）。請問本次要使用哪種語言來撰寫 commit message？」

4. 不使用 AskUserQuestion 工具；所有語言詢問皆以對話文字進行。

### 步驟 3：判斷執行模式

1. 若使用者輸入含 `--fast` 標記，跳至步驟 7 執行快速模式。
2. 否則進入步驟 4 執行標準模式。

### 步驟 4：語意分組（標準模式）

1. 以 `git diff` 完整內容為依據，依**語意邏輯**判斷哪些檔案屬同一個 commit。目錄結構僅供輔助，不得作為唯一分組依據。
2. 套用下列分組原則：
   - **功能相關**：同一 feature 的前端元件、後端邏輯、對應測試歸入同一 commit。
   - **獨立性**：與其他改動無邏輯依賴的修改（如獨立文件更新、chore）單獨成一個 commit。
   - **跟隨慣例**：讀 `git log` 掌握現有 scope 命名方式（例：`auth`、`api`、`ui`）並沿用。新專案則以目錄或模組名稱推斷合理 scope。

### 步驟 5：生成 Commit 計畫

1. 依「輸出格式與 Type 對照」章節的標準模式格式生成計畫，並依 type 對照表選用正確 type。
2. 依該格式將每則 commit 的 type、scope、message、改動描述與涉及檔案填入計畫。
3. 所有文字一律使用步驟 2 確認的語言，不得混用。

### 步驟 6：確認計畫並執行

1. 於對話中呈現完整計畫後，附上下列兩個選項：

   > A）確認執行 — 依序執行上述所有 commit
   >
   > B）提供修改意見 — 輸入意見，整個計畫重新生成

2. 等待使用者明確回覆。若回覆為 B，擷取使用者意見後回到步驟 4 重新分組，反覆直到使用者選 A 為止。
3. 選 A 後，依計畫順序逐一執行：

   ```bash
   git add <commit-1 的檔案>
   git commit -m "<commit-1 message>"

   git add <commit-2 的檔案>
   git commit -m "<commit-2 message>"
   ```

4. 全部完成後，執行 `git log --oneline -<N>`（N 為本次 commit 數）並將結果納入對話內的執行摘要：

   ```
   完成！共執行 N 個 commits：
   - <sha> <message>
   - <sha> <message>
   ```

5. 結束後不執行 `git push`。

### 步驟 7：快速模式（--fast）

1. 執行 `git add <所有選定的檔案>` 以將改動納入 staging（不使用 `git add -A` 或 `git add .`）。
2. 執行 `git diff --cached` 取得涵蓋所有改動的 diff。
3. 依「輸出格式與 Type 對照」章節的快速模式格式生成提案。
4. 依該格式生成單一 commit 提案，於對話中展示並附上步驟 6 的 A／B 選項。等使用者明確回覆後再繼續。
5. 使用者選 A 後執行 `git commit -m "<message>"`，接著執行 `git log --oneline -1` 並輸出執行摘要。

## 輸出格式與 Type 對照

### 標準模式（多個 commits）

**中文：**

```
Commit 計畫：

Commit 1: <type>(<scope>): <message>
詳細內容：
- <改動描述 1>
- <改動描述 2>
檔案：
- path/to/file1
- path/to/file2

Commit 2: <type>(<scope>): <message>
詳細內容：
- <改動描述>
檔案：
- path/to/file3
```

**English:**

```
Commit Plan:

Commit 1: <type>(<scope>): <message>
Changes:
- <change description 1>
- <change description 2>
Files:
- path/to/file1
- path/to/file2

Commit 2: <type>(<scope>): <message>
Changes:
- <change description>
Files:
- path/to/file3
```

### 快速模式（單一 commit）

**中文：**

```
<type>(<scope>): <message>
詳細內容：
- <改動描述 1>
- <改動描述 2>
檔案：
- path/to/file1
- path/to/file2
```

**English:**

```
<type>(<scope>): <message>
Changes:
- <change description 1>
- <change description 2>
Files:
- path/to/file1
- path/to/file2
```

### Conventional Commits type 對照

| type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修 bug |
| `docs` | 文件變更 |
| `style` | 格式調整（不影響邏輯） |
| `refactor` | 重構（非新功能、非 bug fix） |
| `perf` | 效能改善 |
| `test` | 新增或修正測試 |
| `build` | 建構系統或外部相依 |
| `chore` | 雜務（依賴更新、維護任務） |
| `ci` | CI/CD 設定 |
| `revert` | 還原先前 commit |

## 規則速查

| 規則 | 說明 |
|------|------|
| 不詢問意圖 | 全自動讀 diff 生成 message，不詢問「你想寫什麼 commit message？」 |
| 不自動 push | commit 完成即停止，不執行 `git push`。 |
| 不支援局部修改 | 不同意時整個計畫重新生成，不支援只調整其中一則。 |
| 不偵測 breaking change | 由使用者自行判斷；如需要請手動於 message 加上 `!` 或 `BREAKING CHANGE:`。 |
| 跟隨現有慣例 | 讀 `git log` 了解 scope 命名，維持 codebase 一致性。 |
| 不使用 AskUserQuestion | 所有詢問皆以對話文字進行。 |
| 不使用 `git add -A`／`git add .` | 僅加入本次計畫涵蓋的檔案，避免誤納 `.env`、credentials 等敏感檔。 |

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|---|---|
| 「diff 很明顯，不用讀 `git log` 也能猜 scope」 | 跳過 log 會偏離既有 scope 命名慣例，commit 歷史立刻出現風格斷層。 |
| 「語言自動判斷就好，不必詢問」 | log 混用多語時自行選語會讓 commit 歷史進一步混亂；必須詢問以保留決策權。 |
| 「使用者只想調整其中一則 message，幫他局部改」 | 局部修改會打破分組邏輯；規則要求整個計畫重來，不得放行。 |
| 「順便 push 方便一點」 | push 屬另一個動作，未經授權不得執行；commit 完成即停止。 |
| 「`git add -A` 比較快」 | 批次 add 會把 `.env`、credentials、大型 binary 意外納入，必須逐檔加入。 |
| 「--fast 模式小事，跳過確認」 | 未確認就 commit 等同剝奪使用者否決權；A／B 選項不可省略。 |

## 警訊

- commit 計畫送出時，scope 與近期 log 風格不一致，顯示未讀 `git log`。
- commit 執行後出現 `.env`、`credentials.json` 等敏感檔案進入歷史，顯示使用了批次 add。
- 單次執行中出現兩種以上語言的 commit message，顯示步驟 2 未落實。
- 計畫確認前已出現 `git commit` 或 `git push` 操作，顯示略過確認步驟。
- 使用者回覆 B 後，下一版計畫仍與前一版幾近相同，顯示未真正納入意見。

## 驗證

- [ ] `git log --oneline -<N>` 顯示本次所有 commit 皆已寫入歷史，sha 可查。
- [ ] 執行 `git status` 回傳 clean（或僅剩下本次刻意未納入的檔案），確認計畫內檔案皆已提交。
- [ ] 所有 commit message 皆符合 `<type>(<scope>): <subject>` 的 Conventional Commits 格式。
- [ ] 所有 commit message 使用同一自然語言，與步驟 2 決定的語言一致。
- [ ] 未執行 `git push`，未以 `--no-verify` 繞過 hook。

## 錯誤處理

- 若 `git status` 顯示工作區完全 clean，於對話中回報「無改動可 commit」並終止流程。
- 若 `git diff HEAD` 輸出為空但 `git status` 顯示 untracked files，於執行 `git add` 後重讀 `git diff --cached`，確認 diff 非空再繼續。
- 若 pre-commit hook 失敗（commit 未產生），保留現有 staging，於對話中回報錯誤訊息並請使用者決定修正方向；不得以 `--no-verify` 規避。
- 若執行途中使用者要求中止，停在當前 commit 位置，輸出已完成的 commits 清單，不回退已 commit 的內容。
- 若 `git log` 可解析的 commit 少於 10 則（新 repo），以現有 commit 為樣本；若完全無 commit，直接詢問使用者要使用何種語言撰寫 message。
