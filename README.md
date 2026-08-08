# 🌐 Hermes Universal Menu

> Универсальное меню для Telegram-агентов Hermes: постоянная клавиатура, inline-меню внешних сервисов и быстрый доступ к ENOT/Yonote.

## 📦 Возможности

- Постоянное Telegram-меню (`ReplyKeyboard`) с быстрыми кнопками.
- Динамические inline-меню для выбора проектов, коллекций и документов.
- ENOT / Yonote: выбор документа и получение ссылки в чате.
- Отправка последнего сообщения в ENOT.
- Переключатель LLM-модели и управление подключёнными сервисами.
- Установка и обновление скилла из GitHub.

## Требования

- Hermes Agent с поддержкой skills.
- Telegram-профиль Hermes — для работы кнопок в Telegram.
- Python 3.10 или новее — для ручной установки и запуска Python-компонентов.
- Git — для установки из репозитория и обновлений.

## 🚀 Установка

### Способ 1. Через Telegram-бота

Если в профиле уже включены команды установки skills, отправь агенту:

```text
/install https://github.com/Staxan/hermes-universal-menu.git
```

После установки перезапусти профиль Hermes или его gateway, если это требуется текущей конфигурацией. Затем проверь меню командой:

```text
/menu
```

> В текущей версии репозитория Telegram-команда установки должна быть подключена в самом профиле Hermes. Если `/install` не распознаётся, используй ручной способ ниже.

### Способ 2. Ubuntu / WSL

```bash
# 1. Установить зависимости
sudo apt update
sudo apt install -y git python3 python3-venv

# 2. Скачать репозиторий
mkdir -p "$HOME/.hermes/repositories"
git clone https://github.com/Staxan/hermes-universal-menu.git \
  "$HOME/.hermes/repositories/hermes-universal-menu"

# 3. Создать каталог скилла
mkdir -p "$HOME/.hermes/skills/universal-menu"

# 4. Скопировать файлы скилла
cp -r "$HOME/.hermes/repositories/hermes-universal-menu/"* \
  "$HOME/.hermes/skills/universal-menu/"

# 5. Проверить установленные файлы
find "$HOME/.hermes/skills/universal-menu" -maxdepth 2 -type f | sort
```

Если в твоей конфигурации Hermes используется виртуальное окружение, активируй его перед запуском Hermes:

```bash
python3 -m venv "$HOME/.hermes/venvs/universal-menu"
source "$HOME/.hermes/venvs/universal-menu/bin/activate"
python -m pip install --upgrade pip
```

### Способ 3. Windows PowerShell

Открой PowerShell и выполни:

```powershell
# 1. Проверить Git и Python
 git --version
 python --version

# 2. Скачать репозиторий
$repo = "$HOME\.hermes\repositories\hermes-universal-menu"
New-Item -ItemType Directory -Force -Path "$HOME\.hermes\repositories" | Out-Null
git clone https://github.com/Staxan/hermes-universal-menu.git $repo

# 3. Создать каталог скилла
$skill = "$HOME\.hermes\skills\universal-menu"
New-Item -ItemType Directory -Force -Path $skill | Out-Null

# 4. Скопировать файлы
Copy-Item -Path "$repo\*" -Destination $skill -Recurse -Force

# 5. Проверить установку
Get-ChildItem $skill -Recurse -File | Select-Object FullName
```

> Если Hermes запущен внутри WSL, используй инструкцию Ubuntu/WSL и выполняй команды в терминале WSL, а не в PowerShell.

### Способ 4. macOS

```bash
# 1. Проверить Git и Python
xcode-select --install  # можно пропустить, если Git уже установлен
python3 --version

# 2. Скачать репозиторий
mkdir -p "$HOME/.hermes/repositories"
git clone https://github.com/Staxan/hermes-universal-menu.git \
  "$HOME/.hermes/repositories/hermes-universal-menu"

# 3. Установить файлы скилла
mkdir -p "$HOME/.hermes/skills/universal-menu"
cp -r "$HOME/.hermes/repositories/hermes-universal-menu/"* \
  "$HOME/.hermes/skills/universal-menu/"
```

