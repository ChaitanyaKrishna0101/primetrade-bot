"""
Flask web interface for PrimeTrade Bot — redesigned UI.
Run: python app.py
Open: http://localhost:7860
"""
import os
import sys
import json
import traceback
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template_string

sys.path.insert(0, os.path.dirname(__file__))

from bot.logging_config import setup_logging
from bot.client import BinanceFuturesClient, BinanceAPIError, NetworkError
from bot.validators import validate_order_params
from bot.ai_analyst import analyse_trade

setup_logging()

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>PrimeTrade</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;500;600;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
:root {
  --bg: #080c10;
  --surface: #0e1419;
  --surface2: #141b22;
  --border: rgba(255,255,255,0.07);
  --border2: rgba(255,255,255,0.13);
  --gold: #f0b429;
  --gold2: #ffd166;
  --teal: #00d4aa;
  --red: #ff5f57;
  --blue: #4d9fff;
  --text: #e8edf2;
  --muted: #6b7a8d;
  --muted2: #4a5568;
  --success-bg: rgba(0,212,170,0.08);
  --success-border: rgba(0,212,170,0.25);
  --error-bg: rgba(255,95,87,0.08);
  --error-border: rgba(255,95,87,0.25);
  --info-bg: rgba(77,159,255,0.08);
  --info-border: rgba(77,159,255,0.2);
  --radius: 10px;
  --radius-sm: 6px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'DM Sans', sans-serif;
  background: var(--bg);
  color: var(--text);
  height: 100vh;
  overflow: hidden;
  display: grid;
  grid-template-rows: 52px 1fr;
}

/* ── TOPBAR ── */
.topbar {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.logo {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  font-size: 1rem;
  color: var(--gold);
  letter-spacing: 0.04em;
  display: flex;
  align-items: center;
  gap: 8px;
}
.logo-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--teal); box-shadow: 0 0 6px var(--teal); }
.topbar-right { display: flex; align-items: center; gap: 16px; }
.network-badge {
  font-family: 'DM Mono', monospace;
  font-size: 0.68rem;
  color: var(--teal);
  background: rgba(0,212,170,0.1);
  border: 1px solid rgba(0,212,170,0.2);
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.08em;
}
.topbar-nav { display: flex; gap: 2px; }
.nav-btn {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--muted);
  background: none;
  border: none;
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s;
  letter-spacing: 0.02em;
}
.nav-btn:hover { color: var(--text); background: var(--surface2); }
.nav-btn.active { color: var(--gold); background: rgba(240,180,41,0.1); }

/* ── MAIN LAYOUT ── */
.app {
  display: grid;
  grid-template-columns: 280px 1fr 260px;
  height: 100%;
  overflow: hidden;
}

/* ── SIDEBAR ── */
.sidebar {
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.sidebar-section {
  padding: 16px;
  border-bottom: 1px solid var(--border);
}
.section-label {
  font-family: 'DM Mono', monospace;
  font-size: 0.62rem;
  color: var(--muted2);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 12px;
}

/* ── FORM ELEMENTS ── */
.field { margin-bottom: 10px; }
.field label {
  font-size: 0.72rem;
  font-weight: 500;
  color: var(--muted);
  letter-spacing: 0.04em;
  display: block;
  margin-bottom: 5px;
  text-transform: uppercase;
}
.field input, .field select {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border2);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-family: 'DM Mono', monospace;
  font-size: 0.82rem;
  padding: 7px 10px;
  outline: none;
  transition: border-color 0.15s;
  appearance: none;
  -webkit-appearance: none;
}
.field input:focus, .field select:focus { border-color: var(--gold); }
.field select {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%236b7a8d' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 28px;
  cursor: pointer;
}

.radio-row { display: flex; gap: 6px; }
.radio-pill {
  flex: 1;
  text-align: center;
  padding: 6px 0;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border2);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  color: var(--muted);
  background: var(--bg);
  user-select: none;
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.06em;
}
.radio-pill.buy.selected { background: rgba(0,212,170,0.12); border-color: var(--teal); color: var(--teal); }
.radio-pill.sell.selected { background: rgba(255,95,87,0.12); border-color: var(--red); color: var(--red); }
.radio-pill:hover:not(.selected) { border-color: var(--border2); color: var(--text); background: var(--surface2); }

