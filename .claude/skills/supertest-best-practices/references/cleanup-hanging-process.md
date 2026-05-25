---
rule: cleanup-hanging-process
category: 清理與生命週期
tags: [cleanup, vitest, hanging-process, open-handle, debug]
---

# 卡住時用 Vitest 的 hanging-process reporter

> 測試跑完 process 不退出時，用 Vitest 的 `hanging-process` reporter 印出阻止結束的 handle，別急著套 `--no-file-parallelism` 或強制 kill process 來掩蓋。

## 原因

- Vitest 沒有 Jest 的 `--detectOpenHandles`，對應工具是內建的 `hanging-process` reporter，底層用 `why-is-node-running` 列出殘留的 timer、socket、connection。
- 直接看到是哪個 handle 沒關，才能對症下藥（通常是漏關的 app、DB 連線，或 middleware 裡沒清的 `setInterval` / `setTimeout`）。
- 用 `--no-file-parallelism`、`--bail` 或手動 kill 只是把症狀蓋掉，根本問題還在，CI 仍會不穩。

## ❌ Bad

```bash
# process 卡住，直接關平行化掩蓋問題，沒查出真正沒關的 handle
vitest run --no-file-parallelism
```

關掉平行化只是讓問題比較不容易浮現，沒釋放的 handle 依舊存在，換個環境又會卡。

## ✅ Good

```bash
# 印出阻止 process 結束的 handle，定位根因
vitest run --reporter=hanging-process
```

```ts
// 例如查出是 middleware 的 timer 沒清，補上清理
const timer = setInterval(refill, 1000);
// ...
clearInterval(timer); // 測試結束前確實清掉
```

先用 reporter 找出殘留 handle，再回到對應的 app、連線或 timer 把它關掉，從根本解決卡住。

## 補充

- 最常見的殘留是漏關 app（見 `cleanup-close-app`）與沒釋放的 DB 連線（見 `isolation-test-db`）。
- 確認沒有殘留 handle 後再考慮平行化設定，順序別反過來。
