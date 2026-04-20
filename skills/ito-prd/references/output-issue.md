# Issue 輸出與回寫規則（資料擷取用）

本檔案提供 `SKILL.md` 步驟 8 執行 issue 輸出（新建）與回寫（編輯）時需要的具體規則。從中擷取 title、label、body、重複檢查、diff 展示等資料即可，不需要整份執行。

## Title 生成

- **格式**：`[PRD] <功能自然語言描述>`
  - 範例：`[PRD] OTP 登入驗證`、`[PRD] 使用者權限分級`
- **流程**：
  1. agent 依訪談內容生成候選 title
  2. 發 issue 前詢問使用者：「title 用 `[PRD] OTP 登入驗證` 可以嗎？或你要改？」
  3. 使用者確認或修改後才發送

## Label 處理

- **固定 label**：`PRD`
- **label 顏色**：`#0075ca`
- **label description 建議**：`Product Requirements Document`

### Label 不存在時

執行 `gh label list` 檢查；若 `PRD` label 不存在，先執行：

```bash
gh label create "PRD" --color "0075ca" --description "Product Requirements Document"
```

- 建立成功 → 繼續發 issue 並貼 label
- 建立失敗（無權限、repo 設定限制等）→ 警告使用者「label 建立失敗，issue 將不貼 label」後繼續發送

## Body 規範

**Body 為 `assets/prd-template.md` 原樣填入**，包含五個區塊：

- `## 問題描述`（含 `### 現況`、`### 痛點`、`### 目標`）
- `## User Stories`
- `## Out of Scope`
- `## 已知侷限`
- `## Open Questions（選填）`

**禁止附加：**

- 頂部 summary 段落
- Front matter（`---` 包夾的 metadata 區塊）
- 建立時間、版本、模式等 metadata
- 底部附錄（訪談 raw notes、decision log 等）
- 「由 ito-prd 產生」之類的簽名

## 重複 PRD 檢查

發 issue **前**執行以下流程：

1. 執行 `gh issue list --label PRD --state all --json number,title --limit 100` 取得現有 PRD issue 列表
2. 將候選 title 與列表中的 title 做關鍵字 / 語義相似比對
3. 找出相似度最高的前 3 筆（閾值自行判斷，只保留明顯相關的）
4. 若有相似項目 → 列出給使用者：

   ```
   發現 2 筆可能相似的 PRD：
    - #45 [PRD] OTP 登入流程
    - #62 [PRD] 雙因素驗證
   你要：
    - A）仍發為新 issue
    - B）改為編輯其中一個（請指定編號）
   ```

5. 使用者選 A → 繼續發送；選 B → 切換到編輯模式，以該 issue 作為來源重啟流程
6. **若列表為空（repo 無任何 `PRD` issue）→ 跳過檢查，直接發送**

## 發送指令

重複檢查與 label 確認通過後，執行：

```bash
gh issue create --title "[PRD] <功能名稱>" --body "<完整 template 內容>" --label "PRD"
```

發送後展示 issue URL：

```
Issue 已建立：https://github.com/<owner>/<repo>/issues/<number>
```

## 回寫流程（編輯模式 issue 來源）

編輯模式輸入為 issue 時：

1. 執行 `gh issue view <number> --json body` 取得當前 body
2. 將當前 body 與擬寫入的新 body 做 diff 比對
3. 以 unified diff 格式（或簡化版，如「變更區塊列表」）展示給使用者：

   ```
   即將更新 issue #123，變更內容如下：

   ## User Stories
   -  US-02 身為管理員，想要...
   +  US-02 身為管理員，想要...（加上 2FA 驗證）

   ## Out of Scope
   +  這次不做：第三方 SSO 整合
   ```

4. 詢問使用者：「確認覆蓋 issue body？」
5. 使用者同意 → 執行：

   ```bash
   gh issue edit <number> --body "<新 body>"
   ```

6. 使用者不同意 → 回到步驟 6（Review）讓使用者指出要調整的地方

## 編輯模式不涉及的項目

- **Title**：編輯模式預設不改 title；若使用者明確說要改，才詢問新 title 並一併更新（`gh issue edit <number> --title "..."`）
- **Label**：編輯模式不改 label（`PRD` label 維持）
- **重複檢查**：編輯模式不執行（僅新增模式才檢查）

## 錯誤處理

- `gh auth status` 失敗 → 提示使用者執行 `! gh auth login`，保留訪談結果在記憶體中，待登入後再試
- `gh issue view` 回傳 not found → 回報錯誤，要求使用者確認 issue 編號
- `gh issue edit` 回傳權限錯誤 → 回報錯誤，提示使用者確認 repo 推送權限
- Network timeout → 保留 draft，提示使用者稍後重試
