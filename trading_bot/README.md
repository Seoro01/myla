# Upbit 자동매매 봇 (변동성 돌파 전략)

⚠️ **이 봇은 수익을 보장하지 않습니다.** 실전 투입 시 원금 일부 또는 전부를 잃을 수 있습니다.
투자 판단과 결과에 대한 책임은 본인에게 있습니다.

## 전략 요약

- 매수: 당일 시가 + K × (전일 고가 − 전일 저가) 를 상향 돌파하면 설정된 예산만큼 시장가 매수
- 매도: 평단 대비 `STOP_LOSS_PCT` 만큼 하락(손절) 하거나, 한국시간 자정 직전(23:50~)에 무조건 매도
- 상태를 별도 파일에 저장하지 않고 매번 실제 업비트 계좌 잔고를 조회해서 판단하므로,
  GitHub Actions처럼 매번 새로 뜨는 실행 환경에서도 안전하게 동작합니다.

## 실행 방식

`.github/workflows/trading-bot.yml` 이 10분마다 자동으로 `bot.py` 를 실행합니다.
폰이나 이 세션이 꺼져 있어도 GitHub 서버에서 계속 돌아갑니다.

## 시작하기 전 테스트

1. GitHub 저장소의 **Actions** 탭 → **Trading Bot Backtest (manual)** → **Run workflow** 실행
   - 과거 데이터로 전략을 시뮬레이션한 결과를 로그에서 확인할 수 있습니다 (API 키 불필요).
2. `trading-bot.yml` 은 기본적으로 `DRY_RUN: "true"` 로 되어 있어 실제 주문 없이 로그만 남깁니다.
   - Actions 탭에서 **Upbit Trading Bot** → **Run workflow** 로 몇 번 수동 실행해 에러 없이 도는지 확인하세요.

## 실전 전환 방법 (약 5분 소요)

1. 업비트 앱/웹 → 마이페이지 → Open API 관리에서 API 키 발급
   - 권한은 **자산 조회 + 주문** 만 체크하고 **출금은 반드시 비활성화**하세요.
2. GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret
   - `UPBIT_ACCESS_KEY`, `UPBIT_SECRET_KEY` 두 개를 등록
3. `.github/workflows/trading-bot.yml` 에서 `DRY_RUN: "true"` 를 `DRY_RUN: "false"` 로 바꿔서 커밋
4. 이후 10분마다 자동으로 실행되며, 매매 기록은 `trading_bot/trades.csv` 에 자동으로 쌓입니다.

## 설정값 (`trading-bot.yml` 상단 env)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `TICKER` | `KRW-BTC` | 거래할 마켓 |
| `BUDGET_KRW` | `100000` | 1회 매수에 사용할 최대 금액 |
| `K` | `0.5` | 변동성 돌파 계수 |
| `STOP_LOSS_PCT` | `0.10` | 손절 기준 (평단 대비 -10%) |

## 중단하는 방법

Actions 탭 → **Upbit Trading Bot** 워크플로 → **...** → **Disable workflow**.
이미 보유 중인 코인이 있다면 업비트 앱에서 직접 매도해야 합니다 (봇이 자동으로 청산하지 않습니다).