### Способ 5. Через CLI Hermes

Если конкретная версия Hermes поддерживает установку skills из GitHub, используй:

```bash
hermes skills install https://github.com/Staxan/hermes-universal-menu.git
```

Проверь доступные команды в своей версии:

```bash
hermes skills --help
```

Если команда `hermes skills install` отсутствует, используй ручную установку из раздела Ubuntu/WSL, Windows или macOS.

## ⚙️ Настройка ENOT / Yonote

Создай конфигурацию:

```bash
mkdir -p "$HOME/.hermes/skills/universal-menu"
cp examples/config.example.json \
  "$HOME/.hermes/skills/universal-menu/config.json"
```

Открой файл и укажи настоящий токен ENOT:

```json
{
  "services": {
    "enot": {
      "api_url": "https://anewera.yonote.ru/api",
      "token": "YOUR_ENOT_TOKEN",
      "collections": ["projects", "docs"],
      "enabled": true
    }
  }
}
```

Токены не публикуй в GitHub и не вставляй в `config.example.json`.

## 🎛️ Команды

| Команда | Назначение |
|---|---|
| `/menu` | Показать или скрыть постоянную клавиатуру |
| `/services` | Посмотреть и настроить подключённые сервисы |
| `/model` | Открыть переключатель модели |
| `/install <URL>` | Установить скилл из GitHub |
| `/update <name>` | Обновить установленный скилл |

Основные кнопки меню:

- `📎 ENOT` — выбрать документ ENOT/Yonote.
- `⏏️ ENOT` — отправить последнее сообщение в ENOT.
- `⚙️ Services` — открыть настройки сервисов.
- `🔀 Switch Model` — сменить модель.

## 🔄 Обновление

Ubuntu/WSL и macOS:

```bash
cd "$HOME/.hermes/repositories/hermes-universal-menu"
git pull --ff-only
cp -r ./* "$HOME/.hermes/skills/universal-menu/"
```

Windows PowerShell:

```powershell
$repo = "$HOME\.hermes\repositories\hermes-universal-menu"
$skill = "$HOME\.hermes\skills\universal-menu"
Set-Location $repo
git pull --ff-only
Copy-Item -Path "$repo\*" -Destination $skill -Recurse -Force
```

После обновления перезапусти профиль Hermes или gateway, если изменения не подхватились автоматически.

## 🧪 Проверка установки

```bash
# Проверить наличие ключевых файлов
ls "$HOME/.hermes/skills/universal-menu"

# Проверить Python-файлы
python3 -m py_compile \
  "$HOME/.hermes/skills/universal-menu/handlers/menu.py" \
  "$HOME/.hermes/skills/universal-menu/handlers/enot.py" \
  "$HOME/.hermes/skills/universal-menu/commands/install.py"
```

В Telegram отправь:

```text
/menu
```

Затем проверь отображение клавиатуры и команду `/services`.

## 🗑️ Удаление

Ubuntu/WSL и macOS:

```bash
rm -rf "$HOME/.hermes/skills/universal-menu"
rm -rf "$HOME/.hermes/repositories/hermes-universal-menu"
```

Windows PowerShell:

```powershell
Remove-Item "$HOME\.hermes\skills\universal-menu" -Recurse -Force
Remove-Item "$HOME\.hermes\repositories\hermes-universal-menu" -Recurse -Force
```

## ⚠️ Известные ограничения текущей версии

- Поддержка конкретных команд зависит от версии и конфигурации Hermes.
- Интеграция Telegram должна быть зарегистрирована профилем Hermes.
- Установщик и манифест требуют дополнительного согласования форматов перед полностью автоматической установкой.
- GitHub, Notion и Obsidian заявлены как дальнейшие адаптеры и могут быть недоступны в текущей версии.

## Лицензия

MIT. См. файл [LICENSE](LICENSE).
