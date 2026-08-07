"""Install/update commands for universal-menu skill."""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Optional

from hermes_tools import read_file, terminal, write_file


class RepositoryManager:
    """Manages GitHub repositories for skills."""

    SKILLS_DIR = Path.home() / ".hermes" / "skills"
    REPO_DIR = Path.home() / ".hermes" / "repositories"

    def __init__(self):
        self.REPO_DIR.mkdir(parents=True, exist_ok=True)

    def install_from_github(self, url: str) -> Dict:
        """Install a skill from GitHub repository."""
        # Parse repo name from URL
        repo_name = url.split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        repo_path = self.REPO_DIR / repo_name

        # Clone if not exists
        if repo_path.exists():
            # Update
            result = terminal(
                command=f"cd {repo_path} && git pull",
                timeout=60
            )
        else:
            result = terminal(
                command=f"git clone {url}, {repo_path}",
                timeout=120
            )

        if result.get("exit_code") != 0:
            return {"success": False, "error": result.get("error", "Git clone failed")}

        # Read manifest
        manifest_path = repo_path / "manifest.json"
        if not manifest_path.exists():
            return {"success": False, "error": "manifest.json not found"}

        try:
            manifest_content = read_file(path=str(manifest_path))
            manifest = json.loads(manifest_content.get("content", "{}"))
        except Exception as e:
            return {"success": False, "error": f"Invalid manifest: {e}"}

        # Install skills
        installed = []
        for skill in manifest.get("skills", []):
            skill_path = repo_path / skill.get("path", "")
            if skill_path.exists():
                target_path = self.SKILLS_DIR / skill.get("id", skill.get("name", repo_name))
                # Copy skill directory
                terminal(
                    command=f"cp -r {skill_path}, {target_path}",
                    timeout=30
                )
                installed.append(skill.get("id", skill.get("name")))

        # Save repo info
        repo_info = {
            "name": repo_name,
            "url": url,
            "path": str(repo_path),
            "version": manifest.get("version", "0.0.0"),
            "installed": installed
        }
        info_path = self.REPO_DIR / f"{repo_name}.json"
        write_file(path=str(info_path), content=json.dumps(repo_info, indent=2))

        return {
            "success": True,
            "repo_name": repo_name,
            "installed": installed,
            "version": repo_info["version"]
        }

    def update(self, name: str) -> Dict:
        """Update an installed repository."""
        info_path = self.REPO_DIR / f"{name}.json"
        if not info_path.exists():
            return {"success": False, "error": f"Repository '{name}' not found"}

        try:
            info_content = read_file(path=str(info_path))
            repo_info = json.loads(info_content.get("content", "{}"))
        except Exception:
            return {"success": False, "error": "Invalid repo info"}

        repo_path = Path(repo_info.get("path", ""))
        if not repo_path.exists():
            return {"success": False, "error": f"Repository path not found: {repo_path}"}

        result = terminal(
            command=f"cd {repo_path} && git pull && git rev-parse HEAD",
            timeout=60
        )

        if result.get("exit_code") != 0:
            return {"success": False, "error": result.get("error", "Git pull failed")}

        # Re-read manifest and update skills
        manifest_path = repo_path / "manifest.json"
        try:
            manifest_content = read_file(path=str(manifest_path))
            manifest = json.loads(manifest_content.get("content", "{}"))
        except Exception:
            return {"success": False, "error": "Invalid manifest"}

        # Re-install skills
        installed = []
        for skill in manifest.get("skills", []):
            skill_path = repo_path / skill.get("path", "")
            if skill_path.exists():
                target_path = self.SKILLS_DIR / skill.get("id", skill.get("name", name))
                terminal(
                    command=f"cp -r {skill_path}, {target_path}",
                    timeout=30
                )
                installed.append(skill.get("id", skill.get("name")))

        repo_info["version"] = manifest.get("version", repo_info.get("version"))
        repo_info["installed"] = installed
        write_file(path=str(info_path), content=json.dumps(repo_info, indent=2))

        return {
            "success": True,
            "repo_name": name,
            "version": repo_info["version"],
            "updated": installed
        }
