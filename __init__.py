"""Hermes Universal Menu plugin."""

from __future__ import annotations

from .menu import UniversalMenu


def register(ctx) -> None:
    """Register the profile-local Telegram menu provider."""
    ctx.register_telegram_menu(UniversalMenu())
    ctx.register_command("universal-menu", _command, "Show Universal Menu help")


def _command(raw_args: str = "") -> str:
    return (
        "Universal Menu активен. Открой Telegram-клавиатуру кнопкой «☰ Меню». "
        "Настройка сервисов: «⚙ Сервисы». Смена модели использует штатный /model."
    )


__all__ = ["register", "UniversalMenu"]
