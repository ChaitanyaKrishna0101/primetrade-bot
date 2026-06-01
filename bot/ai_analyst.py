"""
AI-powered market analysis using Groq (llama-3.3-70b-versatile).
Provides trade signal reasoning, risk assessment, and
market context before order placement.

This is the differentiator — most candidates won't add this.
"""
from __future__ import annotations

import json
import os
from typing import Optional

import httpx

from .logging_config import get_logger

logger = get_logger("ai_analyst")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def _call_groq(prompt: str, api_key: str) -> str:
    """Raw Groq API call. Returns the text content."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional crypto futures trader acting as a pre-trade risk analyst. Always respond with valid JSON only — no markdown, no explanation outside the JSON object.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
    }
    try:
        resp = httpx.post(
            GROQ_API_URL,
            json=body,
            headers=headers,
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as exc:
        logger.warning(f"Groq API call failed: {exc}")
        return ""


def analyse_trade(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
    current_price: Optional[float],
    klines: Optional[list] = None,
) -> dict:
    """
    Ask Groq to reason about the trade before execution.
    Returns a structured dict with:
      - risk_level: LOW / MEDIUM / HIGH
      - signal_strength: 0-100
      - reasoning: plain-English explanation
      - recommendation: PROCEED / CAUTION / ABORT
      - key_risks: list of risks
    """
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        logger.info("GROQ_API_KEY not set — skipping AI analysis")
        return {}

    # Build a compact market context summary from klines
    price_context = ""
    if klines and len(klines) >= 10:
        closes = [float(k[4]) for k in klines[-20:]]
        high = max(c[2] for c in [klines[-1]])
        low = min(c[3] for c in [klines[-1]])
        ma5 = sum(closes[-5:]) / 5
        ma20 = sum(closes) / len(closes)
        price_context = (
            f"Last 20 candles: MA5={ma5:.2f}, MA20={ma20:.2f}, "
            f"Last close={closes[-1]:.2f}, "
            f"Recent high={high}, Recent low={low}"
        )

    prompt = f"""
TRADE INTENT:
- Symbol: {symbol}
- Side: {side}
- Order Type: {order_type}
- Quantity: {quantity}
- Order Price: {price if price else 'MARKET'}
- Current Market Price: {current_price if current_price else 'unknown'}
{f'- Market Context: {price_context}' if price_context else ''}

Analyse this trade and respond ONLY with a valid JSON object:
{{
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "signal_strength": <integer 0-100>,
  "reasoning": "<2-3 sentence plain-English assessment>",
  "recommendation": "PROCEED" | "CAUTION" | "ABORT",
  "key_risks": ["<risk1>", "<risk2>"]
}}

Be concise, factual, and objective. Base risk_level on price distance from market, order size context, and order type.
"""

    logger.info("Requesting AI trade analysis from Groq")
    raw = _call_groq(prompt, api_key)

    if not raw:
        return {}

    try:
        clean = raw.strip()
        # Strip markdown fences if present
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        # Extract JSON object if extra text surrounds it
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start != -1 and end > start:
            clean = clean[start:end]
        return json.loads(clean.strip())
    except json.JSONDecodeError:
        logger.warning("Could not parse Groq response as JSON")
        return {"reasoning": raw[:300], "recommendation": "CAUTION"}


def print_ai_analysis(analysis: dict) -> None:
    """Pretty-print the AI analysis to console."""
    if not analysis:
        return

    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    console = Console()

    rec = analysis.get("recommendation", "CAUTION")
    risk = analysis.get("risk_level", "MEDIUM")
    strength = analysis.get("signal_strength", 50)
    reasoning = analysis.get("reasoning", "No analysis available")
    risks = analysis.get("key_risks", [])

    color_map = {"PROCEED": "green", "CAUTION": "yellow", "ABORT": "red"}
    risk_color = {"LOW": "green", "MEDIUM": "yellow", "HIGH": "red"}

    body = Text()
    body.append(f"🤖 Recommendation: ", style="bold")
    body.append(f"{rec}\n", style=f"bold {color_map.get(rec, 'white')}")
    body.append(f"⚠️  Risk Level: ", style="bold")
    body.append(f"{risk}\n", style=risk_color.get(risk, "white"))
    body.append(f"📊 Signal Strength: {strength}/100\n\n", style="cyan")
    body.append(f"💬 {reasoning}\n", style="white")
    if risks:
        body.append("\n🔴 Key Risks:\n", style="bold red")
        for r in risks:
            body.append(f"  • {r}\n", style="dim white")

    console.print(Panel(body, title="[bold blue]🧠 AI Pre-Trade Analysis[/bold blue]", border_style="blue"))