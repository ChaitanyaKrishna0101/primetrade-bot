# 🤖 PrimeTrade Bot

> A professional-grade crypto trading bot built on Binance Testnet — with a CLI, a polished web UI, AI-powered trade analysis, structured logging, Docker support, and a full test suite.

---

## 📌 What Is This?

PrimeTrade Bot lets you place and manage cryptocurrency orders on the **Binance Testnet** (a safe practice environment — no real money involved). You can use it two ways:

- **From the terminal** using simple commands (great for automation)
- **From your browser** using a beautiful dark-themed web interface

On top of trading, the bot integrates **Google Gemini AI** to analyse each trade before you place it — giving you a risk level, signal strength, and a recommendation (PROCEED / CAUTION / ABORT).

Think of it as: *a trading terminal + an AI risk analyst, built from scratch.*

---

## 🧠 The Problem It Solves

Manual crypto trading is risky and error-prone. Traders need to:

1. Validate order inputs before sending (wrong price = instant loss)
2. Understand market context before placing (is this a good time to buy?)
3. Track every order with logs for accountability
4. Have both a quick CLI for power users and a UI for visual users

PrimeTrade Bot solves all four.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📤 Market Orders | Execute instantly at current market price |
| 📋 Limit Orders | Set your target price, wait for fill |
| 🛑 Stop Orders | Stop-Market and Stop-Limit for risk management |
| 🧠 AI Analysis | Gemini analyses risk before every trade |
| 💼 Account View | See your testnet balances and open orders |
| 📈 Live Ticker | Fetch real-time price for any symbol |
| 🖥️ Web UI | Full browser interface, no terminal needed |
| ⌨️ CLI | Terminal commands for fast power users |
| 📝 Logging | Every order logged to file automatically |
| ✅ Tests | 16 unit tests, all passing |
| 🐳 Docker | One command to run anywhere |

---

## 🏗️ Project Structure

```
primetrade_bot/
│
├── bot/                        # Core logic (the engine)
│   ├── __init__.py
│   ├── client.py               # Talks to Binance API (handles auth, retries)
│   ├── orders.py               # Builds and sends order requests
│   ├── validators.py           # Checks inputs before sending (symbol, price, qty)
│   ├── ai_analyst.py           # Asks Gemini AI to review the trade
│   ├── monitor.py              # Displays account/ticker info in terminal
│   └── logging_config.py       # Sets up structured logging to file + console
│
├── tests/                      # Automated tests
│   └── test_validators.py      # 16 tests covering all validation logic
│
├── logs/                       # Auto-created, stores all order history
│   ├── trading_bot.log         # Full session log
│   ├── market_order.log        # Sample market order run
│   └── limit_order.log         # Sample limit order run
│
├── app.py                      # Web UI (Flask) — open in browser
├── cli.py                      # Terminal interface (Typer)
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose for easy startup
├── requirements.txt            # Python dependencies
├── .env.example                # Template for your API keys
└── README.md                   # This file
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Binance API | REST via `httpx` with HMAC-SHA256 auth |
| Web UI | Flask + vanilla JS (no frontend framework needed) |
| CLI | Typer + Rich (beautiful terminal output) |
| AI Analysis | Google Gemini 2.0 Flash via REST API |
| Testing | pytest (16 tests) |
| Logging | Python `logging` module → rotating file handler |
| Containerisation | Docker + Docker Compose |
| Config | python-dotenv (`.env` file) |

---

## 🚀 Getting Started (Run Locally)

### Step 1 — Get your API Keys

**Binance Testnet** (free, no real money):
1. Go to [testnet.binance.vision](https://testnet.binance.vision)
2. Log in with GitHub
3. Click **Generate HMAC_SHA256 Key**
4. Copy the API Key and Secret

**Google Gemini** (optional, for AI analysis):
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Click **Create API Key**
3. Copy it

---

### Step 2 — Clone and Set Up

```bash
# 1. Enter the project folder
cd primetrade_bot

