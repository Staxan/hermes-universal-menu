"""Read-only ENOT/Yonote client used by Universal Menu."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


class EnotAdapter:
    """Small profile-aware client for the Yonote RPC API."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        self.api_url = str(config.get("api_url", "https://app.yonote.ru/api")).rstrip("/")
        self.token = str(config.get("token", ""))
        self.timeout = int(config.get("timeout", 15))

    @property
    def configured(self) -> bool:
        return bool(self.api_url and self.token)

    def _request(self, method: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call one Yonote RPC method without leaking credentials."""
        if not self.token:
            return {"ok": False, "error": "missing_token"}
        body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"{self.api_url}/{method.lstrip('/')}",
            data=body,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
            return result if isinstance(result, dict) else {"ok": False, "error": "invalid_response"}
        except urllib.error.HTTPError as exc:
            return {"ok": False, "error": f"HTTP {exc.code}"}
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return {"ok": False, "error": str(exc)[:120] or "network_error"}
        except (ValueError, json.JSONDecodeError):
            return {"ok": False, "error": "invalid_json"}

    @staticmethod
    def _items(response: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
        data = response.get("data", [])
        if isinstance(data, dict):
            data = data.get(key, data.get("items", []))
        elif isinstance(data, list):
            # Yonote отдаёт коллекции и документы списком прямо в поле data.
            data = data
        if not isinstance(data, list):
            return []
        return [item for item in data if isinstance(item, dict)]

    def auth_info(self) -> Dict[str, Any]:
        return self._request("auth.info", {})

    def validate(self) -> bool:
        response = self.auth_info()
        return response.get("ok", True) is not False and "error" not in response

    def get_collections(self) -> List[Dict[str, Any]]:
        return self._items(self._request("collections.list", {"limit": 100, "offset": 0}), "collections")

    def get_documents(self, collection_id: Optional[str] = None) -> List[Dict[str, Any]]:
        payload: Dict[str, Any] = {"limit": 100, "offset": 0}
        if collection_id:
            payload["collectionId"] = collection_id
        return self._items(self._request("documents.list", payload), "documents")

    def get_document(self, document_id: str) -> Dict[str, Any]:
        response = self._request("documents.info", {"id": document_id})
        data = response.get("data")
        return data if isinstance(data, dict) else {}

    @staticmethod
    def document_url(document: Dict[str, Any]) -> str:
        url = document.get("url") or document.get("publicUrl")
        if url:
            url = str(url)
            if url.startswith("/"):
                return "https://app.yonote.ru" + url
            return url
        identifier = document.get("urlId") or document.get("id", "")
        return f"https://app.yonote.ru/doc/{identifier}" if identifier else ""


def adapter_from_profile() -> EnotAdapter:
    """Build an adapter from the active profile without printing the token."""
    try:
        from ..services import enot_settings
    except ImportError:
        try:
            from services import enot_settings
        except ImportError:
            enot_settings = lambda: {}
    settings = enot_settings()
    token_env = str(settings.get("token_env", "YONOTE_API_KEY"))
    config = dict(settings)
    config["api_url"] = settings.get("api_url", "https://app.yonote.ru/api")
    config["token"] = os.environ.get(token_env, "")
    return EnotAdapter(config)


__all__ = ["EnotAdapter", "adapter_from_profile"]
