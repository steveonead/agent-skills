---
rule: cli-run-not-watch
category: CLI 執行
tags: [cli, run, watch, ci, ai-pitfall]
---

# 跑測試用 `vitest run`，不要用裸 `vitest`

> Vitest 預設進 watch mode，會停在前景等待檔案變動。CI、agent 或任何一次性執行都要用 `vitest run` 或 `vitest --run`，否則程序不會結束，自動化流程會停滯或逾時。

## 原因

- 裸 `vitest` 預設開 watch，會停在前景等待檔案變動，agent 或 CI 因此一直無法結束
- Vitest 會嘗試偵測 CI 與非互動環境自動關掉 watch，但偵測不一定可靠
- `vitest run` 跑完即退出，並回傳正確的 exit code 供 CI / agent 判斷成敗

## ❌ Bad

```bash
# agent 或 CI 直接下，會停在 watch mode 等待
vitest
vitest src/userService.test.ts
```

## ✅ Good

```bash
# 跑一次就結束
vitest run
vitest run src/userService.test.ts

# run 等價於 --run flag
vitest --run
```

`package.json` 建議把兩種用途分開：`"test": "vitest run"` 給 CI 與 agent，`"test:watch": "vitest"` 留給本機開發。
