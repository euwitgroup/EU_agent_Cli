"""Enhanced interactive prompt with menu-driven interface."""

import logging
from pathlib import Path
from typing import Optional

from myagent.agent import AgentLoop
from myagent.config import get_settings
from myagent.ui import get_enhanced_display, get_menu
from myagent.ui.console import get_console

logger = logging.getLogger(__name__)


class EnhancedInteractiveREPL:
    """Enhanced interactive REPL with menu system."""

    def __init__(self, workspace_dir: Path):
        """
        Initialize enhanced REPL.

        Args:
            workspace_dir: Workspace root directory
        """
        self.workspace_dir = workspace_dir
        self.console = get_console()
        self.display = get_enhanced_display()
        self.menu = get_menu()
        self.agent_loop: Optional[AgentLoop] = None
        self.running = True

        logger.info("Enhanced REPL initialized")

    def start(self) -> None:
        """Start the enhanced interactive REPL."""
        # Initialize agent loop
        try:
            self.agent_loop = AgentLoop(self.workspace_dir)
        except Exception as e:
            self.display.show_error(f"Failed to initialize agent: {e}")
            return

        # Show banner
        settings = get_settings()
        self.display.show_banner(
            project_name=self.workspace_dir.name,
            provider=settings.get_provider(),
            model=settings.get_model(),
        )

        # Main menu loop
        while self.running:
            try:
                action = self.menu.show_main_menu()

                if action == "chat":
                    self._handle_chat()
                elif action == "task":
                    self._handle_task()
                elif action == "status":
                    self._handle_status()
                elif action == "settings":
                    self._handle_settings()
                elif action == "files":
                    self._handle_files()
                elif action == "git":
                    self._handle_git()
                elif action == "help":
                    self._handle_help()
                elif action == "exit":
                    self.running = False

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted[/yellow]")
                if self.menu.confirm("Do you want to exit?", default=False):
                    self.running = False
            except Exception as e:
                logger.exception("Error in main loop")
                self.display.show_error_flash(f"Error: {e}")

        self.console.print("\n[green]Goodbye! 👋[/green]\n")

    def _handle_chat(self) -> None:
        """Handle chat mode."""
        self.console.print("\n[bold cyan]Chat Mode[/bold cyan]")
        self.console.print("[dim]Type your message or 'back' to return to menu[/dim]\n")

        while True:
            user_input = self.menu.text_input("You")

            if not user_input or user_input.strip().lower() == "back":
                break

            if not user_input.strip():
                continue

            # Execute task
            self._execute_agent_task(user_input)

    def _handle_task(self) -> None:
        """Handle task execution."""
        self.console.print("\n[bold cyan]Execute Task[/bold cyan]")
        
        task = self.menu.multiline_input("Enter your task (editor will open)")

        if task and task.strip():
            self._execute_agent_task(task.strip())
        else:
            self.display.show_warning_flash("Task cancelled")

    def _execute_agent_task(self, task: str) -> None:
        """
        Execute an agent task.

        Args:
            task: Task description
        """
        if not self.agent_loop:
            self.display.show_error_flash("Agent not initialized")
            return

        self.display.start_task(task)
        self.display.show_thinking()

        try:
            result = self.agent_loop.run(task, stream=False)

            if result.get("success"):
                # Show response
                message = result.get("message", "")
                if message:
                    self.display.show_assistant_response(message)

                # Show summary
                state = self.agent_loop.state
                self.display.show_task_complete(
                    files_changed=list(state.files_changed),
                    files_created=list(state.files_created),
                    commands_run=list(state.commands_executed),
                )
            else:
                error = result.get("error", "Unknown error")
                self.display.show_error(f"Task failed: {error}")

        except Exception as e:
            logger.exception("Error executing task")
            self.display.show_error(f"Task execution failed: {e}")

    def _handle_status(self) -> None:
        """Handle status display."""
        if not self.agent_loop:
            self.display.show_error_flash("Agent not initialized")
            return

        state = self.agent_loop.state
        summary = state.get_summary()

        self.console.print("\n[bold cyan]Session Status[/bold cyan]\n")

        status_info = f"""[bold]Iterations:[/bold] {summary['iterations']}/{state.max_iterations}
[bold]Tool Calls:[/bold] {summary['tool_calls']}
[bold]Files Changed:[/bold] {summary['files_changed']}
[bold]Files Created:[/bold] {summary['files_created']}
[bold]Commands Run:[/bold] {summary['commands_executed']}

[bold]Provider:[/bold] {state.provider}
[bold]Model:[/bold] {state.model}
"""

        self.console.print(status_info)

        if state.files_changed:
            self.console.print("\n[bold]Recently Modified:[/bold]")
            for f in list(state.files_changed)[:5]:
                self.console.print(f"  • {f}")

        self.console.print()
        input("Press Enter to continue...")

    def _handle_settings(self) -> None:
        """Handle settings menu."""
        while True:
            action = self.menu.show_settings_menu()

            if action == "provider":
                self._change_provider()
            elif action == "model":
                self._change_model()
            elif action == "view":
                self._view_configuration()
            elif action == "back":
                break

    def _change_provider(self) -> None:
        """Change AI provider."""
        settings = get_settings()
        current = settings.get_provider()

        provider = self.menu.show_provider_menu(current)

        if provider and provider != current:
            settings.provider_override = provider
            self.display.show_flash(f"Provider changed to: {provider}")
            self.display.show_info_flash("Restart agent with /reset to apply")

    def _change_model(self) -> None:
        """Change model."""
        settings = get_settings()
        current = settings.get_model()
        provider = settings.get_provider()

        model = self.menu.show_model_input(current, provider)

        if model and model != current:
            settings.model_override = model
            self.display.show_flash(f"Model changed to: {model}")
            self.display.show_info_flash("Restart agent with /reset to apply")

    def _view_configuration(self) -> None:
        """View current configuration."""
        settings = get_settings()

        self.console.print("\n[bold cyan]Current Configuration[/bold cyan]\n")

        config_info = f"""[bold]Provider:[/bold] {settings.get_provider()}
[bold]Model:[/bold] {settings.get_model()}
[bold]Max Iterations:[/bold] {settings.myagent_max_iterations}
[bold]Workspace:[/bold] {self.workspace_dir}
"""

        self.console.print(config_info)
        input("\nPress Enter to continue...")

    def _handle_files(self) -> None:
        """Handle file operations menu."""
        while True:
            action = self.menu.show_file_operations_menu()

            if action == "view":
                self._view_file()
            elif action == "edit":
                self._edit_file()
            elif action == "search":
                self._search_files()
            elif action == "changes":
                self._show_changes()
            elif action == "back":
                break

    def _view_file(self) -> None:
        """View a file."""
        path = self.menu.text_input("Enter file path")

        if path:
            from myagent.tools.filesystem import FileSystemTools

            fs_tools = FileSystemTools(self.workspace_dir)
            result = fs_tools.read_file(path)

            if result.get("success"):
                content = result.get("content", "")
                self.console.print(f"\n[bold]{path}[/bold]\n")
                self.console.print(content)
                self.console.print()
                input("Press Enter to continue...")
            else:
                self.display.show_error_flash(result.get("error", "Failed to read file"))

    def _edit_file(self) -> None:
        """Edit a file (via agent)."""
        path = self.menu.text_input("Enter file path")

        if path:
            instructions = self.menu.multiline_input(f"How should I edit {path}?")

            if instructions:
                task = f"Edit {path}: {instructions}"
                self._execute_agent_task(task)

    def _search_files(self) -> None:
        """Search files."""
        query = self.menu.text_input("Enter search query (regex)")

        if query:
            from myagent.tools.search import SearchTools

            search_tools = SearchTools(self.workspace_dir)
            result = search_tools.search_files(query, max_results=20)

            if result.get("success"):
                matches = result.get("matches", [])
                self.console.print(f"\n[bold]Found {len(matches)} matches[/bold]\n")

                for match in matches[:10]:
                    self.console.print(
                        f"[cyan]{match['file']}:{match['line']}[/cyan] {match['content']}"
                    )

                if len(matches) > 10:
                    self.console.print(f"\n[dim]... and {len(matches) - 10} more[/dim]")

                self.console.print()
                input("Press Enter to continue...")
            else:
                self.display.show_error_flash(result.get("error", "Search failed"))

    def _show_changes(self) -> None:
        """Show git changes."""
        from myagent.tools.git import GitTools

        git_tools = GitTools(self.workspace_dir)

        if not git_tools.is_git_repo():
            self.display.show_warning_flash("Not a git repository")
            return

        result = git_tools.git_diff()

        if result.get("success"):
            diff = result.get("diff", "")

            if diff:
                from myagent.ui.display import display_diff

                display_diff(diff)
                input("\nPress Enter to continue...")
            else:
                self.display.show_info_flash("No changes to display")
        else:
            self.display.show_error_flash(result.get("error", "Failed to get diff"))

    def _handle_git(self) -> None:
        """Handle git operations menu."""
        while True:
            action = self.menu.show_git_operations_menu()

            if action == "status":
                self._git_status()
            elif action == "diff":
                self._git_diff()
            elif action == "log":
                self._git_log()
            elif action == "add":
                self._git_add()
            elif action == "commit":
                self._git_commit()
            elif action == "back":
                break

    def _git_status(self) -> None:
        """Show git status."""
        from myagent.tools.git import GitTools

        git_tools = GitTools(self.workspace_dir)

        if not git_tools.is_git_repo():
            self.display.show_warning_flash("Not a git repository")
            return

        result = git_tools.git_status()

        if result.get("success"):
            status = result.get("status", "")
            self.console.print(f"\n{status}\n")
            input("Press Enter to continue...")
        else:
            self.display.show_error_flash(result.get("error", "Failed to get status"))

    def _git_diff(self) -> None:
        """Show git diff."""
        self._show_changes()

    def _git_log(self) -> None:
        """Show git log."""
        from myagent.tools.git import GitTools

        git_tools = GitTools(self.workspace_dir)

        if not git_tools.is_git_repo():
            self.display.show_warning_flash("Not a git repository")
            return

        result = git_tools.git_log(max_count=10)

        if result.get("success"):
            log = result.get("log", "")
            self.console.print(f"\n{log}\n")
            input("Press Enter to continue...")
        else:
            self.display.show_error_flash(result.get("error", "Failed to get log"))

    def _git_add(self) -> None:
        """Stage changes."""
        files = self.menu.text_input("Enter files to stage (space-separated, or '.' for all)")

        if files:
            from myagent.tools.terminal import TerminalTools

            terminal_tools = TerminalTools(self.workspace_dir)
            result = terminal_tools.run_command(f"git add {files}")

            if result.get("success"):
                self.display.show_flash("Files staged successfully")
            else:
                self.display.show_error_flash(result.get("error", "Failed to stage files"))

    def _git_commit(self) -> None:
        """Commit changes."""
        message = self.menu.text_input("Enter commit message")

        if message:
            from myagent.tools.terminal import TerminalTools

            terminal_tools = TerminalTools(self.workspace_dir)
            result = terminal_tools.run_command(f'git commit -m "{message}"')

            if result.get("success"):
                self.display.show_flash("Changes committed successfully")
            else:
                self.display.show_error_flash(result.get("error", "Failed to commit"))

    def _handle_help(self) -> None:
        """Show help information."""
        help_text = """
[bold cyan]MyAgent - AI Coding Assistant[/bold cyan]

[bold]Main Features:[/bold]

• [cyan]Chat Mode[/cyan] - Have a conversation with the AI agent
• [cyan]Execute Task[/cyan] - Give the agent a specific task to complete
• [cyan]View Status[/cyan] - Check current session statistics
• [cyan]Settings[/cyan] - Configure provider and model
• [cyan]File Operations[/cyan] - View, edit, and search files
• [cyan]Git Operations[/cyan] - Manage version control

[bold]Tips:[/bold]

• Use arrow keys to navigate menus
• Press Ctrl+C to cancel current operation
• The agent can read, write, and edit files
• The agent can run commands and tests
• All changes are tracked and summarized

[bold]Getting Started:[/bold]

1. Choose "Execute Task" from the main menu
2. Describe what you want to build or fix
3. The agent will analyze, plan, and implement
4. Review the changes and iterate as needed
"""

        self.console.print(help_text)
        input("\nPress Enter to continue...")


def start_enhanced_session(workspace_dir: Path) -> None:
    """
    Start an enhanced interactive session.

    Args:
        workspace_dir: Workspace root directory
    """
    repl = EnhancedInteractiveREPL(workspace_dir)
    repl.start()
