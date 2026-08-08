"""Telegram handlers for the Universal Menu plugin."""

from __future__ import annotations

from typing import Any

try:
    from telegram import KeyboardButton, ReplyKeyboardMarkup
    from telegram.ext import CommandHandler, MessageHandler, filters
except ImportError:  # pragma: no cover - loaded only in Telegram runtime
    KeyboardButton = ReplyKeyboardMarkup = CommandHandler = MessageHandler = filters = None


class UniversalMenu:
    """Small profile-local menu implemented through Hermes' handler API."""

    BUTTONS = (
        ("☰ Меню", "⚙ Сервисы"),
        ("🔀 Сменить модель", "ℹ Помощь"),
    )

    def register_handlers(self, application: Any, adapter: Any) -> None:
        """Wire namespaced Telegram text handling before Hermes core handlers."""
        if MessageHandler is None or CommandHandler is None:
            raise RuntimeError("python-telegram-bot is required for Universal Menu")
        adapter._plugin_reply_markup = self.keyboard()
        application.add_handler(CommandHandler("menu", self.command_menu))
        application.add_handler(CommandHandler("services", self.command_services))
        application.add_handler(CommandHandler("help_menu", self.command_help))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_update)
        )

    async def command_menu(self, update: Any, context: Any) -> None:
        message = getattr(update, "effective_message", None)
        if message is not None:
            await message.reply_text("Меню Universal Menu включено.", reply_markup=self.keyboard())

    async def command_services(self, update: Any, context: Any) -> None:
        message = getattr(update, "effective_message", None)
        if message is not None:
            await message.reply_text(self._services_text(), reply_markup=self.keyboard())

    async def command_help(self, update: Any, context: Any) -> None:
        message = getattr(update, "effective_message", None)
        if message is not None:
            await message.reply_text(self._help_text(), reply_markup=self.keyboard())

    @staticmethod
    def persistent_keyboard() -> Any:
        """Return the keyboard used on a normal outgoing bot reply."""
        return UniversalMenu().keyboard()

    def keyboard(self) -> Any:
        if ReplyKeyboardMarkup is None:
            return None
        return ReplyKeyboardMarkup(
            [[KeyboardButton(label) for label in row] for row in self.BUTTONS],
            resize_keyboard=True,
            is_persistent=False,
        )

    async def handle_update(self, update: Any, context: Any) -> None:
        message = getattr(update, "effective_message", None)
        if message is None:
            return
        text = (getattr(message, "text", None) or "").strip()
        if text == "☰ Меню":
            await message.reply_text("Меню Universal Menu включено.", reply_markup=self.keyboard())
        elif text == "⚙ Сервисы":
            await message.reply_text(self._services_text(), reply_markup=self.keyboard())
        elif text == "🔀 Сменить модель":
            await message.reply_text("Для выбора модели отправь команду /model.", reply_markup=self.keyboard())
        elif text == "ℹ Помощь":
            await message.reply_text(self._help_text(), reply_markup=self.keyboard())

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
