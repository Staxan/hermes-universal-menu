import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace


def load_menu():
    path = Path(__file__).parents[1] / "menu.py"
    spec = importlib.util.spec_from_file_location("universal_menu_menu", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.UniversalMenu


UniversalMenu = load_menu()


def test_menu_labels_and_keyboard_without_telegram_dependency():
    menu = UniversalMenu()
    assert "☰ Меню" in {label for row in menu.BUTTONS for label in row}
    assert menu._services_text().startswith("⚙ Сервисы")


def test_text_handler_consumes_menu_button():
    sent = []

    class Adapter:
        async def send(self, chat_id, content, **kwargs):
            sent.append((chat_id, content, kwargs))

    message = SimpleNamespace(text="ℹ Помощь", chat=SimpleNamespace(id=42), message_thread_id=None)
    update = SimpleNamespace(effective_message=message)
    consumed = asyncio.run(UniversalMenu().handle_text(Adapter(), update, None))
    assert consumed is True
    assert sent[0][0] == "42"
    assert "/model" in sent[0][1]


def test_callback_handler_only_consumes_um_namespace():
    menu = UniversalMenu()

    class Query:
        data = "other:callback"

        async def answer(self):
            pass

    update = SimpleNamespace(callback_query=Query())
    assert asyncio.run(menu.handle_callback(None, update, None)) is False


def test_callback_handler_consumes_um_namespace():
    class Query:
        data = "um:services"

        async def answer(self):
            self.answered = True

    query = Query()
    update = SimpleNamespace(callback_query=query)
    assert asyncio.run(UniversalMenu().handle_callback(None, update, None)) is True
    assert query.answered is True


if __name__ == "__main__":
    for name in (
        "test_menu_labels_and_keyboard_without_telegram_dependency",
        "test_text_handler_consumes_menu_button",
        "test_callback_handler_only_consumes_um_namespace",
        "test_callback_handler_consumes_um_namespace",
    ):
        globals()[name]()
    print("4 smoke tests passed")
