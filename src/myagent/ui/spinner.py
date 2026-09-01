"""Spinner and progress indicators for UI."""

import sys
import threading
import time
from typing import Optional


class Spinner:
    """A simple spinner for showing progress."""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str = "Working"):
        """
        Initialize spinner.

        Args:
            message: Message to display with spinner
        """
        self.message = message
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def _spin(self) -> None:
        """Spin animation loop."""
        idx = 0
        while self.running:
            frame = self.FRAMES[idx % len(self.FRAMES)]
            sys.stdout.write(f"\r{frame} {self.message}...")
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1

    def start(self) -> None:
        """Start the spinner."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._spin, daemon=True)
            self.thread.start()

    def stop(self, final_message: Optional[str] = None) -> None:
        """
        Stop the spinner.

        Args:
            final_message: Optional final message to display
        """
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
            sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
            if final_message:
                print(final_message)
            sys.stdout.flush()

    def __enter__(self):
        """Context manager enter."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False
