# 🎮 OpenClaw Pixel 公司模擬器 MVP - 提案

## 目標

創建一個與 OpenClaw 系統真實連結的 Pixel 風格公司經營遊戲。

---

## MVP 功能

### 1. 創建 Pixel 角色
- 選擇像素風格頭像
- 輸入名字
- 設定職業

### 2. 與 OpenClaw 系統連結
```
🦞 你的 OpenClaw 帳號
├─ 已安裝的 Skills → 員工技能
├─ 排程任務 → 公司任務
├─ API 使用量 → 金幣資源
└─ Agent 數量 → 員工數
```

### 3. 員工系統（真實對應）
| 員工 | 來源 | 技能 |
|------|------|------|
| 雪 (Snow) | OpenClaw Agent | 搜尋、執行任務 |
| Job Hunter | Cron 排程 | 搜尋職缺 |
| AI 監控 | Cron 排程 | 監控 AI 動態 |
| 其他 Skills | 已安裝 Skills | 各種能力 |

### 4. 任務系統（真實執行）
- 每日任務來自排程
- 執行結果作為任務獎勵
- 與真實 OpenClaw 運行的任務同步

### 5. 資源儀表板
- Token 消耗量
- 排程執行次數
- Skills 使用統計

---

## 數據來源

```python
# 從 OpenClaw 獲取
- ~/.openclaw/skills/ → 員工列表
- ~/.openclaw/openclaw.json → 排程任務
- ~/.openclaw/logs/ → 使用統計
- cron jobs → 任務歷史
```

---

## UI 設計

- Pixel 風格頭像
- 簡單的 8-bit 配色
- 顯示真實數據

---

這個方向對嗎？