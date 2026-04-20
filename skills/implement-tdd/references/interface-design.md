# 為可測試性設計介面

好介面讓測試變得自然。三個原則：

## 1. 接受依賴，不要自己造

```typescript
// 可測
function processOrder(order, paymentGateway) {}

// 難測
function processOrder(order) {
  const gateway = new StripeGateway();
}
```

自己 new 依賴 = 測試無法抽換 = 只能被迫連到真實系統。

## 2. 回傳結果，不要產生 side effect

```typescript
// 可測
function calculateDiscount(cart): Discount {}

// 難測
function applyDiscount(cart): void {
  cart.total -= discount;
}
```

回傳值只要 `expect(result).toEqual(...)` 就能測；side effect 要先 mutate 再斷言 mutated 狀態，而且常常逼測試去讀內部欄位（見 `tests.md` BAD 範例），跟實作耦合。

## 3. 介面表面積要小

- 方法越少 → 測試越少
- 參數組合爆炸越慢
- 使用者（人或程式）學習成本越低

如果介面有 20 個方法，八成有三分之二其實是內部輔助函式被誤暴露——拉回去改 private，專注讓剩下的方法做得深。