.btn {
  width: 100%;
  padding: 9px 16px;
  border-radius: var(--radius-sm);
  border: none;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  letter-spacing: 0.03em;
  margin-bottom: 6px;
}
.btn:last-child { margin-bottom: 0; }
.btn-gold { background: var(--gold); color: #080c10; }
.btn-gold:hover { background: var(--gold2); transform: translateY(-1px); }
.btn-ghost { background: var(--surface2); color: var(--text); border: 1px solid var(--border2); }
.btn-ghost:hover { background: rgba(255,255,255,0.06); border-color: var(--border2); }
.btn-teal { background: rgba(0,212,170,0.12); color: var(--teal); border: 1px solid var(--success-border); }
.btn-teal:hover { background: rgba(0,212,170,0.2); }

/* ── MAIN PANEL ── */
.main {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg);
}

.panel { display: none; flex-direction: column; height: 100%; overflow: hidden; }
.panel.active { display: flex; }

/* Order panel */
.order-result-area {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.result-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px;
  animation: slideIn 0.25s ease;
}
@keyframes slideIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: translateY(0); } }

.result-card.success { border-color: var(--success-border); background: var(--success-bg); }
.result-card.error { border-color: var(--error-border); background: var(--error-bg); }
.result-card.info { border-color: var(--info-border); background: var(--info-bg); }

.card-title {
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 12px;
}
.result-card.success .card-title { color: var(--teal); }
.result-card.error .card-title { color: var(--red); }
.result-card.info .card-title { color: var(--blue); }

.order-table { width: 100%; border-collapse: collapse; }
.order-table td { padding: 5px 0; font-size: 0.82rem; }
.order-table td:first-child { color: var(--muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; width: 40%; }
.order-table td:last-child { font-family: 'DM Mono', monospace; font-weight: 500; }

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.06em;
}
.badge-buy { background: rgba(0,212,170,0.15); color: var(--teal); }
.badge-sell { background: rgba(255,95,87,0.15); color: var(--red); }
.badge-filled { background: rgba(0,212,170,0.15); color: var(--teal); }
.badge-new { background: rgba(77,159,255,0.15); color: var(--blue); }
.badge-gold { background: rgba(240,180,41,0.15); color: var(--gold); }

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--muted2);
  gap: 8px;
}
.empty-icon { font-size: 2rem; opacity: 0.3; }
.empty-text { font-size: 0.82rem; }

/* Market panel */
.market-panel { padding: 20px; flex: 1; overflow-y: auto; }
.ticker-display {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  text-align: center;
  margin: 12px 0;
}
.ticker-symbol { font-family: 'Syne', sans-serif; font-size: 0.85rem; color: var(--muted); letter-spacing: 0.1em; }
.ticker-price { font-family: 'DM Mono', monospace; font-size: 2.2rem; font-weight: 500; color: var(--gold); margin: 4px 0; }

/* Account panel */
.account-panel { padding: 20px; flex: 1; overflow-y: auto; }
.data-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
.data-table th {
  text-align: left;
  font-size: 0.67rem;
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.1em;
  color: var(--muted2);
  text-transform: uppercase;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
}
.data-table td {
  padding: 9px 12px;
  font-size: 0.82rem;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  font-family: 'DM Mono', monospace;
}
.data-table tr:last-child td { border-bottom: none; }
.data-table td:first-child { font-weight: 600; color: var(--gold); }

/* Help panel */
.help-panel { padding: 20px; flex: 1; overflow-y: auto; }
.help-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  margin-bottom: 12px;
}
.help-block pre {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 14px;
  font-family: 'DM Mono', monospace;
  font-size: 0.76rem;
  line-height: 1.9;
  color: #a0b4c8;
  overflow-x: auto;
}
.help-comment { color: var(--muted2); }
.help-block h3 { font-family: 'Syne', sans-serif; font-size: 0.85rem; color: var(--muted); letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 14px; }

