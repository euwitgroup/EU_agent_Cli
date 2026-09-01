"""Interactive prompt implementation."""

import logging
from pathlib import Path
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from myagent.agent import AgentLoop
from myagent.config import get_settings
from myagent.ui import display_error, display_markdown, display_status, display_summary, get_console

logger = logging.getLogger(__name__)

# Prompt style - modern gradient look
prompt_style = Style.from_dict({
    'prompt': '#00d9ff bold',  # Cyan/turquoise
    'prompt-arrow': '#7C3AED bold',  # Purple
})

# Command completer for auto-suggestions
command_completer = WordCompleter(
    [
        '/help',
        '/status', 
        '/clear',
        '/exit',
        '/reset',
        '/model',
        '/provider',
        '/tools',
        '/context',
        '/diff',
        '/config',
        '/history',
        '/sessions',
    ],
    ignore_case=True,
    sentence=True,
)


class InteractiveREPL:
    """Interactive REPL for MyAgent."""

    def __init__(self, workspace_dir: Path):
        """
        Initialize interactive REPL.

        Args:
            workspace_dir: Workspace root directory
        """
        self.workspace_dir = workspace_dir
        self.console = get_console()
        self.session: Optional[PromptSession] = None
        self.agent_loop: Optional[AgentLoop] = None
        self.running = True
        
        # Initialize conversation history
        from myagent.agent.history import get_conversation_history
        self.history_manager = get_conversation_history(workspace_dir)

        logger.info("Interactive REPL initialized")

    def start(self) -> None:
        """Start the interactive REPL."""
        # Create prompt session with history and auto-completion
        self.session = PromptSession(
            history=InMemoryHistory(),
            completer=command_completer,
            complete_while_typing=True,
        )

        # Initialize agent loop
        try:
            self.agent_loop = AgentLoop(self.workspace_dir)
        except Exception as e:
            display_error(f"Failed to initialize agent: {e}")
            return

        # Check for previous session and offer to continue
        self._check_and_load_previous_session()

        # Show welcome message
        self._show_welcome()

        # Main REPL loop
        while self.running:
            try:
                # Get user input with enhanced prompt
                user_input = self.session.prompt(
                    [
                        ('class:prompt-arrow', '❯ '),
                        ('class:prompt', ''),
                    ],
                    style=prompt_style,
                )

                # Skip empty input
                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                else:
                    # Execute agent task
                    self._execute_task(user_input)
                    
                    # Auto-save after each interaction
                    self._auto_save_session()

            except KeyboardInterrupt:
                # Ctrl+C pressed
                self.console.print("\n[yellow]Interrupted. Type /exit to quit or continue with a new task.[/yellow]")
                continue

            except EOFError:
                # Ctrl+D pressed
                self.console.print("\n[dim]Exiting...[/dim]")
                break

        # Save session before exiting
        self._save_session_on_exit()
        self.console.print("[green]Goodbye![/green]")

    def _show_welcome(self) -> None:
        """Show enhanced welcome message with logo and menu."""
        settings = get_settings()
        from rich.panel import Panel
        from rich.table import Table
        from rich.align import Align
        from rich.text import Text

        # Combined Logo + Session Info Box
        combined_content = []
        
        # Logo section
        combined_content.append("[bold cyan]")
        combined_content.append("   ███╗   ███╗██╗   ██╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗")
        combined_content.append("   ████╗ ████║╚██╗ ██╔╝    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝")
        combined_content.append("   ██╔████╔██║ ╚████╔╝     ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ")
        combined_content.append("   ██║╚██╔╝██║  ╚██╔╝      ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ")
        combined_content.append("   ██║ ╚═╝ ██║   ██║       ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ")
        combined_content.append("   ╚═╝     ╚═╝   ╚═╝       ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ")
        combined_content.append("[/bold cyan]")
        combined_content.append("")
        combined_content.append("[dim]              🤖 AI-Powered Autonomous Coding Agent[/dim]")
        combined_content.append("")
        combined_content.append("─" * 70)
        combined_content.append("")
        
        # Session Info in same box
        combined_content.append(f"[bold cyan]Session Info[/bold cyan]")
        combined_content.append("")
        combined_content.append(f"  📁 Project:   [yellow]{self.workspace_dir.name}[/yellow]")
        combined_content.append(f"  🔌 Provider:  [blue]{settings.get_provider()}[/blue]")
        combined_content.append(f"  🤖 Model:     [green]{settings.get_model()}[/green]")
        combined_content.append(f"  ⚡ Status:    [green]Ready[/green]")
        
        # Create single panel
        main_panel = Panel(
            "\n".join(combined_content),
            border_style="cyan",
            padding=(1, 2),
            expand=True,
        )
        self.console.print(main_panel)
        self.console.print()

        # Navigation Menu - full width, selectable
        self.console.print("[bold cyan]Quick Commands[/bold cyan] [dim](Use arrow keys or type command)[/dim]\n")
        
        menu_table = Table(show_header=False, box=None, padding=(0, 3), expand=True)
        menu_table.add_column(justify="left", style="bold")
        menu_table.add_column(justify="left", style="bold")
        menu_table.add_column(justify="left", style="bold")
        menu_table.add_column(justify="left", style="bold")
        
        menu_table.add_row(
            "[cyan]💬 /help[/cyan]      Show all commands",
            "[cyan]📊 /status[/cyan]    Session info",
            "[cyan]🧹 /clear[/cyan]     Clear history",
            "[cyan]🚪 /exit[/cyan]      Quit REPL"
        )
        
        menu_table.add_row(
            "[dim]⚙️  /config[/dim]    Edit provider/API",
            "[dim]🔧 /model[/dim]     Change model",
            "[dim]🔌 /provider[/dim]  Switch provider",
            "[dim]🛠️  /tools[/dim]     List tools"
        )
        
        self.console.print(menu_table)
        self.console.print()
        self.console.print("─" * 70)
        self.console.print()

        # Ready prompt
        self.console.print("[bold yellow]✨ Ready to assist![/bold yellow] [cyan]What would you like to build?[/cyan]\n")

    def _handle_command(self, command: str) -> None:
        """
        Handle slash commands.

        Args:
            command: Command string starting with /
        """
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "/help":
            self._cmd_help()
        elif cmd == "/status":
            self._cmd_status()
        elif cmd == "/config":
            self._cmd_config()
        elif cmd == "/clear":
            self._cmd_clear()
        elif cmd == "/reset":
            self._cmd_reset()
        elif cmd == "/model":
            self._cmd_model(args)
        elif cmd == "/provider":
            self._cmd_provider(args)
        elif cmd == "/context":
            self._cmd_context()
        elif cmd == "/tools":
            self._cmd_tools()
        elif cmd == "/diff":
            self._cmd_diff()
        elif cmd == "/history":
            self._cmd_history()
        elif cmd == "/sessions":
            self._cmd_sessions()
        elif cmd in ["/exit", "/quit", "/q"]:
            self._cmd_exit()
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")
            self.console.print("Type /help for available commands")

    def _cmd_help(self) -> None:
        """Show help message."""
        help_text = """
[bold]Available Commands:[/bold]

[cyan]/help[/cyan]         - Show this help message
[cyan]/status[/cyan]       - Show current session status
[cyan]/config[/cyan]       - Edit provider settings and API keys
[cyan]/history[/cyan]      - Show conversation history summary
[cyan]/sessions[/cyan]     - List and manage saved sessions
[cyan]/clear[/cyan]        - Clear conversation history
[cyan]/reset[/cyan]        - Reset agent session
[cyan]/model[/cyan]        - Show or change model
[cyan]/provider[/cyan]     - Show or change provider
[cyan]/context[/cyan]      - Show current context size
[cyan]/tools[/cyan]        - List available tools
[cyan]/diff[/cyan]         - Show git diff of changes
[cyan]/exit[/cyan], [cyan]/quit[/cyan] - Exit the REPL

[bold]Usage:[/bold]

Simply type your task and press Enter:
  > Fix the login bug in auth.py
  > Add unit tests for the payment module
  > Refactor the database connection code

Press [bold]Ctrl+C[/bold] to interrupt current task
Press [bold]Ctrl+D[/bold] to exit
"""
        self.console.print(help_text)

    def _cmd_status(self) -> None:
        """Show session status."""
        if not self.agent_loop:
            self.console.print("[red]Agent not initialized[/red]")
            return

        state = self.agent_loop.state
        summary = state.get_summary()

        status = f"""
[bold]Session Status:[/bold]

Iterations: {summary['iterations']}/{state.max_iterations}
Tool calls: {summary['tool_calls']}
Files changed: {summary['files_changed']}
Files created: {summary['files_created']}
Commands executed: {summary['commands_executed']}

Provider: {state.provider}
Model: {state.model}
"""
        self.console.print(status)

        # Show changed files if any
        if state.files_changed:
            self.console.print("\n[bold]Modified files:[/bold]")
            for f in state.files_changed[:10]:
                self.console.print(f"  • {f}")
            if len(state.files_changed) > 10:
                self.console.print(f"  ... and {len(state.files_changed) - 10} more")

    def _cmd_clear(self) -> None:
        """Clear conversation history."""
        if self.agent_loop:
            self.agent_loop.state.messages.clear()
            self.console.print("[green]✓ Conversation history cleared[/green]")
        else:
            self.console.print("[red]Agent not initialized[/red]")

    def _cmd_reset(self) -> None:
        """Reset agent session."""
        try:
            self.agent_loop = AgentLoop(self.workspace_dir)
            self.console.print("[green]✓ Agent session reset[/green]")
        except Exception as e:
            display_error(f"Failed to reset agent: {e}")

    def _cmd_model(self, args: list) -> None:
        """Show or change model."""
        settings = get_settings()
        
        if not args:
            self.console.print(f"Current model: [green]{settings.get_model()}[/green]")
            self.console.print("\nTo change model, use: /model MODEL_NAME")
        else:
            model_name = args[0]
            settings.model_override = model_name
            self.console.print(f"[green]✓ Model changed to: {model_name}[/green]")
            self.console.print("[yellow]Note: Restart agent session with /reset to apply[/yellow]")

    def _cmd_provider(self, args: list) -> None:
        """Show or change provider."""
        settings = get_settings()
        
        if not args:
            self.console.print(f"Current provider: [green]{settings.get_provider()}[/green]")
            self.console.print("\nTo change provider, use: /provider PROVIDER_NAME")
            self.console.print("Available: openai, anthropic, custom")
        else:
            provider_name = args[0]
            if provider_name in ["openai", "anthropic", "custom"]:
                settings.provider_override = provider_name
                self.console.print(f"[green]✓ Provider changed to: {provider_name}[/green]")
                self.console.print("[yellow]Note: Restart agent session with /reset to apply[/yellow]")
            else:
                self.console.print(f"[red]Unknown provider: {provider_name}[/red]")

    def _cmd_context(self) -> None:
        """Show context information."""
        if not self.agent_loop:
            self.console.print("[red]Agent not initialized[/red]")
            return

        state = self.agent_loop.state
        message_count = len(state.messages)
        
        # Rough estimate of context size
        total_chars = sum(len(str(msg.get('content', ''))) for msg in state.messages)
        
        self.console.print(f"""
[bold]Context Information:[/bold]

Messages: {message_count}
Approximate size: {total_chars:,} characters
""")

    def _cmd_tools(self) -> None:
        """List available tools."""
        if not self.agent_loop:
            self.console.print("[red]Agent not initialized[/red]")
            return

        tools = self.agent_loop.tool_registry.list()
        
        self.console.print(f"\n[bold]Available Tools ({len(tools)}):[/bold]\n")
        
        for tool in tools:
            self.console.print(f"[cyan]{tool.name}[/cyan]")
            self.console.print(f"  {tool.description}")
            self.console.print(f"  Category: [dim]{tool.permission_category}[/dim]\n")

    def _cmd_diff(self) -> None:
        """Show git diff."""
        from myagent.tools.git import GitTools
        
        git_tools = GitTools(self.workspace_dir)
        
        if not git_tools.is_git_repo():
            self.console.print("[yellow]Not a git repository[/yellow]")
            return
        
        result = git_tools.git_diff()
        
        if not result.get("success"):
            display_error(result.get("error", "Failed to get diff"))
            return
        
        diff_content = result.get("diff", "")
        
        if not diff_content:
            self.console.print("[dim]No changes to display[/dim]")
        else:
            from myagent.ui.display import display_diff
            display_diff(diff_content)

    def _cmd_config(self) -> None:
        """Edit provider configuration interactively."""
        from myagent.providers.utils import save_provider_config, list_available_models
        
        self.console.print("\n[bold cyan]Provider Configuration[/bold cyan]\n")
        
        # Show current settings
        settings = get_settings()
        self.console.print(f"[dim]Current provider:[/dim] {settings.get_provider()}")
        self.console.print(f"[dim]Current model:[/dim] {settings.get_model()}\n")
        
        # Ask what to configure
        self.console.print("[bold]What would you like to configure?[/bold]")
        self.console.print("  1. Change provider and API key")
        self.console.print("  2. Change model only")
        self.console.print("  3. Update API key for current provider")
        self.console.print("  4. Cancel\n")
        
        try:
            choice = self.session.prompt("Enter choice (1-4): ", style=prompt_style)
            choice = choice.strip()
            
            if choice == "1":
                # Change provider
                self.console.print("\n[bold]Available providers:[/bold]")
                self.console.print("  • anthropic - Anthropic (Claude)")
                self.console.print("  • openai - OpenAI (GPT)")
                self.console.print("  • custom - Custom OpenAI-compatible API\n")
                
                provider = self.session.prompt("Provider name: ", style=prompt_style).strip().lower()
                
                if provider not in ["anthropic", "openai", "custom"]:
                    self.console.print("[red]Invalid provider. Must be: anthropic, openai, or custom[/red]")
                    return
                
                # Get API key
                from prompt_toolkit import prompt as pt_prompt
                api_key = pt_prompt("API Key: ", is_password=True).strip()
                
                if not api_key:
                    self.console.print("[red]API key cannot be empty[/red]")
                    return
                
                # Get model
                model = self.session.prompt("Model name: ", style=prompt_style).strip()
                
                # Get base URL for custom provider
                base_url = None
                if provider == "custom":
                    base_url = self.session.prompt("Base URL: ", style=prompt_style).strip()
                    if not base_url:
                        self.console.print("[red]Base URL required for custom provider[/red]")
                        return
                
                # Save configuration
                save_provider_config(provider, api_key, model, base_url)
                self.console.print(f"\n[green]✓[/green] Provider configured: {provider}")
                self.console.print(f"[green]✓[/green] Model set: {model}")
                self.console.print("\n[yellow]Note:[/yellow] Restart the REPL for changes to take effect")
                
            elif choice == "2":
                # Change model only
                provider = settings.get_provider()
                
                # Try to list available models
                self.console.print(f"\n[bold]Fetching available models for {provider}...[/bold]")
                try:
                    models = list_available_models(provider)
                    if models:
                        self.console.print("\n[bold]Available models:[/bold]")
                        for model in models[:10]:  # Show first 10
                            self.console.print(f"  • {model}")
                        if len(models) > 10:
                            self.console.print(f"  ... and {len(models) - 10} more")
                        self.console.print()
                except Exception as e:
                    self.console.print(f"[yellow]Could not fetch models: {e}[/yellow]\n")
                
                model = self.session.prompt("New model name: ", style=prompt_style).strip()
                
                if not model:
                    self.console.print("[red]Model name cannot be empty[/red]")
                    return
                
                # Update .env file
                from myagent.providers.utils import update_env_file
                key_map = {
                    "anthropic": "ANTHROPIC_MODEL",
                    "openai": "OPENAI_MODEL",
                    "custom": "CUSTOM_MODEL"
                }
                env_key = key_map.get(provider, "MYAGENT_MODEL")
                update_env_file(env_key, model)
                
                self.console.print(f"\n[green]✓[/green] Model updated: {model}")
                self.console.print("\n[yellow]Note:[/yellow] Restart the REPL for changes to take effect")
                
            elif choice == "3":
                # Update API key only
                provider = settings.get_provider()
                
                from prompt_toolkit import prompt as pt_prompt
                api_key = pt_prompt(f"New API key for {provider}: ", is_password=True).strip()
                
                if not api_key:
                    self.console.print("[red]API key cannot be empty[/red]")
                    return
                
                # Update .env file
                from myagent.providers.utils import update_env_file
                key_map = {
                    "anthropic": "ANTHROPIC_API_KEY",
                    "openai": "OPENAI_API_KEY",
                    "custom": "CUSTOM_API_KEY"
                }
                env_key = key_map.get(provider)
                if not env_key:
                    self.console.print(f"[red]Unknown provider: {provider}[/red]")
                    return
                
                update_env_file(env_key, api_key)
                
                self.console.print(f"\n[green]✓[/green] API key updated for {provider}")
                self.console.print("\n[yellow]Note:[/yellow] Restart the REPL for changes to take effect")
                
            elif choice == "4":
                self.console.print("[dim]Configuration cancelled[/dim]")
                return
            else:
                self.console.print("[red]Invalid choice[/red]")
                
        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[dim]Configuration cancelled[/dim]")
        except Exception as e:
            display_error(f"Configuration error: {e}")

    def _cmd_exit(self) -> None:
        """Exit the REPL."""
        self.running = False

    def _check_and_load_previous_session(self) -> None:
        """Check for previous session and offer to continue."""
        try:
            message_count = self.history_manager.get_message_count()
            
            if message_count > 0:
                self.console.print(f"\n[yellow]📜 Found previous session with {message_count} messages[/yellow]")
                self.console.print("[dim]Would you like to continue from where you left off?[/dim]\n")
                
                try:
                    response = self.session.prompt(
                        "Continue previous session? (y/n): ",
                        style=prompt_style
                    ).strip().lower()
                except (KeyboardInterrupt, EOFError):
                    # User cancelled, start fresh
                    response = 'n'
                
                if response in ['y', 'yes']:
                    session_data = self.history_manager.load_session()
                    if session_data and self.agent_loop:
                        # Restore messages to agent state
                        messages = session_data.get("messages", [])
                        self.agent_loop.state.messages = messages
                        self.console.print(f"[green]✓ Restored {len(messages)} messages from previous session[/green]\n")
                    else:
                        self.console.print("[yellow]Could not load previous session[/yellow]\n")
                else:
                    # Archive old session and start fresh
                    session_id = self.history_manager.archive_current_session()
                    if session_id:
                        self.console.print(f"[dim]Previous session archived as: {session_id}[/dim]\n")
                    self.console.print("[green]Starting fresh session[/green]\n")
        except Exception as e:
            logger.error(f"Error checking previous session: {e}")
            # Continue with fresh session on error

    def _auto_save_session(self) -> None:
        """Auto-save the current session after each interaction."""
        try:
            if self.agent_loop and self.agent_loop.state.messages:
                session_data = {
                    "provider": self.agent_loop.state.provider,
                    "model": self.agent_loop.state.model,
                    "summary": self.agent_loop.state.get_summary(),
                }
                self.history_manager.save_session(
                    self.agent_loop.state.messages,
                    session_data
                )
        except Exception as e:
            logger.error(f"Failed to auto-save session: {e}")

    def _save_session_on_exit(self) -> None:
        """Save session when exiting."""
        try:
            if self.agent_loop and self.agent_loop.state.messages:
                self._auto_save_session()
                self.console.print("[dim]💾 Session saved[/dim]")
        except Exception as e:
            logger.error(f"Failed to save session on exit: {e}")

    def _execute_task(self, task: str) -> None:
        """
        Execute a user task.

        Args:
            task: Task description
        """
        if not self.agent_loop:
            display_error("Agent not initialized")
            return

        display_status(f"Executing task: {task}")
        
        try:
            result = self.agent_loop.run(task, stream=False)
            
            if result.get("success"):
                # Show result message
                message = result.get("message", "")
                if message:
                    self.console.print(f"\n[bold green]Result:[/bold green]\n{message}\n")
                
                # Show summary
                state_summary = result.get("state", {})
                if state_summary:
                    files_changed = self.agent_loop.state.files_changed
                    files_created = self.agent_loop.state.files_created
                    commands = self.agent_loop.state.commands_executed
                    
                    if files_changed or files_created or commands:
                        display_summary(
                            changed_files=files_changed,
                            commands_run=commands,
                            test_results=self.agent_loop.state.last_test_result,
                        )
            else:
                error = result.get("error", "Unknown error")
                display_error(f"Task failed: {error}")
                
        except Exception as e:
            logger.exception("Error executing task")
            display_error(f"Task execution failed: {e}")

    def _cmd_history(self) -> None:
        """Show conversation history summary."""
        if not self.agent_loop:
            self.console.print("[red]Agent not initialized[/red]")
            return
        
        messages = self.agent_loop.state.messages
        
        if not messages:
            self.console.print("[dim]No conversation history yet[/dim]")
            return
        
        self.console.print(f"\n[bold]Conversation History[/bold] ({len(messages)} messages)\n")
        
        from rich.table import Table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Role", style="cyan", width=12)
        table.add_column("Content", style="white")
        
        for i, msg in enumerate(messages[-20:], 1):  # Show last 20 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            if isinstance(content, str):
                # Truncate long messages
                display_content = content[:100] + "..." if len(content) > 100 else content
                table.add_row(role, display_content)
            elif isinstance(content, list):
                # Tool use/result
                table.add_row(role, f"[dim]{len(content)} tool calls[/dim]")
        
        self.console.print(table)
        self.console.print(f"\n[dim]Showing last 20 of {len(messages)} total messages[/dim]")
        self.console.print(f"[dim]History saved to: {self.history_manager.history_dir}[/dim]\n")

    def _cmd_sessions(self) -> None:
        """List and manage saved sessions."""
        sessions = self.history_manager.list_sessions(limit=10)
        
        if not sessions:
            self.console.print("[dim]No saved sessions found[/dim]")
            return
        
        self.console.print(f"\n[bold]Saved Sessions[/bold] (last 10)\n")
        
        from rich.table import Table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Session ID", style="cyan", width=18)
        table.add_column("Date", style="yellow", width=20)
        table.add_column("Messages", style="green", width=10)
        table.add_column("Last Message", style="white")
        
        for i, session in enumerate(sessions, 1):
            session_id = session.get("session_id", "")
            timestamp = session.get("timestamp", "")[:19].replace("T", " ")  # Format datetime
            msg_count = session.get("message_count", 0)
            last_msg = session.get("last_message", "")[:50]
            
            table.add_row(str(i), session_id, timestamp, str(msg_count), last_msg)
        
        self.console.print(table)
        self.console.print(f"\n[dim]Sessions stored in: {self.history_manager.history_dir}[/dim]\n")


def start_interactive_session(workspace_dir: Path) -> None:
    """
    Start an interactive REPL session.

    Args:
        workspace_dir: Workspace root directory
    """
    repl = InteractiveREPL(workspace_dir)
    repl.start()
