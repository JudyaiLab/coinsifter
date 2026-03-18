# CoinSifter

[English](README.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md)

**你設定條件，它幫你找幣。**

CoinSifter 是一款開源加密貨幣篩選工具，自動掃描 Binance 上符合你自訂技術條件的幣種。

## 功能特色

- **8 種技術指標**：RSI、EMA、EMA 交叉、MACD、布林通道、KD 隨機指標、成交量、ATR
- **多時間框架**：同時篩選 4H、1H、15m、1D
- **策略系統**：透過 YAML 檔案儲存和載入篩選策略
- **跨平台**：Windows、Mac、Linux

## 快速開始

### 1. 安裝

```bash
git clone https://github.com/JudyaiLab/coinsifter.git
cd coinsifter
pip install -r requirements.txt
```

### 2. 設定

```bash
cp config.example.yaml config.yaml
# 編輯 config.yaml，填入你的 Binance API Key（唯讀權限即可）
```

### 3. 執行

```bash
# 先試試 Demo 模式（不需要 API Key）
python coinsifter.py --demo

# 使用預設設定
python coinsifter.py

# 使用指定策略
python coinsifter.py -s strategies/custom_template.yaml

# 詳細模式 — 顯示指標數值
python coinsifter.py -v

# 循環模式（每 4 小時掃描一次，interval 單位為分鐘）
python coinsifter.py --loop --interval 240
```

## 策略檔案

策略是簡單的 YAML 檔案。完整範本請參考 `strategies/custom_template.yaml`：

```yaml
name: "My Strategy"
filter_mode: "and"
filters:
  - indicator: rsi
    timeframe: 4h
    period: 14
    condition: between
    value: [50, 70]
  - indicator: ema
    timeframe: 4h
    period: 50
    condition: price_above
  - indicator: volume
    timeframe: 1h
    condition: above_average
    multiplier: 1.5
```

**支援的指標**（[新手指標教學](docs/indicators-guide.md)）：

| 指標 | 條件 | 參數 |
|------|------|------|
| RSI | `above`、`below`、`between` | `period`（預設：14） |
| EMA | `price_above`、`price_below`、`slope_up`、`slope_down` | `period`（預設：20） |
| MACD | `bullish`、`bearish`、`above_zero`、`below_zero` | — |
| 布林通道 | `above_lower`、`below_upper`、`inside` | `period`（預設：20）、`std` |
| KD | `golden_cross`、`death_cross`、`oversold`、`overbought`、`k_above_d` | `period`（預設：14） |
| 成交量 | `above_average` | `multiplier`（預設：1.5） |
| EMA 交叉 | `golden_cross`、`death_cross`、`ema20_above_50`、`ema20_below_50` | — |
| ATR | `above` | `period`（預設：14）、`value` |

## 系統需求

- Python 3.10+
- Binance 帳號及 API Key（唯讀權限即可）— [免費註冊 Binance 帳號](https://accounts.binance.com/register?ref=956950981)
- 網路連線
- 相依套件：ccxt、numpy、pandas、pyyaml（詳見 `requirements.txt`）

## CoinSifter Pro

想要更多功能？**CoinSifter Pro** 包含：

- **網頁介面** — 瀏覽器深色主題儀表板，免開終端機
- **排程掃描** — 設定一次自動定時掃描
- **Telegram 通知** — 符合條件時即時推播
- **預建策略** — 經回測驗證、場外勝率 75%+ 的策略
- **一鍵啟動器** — Windows 和 Mac 捷徑

👉 [取得 CoinSifter Pro](https://judyailab.com/shop/)

## 授權

MIT — 詳見 [LICENSE](LICENSE)

## 連結

- 部落格：[judyailab.com](https://judyailab.com)
- Twitter/X：[@JudyaiLab](https://x.com/judyailab)