/* ── RIGHT PANEL ── */
.right-panel {
  background: var(--surface);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.ai-header {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 8px;
}
.ai-label {
  font-family: 'Syne', sans-serif;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--text);
}
.ai-chip {
  margin-left: auto;
  font-family: 'DM Mono', monospace;
  font-size: 0.6rem;
  color: var(--gold);
  background: rgba(240,180,41,0.1);
  border: 1px solid rgba(240,180,41,0.2);
  padding: 2px 8px;
  border-radius: 10px;
  letter-spacing: 0.08em;
}
.ai-body { flex: 1; overflow-y: auto; padding: 14px 16px; }
.ai-content {
  font-size: 0.82rem;
  line-height: 1.7;
  color: var(--muted);
}
.ai-content b { color: var(--text); font-weight: 600; }
.ai-metric {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.78rem;
}
.ai-metric:last-child { border-bottom: none; }
.ai-metric-label { color: var(--muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; }
.ai-metric-val { font-family: 'DM Mono', monospace; font-weight: 600; }
.signal-bar {
  height: 4px;
  background: var(--border2);
  border-radius: 2px;
  margin: 10px 0 14px;
  overflow: hidden;
}
.signal-fill {
  height: 100%;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--teal), var(--gold));
  transition: width 0.5s ease;
}
.rec-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  font-family: 'DM Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  margin-bottom: 12px;
}
.rec-proceed { background: rgba(0,212,170,0.12); color: var(--teal); border: 1px solid var(--success-border); }
.rec-caution { background: rgba(240,180,41,0.12); color: var(--gold); border: 1px solid rgba(240,180,41,0.3); }
.rec-abort { background: rgba(255,95,87,0.12); color: var(--red); border: 1px solid var(--error-border); }
.reasoning-text { font-size: 0.78rem; color: #8899aa; line-height: 1.65; margin: 10px 0; }
.risks-list { list-style: none; margin-top: 8px; }
.risks-list li {
  font-size: 0.75rem;
  color: var(--muted);
  padding: 4px 0;
  padding-left: 12px;
  position: relative;
}
.risks-list li::before { content: '·'; position: absolute; left: 0; color: var(--red); font-size: 1.2rem; line-height: 1; }

/* loading pulse */
@keyframes pulse { 0%,100%{opacity:.4} 50%{opacity:1} }
.loading-dots span { animation: pulse 1.2s infinite; display: inline-block; }
.loading-dots span:nth-child(2) { animation-delay:.2s; }
.loading-dots span:nth-child(3) { animation-delay:.4s; }

.scrollable { overflow-y: auto; }
.scrollable::-webkit-scrollbar { width: 4px; }
.scrollable::-webkit-scrollbar-track { background: transparent; }
.scrollable::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ticker strip */
.ticker-strip {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 20px;
  height: 36px;
  display: flex;
  align-items: center;
  gap: 24px;
  overflow: hidden;
}
.tick-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'DM Mono', monospace;
  font-size: 0.72rem;
  white-space: nowrap;
}
.tick-sym { color: var(--muted); }
.tick-price { color: var(--text); font-weight: 500; }
.tick-change.up { color: var(--teal); }
.tick-change.down { color: var(--red); }
</style>
</head>
<body>

<div class="topbar">
  <div class="logo">
    <div class="logo-dot"></div>
    PRIMETRADE
  </div>
  <div class="topbar-right">
    <div class="topbar-nav">
      <button class="nav-btn active" onclick="showPanel('order', this)">Order</button>
      <button class="nav-btn" onclick="showPanel('market', this)">Market</button>
      <button class="nav-btn" onclick="showPanel('account', this)">Account</button>
      <button class="nav-btn" onclick="showPanel('help', this)">Help</button>
    </div>
    <span class="network-badge">TESTNET</span>
  </div>
</div>

