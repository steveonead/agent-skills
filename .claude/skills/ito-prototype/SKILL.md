---
name: ito-prototype
description: 建立一次性 prototype 來回答設計問題，依問題性質分為 Logic（terminal TUI 測試狀態機）與 UI（多 variant 瀏覽器切換）兩支。說「做個 prototype」、「先試試看」、「prototype this」、「try a few designs」時使用。不適用於正式功能實作。
---

# ito-prototype

## 概覽

Prototype 是**一次性的程式碼，目的是回答一個問題**。問題的性質決定要走哪個分支，選錯分支整個 prototype 就白做了。

## 使用時機

- 說「做個 prototype」、「先試試看」、「跑個概念驗證」
- 說「prototype this」、「let me play with it」、「try a few designs」
- 想驗證狀態機、資料模型或 API 介面是否符合直覺
- 想在確定設計之前，先在瀏覽器裡看幾個截然不同的版面

**不應使用的情況：** 正式功能實作、需要有測試覆蓋的程式碼、方向已確定只需要直接寫的任務。

## 核心流程

### 步驟 1：判斷分支

從使用者的問題、周圍的程式碼，或直接開口問，判斷問題的本質：

- **「這個邏輯或狀態模型感覺對嗎？」** → 讀取 `LOGIC.md`，建立 terminal TUI。
- **「這個畫面應該長什麼樣子？」** → 讀取 `UI.md`，生成多個 UI variant。

兩個分支的產出截然不同，判斷錯誤等於浪費整個 prototype。若問題真的模稜兩可、使用者又不在線，以周圍程式碼為準（後端模組 → Logic，頁面或元件 → UI），並在 prototype 頂端說明這個假設。

### 步驟 2：執行對應分支

依判斷結果讀取對應文件：

- Logic 分支：讀取 `LOGIC.md`
- UI 分支：讀取 `UI.md`

### 步驟 3：完成後記錄答案

Prototype 回答完問題後，在 prototype 旁邊建立 `NOTES.md`：

```
## 問題
[這個 prototype 要回答什麼]

## 答案
[prototype 教會你什麼]

## 下一步
[刪掉 prototype，或把哪些部分移進正式程式碼]
```

## 兩個分支都適用的規則

1. **一次性，且清楚標示。** 把 prototype 放在實際會用到它的模組或頁面旁邊，但命名要讓讀者一眼看出這不是正式程式碼。
2. **一個指令就能跑。** 使用專案既有的 task runner（`pnpm [name]`），使用者不必思考怎麼啟動。
3. **預設不持久化。** 狀態存在記憶體裡。若問題本身涉及資料庫，用 scratch DB 或本地檔案，命名帶「PROTOTYPE」字樣並標注「可以刪除」。
4. **跳過打磨。** 不寫測試、不做超出「讓 prototype 能跑」所需的錯誤處理、不做抽象化。目標是快速學到東西然後刪掉它。
5. **呈現狀態。** 每次操作後（Logic）或切換 variant 時（UI），印出或渲染完整的相關狀態，讓使用者看到發生了什麼。
6. **回答完就刪掉或吸收進去。** Prototype 完成任務後，要嘛刪掉，要嘛把驗證過的決策摺進正式程式碼，不要讓它在 repo 裡慢慢腐爛。

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|---|---|
| 「使用者說可以了，直接跳過分支判斷」 | 分支選錯會浪費整個 prototype，確認一句話永遠值得 |
| 「先把 prototype 寫好，NOTES.md 之後再補」 | Prototype 的價值在答案，不在程式碼，事後幾乎不會回頭補 |
| 「多加一點錯誤處理比較安全」 | 多餘的處理會模糊掉真正要問的問題，違背 prototype 的目的 |

## 警訊

- Prototype 裡有測試或完整的錯誤處理
- 狀態機邏輯和 TUI shell 混在一起（Logic 分支）
- UI variant 之間差異太小，只是顏色或文案不同
- 沒有 `NOTES.md` 就宣告 prototype 完成

## 驗證

- [ ] 一個指令可以啟動 prototype
- [ ] 每次操作後有完整狀態輸出
- [ ] `NOTES.md` 已建立，問題與答案均已填寫

## 延伸參考

- `LOGIC.md`：terminal TUI 分支的詳細流程
- `UI.md`：UI variant 分支的詳細流程
