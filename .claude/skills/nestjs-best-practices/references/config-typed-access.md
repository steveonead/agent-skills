---
rule: config-typed-access
category: 設定管理
tags: [config, typed, registerAs]
---

# 用 registerAs + ConfigService 取 typed config

> 設定分組用 `registerAs` 定義 namespace，取值透過注入的 `ConfigService<T>`，不要在各處直接讀 `process.env`。

## 原因

- 各處散落 `process.env.XXX` 會讓設定來源失控，也拿不到型別，key 打錯不會被發現。
- `registerAs` 把相關設定分組成 typed config，注入後欄位有型別、有自動完成。
- 透過 `ConfigService` 取值，設定的讀取集中且可測試，不直接耦合到 `process.env`。

## ❌ Bad

```ts
@Injectable()
export class StorageService {
  upload(file: Buffer) {
    // 各處直接讀 process.env，key 打錯不會報錯，且沒型別
    const bucket = process.env.S3_BUKCET; // typo 不會被發現
    const region = process.env.S3_REGION;
  }
}
```

直接讀 `process.env`，typo 與缺漏無從察覺，型別也是 `string | undefined`。

## ✅ Good

```ts
export const s3Config = registerAs('s3', () => ({
  bucket: process.env.S3_BUCKET!,
  region: process.env.S3_REGION!,
}));

@Injectable()
export class StorageService {
  constructor(
    @Inject(s3Config.KEY)
    private readonly config: ConfigType<typeof s3Config>,
  ) {}

  upload(file: Buffer) {
    const { bucket, region } = this.config; // typed，欄位有自動完成
  }
}
```

設定分組成 `s3` namespace，注入後是 typed 物件，欄位打錯編譯期就會報錯，讀取來源集中可控。