<div class="app">

  <!-- SIDEBAR: Order Form -->
  <div class="sidebar scrollable">

    <div class="sidebar-section">
      <div class="section-label">Instrument</div>
      <div class="field">
        <label>Symbol</label>
        <input id="symbol" value="BTCUSDT" placeholder="e.g. BTCUSDT" style="text-transform:uppercase"/>
      </div>
      <div class="field">
        <label>Side</label>
        <div class="radio-row">
          <div class="radio-pill buy selected" onclick="selectSide('BUY')">BUY</div>
          <div class="radio-pill sell" onclick="selectSide('SELL')">SELL</div>
        </div>
        <input type="hidden" id="side" value="BUY"/>
      </div>
      <div class="field">
        <label>Order Type</label>
        <select id="order_type">
          <option value="MARKET">MARKET</option>
          <option value="LIMIT">LIMIT</option>
          <option value="STOP_MARKET">STOP_MARKET</option>
          <option value="STOP_LIMIT">STOP_LIMIT</option>
        </select>
      </div>
    </div>

    <div class="sidebar-section">
      <div class="section-label">Parameters</div>
      <div class="field">
        <label>Quantity</label>
        <input id="quantity" type="number" value="0.01" step="0.001" min="0.001"/>
      </div>
      <div class="field">
        <label>Price <span style="color:var(--muted2);font-size:0.65rem">(LIMIT / STOP_LIMIT)</span></label>
        <input id="price" type="number" value="0" step="0.01" placeholder="0 = market"/>
      </div>
      <div class="field">
        <label>Stop Price <span style="color:var(--muted2);font-size:0.65rem">(STOP_*)</span></label>
        <input id="stop_price" type="number" value="0" step="0.01" placeholder="0 = none"/>
      </div>
      <div class="field">
        <label>Time in Force</label>
        <select id="tif">
          <option value="GTC">GTC — Good Till Cancel</option>
          <option value="IOC">IOC — Immediate or Cancel</option>
          <option value="FOK">FOK — Fill or Kill</option>
        </select>
      </div>
    </div>

    <div class="sidebar-section" style="border-bottom:none">
      <div class="section-label">Actions</div>
      <button class="btn btn-teal" onclick="runAI()">⚡ AI Analysis</button>
      <button class="btn btn-gold" onclick="placeOrder()">▶ Place Order</button>
    </div>

  </div>

  <!-- MAIN CONTENT -->
  <div class="main">

    <!-- Order Panel -->
    <div id="panel-order" class="panel active">
      <div class="order-result-area scrollable" id="order-result-area">
        <div class="empty-state" id="order-empty">
          <div class="empty-icon">📋</div>
          <div class="empty-text">No orders placed yet</div>
          <div style="font-size:0.72rem;color:var(--muted2);margin-top:4px">Fill the form and press Place Order</div>
        </div>
      </div>
    </div>

    <!-- Market Panel -->
    <div id="panel-market" class="panel">
      <div class="market-panel scrollable">
        <div class="section-label" style="margin-bottom:14px">Ticker Lookup</div>
        <div style="display:flex;gap:8px;align-items:center">
          <input id="tick-symbol" value="BTCUSDT" style="background:var(--surface);border:1px solid var(--border2);border-radius:var(--radius-sm);color:var(--text);font-family:'DM Mono',monospace;font-size:0.82rem;padding:7px 10px;outline:none;width:160px;text-transform:uppercase"/>
          <button class="btn btn-gold" onclick="getTicker()" style="width:auto;padding:7px 18px;margin:0">Get Price</button>
        </div>
        <div id="ticker-display" class="ticker-display" style="display:none">
          <div class="ticker-symbol" id="ticker-sym"></div>
          <div class="ticker-price" id="ticker-price"></div>
        </div>
        <div id="ticker-error" class="result-card error" style="display:none;margin-top:12px"></div>
      </div>
    </div>

    <!-- Account Panel -->
    <div id="panel-account" class="panel">
      <div class="account-panel scrollable">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
          <div class="section-label" style="margin:0">Balances</div>
          <button class="btn btn-ghost" onclick="getAccount()" style="width:auto;padding:5px 14px;margin:0;font-size:0.75rem">↻ Refresh</button>
        </div>
        <div id="account-result">
          <div class="empty-state" style="padding:30px 0">
            <div class="empty-text">Click Refresh to load balances</div>
          </div>
        </div>

        <div style="display:flex;align-items:center;justify-content:space-between;margin:20px 0 16px">
          <div class="section-label" style="margin:0">Open Orders</div>
          <button class="btn btn-ghost" onclick="getOrders()" style="width:auto;padding:5px 14px;margin:0;font-size:0.75rem">↻ Refresh</button>
        </div>
        <div id="orders-result">
          <div class="empty-state" style="padding:30px 0">
            <div class="empty-text">Click Refresh to load orders</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Help Panel -->
    <div id="panel-help" class="panel">
      <div class="help-panel scrollable">
        <div class="help-block">
          <h3>CLI Quick Reference</h3>
          <pre><span class="help-comment"># Market order</span>
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --qty 0.01 --yes

