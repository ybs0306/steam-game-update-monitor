# Steam Game Update Monitor

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

監控指定 Steam 遊戲的更新狀態，並透過 Telegram 發送通知。

## 功能

* 監控多個 Steam 遊戲的 BuildID 變化
* 支援批次查詢以減少 API 請求
* 支援 Telegram 通知
* 自動儲存遊戲更新狀態

## 安裝

### 1. 專案執行前置

#### clone 專案

```bash
git clone https://github.com/ybs0306/steam-game-update-monitor.git
cd steam-game-update-monitor
```

#### 使用 uv 執行程式

專案使用 uv 管理套件  
此專案 python version 需要 >=3.12

* 如何安裝 uv

> [使用 uv 管理 Python 環境](https://dev.to/codemee/shi-yong-uv-guan-li-python-huan-jing-53hg)
> Windows 推薦用 `scoop` 直接裝

### 2. 準備外部執行程式

#### SteamCMD

用來訪問 Steam server 的工具

- 下載 [SteamCMD](https://developer.valvesoftware.com/wiki/SteamCMD)
找一個地方建立單獨的資料夾存放此程式

### 3. 平台通知機器人

#### Telegram

- 取得自身的 Telegram user ID
    - 如果你使用公開機器人取得，例如 `@userinfobot`，請**千萬記得檢查拼寫正確與否**，有非常多的仿冒機器人，仿冒機器人可能會記錄你的 user ID 與其他資訊
- 使用 Telegram BotFather 申請一個 bot，並保管好 bot token，後續會使用到

## 使用方法

### 設定

將 3 個範例檔案 `./config/games.example.json`, `./config/secrets.example.json`, `./config/targets.example.json`

各複製一份到同路徑下，並且把檔名內的 ".example" 字樣刪除，並進行下列配置

#### 1. 檢查遊戲清單 (`games.json`)

```json
{
    "games": [
        { "appid": "<APP_ID_1>", "name": "<GAME_NAME_1>" },
        { "appid": "<APP_ID_2>", "name": "<GAME_NAME_2>" }
    ],
    "steamcmd_path": "<ABSOLUTE_PATH_TO_STEAMCMD>",
    "query_batch_size": 10
}
```

* `appid` (require)：要檢查 Steam 遊戲的 AppID
* `name` (optional)：要檢查 Steam 遊戲的自訂名稱，此欄位不存在時，將使用官方預設遊戲名稱
* `steamcmd_path` (require)：steamcmd.exe 的絕對路徑
* `query_batch_size` (require)：指定批次查詢數量，減少 API 請求次數

#### 2. 機密資訊 (`secrets.json`)

```json
{
    "telegram_bot_token": "<YOUR_TELEGRAM_BOT_TOKEN>"
}
```

* `telegram_bot_token` (require)：填入通知時所使用的 bot token

#### 3. 通知目標 (`targets.json`)

```json
{
    "telegram": {
        "chat_ids": [
            "<TELEGRAM_CHAT_ID_1>",
            "<TELEGRAM_CHAT_ID_2>"
        ]
    }
}
```

* `chat_ids` (require)：填入需要接收通知的使用者

### 執行

直接執行主程式：

```bash
uv run main.py
```

程式會：

1. 讀取設定檔與狀態檔
2. 檢查遊戲的 BuildID 是否變動
3. 若有更新，發送通知
4. 若有更新，儲存最新狀態到 `data/state.json`

### 日誌

日誌檔會自動生成並記錄程式執行資訊，包括檢查結果與錯誤訊息。

### 注意事項

* 首次執行時，程式只會記錄當前 BuildID，不會發送通知。
* 確保 `steamcmd_path` 路徑正確，否則程式無法抓取遊戲資訊。
* 使用者必須先與對應的 Telegram bot 傳送至少一次 `/start` 訊息，才能接收 bot 發送的通知 (Telegram API 的保護機制)。