# 2. Create a virtual environment (isolated Python sandbox)
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install all dependencies
pip install -r requirements.txt
```

---

### Step 3 — Configure Your Keys

Create a file called `.env` in the project root (copy from the example):

```bash
cp .env.example .env
```

Then open `.env` and fill in your keys:

```dotenv
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
BINANCE_BASE_URL=https://testnet.binance.vision
GEMINI_API_KEY=your_gemini_api_key_here   # optional
LOG_DIR=logs
```

> ⚠️ Never commit your `.env` file. It's already in `.gitignore`.

---

### Step 4 — Run It

**Option A — Web UI (recommended for beginners):**
```bash
python app.py
```
Then open [http://localhost:7860](http://localhost:7860) in your browser.

**Option B — Terminal CLI:**
```bash
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --qty 0.01
```

---

## 🐳 Run with Docker (Zero Setup)

If you have Docker installed, you don't need Python or any setup at all.

```bash
# Build and start
docker-compose up --build

# Open browser at:
http://localhost:7860
```

To stop:
```bash
docker-compose down
```

The `docker-compose.yml` automatically loads your `.env` file — just make sure it exists before running.

---

## ⌨️ CLI Command Reference

```bash
# Place a MARKET order (executes immediately)
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --qty 0.01

# Place a LIMIT order (waits for your target price)
python cli.py order --symbol BTCUSDT --side BUY --type LIMIT --qty 0.01 --price 69000

# Place a SELL order
python cli.py order --symbol BTCUSDT --side SELL --type MARKET --qty 0.01

# Place a STOP_LIMIT order (advanced risk management)
python cli.py order --symbol BTCUSDT --side SELL --type STOP_LIMIT --qty 0.01 --price 68000 --stop-price 68500

# Skip AI analysis and confirmation prompt (for automation)
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --qty 0.01 --no-ai --yes

# View your account balances
python cli.py account

# View open orders
python cli.py orders --symbol BTCUSDT

# Get current price
python cli.py ticker --symbol BTCUSDT

# Live price monitor (refreshes every 5 seconds)
python cli.py monitor --symbol BTCUSDT --refresh 5

# Cancel an order
python cli.py cancel --symbol BTCUSDT --order-id 12345678
```

---

## 🖥️ Web UI Guide

After running `python app.py` and opening `http://localhost:7860`:

| Tab | What it does |
|---|---|
| **Order** | Place trades — fill the form on the left, results appear in the centre |
| **Market** | Type any symbol (e.g. `ETHUSDT`) and get the live price |
| **Account** | See your testnet balances and all open orders |
| **Help** | CLI cheat sheet and environment variable reference |

The **AI Analysis panel** on the right updates every time you click `⚡ AI Analysis` — it shows Gemini's recommendation, risk level, signal strength, reasoning, and key risks before you place the order.

---

## 🧠 How AI Analysis Works

Before every trade, the bot sends the trade details + recent market data (last 20 candles, moving averages) to Google Gemini and asks it to act as a risk analyst.

Gemini returns a structured JSON response:

```json
{
  "risk_level": "MEDIUM",
  "signal_strength": 62,
  "reasoning": "BTC is trading below the 20-period MA suggesting bearish momentum. A limit buy at $69,000 provides a 5% buffer from current price.",
  "recommendation": "CAUTION",
  "key_risks": ["Downtrend may continue", "Low volume environment"]
}
```

This is then displayed in the UI with a colour-coded badge — green for PROCEED, amber for CAUTION, red for ABORT.

> The bot works perfectly without a Gemini key — AI analysis is gracefully skipped if not configured.

---

## ✅ Running Tests

```bash
pytest tests/ -v
```

Expected output — all 16 passing:

```
tests/test_validators.py::TestValidateSymbol::test_normalises_to_uppercase    PASSED
tests/test_validators.py::TestValidateSymbol::test_strips_whitespace          PASSED
tests/test_validators.py::TestValidateSymbol::test_rejects_empty              PASSED
tests/test_validators.py::TestValidateSymbol::test_rejects_special_chars      PASSED
tests/test_validators.py::TestValidateSide::test_valid_buy                    PASSED
tests/test_validators.py::TestValidateSide::test_valid_sell                   PASSED
tests/test_validators.py::TestValidateSide::test_rejects_invalid              PASSED
tests/test_validators.py::TestValidateQuantity::test_valid_quantity           PASSED
tests/test_validators.py::TestValidateQuantity::test_rejects_zero             PASSED
tests/test_validators.py::TestValidateQuantity::test_rejects_negative         PASSED
tests/test_validators.py::TestValidateQuantity::test_rejects_non_numeric      PASSED
tests/test_validators.py::TestValidateOrderParams::test_market_order_no_price PASSED
tests/test_validators.py::TestValidateOrderParams::test_limit_requires_price  PASSED
tests/test_validators.py::TestValidateOrderParams::test_market_rejects_price  PASSED
tests/test_validators.py::TestValidateOrderParams::test_stop_limit_requires_stop_price PASSED
tests/test_validators.py::TestValidateOrderParams::test_valid_limit_order     PASSED

16 passed in 0.12s
```

---

## 📝 Logging

Every API call, order placement, and error is automatically logged to `logs/trading_bot.log`.

Sample log entry:
```
15:40:35  INFO   trading_bot.client   Placing order: {'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': '0.010'}
15:40:35  INFO   trading_bot.client   Order placed orderId=9363303 status=FILLED
```

Pre-recorded sample logs are included:
- `logs/market_order.log` — a completed MARKET order execution
- `logs/limit_order.log` — a LIMIT order placed and waiting

---

## 📋 Sample Output

**CLI — Market Order:**
```
📤 Order Request
╭──────────┬─────────╮
│ SYMBOL   │ BTCUSDT │
│ SIDE     │ BUY     │
│ TYPE     │ MARKET  │
│ QUANTITY │ 0.010   │
╰──────────┴─────────╯

✅ Order FILLED successfully!
Order ID: 9363303 | Status: FILLED | Executed: 0.01 BTC
```

**CLI — Limit Order:**
```
📤 Order Request
╭─────────────┬──────────╮
│ SYMBOL      │ BTCUSDT  │
│ SIDE        │ BUY      │
│ TYPE        │ LIMIT    │
│ QUANTITY    │ 0.010    │
│ PRICE       │ 69000.00 │
│ TIMEINFORCE │ GTC      │
╰─────────────┴──────────╯

🕐 Order placed and waiting to be filled
Order ID: 9363409 | Status: NEW
```

---

## ⚙️ Assumptions & Design Decisions

- **Binance Spot Testnet** is used (`testnet.binance.vision`) — Futures Testnet requires full KYC verification which is not practical for development
- **Spot API endpoints** (`/api/v3/`) are used instead of Futures endpoints (`/fapi/v1/`)
- **Gemini AI is optional** — the bot works fully without it; AI analysis is gracefully skipped
- **STOP_LIMIT** orders are supported as the bonus third order type (mapped to Binance's `STOP` type internally)
- **Prices must be within ~10% of market price** — this is a Binance `PERCENT_PRICE_BY_SIDE` filter to prevent fat-finger errors
- **Python 3.10+** recommended (tested and confirmed working on Python 3.13)

---

## 🔒 Security Notes

- API keys are stored in `.env` and never hardcoded
- `.env` is listed in `.gitignore` — it will never be committed
- All signing uses HMAC-SHA256 as required by Binance
- This bot only operates on **testnet** — no real funds are at risk

---

## 🧩 Dependencies

```
flask          # Web server for the UI
httpx          # HTTP client for Binance and Gemini API calls
typer          # CLI framework
rich           # Beautiful terminal output (tables, panels, colours)
python-dotenv  # Loads .env file into environment variables
pytest         # Test runner
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 👨‍💻 Author

Built as part of the **PrimeTrade AI Internship Task** — demonstrating full-stack bot development with API integration, AI enhancement, testing, and deployment.