<span class="help-comment"># Limit order</span>
python cli.py order --symbol BTCUSDT --side BUY --type LIMIT --qty 0.01 --price 50000

<span class="help-comment"># Stop-Limit</span>
python cli.py order --symbol BTCUSDT --side SELL --type STOP_LIMIT --qty 0.01 --price 58000 --stop-price 58500

<span class="help-comment"># Account info</span>
python cli.py account

<span class="help-comment"># Live monitor</span>
python cli.py monitor --symbol BTCUSDT --refresh 5</pre>
        </div>
        <div class="help-block">
          <h3>Environment Variables</h3>
          <table class="data-table">
            <thead><tr><th>Variable</th><th>Description</th></tr></thead>
            <tbody>
              <tr><td>BINANCE_API_KEY</td><td style="color:var(--muted);font-family:'DM Sans',sans-serif;font-size:0.8rem">API key from testnet.binance.vision</td></tr>
              <tr><td>BINANCE_API_SECRET</td><td style="color:var(--muted);font-family:'DM Sans',sans-serif;font-size:0.8rem">API secret from testnet.binance.vision</td></tr>
              <tr><td>BINANCE_BASE_URL</td><td style="color:var(--muted);font-family:'DM Sans',sans-serif;font-size:0.8rem">https://testnet.binance.vision</td></tr>
              <tr><td>GEMINI_API_KEY</td><td style="color:var(--muted);font-family:'DM Sans',sans-serif;font-size:0.8rem">For AI trade analysis (optional)</td></tr>
            </tbody>
          </table>
        </div>
        <div class="help-block">
          <h3>Order Types</h3>
          <table class="data-table">
            <thead><tr><th>Type</th><th>Description</th></tr></thead>
            <tbody>
              <tr><td>MARKET</td><td style="color:var(--muted);font-family:'DM Sans',sans-serif;font-size:0.8rem">Execute immediately at best available price</td></tr>
              <tr><td>LIMIT</td><td style="color:var(--muted);font-family:'DM Sans',sans-serif;font-size:0.8rem">Execute at specified price or better</td></tr>
              <tr><td>STOP_MARKET</td><td style="color:var(--muted);font-family:'DM Sans',sans-serif;font-size:0.8rem">Market order triggered at stop price</td></tr>
              <tr><td>STOP_LIMIT</td><td style="color:var(--muted);font-family:'DM Sans',sans-serif;font-size:0.8rem">Limit order triggered at stop price</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>

  <!-- RIGHT PANEL: AI Analysis -->
  <div class="right-panel">
    <div class="ai-header">
      <span style="font-size:1rem">⚡</span>
      <span class="ai-label">AI Analysis</span>
      <span class="ai-chip">GEMINI</span>
    </div>
    <div class="ai-body scrollable" id="ai-body">
      <div class="empty-state" style="height:100%;min-height:200px">
        <div class="empty-icon">🧠</div>
        <div class="empty-text">No analysis yet</div>
        <div style="font-size:0.72rem;color:var(--muted2);margin-top:4px;text-align:center">Click AI Analysis<br>to get pre-trade insights</div>
      </div>
    </div>
  </div>

