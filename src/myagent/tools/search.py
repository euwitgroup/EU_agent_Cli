"""Search tools for finding files and content."""

import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SearchTools:
    """Search operations for finding files and content."""

    def __init__(self, workspace_dir: Path):
        """
        Initialize search tools.

        Args:
            workspace_dir: Root directory for search operations
        """
        self.workspace_dir = workspace_dir.resolve()
        self._has_ripgrep = self._check_ripgrep()
        logger.info(f"Search tools initialized: ripgrep={self._has_ripgrep}")

    def _check_ripgrep(self) -> bool:
        """Check if ripgrep (rg) is available."""
        try:
            result = subprocess.run(
                ["rg", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def search_files(
        self,
        query: str,
        path: str = ".",
        case_sensitive: bool = False,
        max_results: int = 100,
    ) -> Dict[str, Any]:
        """
        Search for content within files.

        Args:
            query: Search query (regex pattern)
            path: Directory to search in (relative to workspace)
            case_sensitive: Whether search is case sensitive
            max_results: Maximum number of results to return

        Returns:
            Dict with search results
        """
        try:
            # Resolve search path
            if Path(path).is_absolute():
                search_path = Path(path).resolve()
            else:
                search_path = (self.workspace_dir / path).resolve()

            # Validate path is within workspace
            if not str(search_path).startswith(str(self.workspace_dir)):
                return {"error": "Search path outside workspace", "success": False}

            if not search_path.exists():
                return {"error": f"Path not found: {path}", "success": False}

            # Use ripgrep if available, otherwise fallback to Python
            if self._has_ripgrep:
                results = self._search_with_ripgrep(
                    query, search_path, case_sensitive, max_results
                )
            else:
                results = self._search_with_python(
                    query, search_path, case_sensitive, max_results
                )

            return {
                "success": True,
                "query": query,
                "path": str(search_path.relative_to(self.workspace_dir)),
                "results": results,
                "count": len(results),
                "truncated": len(results) >= max_results,
            }

        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return {"error": f"Search failed: {e}", "success": False}

    def _search_with_ripgrep(
        self, query: str, search_path: Path, case_sensitive: bool, max_results: int
    ) -> List[Dict[str, Any]]:
        """Search using ripgrep (fast)."""
        cmd = ["rg", "--json", "--max-count", str(max_results)]

        if not case_sensitive:
            cmd.append("--ignore-case")

        # Add ignore patterns
        cmd.extend(
            [
                "--glob",
                "!.git/",
                "--glob",
                "!node_modules/",
                "--glob",
                "!__pycache__/",
                "--glob",
                "!.venv/",
                "--glob",
                "!venv/",
                "--glob",
                "!dist/",
                "--glob",
                "!build/",
            ]
        )

        cmd.extend([query, str(search_path)])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.workspace_dir,
            )

            # Parse JSON output
            import json

            matches = []
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if data.get("type") == "match":
                        match_data = data["data"]
                        file_path = Path(match_data["path"]["text"])
                        rel_path = file_path.relative_to(self.workspace_dir)

                        matches.append(
                            {
                                "file": str(rel_path),
                                "line": match_data["line_number"],
                                "content": match_data["lines"]["text"].rstrip(),
                            }
                        )
                except json.JSONDecodeError:
                    continue

            return matches[:max_results]

        except subprocess.TimeoutExpired:
            logger.warning("Ripgrep search timed out")
            return []
        except Exception as e:
            logger.error(f"Ripgrep search error: {e}")
            return []

    def _search_with_python(
        self, query: str, search_path: Path, case_sensitive: bool, max_results: int
    ) -> List[Dict[str, Any]]:
        """Fallback search using Python (slower but always available)."""
        try:
            # Compile regex
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(query, flags)

            matches = []
            ignore_dirs = {
                ".git",
                "node_modules",
                "__pycache__",
                ".venv",
                "venv",
                "dist",
                "build",
            }

            # Walk directory tree
            for root, dirs, files in search_path.walk():
                # Filter out ignored directories
                dirs[:] = [d for d in dirs if d not in ignore_dirs]

                for file_name in files:
                    file_path = root / file_name

                    # Skip binary files
                    if file_path.suffix.lower() in {
                        ".pyc",
                        ".png",
                        ".jpg",
                        ".gif",
                        ".pdf",
                        ".zip",
                    }:
                        continue

                    try:
                        content = file_path.read_text(encoding="utf-8")
                        for line_num, line in enumerate(content.splitlines(), 1):
                            if pattern.search(line):
                                rel_path = file_path.relative_to(self.workspace_dir)
                                matches.append(
                                    {
                                        "file": str(rel_path),
                                        "line": line_num,
                                        "content": line.rstrip(),
                                    }
                                )

                                if len(matches) >= max_results:
                                    return matches

                    except (UnicodeDecodeError, PermissionError):
                        # Skip files we can't read
                        continue

            return matches

        except Exception as e:
            logger.error(f"Python search error: {e}")
            return []

    def find_files(self, pattern: str, path: str = ".") -> Dict[str, Any]:
        """
        Find files by name pattern.

        Args:
            pattern: Glob pattern (e.g., "*.py", "test_*.py")
            path: Directory to search in

        Returns:
            Dict with matching file paths
        """
        try:
            # Resolve search path
            if Path(path).is_absolute():
                search_path = Path(path).resolve()
            else:
                search_path = (self.workspace_dir / path).resolve()

            # Validate path
            if not str(search_path).startswith(str(self.workspace_dir)):
                return {"error": "Search path outside workspace", "success": False}

            if not search_path.exists():
                return {"error": f"Path not found: {path}", "success": False}

            # Find matching files
            matches = []
            for file_path in search_path.rglob(pattern):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.workspace_dir)
                    matches.append(str(rel_path))

            return {
                "success": True,
                "pattern": pattern,
                "path": str(search_path.relative_to(self.workspace_dir)),
                "files": matches,
                "count": len(matches),
            }

        except Exception as e:
            logger.error(f"Error finding files: {e}")
            return {"error": f"Find files failed: {e}", "success": False}
