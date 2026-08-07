"""Menu handler for universal-menu skill."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class MenuManager:
    """Manages ReplyKeyboard and InlineKeyboard menus."""

    def __init__(self, config_path: str = "~/.hermes/skills/universal-menu/config.json"):
        self.config_path = Path(config_path).expanduser()
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            return {"services": {}}
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception:
            return {"services": {}}

    def _save_config(self) -> None:
        """Save configuration."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_reply_keyboard(self, user_id: str = None) -> List[List[str]]:
        """Get ReplyKeyboard layout."""
        services = self.config.get("services", {})
        buttons = []

        if "enot" in services and services["enot"].get("enabled", True):
            buttons.append(["📎 ENOT", "⏏️ ENOT"])

        if services:
            buttons.append(["⚙️ Services"])

        buttons.append(["🔀 Switch Model"])

        return buttons

    def get_inline_menu(self, menu_type: str, data: Any = None) -> List[List[Dict[str, str]]]:
        """Get InlineKeyboard layout for dynamic menus."""
        if menu_type == "enot_collections":
            return self._build_collection_menu(data)
        elif menu_type == "enot_documents":
            return self._build_document_menu(data)
        elif menu_type == "services":
            return self._build_services_menu()
        return []

    def _build_collection_menu(self, collections: List[Dict]) -> List[List[Dict[str, str]]]:
        """Build collection selection menu."""
        menu = []
        for col in collections[:10]:
            menu.append([{
                "text": col.get("name", "Untitled"),
                "callback_data": f"enot_collection:{col.get('id')}"
            }])
        menu.append([{
            "text": "🔙 Back",
            "callback_data": "enot_back"
        }])
        return menu

    def _build_document_menu(self, documents: List[Dict]) -> List[List[Dict[str, str]]]:
        """Build document selection menu."""
        menu = []
        for doc in documents[:10]:
            menu.append([{
                "text": doc.get("title", "Untitled"),
                "callback_data": f"enot_document:{doc.get('id')}"
            }])
        menu.append([{
            "text": "🔙 Back",
            "callback_data": "enot_back"
        }])
        return menu

    def _build_services_menu(self) -> List[List[Dict[str, str]]]:
        """Build services management menu."""
        services = self.config.get("services", {})
        menu = []
        for name, config in services.items():
            status = "✅" if config.get("enabled", True) else "❌"
            menu.append([{
                "text": f"{status}, {name.upper()}",
                "callback_data": f"service_toggle:{name}"
            }])
        menu.append([{
            "text": "➕ Add Service",
            "callback_data": "service_add"
        }])
        menu.append([{
            "text": "🔙 Back",
            "callback_data": "menu_back"
        }])
        return menu

    def add_service(self, name: str, config: Dict) -> None:
        """Add or update a service configuration."""
        self.config.setdefault("services", {})[name] = config
        self._save_config()

    def toggle_service(self, name: str) -> bool:
        """Toggle service enabled state. Returns new state."""
        services = self.config.get("services", {})
        if name not in services:
            return False
        current = services[name].get("enabled", True)
        services[name]["enabled"] = not current
        self._save_config()
        return not current
