"""Hermes Universal Menu plugin."""

from __future__ import annotations

from .menu import UniversalMenu


def register(ctx) -> None:
    """Register handlers through the stable Telegram plugin extension point."""
    menu = UniversalMenu()
    ctx.register_telegram_handler(menu.register_handlers)
    menu.register_context_hook(ctx)
    ctx.register_command("universal-menu", _command, "Show Universal Menu help")


def _command(raw_args: str = "") -> str:
    return (
        "Universal Menu активен. Открой Telegram-клавиатуру кнопкой «☰ Меню». "
        "Настройка сервисов: «⚙ Сервисы». Смена модели использует штатный /model."
    )


def _after_agent_response(event) -> None:
    """Reserved host hook; reply keyboards are attached by Telegram adapter."""
    return None


__all__ = ["register", "UniversalMenu"]