</div>

<script>
function showPanel(name, btn) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + name).classList.add('active');
  btn.classList.add('active');
}

function selectSide(side) {
  document.getElementById('side').value = side;
  document.querySelectorAll('.radio-pill').forEach(p => p.classList.remove('selected'));
  const pills = document.querySelectorAll('.radio-pill');
  pills.forEach(p => {
    if (p.textContent === side) p.classList.add('selected');
  });
}

function orderResultArea() { return document.getElementById('order-result-area'); }

function clearEmpty() {
  const e = document.getElementById('order-empty');
  if (e) e.remove();
}

async function placeOrder() {
  const symbol = document.getElementById('symbol').value.toUpperCase();
  const side = document.getElementById('side').value;
  const order_type = document.getElementById('order_type').value;
  const quantity = document.getElementById('quantity').value;
  const price = document.getElementById('price').value;
  const stop_price = document.getElementById('stop_price').value;
  const tif = document.getElementById('tif').value;

  clearEmpty();
  const card = document.createElement('div');
  card.className = 'result-card';
  card.innerHTML = '<div class="card-title">Placing order…</div><div class="loading-dots"><span>•</span><span>•</span><span>•</span></div>';
  orderResultArea().prepend(card);

  const res = await fetch('/api/order', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({symbol, side, order_type, quantity, price, stop_price, tif})
  });
  const data = await res.json();

  if (data.success) {
    const r = data.result;
    const statusCls = r.status === 'FILLED' ? 'badge-filled' : 'badge-new';
    const sideCls = r.side === 'BUY' ? 'badge-buy' : 'badge-sell';
    card.className = 'result-card success';
    card.innerHTML = `
      <div class="card-title">Order Confirmed · ${new Date().toLocaleTimeString()}</div>
      <table class="order-table">
        <tr><td>Order ID</td><td><b>${r.orderId}</b></td></tr>
        <tr><td>Symbol</td><td>${r.symbol}</td></tr>
        <tr><td>Side</td><td><span class="badge ${sideCls}">${r.side}</span></td></tr>
        <tr><td>Type</td><td>${r.type}</td></tr>
        <tr><td>Quantity</td><td>${r.origQty}</td></tr>
        <tr><td>Executed</td><td>${r.executedQty}</td></tr>
        <tr><td>Avg Price</td><td>${r.avgPrice || '—'}</td></tr>
        <tr><td>Status</td><td><span class="badge ${statusCls}">${r.status}</span></td></tr>
      </table>`;
  } else {
    card.className = 'result-card error';
    card.innerHTML = `<div class="card-title">Order Failed</div><div style="font-size:0.82rem;color:#ff8880">${data.error}</div>`;
  }
}

async function runAI() {
  const symbol = document.getElementById('symbol').value.toUpperCase();
  const side = document.getElementById('side').value;
  const order_type = document.getElementById('order_type').value;
  const quantity = document.getElementById('quantity').value;
  const price = document.getElementById('price').value;

  document.getElementById('ai-body').innerHTML = `
    <div style="padding-top:20px;color:var(--muted);font-size:0.8rem">
      <div class="loading-dots" style="margin-bottom:8px"><span>•</span><span>•</span><span>•</span></div>
      Analysing ${symbol}…
    </div>`;

  const res = await fetch('/api/analyse', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({symbol, side, order_type, quantity, price})
  });
  const data = await res.json();
  document.getElementById('ai-body').innerHTML = data.html;
}

