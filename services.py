"""Profile-aware, read-only ENOT/Yonote service status."""

from __future__ import annotations

import os
from typing import Any, Dict


def _plugin_config() -> Dict[str, Any]:
    # Читаем именно конфиг активного профиля, а не пользователя по умолчанию.
    try:
        from hermes_constants import get_hermes_home
        import yaml
        from pathlib import Path
        path = Path(get_hermes_home()) / "config.yaml"
        if path.is_file():
            config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            section = config.get("universal_menu", {}) if isinstance(config, dict) else {}
            return section if isinstance(section, dict) else {}
    except Exception:
        pass
    # Совместимость со средами, где конфиг уже корректно профильный через Hermes.
    try:
        from hermes_cli.config import load_config_readonly
        config = load_config_readonly() or {}
        section = config.get("universal_menu", {}) if isinstance(config, dict) else {}
        return section if isinstance(section, dict) else {}
    except Exception:
        return {}


def enot_settings() -> Dict[str, Any]:
    """Read ENOT settings from the active Hermes profile config."""
    services = _plugin_config().get("services", {})
    enot = services.get("enot", {}) if isinstance(services, dict) else {}
    return enot if isinstance(enot, dict) else {}


def enot_status() -> Dict[str, Any]:
    """Return a safe status summary; actual API calls live in EnotAdapter."""
    settings = enot_settings()
    if not settings.get("enabled", False):
        return {"ok": False, "error": "disabled"}
    token_env = str(settings.get("token_env", "YONOTE_API_KEY"))
    if not os.environ.get(token_env):
        return {"ok": False, "error": "missing_token", "hint": token_env}
    return {"ok": True, "configured": True}


__all__ = ["enot_settings", "enot_status"]
