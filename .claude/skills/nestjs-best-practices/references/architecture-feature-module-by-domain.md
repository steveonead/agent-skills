---
rule: architecture-feature-module-by-domain
category: 模組與分層架構
tags: [architecture, module, structure]
---

# 依業務領域切 feature module

> 用業務領域劃分 module，每個領域一個資料夾，不要在 root 放 `controllers/`、`services/` 這種技術分層資料夾。

## 原因

- 依領域分組讓相關程式碼放在一起，改一個功能不用在多個技術資料夾間跳來跳去。
- 技術分層（所有 controller 一包、所有 service 一包）在專案長大後會變得雜亂，邊界模糊。
- 領域模組天然對應團隊分工與後續可能的 lazy loading 切割。

## ❌ Bad

```
src/
  controllers/
    users.controller.ts
    orders.controller.ts
  services/
    users.service.ts
    orders.service.ts
  repositories/
    users.repository.ts
    orders.repository.ts
```

依技術型別分資料夾，要動 `orders` 功能得橫跨三個資料夾，模組邊界不存在。

## ✅ Good

```
src/
  users/
    dto/
    users.controller.ts
    users.service.ts
    users.repository.ts
    users.module.ts
  orders/
    dto/
    orders.controller.ts
    orders.service.ts
    orders.repository.ts
    orders.module.ts
  common/        # 只放真正跨領域的 guard / pipe / interceptor / decorator
  app.module.ts
```

每個領域自成一個資料夾與 module，職責內聚，邊界清楚。`common/` 只收真正跨領域的東西。
