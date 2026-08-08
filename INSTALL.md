# Установка Hermes Universal Menu

Этот файл содержит подробную инструкцию для Ubuntu/WSL, Windows, macOS и Telegram.

## Что устанавливается

Скилл устанавливается в каталог:

```text
~/.hermes/skills/universal-menu
```

Исходный репозиторий рекомендуется хранить отдельно:

```text
~/.hermes/repositories/hermes-universal-menu
```

## Вариант 1. Установка через Telegram

В чате с агентом Hermes отправь:

```text
/install https://github.com/Staxan/hermes-universal-menu.git
```

После установки выполни:

```text
/menu
```

Если команда `/install` не поддерживается текущим профилем, используй ручную установку.

## Вариант 2. Ubuntu / WSL

```bash
sudo apt update
sudo apt install -y git python3 python3-venv

mkdir -p "$HOME/.hermes/repositories"
git clone https://github.com/Staxan/hermes-universal-menu.git \
  "$HOME/.hermes/repositories/hermes-universal-menu"

mkdir -p "$HOME/.hermes/skills/universal-menu"
cp -r "$HOME/.hermes/repositories/hermes-universal-menu/"* \
  "$HOME/.hermes/skills/universal-menu/"
```

Проверка Python-файлов:

```bash
python3 -m py_compile \
  "$HOME/.hermes/skills/universal-menu/handlers/menu.py" \
  "$HOME/.hermes/skills/universal-menu/handlers/enot.py" \
  "$HOME/.hermes/skills/universal-menu/commands/install.py"
```

## Вариант 3. Windows PowerShell

Установи Git и Python 3.10+ заранее, затем выполни:

```powershell
git --version
python --version

$repo = "$HOME\.hermes\repositories\hermes-universal-menu"
$skill = "$HOME\.hermes\skills\universal-menu"

New-Item -ItemType Directory -Force -Path "$HOME\.hermes\repositories" | Out-Null
git clone https://github.com/Staxan/hermes-universal-menu.git $repo

New-Item -ItemType Directory -Force -Path $skill | Out-Null
Copy-Item -Path "$repo\*" -Destination $skill -Recurse -Force

Get-ChildItem $skill -Recurse -File | Select-Object FullName
```

Если Hermes работает внутри WSL, выполняй команды из раздела Ubuntu/WSL.

## Вариант 4. macOS

```bash
xcode-select --install  # пропусти, если Git уже установлен
python3 --version

git clone https://github.com/Staxan/hermes-universal-menu.git \
  "$HOME/.hermes/repositories/hermes-universal-menu"

mkdir -p "$HOME/.hermes/skills/universal-menu"
cp -r "$HOME/.hermes/repositories/hermes-universal-menu/"* \
  "$HOME/.hermes/skills/universal-menu/"
```

## Вариант 5. CLI Hermes

Если команда доступна в установленной версии Hermes:

```bash
hermes skills install https://github.com/Staxan/hermes-universal-menu.git
```

Проверка:

```bash
hermes skills --help
```

## Настройка ENOT / Yonote

Создай конфигурацию на Linux/macOS:

```bash
cp "$HOME/.hermes/repositories/hermes-universal-menu/examples/config.example.json" \
  "$HOME/.hermes/skills/universal-menu/config.json"
```

На Windows PowerShell:

```powershell
Copy-Item `
  "$HOME\.hermes\repositories\hermes-universal-menu\examples\config.example.json" `
  "$HOME\.hermes\skills\universal-menu\config.json"
```

В `config.json` укажи токен ENOT:

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

Не публикуй настоящий токен в GitHub.

## Проверка в Telegram

1. Перезапусти профиль Hermes или gateway, если он не перечитал skills автоматически.
2. Отправь `/menu`.
3. Убедись, что появилась клавиатура.
4. Отправь `/services` и проверь подключённые сервисы.

## Обновление

Linux/macOS:

```bash
cd "$HOME/.hermes/repositories/hermes-universal-menu"
git pull --ff-only
cp -r ./* "$HOME/.hermes/skills/universal-menu/"
```

Windows PowerShell:

```powershell
Set-Location "$HOME\.hermes\repositories\hermes-universal-menu"
git pull --ff-only
Copy-Item -Path "$HOME\.hermes\repositories\hermes-universal-menu\*" `
  -Destination "$HOME\.hermes\skills\universal-menu" -Recurse -Force
```

## Удаление

Linux/macOS:

```bash
rm -rf "$HOME/.hermes/skills/universal-menu"
rm -rf "$HOME/.hermes/repositories/hermes-universal-menu"
```

Windows PowerShell:

```powershell
Remove-Item "$HOME\.hermes\skills\universal-menu" -Recurse -Force
Remove-Item "$HOME\.hermes\repositories\hermes-universal-menu" -Recurse -Force
```

## Известное ограничение

Автоматическая установка через текущий `commands/install.py` требует отдельного исправления: сейчас код ожидает `manifest.json`, а репозиторий содержит `manifest.yaml`. Поэтому до исправления установщика используй ручную установку или CLI-команду Hermes, если она поддерживается твоей версией.
