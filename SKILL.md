---
name: universal-menu
description: Universal menu system for Hermes Telegram agents — dynamic inline/ReplyKeyboard menus, external service adapters (ENOT, GitHub, Notion), model switcher, and GitHub auto-update.
version: 0.1.0
author: Staxan
---

# Universal Menu Skill

Provides a persistent ReplyKeyboard with quick-access buttons and dynamic InlineKeyboard menus for external services. Supports installation and updates directly from GitHub.

## Features

- Persistent ReplyKeyboard (`/menu` toggles it)
- Dynamic InlineKeyboard menus from external services
- ENOT/Yonote document picker (projects → collections → documents)
- Model switcher shortcut
- Service configuration via `~/.hermes/skills/universal-menu/config.yaml`
- GitHub auto-update: `/install <url>` and `/update <skill>`

## Commands

| Command | Description |
|---------|-------------|
| `/menu` | Show/hide ReplyKeyboard |
| `/services` | Manage connected services |
| `/model` | Switch model (enhanced) |
| `/install <url>` | Install skill from GitHub |
| `/update <name>` | Update installed skill |

## Configuration

