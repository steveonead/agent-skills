# [slug] — 驗證報告

## Summary

- 驗證時間：[YYYY-MM-DD HH:MM:SS +TZ]
- 驗證目標來源：[issue URL / 檔案路徑 / inline text]
- 使用工具：[playwriter / Playwright MCP / Chrome DevTools MCP / ...]
- 結果統計：✅ [N] ／ ❌ [M] ／ ⏭️ [K]
- 工具能力限制提醒（可選）：[例如 console log 未取得]

## 每條驗收標準

### AC-1：[原始驗收標準句]

- 狀態：✅ Pass ／ ❌ Fail ／ ⏭️ Skipped — [原因類別]：[一句話說明]
- 執行步驟：
  1. [操作 1]
  2. [操作 2]
- 預期：[預期觀察結果]
- 實際：[實際觀察結果]

#### Evidence（僅 Fail 項）

- **Screenshot**：[路徑或嵌入]
- **Console**：
  ```
  [完整 log 內容]
  ```
- **DOM**：
  ```html
  <!-- 失敗元素及上層容器 -->
  ```
  Selector：`[可複製的 CSS selector 或 XPath]`
- **Network**：
  | Method | URL | Status | Notes |
  |---|---|---|---|
  | [METHOD] | [URL] | [code] | [payload／response 摘要] |
- **Actual vs Expected**：
  | 項目 | 預期 | 實際 |
  |---|---|---|
  | [項目 1] | [預期值] | [實際值] |

### AC-2：...

（依上述格式重複）

## TDD Prove-it Reproduction Spec

僅列出 Fail 項，供 `ito-tdd` Prove-it 變體直接取用。

### AC-[N]：[原始驗收標準句]

- **失敗操作序列**：
  1. [動作 + 目標元素 + 輸入值]
  2. ...
- **Failure Signature**：[一句話描述失敗本質]
- **URL／User／State Context**：
  - URL：[失敗當下 URL]
  - User：[email 或 user id，勿含密碼]
  - State：[相關 app 狀態，如 cart=2, step=2]
- **相關 API Response 或 DOM 節點**：
  ```json
  {
    "[欄位]": "[值]"
  }
  ```

---

備註：本報告為事實紀錄，不含整體 PASS／FAIL 結論；是否收貨由使用者依報告內容裁量。
