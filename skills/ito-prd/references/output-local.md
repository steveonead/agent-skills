# Local 輸出規則（資料擷取用）

本檔案提供 `SKILL.md` 步驟 8 執行 local 輸出時需要的具體規則。從中擷取路徑、命名、gitignore 提示等資料即可，不需要整份執行。

## 路徑與命名

- **預設路徑格式**：`docs/prd/<slug>.md`
- **slug 生成規則**：依 PRD 主題生成 kebab-case
  - 中文主題先翻譯為英文片語
  - 全小寫
  - 以 `-` 連接（e.g., `user-auth-refactor`、`otp-login`）
- **路徑彈性**：agent 展示預設路徑給使用者，允許使用者修改為其他路徑
  - 詢問格式範例：「預設存到 `docs/prd/otp-login.md`，可以嗎？或你要改路徑？」

## 父目錄處理

- 若使用者確認的路徑其父目錄不存在：寫入前先以 `mkdir -p` 建立
- 建立失敗時：回報錯誤並要求使用者確認路徑

## Gitignore 提醒

寫入本地檔案後，向使用者提醒：

> Local PRD 為純 review 用途，建議將 `docs/prd/` 加入 `.gitignore`（issue 才是 source of truth）。

此提醒僅呈現一次，不強制使用者執行。

## 編輯模式覆蓋行為

- 編輯模式輸入為 local path 時：**直接覆蓋原檔案**
- 不詢問輸出目的地（回寫來源）
- 不備份舊檔案（local 僅為 review 輔助，不保留歷史）

## 檔案內容

- 格式完全依 `assets/prd-template.md` 結構
- 填入訪談結果前的必填檢查清單見 `SKILL.md` 步驟 8
- Placeholder（如 `[一到兩句說明...]`）不得殘留

## 寫入後的展示

完成後展示絕對路徑給使用者，供其打開檔案進行完整 review：

```
PRD 已寫入：/absolute/path/to/docs/prd/<slug>.md
```
