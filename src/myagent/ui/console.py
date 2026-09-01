"""Console management for Rich output."""

from typing import Optional

from rich.console import Console

# Global console instance
_console: Optional[Console] = None


def get_console(no_color: bool = False) -> Console:
    """Get or create the global console instance."""
    global _console
    if _console is None:
        _console = Console(
            force_terminal=not no_color,
            force_interactive=True,
            highlight=True,
            markup=True,
        )
    return _console


def reset_console() -> None:
    """Reset the global console instance (useful for testing)."""
    global _console
    _console = None


# Convenience export
console = get_console()
