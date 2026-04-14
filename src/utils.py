"""Hilfsfunktionen."""
from __future__ import annotations

import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


def load_config(settings_path: str = "config/settings.yaml") -> dict:
    load_dotenv()
    path = Path(settings_path)
    if not path.exists():
        path = Path(__file__).parent.parent / "config" / "settings.yaml"
        
    if not path.exists():
        return {"bot": {"log_level": "INFO"}}
        
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_logging(level: str = "INFO", log_file: str | None = None) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logging.getLogger("ccxt").setLevel(logging.WARNING)
