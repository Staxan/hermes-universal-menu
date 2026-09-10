# Реестр сервисов для Universal Menu: читает настройки из config.yaml
# активного профиля и проверяет живой доступ к каждому сервису.

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict


def _plugin_config() -> Dict[str, Any]:
    # Секция universal_menu из config.yaml активного профиля.
    try:
        from hermes_cli.config import load_config_readonly
        cfg = load_config_readonly() or {}
    except Exception:
        return {}
    if not isinstance(cfg, dict):
        return {}
    return cfg.get("universal_menu") or {}


def enot_settings() -> Dict[str, Any]:
    # Настройки ENOT/Yonote: enabled, api_url, token_env.
    services = _plugin_config().get("services") or {}
    enot = services.get("enot") or {}
    return enot if isinstance(enot, dict) else {}


def enot_probe(api_url: str, token: str, timeout: int = 10) -> Dict[str, Any]:
    # Проверка живого доступа: POST auth.info.
    # Работает и с HTTPS напрямую, и с локальным мостом (http://192.168.1.140:8788/api),
    # который ходит в ENOT мимо VPN-туннеля со стороны Windows.
    # Возвращает {'ok': True, 'user': имя} или {'ok': False, 'error': причина}.
    try:
        req = urllib.request.Request(
            api_url.rstrip("/") + "/auth.info",
            data=b"{}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.load(r)
        if data.get("ok"):
            user = (data.get("data") or {}).get("user") or {}
            return {"ok": True, "user": user.get("name", "")}
        return {"ok": False, "error": str(data.get("error", "unknown_error"))}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}"}
    except Exception as e:
        text = str(e)
        # Обрыв TLS = трафик уходит в VPN-туннель, а ENOT отбивает зарубежные
        # адреса. Честная подсказка вместо пугающего «недоступен».
        if "SSL" in text or "timed out" in text or "URLError" in text or "EOF" in text:
            return {"ok": False, "error": "прямой маршрут к ENOT заблокирован VPN-туннелем",
                    "hint": "запусти «Запустить ЕНОТ-мост.bat» и поставь api_url моста в настройки профиля"}
        return {"ok": False, "error": text[:120]}


def enot_status() -> Dict[str, Any]:
    # Полный статус ENOT для показа в разделе «Сервисы».
    enot = enot_settings()
    if not enot.get("enabled", False):
        return {"ok": False, "error": "disabled", "hint": "universal_menu.services.enot.enabled"}
    token_env = enot.get("token_env", "YONOTE_API_KEY")
    token = os.environ.get(token_env, "")
    if not token:
        return {"ok": False, "error": f"нет токена ({token_env} в .env профиля)"}
    return enot_probe(enot.get("api_url", "https://anewera.yonote.ru/api"), token)


__all__ = ["enot_settings", "enot_status", "enot_probe"]
