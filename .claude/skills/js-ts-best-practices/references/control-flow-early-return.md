---
rule: control-flow-early-return
category: control-flow
tags: [control-flow, readability, guard-clause]
---

# 邊界條件 early return，禁深層巢狀

> 邊界條件與失敗情況先處理並 return，主邏輯維持在最外層，禁止寫成多層 `if-else` 包裹。

## 原因

- 巢狀越深，閱讀時要追蹤的條件越多，認知負擔線性上升
- Early return 等於把錯誤路徑收斂在函式開頭，主流程一眼看完
- 後續加新邊界條件時，加一行 guard 就好，不必動既有縮排

## ❌ Bad

```ts
function validateUser(user: User | null): boolean {
  if (user) {
    if (user.email) {
      if (user.age && user.age >= 18) {
        return true;
      } else {
        return false;
      }
    } else {
      return false;
    }
  } else {
    return false;
  }
}
```

四層巢狀，主邏輯被推到最內層，每多一個條件就再縮一層，後續難維護。

## ✅ Good

```ts
function validateUser(user: User | null): boolean {
  if (!user) return false;
  if (!user.email) return false;
  if (!user.age || user.age < 18) return false;

  return true;
}
```

每個 guard 各管一件事，主結果留在最後一行，加新條件只需插一行。
