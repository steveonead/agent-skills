# 輸入型態解析規則

本檔供 `ito-browser-verify` 主流程於步驟 2 擷取「如何辨識輸入型態」與「如何抽取驗收標準」兩類規則，作為資料參照，非執行指令。

## 三種輸入型態的判別

### 型態 A：GitHub issue URL 或 issue number

符合以下任一形式視為本型態：

- 完整 URL：`https://github.com/<owner>/<repo>/issues/<number>`
- 精簡 URL：`github.com/<owner>/<repo>/issues/<number>`（不含 scheme）
- 形如 `#<number>` 的純數字引用（此情況需向使用者確認 owner／repo 或從當前 git remote 推斷）

擷取流程：

1. 以 `gh issue view <url-or-number> --json title,body` 取得 issue title 與 body。
2. title 作為 report slug 的候選來源。
3. body 作為驗收標準擷取的原始文本。

### 型態 B：本地 markdown 檔路徑

符合以下任一條件視為本型態：

- 路徑以 `.md` 結尾。
- 路徑對應到實際存在的檔案（以 Read 工具探測）。

擷取流程：

1. 以 Read 工具讀取檔案完整內容。
2. 檔名（去除副檔名）作為 report slug 的候選來源。
3. 檔案內容作為驗收標準擷取的原始文本。

### 型態 C：對話中貼入的自由文字

不符合型態 A、B 的內容視為本型態。

擷取流程：

1. 直接以使用者提供的文字作為原始文本。
2. 向使用者詢問一個簡短主題詞（供 slug 使用），若使用者不提供則以 `verify` 作為預設 slug。

## 驗收標準的擷取原則

不論來源為何，從原始文本中辨識驗收標準條目時，優先以下列標記為切分依據：

- Markdown checklist：`- [ ]`、`- [x]`。
- 編號清單：`1.`、`2.`、…。
- 明確標題下的條列：`## 驗收標準`、`## Acceptance Criteria`、`## AC`。
- 句型特徵：「使用者可以…」、「當…時，應…」、「Given …, When …, Then …」。

每條驗收標準以獨立一行或獨立段落為單位，編號為 AC-1、AC-2、…，保留原句以利後續在報告中回顧。

## 歧義情境

- 同一輸入同時符合型態 A 與 B（例如 URL 指向本地 markdown 檔）時，以型態 A 為優先。
- 文本中混雜驗收標準與其他段落（例如 background、non-goals）時，僅擷取驗收標準區塊，忽略其餘。
- 文本中找不到任何可辨識的驗收標準條目時，向使用者回報並停止流程，不進入 Planning。