async function getTicker() {
  const symbol = document.getElementById('tick-symbol').value.toUpperCase();
  document.getElementById('ticker-display').style.display = 'none';
  document.getElementById('ticker-error').style.display = 'none';
  const res = await fetch('/api/ticker?symbol=' + symbol);
  const data = await res.json();
  if (data.success) {
    document.getElementById('ticker-sym').textContent = symbol;
    document.getElementById('ticker-price').textContent = '$' + parseFloat(data.price).toLocaleString('en-US', {minimumFractionDigits: 2});
    document.getElementById('ticker-display').style.display = 'block';
  } else {
    document.getElementById('ticker-error').innerHTML = '⚠ ' + data.error;
    document.getElementById('ticker-error').style.display = 'block';
  }
}

async function getAccount() {
  document.getElementById('account-result').innerHTML = '<div style="color:var(--muted);font-size:0.8rem;padding:12px 0">Loading…</div>';
  const res = await fetch('/api/account');
  const data = await res.json();
  if (data.success) {
    if (!data.assets.length) {
      document.getElementById('account-result').innerHTML = '<div style="color:var(--muted2);font-size:0.8rem;padding:12px 0">No funded assets.</div>';
      return;
    }
    let html = '<table class="data-table"><thead><tr><th>Asset</th><th>Total</th><th>Free</th><th>Locked</th></tr></thead><tbody>';
    for (const a of data.assets) {
      const total = (parseFloat(a.free) + parseFloat(a.locked)).toFixed(4);
      html += `<tr><td>${a.asset}</td><td>${total}</td><td>${parseFloat(a.free).toFixed(4)}</td><td>${parseFloat(a.locked).toFixed(4)}</td></tr>`;
    }
    html += '</tbody></table>';
    document.getElementById('account-result').innerHTML = html;
  } else {
    document.getElementById('account-result').innerHTML = `<div style="color:var(--red);font-size:0.8rem;padding:12px 0">⚠ ${data.error}</div>`;
  }
}

