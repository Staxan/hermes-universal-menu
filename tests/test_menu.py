import asyncio
import importlib.util
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))


def load_menu():
    path = Path(__file__).parents[1] / "menu.py"
    spec = importlib.util.spec_from_file_location("universal_menu_test_menu", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.UniversalMenu


UniversalMenu = load_menu()


class Message:
    def __init__(self, text):
        self.text = text
        self.replies = []

    async def reply_text(self, text, **kwargs):
        self.replies.append((text, kwargs))


def test_labels():
    assert UniversalMenu.BUTTONS[0] == ("☰ Меню", "⚙ Сервисы")
    assert UniversalMenu.BUTTONS[1] == ("🔀 Сменить модель", "ℹ Помощь")


def test_text_handler_replies_to_menu_button():
    message = Message("☰ Меню")
    update = SimpleNamespace(effective_message=message)
    asyncio.run(UniversalMenu().handle_update(update, None))
    assert message.replies
    assert "включено" in message.replies[0][0]


def test_services_button_is_not_static_placeholder():
    message = Message("⚙ Сервисы")
    update = SimpleNamespace(effective_message=message)
    asyncio.run(UniversalMenu().handle_update(update, None))
    assert message.replies
    assert "inline" in message.replies[0][0]


def test_unknown_text_is_safe():
    message = Message("обычный текст")
    update = SimpleNamespace(effective_message=message)
    asyncio.run(UniversalMenu().handle_update(update, None))
    assert message.replies == []


def test_register_handlers_public_api_exists():
    assert callable(UniversalMenu().register_handlers)


def test_help_text_is_non_secret():
    assert "token" not in UniversalMenu._help_text().lower()


def test_model_button_mentions_builtin_command():
    message = Message("🔀 Сменить модель")
    update = SimpleNamespace(effective_message=message)
    asyncio.run(UniversalMenu().handle_update(update, None))
    assert "/model" in message.replies[0][0]


def test_help_text_explains_service_integration():
    text = UniversalMenu._help_text()
    assert "адаптер" in text
    assert "config.yaml" in text
    assert ".env" in text
    assert "Notion" in text and "Confluence" in text
    assert "не уже подключённые сервисы" in text


def test_callback_namespace_is_compact():
    assert UniversalMenu.CALLBACK_PREFIX == "um:"


def test_active_document_context_is_injected_until_cleared():
    menu = UniversalMenu()
    menu._active_documents["42"] = {
        "id": "doc-1",
        "title": "Книга. Версия 6.0",
        "url": "https://app.yonote.ru/doc/doc-1",
        "text": "Текст документа",
    }
    result = menu._inject_active_document(
        platform="telegram", sender_id="42", user_message="Сделай краткий план"
    )
    assert result and "Книга. Версия 6.0" in result["context"]
    assert "Текст документа" in result["context"]
    assert menu._inject_active_document(
        platform="telegram", sender_id="42", user_message="новая тема"
    ) is None
    assert "42" not in menu._active_documents


def test_active_document_storage_round_trip():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "active.json"
        original = UniversalMenu._active_documents_path
        UniversalMenu._active_documents_path = staticmethod(lambda: path)
        try:
            documents = {"42": {"id": "doc-1", "title": "Книга", "text": "текст"}}
            UniversalMenu._save_active_documents(documents)
            assert UniversalMenu._load_active_documents() == documents
        finally:
            UniversalMenu._active_documents_path = original


if __name__ == "__main__":
    tests = [
        value for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    ]
    for test in sorted(tests, key=lambda item: item.__name__):
        test()
    print(f"{len(tests)} smoke tests passed")
