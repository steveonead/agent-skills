# 何時 Mock

只在**系統邊界** mock：

- 外部 API（金流、email、推播等）
- 資料庫（有時——能用 test DB 就優先用 test DB）
- 時間 / 亂數
- 檔案系統（有時）

**不要** mock：

- 你自家的類別 / 模組
- 內部 collaborator
- 任何你控制的東西

原因：mock 自家模組 = 把測試釘在你**當下**的實作結構上。搬檔案、改依賴方向、重命名，測試就壞——但 behavior 根本沒變。這種測試會阻礙重構。

---

## 為可 mock 而設計介面

在系統邊界，把介面設計成容易 mock：

### 1. 依賴注入

把外部依賴從外面傳進來，而不是內部自己 new：

```typescript
// 容易 mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// 難 mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

### 2. 介面要小

只暴露你真正用到的方法，不是整個 SDK。Mock 只需要實作 2-3 個 method，而不是百來個。

### 3. 回傳值優於 side effect

Mock 回傳值比 mock 「它有沒有被呼叫」直觀得多，也比較不會跟實作細節耦合。

---

## Mock 的兩個用途

混淆這兩個用途是測試品質崩壞的常見原因：

1. **Stub**：讓外部依賴回傳預先安排好的資料，用來驅動被測系統的 behavior
2. **Spy / Verify**：檢查某個呼叫真的發生了（用於驗證「送了 email」這類**副作用本身就是 behavior**的情況）

絕大多數測試要的是 stub，不是 spy。**預設先用 stub**；只有當副作用本身是外部可觀察的 behavior（例如「下單後會發送 email」），才用 spy。
