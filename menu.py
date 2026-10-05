"""Telegram handlers for the Universal Menu plugin."""

from __future__ import annotations

import re
from typing import Any, Dict, List

try:
    from telegram import (
        InlineKeyboardButton,
        InlineKeyboardMarkup,
        KeyboardButton,
        ReplyKeyboardMarkup,
    )
    from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, filters
except ImportError:  # pragma: no cover - loaded only in Telegram runtime
    InlineKeyboardButton = InlineKeyboardMarkup = KeyboardButton = ReplyKeyboardMarkup = None
    CallbackQueryHandler = CommandHandler = MessageHandler = filters = None

try:
    from .handlers.enot import EnotAdapter, adapter_from_profile
    from .services import enot_settings
except ImportError:  # pragma: no cover - direct smoke-test import
    from handlers.enot import EnotAdapter, adapter_from_profile
    from services import enot_settings


class UniversalMenu:
    """Profile-local Telegram menu with a read-only ENOT picker."""

    BUTTONS = (
        ("☰ Меню", "⚙ Сервисы"),
        ("🔀 Сменить модель", "ℹ Помощь"),
    )
    CALLBACK_PREFIX = "um:"

    def __init__(self) -> None:
        self._state: Dict[int, Dict[str, List[Dict[str, Any]]]] = {}
        self._active_documents: Dict[str, Dict[str, Any]] = {}

    def register_handlers(self, application: Any, adapter: Any) -> None:
        if any(item is None for item in (MessageHandler, CommandHandler, CallbackQueryHandler, filters)):
            raise RuntimeError("python-telegram-bot is required for Universal Menu")
        adapter._plugin_reply_markup = self.keyboard()
        # Inject the selected ENOT document into every subsequent agent turn.
        application._universal_menu = self
        application.add_handler(CommandHandler("menu", self.command_menu))
        application.add_handler(CommandHandler("services", self.command_services))
        application.add_handler(CommandHandler("help_menu", self.command_help))
        button_labels = [label for row in self.BUTTONS for label in row]
        button_filter = filters.Regex(r"^(?:" + "|".join(re.escape(label) for label in button_labels) + r")$")
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & button_filter, self.handle_update))
        application.add_handler(CallbackQueryHandler(self.handle_callback, pattern=r"^um:"))

    def register_context_hook(self, ctx: Any) -> None:
        """Register the active-document context through Hermes' public hook API."""
        ctx.register_hook("pre_llm_call", self._inject_active_document)

    async def command_menu(self, update: Any, context: Any) -> None:
        message = getattr(update, "effective_message", None)
        if message is not None:
            await message.reply_text("Меню Universal Menu включено.", reply_markup=self.keyboard())

    async def command_services(self, update: Any, context: Any) -> None:
        message = getattr(update, "effective_message", None)
        if message is not None:
            await message.reply_text(self._services_text(), reply_markup=self.keyboard())
            await self._show_services(update)

    async def command_help(self, update: Any, context: Any) -> None:
        message = getattr(update, "effective_message", None)
        if message is not None:
            await message.reply_text(self._help_text(), reply_markup=self.keyboard())

    @staticmethod
    def persistent_keyboard() -> Any:
        return UniversalMenu().keyboard()

    def keyboard(self) -> Any:
        if ReplyKeyboardMarkup is None:
            return None
        return ReplyKeyboardMarkup(
            [[KeyboardButton(label) for label in row] for row in self.BUTTONS],
            resize_keyboard=True,
            is_persistent=False,
        )

    @staticmethod
    def _chat_id(update: Any) -> int:
        chat = getattr(update, "effective_chat", None)
        return int(getattr(chat, "id", 0) or 0)

    async def handle_update(self, update: Any, context: Any) -> None:
        message = getattr(update, "effective_message", None)
        if message is None:
            return
        text = (getattr(message, "text", None) or "").strip()
        if text == "☰ Меню":
            await message.reply_text("Меню Universal Menu включено.", reply_markup=self.keyboard())
        elif text == "⚙ Сервисы":
            await message.reply_text(self._services_text(), reply_markup=self.keyboard())
            await self._show_services(update)
        elif text == "🔀 Сменить модель":
            await message.reply_text("Для выбора модели отправь команду /model.", reply_markup=self.keyboard())
        elif text == "ℹ Помощь":
            await message.reply_text(self._help_text(), reply_markup=self.keyboard())

    async def _show_services(self, update: Any) -> None:
        message = getattr(update, "effective_message", None)
        if message is None or InlineKeyboardMarkup is None:
            return
        settings = enot_settings()
        enabled = bool(settings.get("enabled", False))
        label = "✅ ENOT" if enabled else "⛔ ENOT выключен"
        rows = [[InlineKeyboardButton(label, callback_data=f"{self.CALLBACK_PREFIX}enot")]]
        await message.reply_text("Выбери сервис:", reply_markup=InlineKeyboardMarkup(rows))

    async def handle_callback(self, update: Any, context: Any) -> None:
        query = getattr(update, "callback_query", None)
        if query is None:
            return
        await query.answer()
        action = str(getattr(query, "data", "")).removeprefix(self.CALLBACK_PREFIX)
        if action == "enot":
            await self._show_enot_root(update)
        elif action == "collections":
            await self._show_collections(update)
        elif action.startswith("collection:"):
            await self._show_documents(update, action.split(":", 1)[1])
        elif action.startswith("document:"):
            await self._show_document(update, action.split(":", 1)[1])
        elif action == "back":
            await self._show_services(update)

    async def _show_enot_root(self, update: Any) -> None:
        query = update.callback_query
        adapter = adapter_from_profile()
        if not adapter.configured:
            await query.edit_message_text("❌ ENOT не настроен: проверь token_env и .env профиля.")
            return
        result = adapter.auth_info()
        if result.get("ok") is False or result.get("error"):
            await query.edit_message_text(f"❌ ENOT недоступен: {result.get('error', 'ошибка авторизации')}")
            return
        user = (result.get("data") or {}).get("user") or {}
        name = user.get("name") or user.get("email") or "доступ подтверждён"
        keyboard = [[InlineKeyboardButton("📚 Коллекции", callback_data=f"{self.CALLBACK_PREFIX}collections")],
                    [InlineKeyboardButton("🔙 Назад", callback_data=f"{self.CALLBACK_PREFIX}back")]]
        await query.edit_message_text(f"✅ ENOT подключён: {name}", reply_markup=InlineKeyboardMarkup(keyboard))

    async def _show_collections(self, update: Any) -> None:
        query = update.callback_query
        adapter = adapter_from_profile()
        collections = adapter.get_collections()
        chat_id = self._chat_id(update)
        self._state.setdefault(chat_id, {})["collections"] = collections
        if not collections:
            await query.edit_message_text("Коллекции не найдены или ENOT недоступен.", reply_markup=self._back_markup())
            return
        rows = []
        for index, collection in enumerate(collections[:20]):
            title = collection.get("name") or collection.get("title") or f"Коллекция {index + 1}"
            rows.append([InlineKeyboardButton(str(title)[:50], callback_data=f"{self.CALLBACK_PREFIX}collection:{index}")])
        rows.append([InlineKeyboardButton("🔙 Назад", callback_data=f"{self.CALLBACK_PREFIX}enot")])
        await query.edit_message_text("Выбери коллекцию:", reply_markup=InlineKeyboardMarkup(rows))

    async def _show_documents(self, update: Any, index_text: str) -> None:
        query = update.callback_query
        chat_id = self._chat_id(update)
        collections = self._state.get(chat_id, {}).get("collections", [])
        try:
            collection = collections[int(index_text)]
        except (ValueError, IndexError):
            await query.edit_message_text("Коллекция устарела. Открой меню заново.")
            return
        collection_id = collection.get("id")
        documents = adapter_from_profile().get_documents(collection_id)
        self._state.setdefault(chat_id, {})["documents"] = documents
        rows = []
        for index, document in enumerate(documents[:30]):
            title = document.get("title") or document.get("name") or f"Документ {index + 1}"
            rows.append([InlineKeyboardButton(str(title)[:50], callback_data=f"{self.CALLBACK_PREFIX}document:{index}")])
        rows.append([InlineKeyboardButton("🔙 Назад", callback_data=f"{self.CALLBACK_PREFIX}collections")])
        text = f"Документы коллекции: {collection.get('name', '')}" if documents else "Документы не найдены."
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows))

    async def _show_document(self, update: Any, index_text: str) -> None:
        query = update.callback_query
        documents = self._state.get(self._chat_id(update), {}).get("documents", [])
        try:
            document = documents[int(index_text)]
        except (ValueError, IndexError):
            await query.edit_message_text("Документ устарел. Открой меню заново.")
            return
        identifier = document.get("id") or document.get("urlId")
        fresh = adapter_from_profile().get_document(str(identifier)) if identifier else document
        title = fresh.get("title") or document.get("title") or "Документ"
        url = EnotAdapter.document_url(fresh or document)
        body = fresh.get("text", "")
        active_document = {
            "id": identifier,
            "title": title,
            "url": url,
            "text": str(body),
        }
        self._active_documents[str(self._chat_id(update))] = active_document
        user = getattr(update.callback_query, "from_user", None)
        user_id = getattr(user, "id", None)
        if user_id is not None:
            self._active_documents[str(user_id)] = active_document
        preview = str(body).strip()[:2500] if body else "Содержимое доступно в документе ENOT."
        suffix = f"\n\nОткрыть: {url}" if url else ""
        await query.edit_message_text(
            f"📄 {title}\n\n✅ Документ выбран. Следующие поручения относятся к нему.\n\n"
            f"{preview}{suffix}",
            reply_markup=self._back_markup(),
        )

    @staticmethod
    def _clear_document_command(text: str) -> bool:
        normalized = " ".join(text.casefold().replace("ё", "е").split())
        return normalized in {
            "сбросить документ",
            "снять документ",
            "перейти к другой теме",
            "переходим к другой теме",
            "новая тема",
        }

    def _inject_active_document(self, **kwargs: Any) -> Any:
        """Attach the active ENOT document to the current agent turn."""
        platform = kwargs.get("platform", "")
        platform = getattr(platform, "value", platform)
        if str(platform).casefold() not in {"telegram", ""}:
            return None
        user_message = str(kwargs.get("user_message", "") or "")
        key = str(kwargs.get("sender_id", "") or "")
        document = self._active_documents.get(key)
        if self._clear_document_command(user_message):
            self._active_documents.pop(key, None)
            return None
        if not document:
            return None
        content = document.get("text", "")
        if len(content) > 30000:
            content = content[:30000] + "\n[Содержимое сокращено; используй ID/ссылку документа для дальнейшей загрузки.]"
        return {
            "context": (
                "[АКТИВНЫЙ ДОКУМЕНТ ENOT]\n"
                f"Название: {document.get('title', 'Документ')}\n"
                f"ID: {document.get('id', '')}\n"
                f"Ссылка: {document.get('url', '')}\n"
                "Используй этот документ как объект текущего поручения. "
                "Не проси пользователя повторно присылать ссылку, пока он не выбрал другой документ "
                "или не сменил тему.\n"
                f"Содержимое:\n{content}\n"
                "[КОНЕЦ АКТИВНОГО ДОКУМЕНТА]"
            )
        }

    @staticmethod
    def _back_markup() -> Any:
        return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="um:collections")]])

    @staticmethod
    def _services_text() -> str:
        return "⚙ Сервисы\n\nENOT/Yonote открывается через inline-меню."

    @staticmethod
    def _help_text() -> str:
        return (
            "ℹ Как подключать сервисы\n\n"
            "Сервис подключается отдельным адаптером: задаём API-адрес и способ входа "
            "(ключ или OAuth), проверяем доступ, затем добавляем нужные действия и кнопки. "
            "Секреты хранятся в .env профиля, настройки — в config.yaml.\n\n"
            "Так же можно подключить, например, Notion, Google Drive/Docs, Confluence, "
            "Dropbox Paper, GitHub или Nextcloud — если у сервиса есть доступный API.\n\n"
            "Это примеры возможных интеграций, не уже подключённые сервисы."
        )


__all__ = ["UniversalMenu"]
