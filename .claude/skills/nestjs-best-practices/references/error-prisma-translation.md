---
rule: error-prisma-translation
category: 錯誤處理
tags: [error, prisma, http-exception]
---

# 在邊界轉譯 Prisma known error

> 在 service / repository 邊界把 Prisma 的 known error（如 `P2002` 唯一鍵衝突、`P2025` 找不到）轉譯成對應的 `HttpException`，別讓 Prisma 例外直接漏到 controller 或 client。

## 原因

- Prisma 例外帶有資料庫層的訊息與欄位細節，直接回給 client 會洩漏 schema 資訊。
- 沒轉譯的話，唯一鍵衝突這類本該回 409 的錯誤會變成未處理的 500，狀態碼失真。
- 在資料邊界統一轉譯，business 層以上只需面對語意明確的 HTTP 例外。

## ❌ Bad

```ts
@Injectable()
export class UsersService {
  async create(dto: CreateUserDto) {
    // email 重複時，Prisma 直接拋 P2002，未處理會變成 500 並漏出 DB 細節
    return this.prisma.user.create({ data: dto });
  }
}
```

唯一鍵衝突未被攔截，回應變成 500 且夾帶 Prisma 的內部訊息。

## ✅ Good

```ts
import { Prisma } from '@prisma/client';

@Injectable()
export class UsersService {
  async create(dto: CreateUserDto) {
    try {
      return await this.prisma.user.create({ data: dto });
    } catch (error) {
      if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2002') {
        throw new ConflictException('Email already exists');
      }
      throw error;
    }
  }
}
```

在邊界判斷 `P2002` 並轉譯成 `ConflictException`（409），語意明確且不外洩資料庫細節。其餘未知例外往上拋，交給全域 filter 處理。
