---
title: PrimeTrade Bot
emoji: 🤖
colorFrom: blue
colorTo: cyan
sdk: gradio
sdk_version: 4.40.0
app_file: app.py
pinned: false
license: mit
short_description: Binance Futures Testnet Trading Bot with AI Analysis
---

# PrimeTrade Bot

A production-grade Binance Futures Testnet trading bot with:
- Market, Limit, Stop-Market, and Stop-Limit orders
- AI pre-trade analysis via Google Gemini
- Live position & P&L monitoring
- Structured JSON logging

## Setup (HF Secrets)

Add these in Settings → Repository secrets:

- `BINANCE_API_KEY`
- `BINANCE_API_SECRET`  
- `GEMINI_API_KEY` (optional)
