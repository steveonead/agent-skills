---
rule: migration-pin-safe-version
category: 版本與遷移
tags: [migration, version, server-lifecycle, flaky]
---

# 釘在修好 server lifecycle 的版本以上

> supertest `7.0.0` 到 `7.1.1` 的 server lifecycle 尚未補齊（server re-use race、Express 並發、multipart 卡住等），請釘在 `7.1.3+` 搭 superagent `10.2.2+`。

## 原因

- v7.0.0 剛換上 superagent v9，v7.1.0 才修 server re-use 的 race condition，但要到 v7.1.2 / v7.1.3 搭 superagent v10.2.2 才真正補齊 server lifecycle、callback 處理、multipart 卡住與 `agent.query()` 被 HTTP verb 覆蓋等問題。
- 卡在中間版本時，症狀是 e2e 測試在本機會過、在 CI 平行跑卻偶發 flaky，非常難查。
- 直接釘安全版本是最便宜的修法，比事後追 race condition 划算太多。

## ❌ Bad

```jsonc
// 用了剛發布、lifecycle 還沒修好的版本
{
  "devDependencies": {
    "supertest": "7.0.0" // server re-use race condition 尚未修正
  }
}
```

停在 `7.0.0`～`7.1.1`，等於把已知的並發 bug 帶進 CI，換來難以重現的 flaky 測試。

## ✅ Good

```jsonc
{
  "devDependencies": {
    "supertest": "^7.1.3", // server lifecycle、callback、multipart 都已修正
    "superagent": "^10.2.2"
  }
}
```

把版本下限設在修正完成之後，並讓 superagent 一起對齊。實務上裝最新的穩定版即可，重點是不要停留在已知有並發問題的區間。

## 補充

- 對應的官方修正在 supertest commit `6d060e3`（feat: fix server lifecycle, callback handling, and SuperAgent v10 compatibility）。
- server 不關導致卡住的另一面見 `cleanup-close-app`。
