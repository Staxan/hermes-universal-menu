import asyncio
import importlib.util
import sys
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


def test_callback_namespace_is_compact():
    assert UniversalMenu.CALLBACK_PREFIX == "um:"


if __name__ == "__main__":
    for name in sorted(globals()):
        if name.startswith("test_"):
            globals()[name]()
    print("8 smoke tests passed")
