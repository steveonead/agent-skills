---
rule: error-builtin-http-exception
category: 錯誤處理
tags: [error, http-exception]
---

# 用內建 HttpException 子類別

> 在 service 拋錯時用 NestJS 內建的 `HttpException` 子類別（`NotFoundException`、`BadRequestException` 等），別自己拼 status code 或回傳錯誤物件。

## 原因

- 內建例外類別自帶正確的 HTTP status 與標準回應格式，NestJS 的 exception layer 會自動處理。
- service 回傳 `{ error: ... }` 這種自訂錯誤物件，會讓 controller 多寫判斷邏輯，且狀態碼容易寫錯。
- 統一用內建例外，全應用的錯誤語意一致，前端也能依 status code 一致處理。

## ❌ Bad

```ts
@Injectable()
export class UsersService {
  async findById(id: string) {
    const user = await this.repo.findById(id);
    if (!user) {
      // 回傳自訂錯誤物件，controller 還得自己判斷、自己決定 status
      return { error: 'USER_NOT_FOUND' };
    }
    return user;
  }
}
```

用回傳值表達錯誤，呼叫端得層層判斷，狀態碼也得手動對應，容易不一致。

## ✅ Good

```ts
@Injectable()
export class UsersService {
  async findById(id: string) {
    const user = await this.repo.findById(id);
    if (!user) {
      throw new NotFoundException(`User ${id} not found`);
    }
    return user;
  }
}
```

直接拋 `NotFoundException`，NestJS 自動回 404 與標準錯誤格式，controller 不需任何額外處理。
