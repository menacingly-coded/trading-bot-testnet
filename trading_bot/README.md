# Simplified Binance Futures Testnet Trading Bot (Python)

This project places **MARKET** and **LIMIT** orders on **Binance USDT-M Futures Testnet** using signed REST calls.

Base URL (testnet): `https://testnet.binancefuture.com`

## Requirements
- Python 3.10+ (works on Python 3.x)
- Binance Futures Testnet account + API key/secret

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configure API credentials
Set environment variables:

```bash
export BINANCE_API_KEY="..."
export BINANCE_API_SECRET="..."
```

Or create a `.env` file:

```env
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
```

## Usage

### Market order (example)
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Limit order (example)
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 90000
```

Logs are written to `./logs/trading_bot.log` by default (rotating).  
You can choose a different log file name:

```bash
python cli.py ... --log-file market_order.log
python cli.py ... --log-file limit_order.log
```

## Output
The CLI prints:
- order request summary
- order response details (orderId, status, executedQty, avgPrice when available)
- success/failure message

## Assumptions / Notes
- This is a simplified task-focused bot: it only places orders (no position management).
- For LIMIT orders, `timeInForce=GTC`.
- Uses `newOrderRespType=RESULT` to try to return execution info like `avgPrice` when available.
- Some fields may differ depending on Binance response payload.