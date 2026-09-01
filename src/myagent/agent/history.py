"""Conversation history persistence for MyAgent."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ConversationHistory:
    """Manages conversation history persistence."""

    def __init__(self, workspace_dir: Path, history_dir: Optional[Path] = None):
        """
        Initialize conversation history manager.

        Args:
            workspace_dir: Workspace directory
            history_dir: Directory to store history files (default: workspace/.myagent/history)
        """
        self.workspace_dir = workspace_dir
        self.history_dir = history_dir or workspace_dir / ".myagent" / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session file
        self.session_file = self.history_dir / "current_session.json"
        self.sessions_index = self.history_dir / "sessions.json"

    def save_session(
        self,
        messages: List[Dict[str, Any]],
        session_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save current session to file.

        Args:
            messages: Conversation messages
            session_data: Additional session metadata

        Returns:
            Session ID
        """
        try:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            session = {
                "session_id": session_id,
                "workspace": str(self.workspace_dir),
                "timestamp": datetime.now().isoformat(),
                "messages": messages,
                "data": session_data or {},
            }

            # Save to current session file
            self.session_file.write_text(json.dumps(session, indent=2))
            
            # Update sessions index
            self._update_sessions_index(session_id, session)
            
            logger.info(f"Saved session {session_id}")
            return session_id

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return ""

    def load_session(self, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load a session from file.

        Args:
            session_id: Specific session to load (default: load current/last session)

        Returns:
            Session data or None if not found
        """
        try:
            if session_id:
                # Load specific session
                session_file = self.history_dir / f"session_{session_id}.json"
                if not session_file.exists():
                    logger.warning(f"Session {session_id} not found")
                    return None
                return json.loads(session_file.read_text())
            else:
                # Load current session
                if not self.session_file.exists():
                    logger.info("No current session found")
                    return None
                return json.loads(self.session_file.read_text())

        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return None

    def list_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent sessions.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session summaries
        """
        try:
            if not self.sessions_index.exists():
                return []

            index = json.loads(self.sessions_index.read_text())
            sessions = index.get("sessions", [])
            
            # Sort by timestamp (most recent first)
            sessions.sort(key=lambda s: s.get("timestamp", ""), reverse=True)
            
            return sessions[:limit]

        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a specific session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted successfully
        """
        try:
            session_file = self.history_dir / f"session_{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            
            # Update index
            if self.sessions_index.exists():
                index = json.loads(self.sessions_index.read_text())
                sessions = index.get("sessions", [])
                sessions = [s for s in sessions if s.get("session_id") != session_id]
                index["sessions"] = sessions
                self.sessions_index.write_text(json.dumps(index, indent=2))
            
            logger.info(f"Deleted session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False

    def clear_current_session(self) -> bool:
        """
        Clear the current session file.

        Returns:
            True if cleared successfully
        """
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            logger.info("Cleared current session")
            return True

        except Exception as e:
            logger.error(f"Failed to clear current session: {e}")
            return False

    def archive_current_session(self) -> Optional[str]:
        """
        Archive the current session (move to dated file).

        Returns:
            Session ID if archived successfully
        """
        try:
            if not self.session_file.exists():
                return None

            session = json.loads(self.session_file.read_text())
            session_id = session.get("session_id")
            
            if session_id:
                # Save to dated file
                archive_file = self.history_dir / f"session_{session_id}.json"
                archive_file.write_text(json.dumps(session, indent=2))
                
                # Clear current
                self.session_file.unlink()
                
                logger.info(f"Archived session {session_id}")
                return session_id

            return None

        except Exception as e:
            logger.error(f"Failed to archive session: {e}")
            return None

    def get_message_count(self) -> int:
        """
        Get the number of messages in current session.

        Returns:
            Message count
        """
        try:
            if not self.session_file.exists():
                return 0

            session = json.loads(self.session_file.read_text())
            return len(session.get("messages", []))

        except Exception as e:
            logger.error(f"Failed to get message count: {e}")
            return 0

    def _update_sessions_index(self, session_id: str, session: Dict[str, Any]) -> None:
        """Update the sessions index file."""
        try:
            # Load existing index
            if self.sessions_index.exists():
                index = json.loads(self.sessions_index.read_text())
            else:
                index = {"sessions": []}

            # Add or update session summary
            summary = {
                "session_id": session_id,
                "timestamp": session.get("timestamp"),
                "workspace": session.get("workspace"),
                "message_count": len(session.get("messages", [])),
                "last_message": self._get_last_user_message(session.get("messages", [])),
            }

            # Remove old entry if exists
            sessions = [s for s in index["sessions"] if s.get("session_id") != session_id]
            sessions.append(summary)
            
            # Keep only last 100 sessions in index
            sessions.sort(key=lambda s: s.get("timestamp", ""), reverse=True)
            index["sessions"] = sessions[:100]

            # Save index
            self.sessions_index.write_text(json.dumps(index, indent=2))

        except Exception as e:
            logger.error(f"Failed to update sessions index: {e}")

    def _get_last_user_message(self, messages: List[Dict[str, Any]]) -> str:
        """Get the last user message content."""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content[:100]  # Truncate for summary
        return ""


def get_conversation_history(workspace_dir: Path) -> ConversationHistory:
    """
    Get conversation history manager for a workspace.

    Args:
        workspace_dir: Workspace directory

    Returns:
        ConversationHistory instance
    """
    return ConversationHistory(workspace_dir)
