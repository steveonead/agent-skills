---
rule: migration-superagent-bump
category: 版本與遷移
tags: [migration, superagent, breaking-change, upload]
---

# 升級到 v7 時，連帶處理 superagent 的 breaking change

> SuperTest v7 把底層 superagent 從 v8 拉到 v9 / v10，supertest 自身 API 幾乎沒變，真正會踩到雷的是 superagent 的行為改動。

## 原因

- supertest 本質是 superagent 的薄封裝，request、回應解析、multipart 上傳全部走 superagent，所以 superagent 的 breaking change 會直接傳遞上來。
- v7.0 對應 superagent v9，v7.1.2+ 對應 superagent v10。superagent v10 把檔案上傳用的 formidable 升到 v3，multipart / form-data 的解析與回應處理因此改變。
- 升級後若出現上傳測試卡住、回應 body 解析不到、或型別對不上，根因通常不在 supertest 而在 superagent。

## ❌ Bad

```jsonc
// package.json：升了 supertest，卻沒注意底層 superagent 一起跳大版號
{
  "devDependencies": {
    "supertest": "^7.0.0"
    // 以為只是 supertest 小升級，沿用 v6 時代的上傳測試寫法，
    // 結果 multipart 測試在 CI 偶發卡住，誤判成 supertest 的 bug
  }
}
```

把升級當成單純的 supertest 版本變動，忽略 superagent 才是行為來源，排查方向會整個偏掉。

## ✅ Good

```jsonc
// package.json：明確認知 supertest v7.1.2+ = superagent v10 這條鏈（v7.0~7.1.1 是 superagent v9）
{
  "devDependencies": {
    "supertest": "^7.1.3",
    "superagent": "^10.2.2" // 顯式對齊，遇到上傳 / 回應問題先查 superagent changelog
  }
}
```

升級前先把 supertest 與 superagent 視為一組相依，遇到行為差異時直接對照 superagent 的版本紀錄，而不是只盯著 supertest。檔案上傳相關測試在升級後要重跑驗證。

## 補充

- supertest v7 要求 Node.js `>= 14.18`，這部分由 `package.json` engines 與 npm 自動把關，不需另立規則。
- 與上傳相關的具體寫法見 `request-file-upload`。
