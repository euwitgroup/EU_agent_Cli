"""Filesystem tools for reading, writing, and editing files."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Binary file extensions to avoid reading as text
BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".pyc",
    ".pyo",
    ".bin",
    ".dat",
}

# Files to ignore by default (sensitive)
SENSITIVE_PATTERNS = {
    ".env",
    ".env.local",
    ".env.production",
    "credentials.json",
    "secrets.json",
    ".pem",
    ".key",
    "id_rsa",
    "id_ed25519",
}


def is_binary_file(file_path: Path) -> bool:
    """Check if a file is likely binary based on extension."""
    return file_path.suffix.lower() in BINARY_EXTENSIONS


def is_sensitive_file(file_path: Path) -> bool:
    """Check if a file is sensitive (contains secrets)."""
    name = file_path.name.lower()
    return any(pattern in name for pattern in SENSITIVE_PATTERNS)


def validate_path(workspace_dir: Path, file_path: str) -> Path:
    """
    Validate and resolve a file path within workspace.

    Args:
        workspace_dir: Workspace root directory
        file_path: File path to validate (can be relative or absolute)

    Returns:
        Resolved absolute path

    Raises:
        ValueError: If path is outside workspace or invalid
    """
    try:
        # Convert to Path and resolve
        if os.path.isabs(file_path):
            target = Path(file_path).resolve()
        else:
            target = (workspace_dir / file_path).resolve()

        # Ensure it's within workspace
        workspace_resolved = workspace_dir.resolve()
        if not str(target).startswith(str(workspace_resolved)):
            raise ValueError(f"Path outside workspace: {file_path}")

        return target

    except Exception as e:
        raise ValueError(f"Invalid path: {file_path} - {e}")


class FilesystemTools:
    """Filesystem operations for the agent."""

    def __init__(self, workspace_dir: Path):
        """
        Initialize filesystem tools.

        Args:
            workspace_dir: Root directory for file operations
        """
        self.workspace_dir = workspace_dir.resolve()
        logger.info(f"Filesystem tools initialized: {self.workspace_dir}")

    def read_file(
        self, path: str, start_line: Optional[int] = None, end_line: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Read a file's contents.

        Args:
            path: File path (relative to workspace or absolute)
            start_line: Optional starting line number (1-indexed)
            end_line: Optional ending line number (1-indexed, inclusive)

        Returns:
            Dict with content, path, lines, is_binary, is_sensitive
        """
        try:
            file_path = validate_path(self.workspace_dir, path)

            if not file_path.exists():
                return {"error": f"File not found: {path}", "success": False}

            if not file_path.is_file():
                return {"error": f"Not a file: {path}", "success": False}

            # Check if binary
            if is_binary_file(file_path):
                stats = file_path.stat()
                return {
                    "success": True,
                    "path": str(file_path.relative_to(self.workspace_dir)),
                    "is_binary": True,
                    "size": stats.st_size,
                    "message": "Binary file, content not read",
                }

            # Check if sensitive
            is_sensitive = is_sensitive_file(file_path)

            # Read file
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines(keepends=True)

            # Apply line range if specified
            if start_line is not None or end_line is not None:
                start_idx = (start_line - 1) if start_line else 0
                end_idx = end_line if end_line else len(lines)
                lines = lines[start_idx:end_idx]
                content = "".join(lines)

            return {
                "success": True,
                "path": str(file_path.relative_to(self.workspace_dir)),
                "content": content,
                "lines": len(content.splitlines()),
                "is_binary": False,
                "is_sensitive": is_sensitive,
            }

        except ValueError as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return {"error": f"Failed to read file: {e}", "success": False}

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Write content to a file (create or overwrite).

        Args:
            path: File path (relative to workspace or absolute)
            content: Content to write

        Returns:
            Dict with success status and metadata
        """
        try:
            file_path = validate_path(self.workspace_dir, path)

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if file exists (for reporting)
            existed = file_path.exists()

            # Write file
            file_path.write_text(content, encoding="utf-8")

            action = "modified" if existed else "created"
            return {
                "success": True,
                "path": str(file_path.relative_to(self.workspace_dir)),
                "action": action,
                "lines": len(content.splitlines()),
            }

        except ValueError as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            logger.error(f"Error writing file {path}: {e}")
            return {"error": f"Failed to write file: {e}", "success": False}

    def edit_file(self, path: str, old_text: str, new_text: str) -> Dict[str, Any]:
        """
        Edit a file by replacing old_text with new_text.

        Args:
            path: File path (relative to workspace or absolute)
            old_text: Text to find and replace (must match exactly)
            new_text: Replacement text

        Returns:
            Dict with success status and metadata
        """
        try:
            file_path = validate_path(self.workspace_dir, path)

            if not file_path.exists():
                return {"error": f"File not found: {path}", "success": False}

            # Read current content
            content = file_path.read_text(encoding="utf-8")

            # Check if old_text exists
            if old_text not in content:
                return {
                    "error": f"Text to replace not found in file",
                    "success": False,
                    "hint": "Make sure old_text matches exactly, including whitespace",
                }

            # Check if old_text appears multiple times
            count = content.count(old_text)
            if count > 1:
                return {
                    "error": f"Text appears {count} times in file. Be more specific.",
                    "success": False,
                    "hint": "Include more context to make the match unique",
                }

            # Replace text
            new_content = content.replace(old_text, new_text, 1)

            # Write back
            file_path.write_text(new_content, encoding="utf-8")

            return {
                "success": True,
                "path": str(file_path.relative_to(self.workspace_dir)),
                "action": "modified",
                "lines_changed": len(new_text.splitlines()) - len(old_text.splitlines()),
            }

        except ValueError as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            logger.error(f"Error editing file {path}: {e}")
            return {"error": f"Failed to edit file: {e}", "success": False}

    def list_files(self, path: str = ".", max_depth: int = 2) -> Dict[str, Any]:
        """
        List files and directories.

        Args:
            path: Directory path (relative to workspace or absolute)
            max_depth: Maximum depth to traverse (0 = current dir only)

        Returns:
            Dict with file listing
        """
        try:
            dir_path = validate_path(self.workspace_dir, path)

            if not dir_path.exists():
                return {"error": f"Directory not found: {path}", "success": False}

            if not dir_path.is_dir():
                return {"error": f"Not a directory: {path}", "success": False}

            # Default ignore patterns
            ignore_dirs = {
                ".git",
                "node_modules",
                "__pycache__",
                ".venv",
                "venv",
                "env",
                "dist",
                "build",
                ".pytest_cache",
                ".mypy_cache",
                "vendor",
                "coverage",
            }

            def scan_dir(current_path: Path, depth: int) -> List[Dict[str, Any]]:
                """Recursively scan directory."""
                if depth > max_depth:
                    return []

                items = []
                try:
                    for entry in sorted(current_path.iterdir()):
                        # Skip ignored directories
                        if entry.is_dir() and entry.name in ignore_dirs:
                            continue

                        rel_path = entry.relative_to(self.workspace_dir)
                        item = {
                            "name": entry.name,
                            "path": str(rel_path),
                            "type": "directory" if entry.is_dir() else "file",
                        }

                        if entry.is_file():
                            item["size"] = entry.stat().st_size

                        items.append(item)

                        # Recurse into directories
                        if entry.is_dir() and depth < max_depth:
                            item["children"] = scan_dir(entry, depth + 1)

                except PermissionError:
                    logger.warning(f"Permission denied: {current_path}")

                return items

            items = scan_dir(dir_path, 0)

            return {
                "success": True,
                "path": str(dir_path.relative_to(self.workspace_dir)),
                "items": items,
                "count": len(items),
            }

        except ValueError as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return {"error": f"Failed to list directory: {e}", "success": False}
