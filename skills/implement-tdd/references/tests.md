# 好測試與壞測試

## 好測試

**Integration-style**：透過真實介面測試，不 mock 內部零件。

```typescript
// GOOD：測觀察得到的 behavior
test("使用者可以用合法購物車結帳", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

特徵：

- 測使用者 / caller 真的在意的 behavior
- 只用 public API
- 內部重構不會壞
- 描述 WHAT，不是 HOW
- 每個測試一個 logical assertion

---

## 壞測試

**測實作細節**：跟內部結構耦合。

```typescript
// BAD：用 spy 測「內部」呼叫（跟實作耦合）
// 注意：spy 本身不壞——spy 外部副作用（如「送了 email」）是 OK 的，見 mocking.md
test("checkout 會呼叫 validateCart", async () => {
  const spy = jest.spyOn(internal, "validateCart");
  await checkout(cart, paymentMethod);
  expect(spy).toHaveBeenCalled();
});

// BAD：透過內部狀態驗證
test("結帳後 cart.internalFlag 為 true", async () => {
  await checkout(cart, paymentMethod);
  expect(cart.internalFlag).toBe(true);
});

// BAD：跳過介面直接查 DB
test("結帳後 DB 有紀錄", async () => {
  await checkout(cart, paymentMethod);
  const row = await db.query("SELECT * FROM orders WHERE ...");
  expect(row).toBeDefined();
});
```

特徵：

- 用 spy / mock 檢查內部呼叫
- 讀內部欄位 / private 狀態
- 繞過 public interface 驗證結果
- 重新命名內部函式就會壞
- 測的是 HOW，不是 WHAT

---

## 警訊

**重構沒改 behavior，但測試壞了** → 這個測試測的是實作，不是 behavior。兩個選擇：改測試讓它走 public interface，或直接刪掉。留著它只會阻礙未來的重構。
