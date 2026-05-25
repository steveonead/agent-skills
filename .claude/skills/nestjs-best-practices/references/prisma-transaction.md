---
rule: prisma-transaction
category: Prisma 整合
tags: [prisma, transaction, atomicity]
---

# 多步驟寫入用 $transaction

> 一個操作牽涉多筆寫入且必須一起成功或一起失敗時，用 `prisma.$transaction` 包起來，確保原子性。

## 原因

- 多筆寫入若沒包在交易裡，中途失敗會留下寫一半的資料，造成不一致。
- `$transaction` 保證全部成功才提交，任一步失敗就整批 rollback。
- 互動式交易（傳 callback）能在交易內依前一步結果決定後續操作。

## ❌ Bad

```ts
async transfer(fromId: string, toId: string, amount: number) {
  // 兩筆更新沒包交易，第二筆失敗會留下扣了款卻沒入帳的狀態
  await this.prisma.account.update({
    where: { id: fromId },
    data: { balance: { decrement: amount } },
  });
  await this.prisma.account.update({
    where: { id: toId },
    data: { balance: { increment: amount } },
  });
}
```

兩筆更新各自獨立，第二筆若失敗，資料就停在扣款成功但入帳失敗的不一致狀態。

## ✅ Good

```ts
async transfer(fromId: string, toId: string, amount: number) {
  await this.prisma.$transaction(async (tx) => {
    await tx.account.update({
      where: { id: fromId },
      data: { balance: { decrement: amount } },
    });
    await tx.account.update({
      where: { id: toId },
      data: { balance: { increment: amount } },
    });
  });
}
```

兩筆更新包在 `$transaction` 內，任一步失敗整批 rollback，帳務不會停在中間狀態。
