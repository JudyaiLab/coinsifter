# CoinSifter

[English](README.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md)

**조건을 설정하면, 코인을 찾아줍니다.**

CoinSifter는 사용자가 설정한 기술적 조건에 맞는 암호화폐를 바이낸스에서 자동으로 스캔하는 오픈소스 스크리닝 도구입니다.

## 주요 기능

- **8가지 기술 지표**: RSI, EMA, EMA 크로스, MACD, 볼린저 밴드, KD(스토캐스틱), 거래량, ATR
- **멀티 타임프레임**: 4H, 1H, 15m, 1D 동시 스캔
- **전략 시스템**: YAML 파일로 스크리닝 전략 저장 및 불러오기
- **크로스 플랫폼**: Windows, Mac, Linux

## 빠른 시작

### 1. 설치

```bash
git clone https://github.com/JudyaiLab/coinsifter.git
cd coinsifter
pip install -r requirements.txt
```

### 2. 설정

```bash
cp config.example.yaml config.yaml
# config.yaml을 편집하여 Binance API 키를 입력하세요 (읽기 전용 권한이면 충분합니다)
```

### 3. 실행

```bash
# 먼저 데모 모드를 실행해 보세요 (API 키 불필요)
python coinsifter.py --demo

# 기본 설정으로 실행
python coinsifter.py

# 특정 전략 사용
python coinsifter.py -s strategies/custom_template.yaml

# 상세 모드 — 지표 수치 표시
python coinsifter.py -v

# 루프 모드 (4시간마다 스캔, interval 단위는 분)
python coinsifter.py --loop --interval 240
```

## 전략 파일

전략은 간단한 YAML 파일입니다. 전체 템플릿은 `strategies/custom_template.yaml`을 참고하세요:

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

**지원되는 지표** ([초보자 가이드](docs/indicators-guide.md)):

| 지표 | 조건 | 매개변수 |
|------|------|----------|
| RSI | `above`, `below`, `between` | `period` (기본값: 14) |
| EMA | `price_above`, `price_below`, `slope_up`, `slope_down` | `period` (기본값: 20) |
| MACD | `bullish`, `bearish`, `above_zero`, `below_zero` | — |
| 볼린저 밴드 | `above_lower`, `below_upper`, `inside` | `period` (기본값: 20), `std` |
| KD | `golden_cross`, `death_cross`, `oversold`, `overbought`, `k_above_d` | `period` (기본값: 14) |
| 거래량 | `above_average` | `multiplier` (기본값: 1.5) |
| EMA 크로스 | `golden_cross`, `death_cross`, `ema20_above_50`, `ema20_below_50` | — |
| ATR | `above` | `period` (기본값: 14), `value` |

## 시스템 요구사항

- Python 3.10+
- Binance 계정 및 API 키 (읽기 전용 권한) — [무료 Binance 계정 만들기](https://accounts.binance.com/register?ref=956950981)
- 인터넷 연결
- 의존성: ccxt, numpy, pandas, pyyaml (`requirements.txt` 참고)

## CoinSifter Pro

더 많은 기능을 원하시나요? **CoinSifter Pro**에는 다음이 포함됩니다:

- **웹 UI** — 브라우저 기반 다크 테마 대시보드, 터미널 불필요
- **예약 스캔** — 한 번 설정하면 자동으로 정기 스캔
- **텔레그램 알림** — 조건에 맞는 코인 발견 시 즉시 알림
- **사전 구축 전략** — 백테스트 검증 완료, OOS 승률 75%+
- **원클릭 런처** — Windows & Mac 바로가기

👉 [CoinSifter Pro 구매하기](https://judyailab.com/shop/)

## 라이선스

MIT — [LICENSE](LICENSE) 참고

## 링크

- 블로그: [judyailab.com](https://judyailab.com)
- Twitter/X: [@JudyaiLab](https://x.com/judyailab)
