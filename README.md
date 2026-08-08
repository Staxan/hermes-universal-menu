# Hermes Universal Menu

Profile-local Telegram menu plugin for Hermes Agent.

## Что это

Пакет состоит из двух частей:

- **Hermes plugin** — регистрирует провайдер Telegram-меню через официальный plugin API;
- **skill/documentation** — описывает работу меню и настройку сервисов.

Установщик не патчит `telegram.py` и не меняет ядро Hermes. Сервисы не нужны для запуска базового меню.

## Требования

- Hermes Agent с plugin API `register_telegram_menu`;
- Telegram Gateway;
- профиль Hermes, для которого включается plugin.

## Установка

```bash
hermes --profile <профиль> plugins install \
  https://github.com/Staxan/hermes-universal-menu.git \
  --enable
```

Если версия CLI не поддерживает `--enable`:

```bash
hermes --profile <профиль> plugins install \
  https://github.com/Staxan/hermes-universal-menu.git
hermes --profile <профиль> plugins enable universal-menu
```

После этого перезапусти только gateway целевого профиля:

```bash
hermes --profile <профиль> gateway restart
hermes --profile <профиль> gateway status
```

Базовые кнопки появляются после первого ответа бота:

```text
☰ Меню     ⚙ Сервисы
🔀 Сменить модель     ℹ Помощь
```

## Смена модели

Кнопка показывает команду `/model`. Это намеренно: выбор модели и callback-логика остаются в штатном Hermes Gateway. Переключение модели для текущей сессии выполняется без перезапуска gateway.

## Сервисы

Кнопка `⚙ Сервисы` пока показывает безопасный статус и не требует секретов. ENOT/Yonote подключается следующим этапом через service adapter.

Ручной шаблон настроек:

```bash
cp config.example.yaml ~/.hermes/profiles/<профиль>/universal_menu.yaml
chmod 600 ~/.hermes/profiles/<профиль>/universal_menu.yaml
```

Секреты хранятся только в profile `.env`:

```bash
chmod 600 ~/.hermes/profiles/<профиль>/.env
# ENOT_API_TOKEN=<секрет>
```

Никогда не добавляй токены в GitHub, `config.example.yaml` или сообщения Telegram.

## Обновление и удаление

```bash
hermes --profile <профиль> plugins update universal-menu
hermes --profile <профиль> gateway restart

hermes --profile <профиль> plugins disable universal-menu
hermes --profile <профиль> plugins remove universal-menu
```

## Структура plugin API

Провайдер может реализовать:

- `build_reply_keyboard(adapter, chat_id, metadata)`;
- `handle_text(adapter, update, context)`;
- `handle_callback(adapter, update, context)`.

Обработчики вызываются только для загруженных и включённых plugin-ов. Ошибка стороннего провайдера не ломает основной Telegram Gateway.

## Ограничения MVP

- Telegram wizard добавления ENOT ещё не подключён;
- callback `um:` зарезервирован, но сервисные операции ещё не реализованы;
- установка требует версии Hermes, где есть `register_telegram_menu`;
- для изменения Python-кода Hermes нужен перезапуск gateway.

Проверка локального пакета:

```bash
python3 -m py_compile __init__.py menu.py
```

Проверка изменённого Hermes:

```bash
python3 -m py_compile \
  ~/.hermes/hermes-agent/hermes_cli/plugins.py \
  ~/.hermes/hermes-agent/plugins/platforms/telegram/adapter.py
```

## Лицензия

MIT

---

Состояние `v0.2.0`: минимальный plugin API и profile-local Telegram keyboard MVP.
