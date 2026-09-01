"""Display utilities for terminal UI."""

from typing import Any, Dict, List, Optional

from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from myagent.ui.console import get_console


def display_banner(project_name: str, provider: str, model: str) -> None:
    """Display the MyAgent banner."""
    console = get_console()

    banner_text = """
    [bold cyan]MyAgent[/bold cyan]
    [dim]AI Coding Agent[/dim]
    """

    info_table = Table.grid(padding=(0, 2))
    info_table.add_column(style="dim", justify="right")
    info_table.add_column()

    info_table.add_row("Project:", f"[yellow]{project_name}[/yellow]")
    info_table.add_row("Provider:", f"[blue]{provider}[/blue]")
    info_table.add_row("Model:", f"[green]{model}[/green]")

    panel = Panel(
        banner_text.strip(),
        border_style="cyan",
        padding=(1, 2),
    )

    console.print(panel)
    console.print(info_table)
    console.print()


def display_status(message: str, spinner: bool = False) -> None:
    """Display a status message."""
    console = get_console()
    prefix = "●" if not spinner else "⋯"
    console.print(f"{prefix} [dim]{message}[/dim]")


def display_tool_call(tool_name: str, args: Optional[Dict[str, Any]] = None) -> None:
    """Display a tool call."""
    console = get_console()
    if args:
        # Show brief args preview
        args_preview = ", ".join(f"{k}={repr(v)[:50]}" for k, v in list(args.items())[:2])
        if len(args) > 2:
            args_preview += ", ..."
        console.print(f"→ [cyan]{tool_name}[/cyan]([dim]{args_preview}[/dim])")
    else:
        console.print(f"→ [cyan]{tool_name}[/cyan]")


def display_tool_result(success: bool, message: Optional[str] = None) -> None:
    """Display a tool result."""
    console = get_console()
    if success:
        status = "✓"
        style = "green"
    else:
        status = "✗"
        style = "red"

    if message:
        console.print(f"{status} [{style}]{message}[/{style}]")
    else:
        console.print(f"{status}")


def display_error(error: str, title: str = "Error") -> None:
    """Display an error message."""
    console = get_console()
    panel = Panel(
        f"[red]{error}[/red]",
        title=f"[bold red]{title}[/bold red]",
        border_style="red",
    )
    console.print(panel)


def display_summary(
    changed_files: List[str],
    commands_run: List[str],
    test_results: Optional[Dict[str, Any]] = None,
) -> None:
    """Display a task completion summary."""
    console = get_console()

    summary_parts = []

    if changed_files:
        summary_parts.append("[bold]Changed:[/bold]")
        for file in changed_files[:10]:  # Limit display
            summary_parts.append(f"  M {file}")
        if len(changed_files) > 10:
            summary_parts.append(f"  ... and {len(changed_files) - 10} more")

    if commands_run:
        summary_parts.append("")
        summary_parts.append("[bold]Commands:[/bold]")
        for cmd in commands_run[-5:]:  # Show last 5
            summary_parts.append(f"  {cmd}")

    if test_results:
        summary_parts.append("")
        summary_parts.append("[bold]Tests:[/bold]")
        if test_results.get("passed"):
            summary_parts.append(f"  ✓ {test_results['passed']} passed")
        if test_results.get("failed"):
            summary_parts.append(f"  ✗ {test_results['failed']} failed")

    if summary_parts:
        panel = Panel(
            "\n".join(summary_parts),
            title="[bold green]Completed[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
        console.print(panel)


def display_markdown(content: str) -> None:
    """Display markdown content."""
    console = get_console()
    md = Markdown(content)
    console.print(md)


def display_code(code: str, language: str = "python") -> None:
    """Display syntax-highlighted code."""
    console = get_console()
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)


def display_diff(diff_content: str) -> None:
    """Display a git diff."""
    console = get_console()
    syntax = Syntax(diff_content, "diff", theme="monokai")
    console.print(syntax)