async function getOrders() {
  document.getElementById('orders-result').innerHTML = '<div style="color:var(--muted);font-size:0.8rem;padding:12px 0">Loading…</div>';
  const res = await fetch('/api/orders');
  const data = await res.json();
  if (data.success) {
    if (!data.orders.length) {
      document.getElementById('orders-result').innerHTML = '<div style="color:var(--muted2);font-size:0.8rem;padding:12px 0">No open orders.</div>';
      return;
    }
    let html = '<table class="data-table"><thead><tr><th>ID</th><th>Symbol</th><th>Side</th><th>Type</th><th>Qty</th><th>Price</th><th>Status</th></tr></thead><tbody>';
    for (const o of data.orders) {
      const sc = o.side === 'BUY' ? 'badge-buy' : 'badge-sell';
      html += `<tr><td>${o.orderId}</td><td>${o.symbol}</td><td><span class="badge ${sc}">${o.side}</span></td><td>${o.type}</td><td>${o.origQty}</td><td>${o.price}</td><td>${o.status}</td></tr>`;
    }
    html += '</tbody></table>';
    document.getElementById('orders-result').innerHTML = html;
  } else {
    document.getElementById('orders-result').innerHTML = `<div style="color:var(--red);font-size:0.8rem;padding:12px 0">⚠ ${data.error}</div>`;
  }
}
</script>
</body>
</html>"""


def _client():
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    base_url = os.getenv("BINANCE_BASE_URL", "https://testnet.binance.vision")
    if not api_key or not api_secret:
        raise ValueError("Missing API credentials in .env file")
    return BinanceFuturesClient(api_key, api_secret, base_url)


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/order", methods=["POST"])
def api_order():
    data = request.json
    try:
        params = validate_order_params(
            symbol=data["symbol"].upper(),
            side=data["side"],
            order_type=data["order_type"],
            quantity=float(data["quantity"]),
            price=float(data["price"]) if float(data.get("price", 0)) > 0 else None,
            stop_price=float(data["stop_price"]) if float(data.get("stop_price", 0)) > 0 else None,
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)})

    try:
        c = _client()
        from bot.orders import _get_precision
        ot = str(params["order_type"])
        qp, pp = _get_precision(c, str(params["symbol"]))

        order_params = dict(
            symbol=str(params["symbol"]),
            side=str(params["side"]),
            type=ot if ot != "STOP_LIMIT" else "STOP",
            quantity=f"{params['quantity']:.{qp}f}",
        )
        if ot in ("LIMIT", "STOP_LIMIT") and params.get("price"):
            order_params["price"] = f"{params['price']:.{pp}f}"
            order_params["timeInForce"] = data.get("tif", "GTC")
        if ot in ("STOP_MARKET", "STOP_LIMIT") and params.get("stop_price"):
            order_params["stopPrice"] = f"{params['stop_price']:.{pp}f}"

        result = c.place_order(**order_params)
        c.close()
        return jsonify({"success": True, "result": result})
    except BinanceAPIError as e:
        return jsonify({"success": False, "error": f"API Error [{e.code}]: {e.message}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/ticker")
def api_ticker():
    symbol = request.args.get("symbol", "BTCUSDT").upper()
    try:
        c = _client()
        t = c.get_ticker(symbol)
        c.close()
        return jsonify({"success": True, "price": t["price"]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/account")
def api_account():
    try:
        c = _client()
        acc = c.get_account_info()
        c.close()
        assets = [a for a in acc.get("balances", []) if float(a.get("free", 0)) + float(a.get("locked", 0)) > 0]
        return jsonify({"success": True, "assets": assets})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/orders")
def api_orders():
    try:
        c = _client()
        orders = c.get_open_orders()
        c.close()
        return jsonify({"success": True, "orders": orders})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/analyse", methods=["POST"])
def api_analyse():
    data = request.json
    try:
        c = _client()
        ticker = c.get_ticker(data["symbol"].upper())
        klines = c.get_klines(data["symbol"].upper(), "15m", 20)
        c.close()
        current_price = float(ticker.get("price", 0))
    except Exception:
        current_price = None
        klines = None

    analysis = analyse_trade(
        symbol=data["symbol"].upper(),
        side=data["side"],
        order_type=data["order_type"],
        quantity=float(data["quantity"]),
        price=float(data["price"]) if float(data.get("price", 0)) > 0 else None,
        current_price=current_price,
        klines=klines,
    )

    if not analysis:
        return jsonify({
            "success": False,
            "html": '<div style="color:var(--muted);font-size:0.8rem;padding:8px 0">⚠ AI analysis unavailable.<br><span style="color:var(--muted2);font-size:0.72rem">Add GEMINI_API_KEY to .env</span></div>'
        })

    rec = analysis.get("recommendation", "CAUTION")
    risk = analysis.get("risk_level", "UNKNOWN")
    strength = analysis.get("signal_strength", 0)
    reasoning = analysis.get("reasoning", "")
    risks = analysis.get("key_risks", [])

    emoji = {"PROCEED": "✅", "CAUTION": "⚠", "ABORT": "🛑"}.get(rec, "❓")
    rec_cls = {"PROCEED": "rec-proceed", "CAUTION": "rec-caution", "ABORT": "rec-abort"}.get(rec, "rec-caution")

    risks_html = "".join(f"<li>{r}</li>" for r in risks) if risks else "<li>No specific risks flagged</li>"

    html = f"""
<div class="rec-badge {rec_cls}">{emoji} {rec}</div>
<div class="ai-metric">
  <span class="ai-metric-label">Risk Level</span>
  <span class="ai-metric-val">{risk}</span>
</div>
<div class="ai-metric">
  <span class="ai-metric-label">Signal Strength</span>
  <span class="ai-metric-val">{strength}/100</span>
</div>
<div class="signal-bar"><div class="signal-fill" style="width:{strength}%"></div></div>
<div style="font-family:'DM Mono',monospace;font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted2);margin-bottom:6px">Reasoning</div>
<div class="reasoning-text">{reasoning}</div>
<div style="font-family:'DM Mono',monospace;font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted2);margin:10px 0 4px">Key Risks</div>
<ul class="risks-list">{risks_html}</ul>"""

    return jsonify({"success": True, "html": html})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    print(f"\n🚀 PrimeTrade Bot UI running at http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)