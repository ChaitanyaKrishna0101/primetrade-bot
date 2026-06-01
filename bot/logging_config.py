"""
Structured logging configuration for the trading bot.
Logs to both console (INFO) and rotating file (DEBUG).
"""
import logging
import logging.handlers
import json
import os
from datetime import datetime
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """
    Emits each log record as a single JSON line — machine-parseable,
    easy to ship to any log aggregator.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        if hasattr(record, "extra"):
            payload.update(record.extra)
        return json.dumps(payload)


def setup_logging(log_dir: str = "logs", log_level: str = "DEBUG") -> logging.Logger:
    """
    Configure root logger:
      - Rotating file handler  → JSON, DEBUG+
      - Console handler        → human-readable, INFO+
    Returns the root 'trading_bot' logger.
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = os.path.join(log_dir, "trading_bot.log")

    root = logging.getLogger("trading_bot")
    root.setLevel(logging.DEBUG)

    # Avoid duplicate handlers on repeated imports
    if root.handlers:
        return root

    # ── File handler (JSON, rotating 5 MB × 5 backups) ──────────────────
    fh = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(JSONFormatter())

    # ── Console handler (readable) ────────────────────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    root.addHandler(fh)
    root.addHandler(ch)
    return root


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"trading_bot.{name}")
