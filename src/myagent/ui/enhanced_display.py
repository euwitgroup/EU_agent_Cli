"""Enhanced display utilities with clean, modern UI."""

import time
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from myagent.ui.console import get_console


class EnhancedDisplay:
    """Enhanced display manager for clean CLI output."""

    def __init__(self):
        """Initialize enhanced display."""
        self.console = get_console()
        self.current_task = None
        self.tool_calls_count = 0
        self.start_time = None

    def show_banner(self, project_name: str, provider: str, model: str) -> None:
        """
        Show enhanced banner.

        Args:
            project_name: Name of the project
            provider: AI provider name
            model: Model name
        """
        self.console.clear()
        
        # Create banner content
        banner = Text()
        banner.append("✨ ", style="bold yellow")
        banner.append("MyAgent", style="bold cyan")
        banner.append(" - AI Coding Assistant\n", style="dim")
        
        # Project info
        info_table = Table.grid(padding=(0, 2))
        info_table.add_column(style="dim cyan", justify="right")
        info_table.add_column(style="white")
        
        info_table.add_row("Project", project_name)
        info_table.add_row("Provider", provider)
        info_table.add_row("Model", model)
        
        panel = Panel(
            info_table,
            border_style="cyan dim",
            padding=(1, 2),
            title="[bold cyan]Session Info[/bold cyan]",
            title_align="left",
        )
        
        self.console.print(banner)
        self.console.print(panel)
        self.console.print()

    def show_flash(self, message: str, style: str = "green", icon: str = "✓") -> None:
        """
        Show a flash message.

        Args:
            message: Message to display
            style: Style for the message
            icon: Icon to show
        """
        self.console.print(f"[{style}]{icon}[/{style}] {message}")

    def show_error_flash(self, message: str) -> None:
        """
        Show an error flash message.

        Args:
            message: Error message
        """
        self.show_flash(message, style="red", icon="✗")

    def show_warning_flash(self, message: str) -> None:
        """
        Show a warning flash message.

        Args:
            message: Warning message
        """
        self.show_flash(message, style="yellow", icon="⚠")

    def show_info_flash(self, message: str) -> None:
        """
        Show an info flash message.

        Args:
            message: Info message
        """
        self.show_flash(message, style="cyan", icon="ℹ")

    def start_task(self, task: str) -> None:
        """
        Start a new task.

        Args:
            task: Task description
        """
        self.current_task = task
        self.tool_calls_count = 0
        self.start_time = time.time()
        
        self.console.print()
        self.console.print(f"[bold]Task:[/bold] {task}")
        self.console.print()

    def show_thinking(self) -> None:
        """Show thinking indicator."""
        self.console.print("[dim]⋯ Thinking...[/dim]", end="\r")

    def clear_thinking(self) -> None:
        """Clear thinking indicator."""
        self.console.print(" " * 50, end="\r")

    def show_tool_call(self, tool_name: str, args: Optional[Dict[str, Any]] = None) -> None:
        """
        Show a tool call in a clean format.

        Args:
            tool_name: Name of the tool
            args: Tool arguments
        """
        self.tool_calls_count += 1
        self.clear_thinking()
        
        # Show compact tool call
        if tool_name == "read_file":
            path = args.get("path", "") if args else ""
            self.console.print(f"  [cyan]→[/cyan] Reading [dim]{path}[/dim]")
        elif tool_name == "write_file":
            path = args.get("path", "") if args else ""
            self.console.print(f"  [cyan]→[/cyan] Writing [dim]{path}[/dim]")
        elif tool_name == "edit_file":
            path = args.get("path", "") if args else ""
            self.console.print(f"  [cyan]→[/cyan] Editing [dim]{path}[/dim]")
        elif tool_name == "run_command":
            cmd = args.get("command", "") if args else ""
            self.console.print(f"  [cyan]→[/cyan] Running [dim]{cmd}[/dim]")
        elif tool_name == "search_files":
            query = args.get("query", "") if args else ""
            self.console.print(f"  [cyan]→[/cyan] Searching [dim]{query}[/dim]")
        elif tool_name == "git_diff":
            self.console.print(f"  [cyan]→[/cyan] Checking diff")
        elif tool_name == "git_status":
            self.console.print(f"  [cyan]→[/cyan] Checking status")
        else:
            self.console.print(f"  [cyan]→[/cyan] {tool_name}")

    def show_tool_result(self, success: bool, message: Optional[str] = None) -> None:
        """
        Show tool result (minimal output).

        Args:
            success: Whether the tool succeeded
            message: Optional message (only shown on error)
        """
        # Only show errors
        if not success and message:
            self.console.print(f"    [red]✗ {message}[/red]")

    def show_assistant_response(self, content: str) -> None:
        """
        Show assistant's response.

        Args:
            content: Response content
        """
        self.clear_thinking()
        self.console.print()
        self.console.print(Panel(
            content.strip(),
            border_style="green dim",
            padding=(1, 2),
            title="[bold green]Response[/bold green]",
            title_align="left",
        ))
        self.console.print()

    def show_task_complete(
        self,
        files_changed: List[str],
        files_created: List[str],
        commands_run: List[str],
    ) -> None:
        """
        Show task completion summary.

        Args:
            files_changed: List of changed files
            files_created: List of created files
            commands_run: List of commands run
        """
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        # Create summary table
        summary_parts = []
        
        if files_created:
            summary_parts.append(f"[green]✓[/green] Created {len(files_created)} file(s)")
        
        if files_changed:
            summary_parts.append(f"[green]✓[/green] Modified {len(files_changed)} file(s)")
        
        if commands_run:
            summary_parts.append(f"[green]✓[/green] Ran {len(commands_run)} command(s)")
        
        summary_parts.append(f"[dim]Completed in {elapsed:.1f}s[/dim]")
        
        self.console.print()
        for part in summary_parts:
            self.console.print(f"  {part}")
        self.console.print()

    def show_error(self, error: str, title: str = "Error") -> None:
        """
        Show error panel.

        Args:
            error: Error message
            title: Error title
        """
        self.console.print()
        self.console.print(Panel(
            f"[red]{error}[/red]",
            border_style="red",
            padding=(1, 2),
            title=f"[bold red]{title}[/bold red]",
            title_align="left",
        ))
        self.console.print()


# Global enhanced display instance
_enhanced_display: Optional[EnhancedDisplay] = None


def get_enhanced_display() -> EnhancedDisplay:
    """Get or create the global enhanced display instance."""
    global _enhanced_display
    if _enhanced_display is None:
        _enhanced_display = EnhancedDisplay()
    return _enhanced_display
