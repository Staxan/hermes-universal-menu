"""Profile-local Telegram menu provider for Hermes Universal Menu."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    from telegram import KeyboardButton, ReplyKeyboardMarkup
except ImportError:  # pragma: no cover - Hermes imports this only with Telegram
    KeyboardButton = None
    ReplyKeyboardMarkup = None


class UniversalMenu:
    """Small, safe provider: it only owns its labels and `um:` callbacks."""

    BUTTONS = (
        ("☰ Меню", "⚙ Сервисы"),
        ("🔀 Сменить модель", "ℹ Помощь"),
    )

    def build_reply_keyboard(self, adapter: Any, *, chat_id: str, metadata: dict | None = None):
        """Return a persistent keyboard without requiring any service secret."""
        if ReplyKeyboardMarkup is None:
            return None
        return ReplyKeyboardMarkup(
            [[KeyboardButton(label) for label in row] for row in self.BUTTONS],
            resize_keyboard=True,
            is_persistent=False,
        )

    async def handle_text(self, adapter: Any, update: Any, context: Any) -> bool:
        message = getattr(update, "effective_message", None) or getattr(update, "message", None)
        text = (getattr(message, "text", None) or "").strip()
        chat_id = str(getattr(getattr(message, "chat", None), "id", ""))
        if not text or not chat_id:
            return False
        if text == "☰ Меню":
            await adapter.send(chat_id, "Меню Universal Menu включено.")
            return True
        if text == "⚙ Сервисы":
            await adapter.send(chat_id, self._services_text(), metadata=self._metadata(message))
            return True
        if text == "🔀 Сменить модель":
            await self._open_model_picker(adapter, chat_id, message)
            return True
        if text == "ℹ Помощь":
            await adapter.send(chat_id, self._help_text(), metadata=self._metadata(message))
            return True
        return False

    async def handle_callback(self, adapter: Any, update: Any, context: Any) -> bool:
        query = getattr(update, "callback_query", None)
        data = getattr(query, "data", "") if query else ""
        if not data.startswith("um:"):
            return False
        if query:
            await query.answer()
        return True

    async def _open_model_picker(self, adapter: Any, chat_id: str, message: Any) -> None:
        """Delegate model selection to Hermes' existing picker entry point."""
        bot = getattr(adapter, "_bot", None)
        if bot is not None:
            await adapter.send(chat_id, "Для смены модели отправь команду /model.", metadata=self._metadata(message))

    @staticmethod
    def _metadata(message: Any) -> dict:
        thread_id = getattr(message, "message_thread_id", None)
        return {"thread_id": thread_id} if thread_id is not None else {}

    @staticmethod
    def _services_text() -> str:
        return (
            "⚙ Сервисы\n\n"
            "Базовое меню работает без ключей.\n"
            "ENOT/Yonote пока не настроен.\n\n"
            "Для ручной настройки см. config.example.yaml и INSTALL.md."
        )

    @staticmethod
    def _help_text() -> str:
        return "Команды: /menu, /services, /model, /install, /update."


__all__ = ["UniversalMenu"]
