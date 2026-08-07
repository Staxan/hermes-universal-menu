"""ENOT/Yonote adapter for universal-menu skill."""

import json
from typing import Any, Dict, List, Optional

from hermes_tools import terminal


class EnotAdapter:
    """Adapter for ENOT/Yonote API."""

    def __init__(self, config: Dict[str, Any]):
        self.api_url = config.get("api_url", "https://anewera.yonote.ru/api")
        self.token = config.get("token", "")
        self.collections = config.get("collections", [])

    def _request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Make an API request to ENOT."""
        cmd = f'curl -s -X {method} "{self.api_url}, {endpoint}"'
        if self.token:
            cmd += f' -H "Authorization: Bearer {self.token}"'
        if data:
            cmd += f' -H "Content-Type: application/json" -d \'{json.dumps(data)}\' '
        result = terminal(command=cmd, timeout=30)
        if result.get("exit_code") != 0:
            return {"error": result.get("error", "Unknown error")}
        try:
            return json.loads(result.get("output", "{}"))
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw": result.get("output")}

    def get_collections(self) -> List[Dict]:
        """Get list of collections/projects."""
        resp = self._request("collections")
        if "error" in resp:
            return []
        return resp.get("data", [])

    def get_documents(self, collection_id: str) -> List[Dict]:
        """Get documents in a collection."""
        resp = self._request(f"collections/{collection_id}/documents")
        if "error" in resp:
            return []
        return resp.get("data", [])

    def get_document_url(self, document_id: str) -> str:
        """Get public URL for a document."""
        return f"https://anewera.yonote.ru/doc/{document_id}"

    def validate(self) -> bool:
        """Validate API access."""
        resp = self._request("auth.info")
        return "error" not in resp
