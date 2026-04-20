## 描述

<AC 原文。例：「使用者提交表單後，錯誤狀態按鈕應顯示紅色邊框」>

## 失敗證據

<驗證失敗的具體證據。依驗證手段分類：

Integration test：
- 測試檔：<relative-path>
- 測試名稱：<test-name>
- 輸出摘要（最多 20 行）：
  ```
  <stdout/stderr>
  ```

MCP 互動驗證：
- MCP：<tool-name>
- 失敗步驟：<第 N 步 — 描述>
- 錯誤訊息：<message>
- 截圖 / DOM 片段：<若 MCP 支援則附 reference>
>

## 重現步驟

<依 AC 展開的人工重現路徑（1-4 步），讓工程師不需讀 MCP log 就能重跑。>

1. <step 1>
2. <step 2>
3. <step 3>

## 相關連結

- 對應 PRD：#<prd-number>
- 對應 task sub-issue：#<task-number>（若可辨識；無法辨識時省略此行）

## 驗證對照

- PRD：#<prd-number>
- AC 編號：<n>
- AC 雜湊：`<8-char-sha1>`
- 最後驗證：<ISO-date>
- 分類：<ui|non-ui>
- 對應 package：<package-name|n/a>
