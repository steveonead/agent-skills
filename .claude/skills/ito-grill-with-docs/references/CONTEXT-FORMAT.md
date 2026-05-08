# CONTEXT.md 格式

## 結構

```md
# {Context 名稱}

{一至兩句話：這個 context 是什麼、為何存在。}

## 術語

**訂單 (Order)**：
{簡潔的術語定義}
_避免使用_：Purchase、transaction

**發票 (Invoice)**：
交貨後寄給客戶的付款要求。
_避免使用_：Bill、payment request

**客戶 (Customer)**：
下訂單的個人或組織。
_避免使用_：Client、buyer、account

## 關係

- 一個**訂單**產生一張或多張**發票**
- 一張**發票**屬於一個**客戶**

## 情境對話範例

> **開發者：**「當**客戶**下了**訂單**，我們要立刻建立**發票**嗎？」
> **領域專家：**「不，**發票**只在**出貨**確認後才產生。」

## 待釐清的歧義

- 「account」曾被用來指**客戶**和**使用者**兩種概念，已解決：這是兩個不同的概念。
```

## 規則

- **明確取捨。** 當同一個概念有多個詞時，選最好的一個，其他列為「避免使用」的別名。
- **明確標示衝突。** 若某個術語被模糊使用，在「待釐清的歧義」中點出並附上明確的解決方式。
- **定義要精簡。** 最多一句話。定義「這是什麼概念」，不是「它有什麼行為」。
- **呈現關係。** 用粗體標示術語名稱，有明確基數時就表達出來。
- **只放專屬於這個 context 的術語。** 通用程式設計概念（timeout、error type、utility pattern）不屬於這裡，即使專案大量使用也一樣。加入術語前先問：這個概念在這個 context 裡是獨特的嗎？確認「是」才收錄進來。
- **有自然的群組時加小標題。** 若所有術語屬於同一個領域，維持不分組的清單即可。
- **寫一段情境對話。** 開發者和領域專家之間的對話，自然展現術語如何互動並釐清相關概念的邊界。

## 單一 context 與多 context

**單一 context（多數專案）：** 一個 `CONTEXT.md` 放在 repo 根目錄。

**多個 context：** 在 repo 根目錄放一個 `CONTEXT-MAP.md`，列出各 context、位置及其關係：

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — 接收並追蹤客戶訂單
- [Billing](./src/billing/CONTEXT.md) — 產生發票並處理付款
- [Fulfillment](./src/fulfillment/CONTEXT.md) — 管理倉儲揀貨與出貨

## 關係

- **Ordering → Fulfillment**：Ordering 發出 `OrderPlaced` 事件，Fulfillment 消費後開始揀貨
- **Fulfillment → Billing**：Fulfillment 發出 `ShipmentDispatched` 事件，Billing 消費後產生發票
- **Ordering ↔ Billing**：共用 `CustomerId` 和 `Money` 的類型
```

推斷適用哪種結構的規則：

- 若 `CONTEXT-MAP.md` 存在，讀取後找到各 context
- 若只有根目錄的 `CONTEXT.md`，單一 context
- 若兩者都不存在，在第一個術語確認時 lazy 建立根目錄 `CONTEXT.md`

多個 context 存在時，從討論主題推斷屬於哪個 context。若無法推斷，列出 contexts 請使用者選擇。
