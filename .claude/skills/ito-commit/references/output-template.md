# Commit 計畫輸出格式與 type 對照

本檔案供 `SKILL.md` 步驟 5 與步驟 7 擷取輸出模板與 Conventional Commits 的 type 對照。所有文字一律使用當次確認的語言，不得於同一則計畫中混用。

## 標準模式（多個 commits）

**中文：**

```
Commit 計畫：

Commit 1: <type>(<scope>): <message>
詳細內容：
- <改動描述 1>
- <改動描述 2>
檔案：
- path/to/file1
- path/to/file2

Commit 2: <type>(<scope>): <message>
詳細內容：
- <改動描述>
檔案：
- path/to/file3
```

**English:**

```
Commit Plan:

Commit 1: <type>(<scope>): <message>
Changes:
- <change description 1>
- <change description 2>
Files:
- path/to/file1
- path/to/file2

Commit 2: <type>(<scope>): <message>
Changes:
- <change description>
Files:
- path/to/file3
```

## 快速模式（單一 commit）

**中文：**

```
<type>(<scope>): <message>
詳細內容：
- <改動描述 1>
- <改動描述 2>
檔案：
- path/to/file1
- path/to/file2
```

**English:**

```
<type>(<scope>): <message>
Changes:
- <change description 1>
- <change description 2>
Files:
- path/to/file1
- path/to/file2
```

## Conventional Commits type 對照

| type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修 bug |
| `docs` | 文件變更 |
| `style` | 格式調整（不影響邏輯） |
| `refactor` | 重構（非新功能、非 bug fix） |
| `perf` | 效能改善 |
| `test` | 新增或修正測試 |
| `build` | 建構系統或外部相依 |
| `chore` | 雜務（依賴更新、維護任務） |
| `ci` | CI/CD 設定 |
| `revert` | 還原先前 commit |
