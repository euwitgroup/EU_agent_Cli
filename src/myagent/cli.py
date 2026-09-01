"""CLI entry point for MyAgent."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table
from typing_extensions import Annotated
from dotenv import load_dotenv

from myagent import __version__
from myagent.config import get_settings
from myagent.ui import display_banner, display_error, get_console

# Initialize Typer app
app = typer.Typer(
    name="myagent",
    help="AI-powered coding agent for terminal",
    add_completion=False,
    invoke_without_command=True,  # Allow running without specifying command
)

# Provider management subcommand
provider_app = typer.Typer(
    name="provider",
    help="Manage AI provider configurations",
    add_completion=False,
)
app.add_typer(provider_app, name="provider")


@app.callback()
def callback(ctx: typer.Context):
    """
    Main callback - starts interactive mode when no command is given.
    """
    # If no subcommand was invoked, start interactive mode
    if ctx.invoked_subcommand is None:
        try:
            # Debug: confirm callback is running
            console = get_console()
            console.print("[dim]Starting MyAgent...[/dim]")
            
            # Import here to avoid circular imports
            from myagent.ui.prompt import start_interactive_session
            
            # Start interactive session in current directory
            workspace_dir = Path.cwd()
            
            console.print(f"[dim]Workspace: {workspace_dir}[/dim]")
            start_interactive_session(workspace_dir)
            console.print("[dim]Session ended[/dim]")
        except KeyboardInterrupt:
            console = get_console()
            console.print("\n[yellow]Interrupted[/yellow]")
        except Exception as e:
            console = get_console()
            console.print(f"\n[red]Callback Error:[/red] {e}")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            raise typer.Exit(1)


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    settings = get_settings()
    log_level = logging.DEBUG if verbose else settings.get_log_level()

    # Configure logging to only show in verbose mode
    if verbose:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stderr)],
        )
    else:
        # In normal mode, suppress all logs except critical
        logging.basicConfig(
            level=logging.CRITICAL,
            format="%(message)s",
            handlers=[logging.NullHandler()],
        )

    # Reduce noise from libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console = get_console()
        console.print(f"MyAgent version {__version__}")
        raise typer.Exit()


@app.command()
def main(
    task: Annotated[
        Optional[str],
        typer.Argument(help="Task to execute (if not provided, starts interactive mode)"),
    ] = None,
    provider: Annotated[
        Optional[str],
        typer.Option("--provider", "-p", help="AI provider: openai, anthropic, custom"),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Model name to use"),
    ] = None,
    cwd: Annotated[
        Optional[Path],
        typer.Option("--cwd", help="Working directory (defaults to current directory)"),
    ] = None,
    config: Annotated[
        Optional[Path],
        typer.Option("--config", "-c", help="Path to configuration file"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
    no_color: Annotated[
        bool,
        typer.Option("--no-color", help="Disable colored output"),
    ] = False,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True, help="Show version"),
    ] = None,
) -> None:
    """
    MyAgent - AI-powered coding agent for terminal.

    Start interactive mode:
        myagent

    Execute a single task:
        myagent "fix the authentication bug"

    Use specific provider and model:
        myagent --provider openai --model gpt-4-turbo-preview
    """
    # Setup logging first
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load settings and apply CLI overrides
        settings = get_settings()
        settings.verbose = verbose
        settings.no_color = no_color

        if provider:
            settings.provider_override = provider
        if model:
            settings.model_override = model
        if cwd:
            settings.cwd_override = cwd.resolve()

        # Determine working directory
        workspace_dir = settings.cwd_override or Path.cwd()
        logger.debug(f"Working directory: {workspace_dir}")

        # Validate API key
        api_key = settings.get_api_key()
        if not api_key:
            console = get_console()
            console.print("\n[yellow]⚠ No API key found![/yellow]\n")
            console.print(f"[dim]Provider '{settings.get_provider()}' is not configured.[/dim]\n")
            
            if typer.confirm("Would you like to configure a provider now?", default=True):
                console.print("\n[cyan]Let's set up your AI provider...[/cyan]\n")
                
                # Import inquirer for interactive selection
                import inquirer
                
                questions = [
                    inquirer.List(
                        'provider',
                        message="Select AI provider",
                        choices=['anthropic', 'openai', 'custom'],
                        default='anthropic'
                    ),
                ]
                answers = inquirer.prompt(questions)
                selected_provider = answers['provider']
                
                # Prompt for API key
                console.print(f"\n[cyan]Configuring {selected_provider}...[/cyan]")
                api_key_input = typer.prompt(f"{selected_provider.upper()} API key")
                
                # Prompt for model
                base_url = None
                if selected_provider == 'anthropic':
                    model_input = typer.prompt("Model name", default="claude-3-5-sonnet-20241022")
                elif selected_provider == 'openai':
                    model_input = typer.prompt("Model name", default="gpt-4-turbo-preview")
                else:  # custom
                    model_input = typer.prompt("Model name")
                    base_url = typer.prompt("Base URL (e.g., https://api.example.com/v1)")
                
                # Save configuration
                from myagent.providers.utils import save_provider_config
                
                saved = save_provider_config(
                    provider=selected_provider,
                    api_key=api_key_input,
                    model=model_input,
                    base_url=base_url if selected_provider == 'custom' else None,
                )
                
                if saved:
                    console.print(f"\n[green]✓ Configuration saved![/green]")
                    console.print(f"[dim]Config saved to: ~/.myagent/.env[/dim]")
                    console.print(f"[dim]Restarting with your configuration...[/dim]\n")
                    
                    # Force reload environment variables from the new .env file
                    import os
                    from dotenv import load_dotenv
                    
                    # Load the new .env file
                    home_env = Path.home() / ".myagent" / ".env"
                    load_dotenv(home_env, override=True)
                    
                    # Reset settings to force reload
                    from myagent.config import reset_settings
                    reset_settings()
                    settings = get_settings()
                    
                    # Apply overrides again
                    if selected_provider:
                        settings.provider_override = selected_provider
                    if model_input:
                        settings.model_override = model_input
                else:
                    display_error("Failed to save configuration", title="Configuration Error")
                    raise typer.Exit(1)
            else:
                display_error(
                    f"No API key found for provider '{settings.get_provider()}'.\n\n"
                    f"Please set the appropriate environment variable:\n"
                    f"  - OpenAI: OPENAI_API_KEY\n"
                    f"  - Anthropic: ANTHROPIC_API_KEY\n"
                    f"  - Custom: CUSTOM_API_KEY\n\n"
                    f"Or create a .env file with your credentials.\n\n"
                    f"You can also run: myagent provider add --provider anthropic",
                    title="Configuration Error",
                )
                raise typer.Exit(1)

        # Display banner (only in interactive mode or verbose)
        if not task or verbose:
            project_name = workspace_dir.name
            # Banner will be shown by enhanced display in both modes
            if not task:
                # Interactive mode - banner shown by enhanced session
                pass
            else:
                # Verbose mode for single task - banner shown by enhanced display
                pass

        # Import here to avoid circular dependencies
        if task:
            # Single task execution mode
            logger.info(f"Executing task: {task}")
            from myagent.agent.loop import AgentLoop
            from myagent.ui import get_enhanced_display

            # Use enhanced display for single tasks too
            display = get_enhanced_display()
            display.show_banner(
                project_name=workspace_dir.name,
                provider=settings.get_provider(),
                model=settings.get_model(),
            )
            
            loop = AgentLoop(workspace_dir=workspace_dir, use_enhanced_display=True)
            display.start_task(task)
            
            result = loop.run(task)

            if result.get("success"):
                logger.info("Task completed successfully")
                
                # Show response
                message = result.get("message", "")
                if message:
                    display.show_assistant_response(message)
                
                # Show summary
                display.show_task_complete(
                    files_changed=list(loop.state.files_changed),
                    files_created=list(loop.state.files_created),
                    commands_run=list(loop.state.commands_executed),
                )
                
                raise typer.Exit(0)
            else:
                logger.error("Task failed")
                error = result.get("error", "Unknown error")
                display.show_error(f"Task failed: {error}")
                raise typer.Exit(1)
        else:
            # Interactive REPL mode
            logger.info("Starting interactive mode")
            
            # Use simple prompt_toolkit REPL
            from myagent.ui.prompt import start_interactive_session
            
            start_interactive_session(workspace_dir=workspace_dir)

    except KeyboardInterrupt:
        console = get_console()
        console.print("\n[yellow]Interrupted by user[/yellow]")
        raise typer.Exit(130)
    except typer.Exit:
        # Let typer.Exit propagate without catching it
        raise
    except Exception as e:
        logger.exception("Unexpected error")
        console = get_console()
        console.print(f"\n[red]Error:[/red] {e}")
        console.print(f"[dim]Type: {type(e).__name__}[/dim]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        display_error(str(e), title="Unexpected Error")
        raise typer.Exit(1)


@provider_app.command("add")
def provider_add(
    provider: Annotated[
        str,
        typer.Option("--provider", "-p", help="Provider: openai, anthropic, custom"),
    ],
    api_key: Annotated[
        Optional[str],
        typer.Option("--api-key", "-k", help="API key (will prompt if not provided)"),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Model name (will prompt if not provided)"),
    ] = None,
    base_url: Annotated[
        Optional[str],
        typer.Option("--base-url", "-u", help="Base URL (for custom provider)"),
    ] = None,
    save: Annotated[
        bool,
        typer.Option("--save", "-s", help="Save configuration to .env file"),
    ] = True,
    test_connection: Annotated[
        bool,
        typer.Option("--test/--no-test", help="Test connection before saving"),
    ] = True,
) -> None:
    """
    Add and configure a new AI provider.

    Non-interactive (provide all parameters):
        myagent provider add --provider anthropic --api-key sk-ant-xxx --model claude-3-5-sonnet-20241022

    Interactive (will prompt for missing parameters):
        myagent provider add --provider anthropic
    """
    console = get_console()

    # Validate provider
    if provider not in ["openai", "anthropic", "custom"]:
        display_error(f"Invalid provider: {provider}", title="Configuration Error")
        raise typer.Exit(1)

    # Require base_url for custom provider
    if provider == "custom" and not base_url:
        if typer.confirm("Custom provider requires a base URL. Provide it now?", default=True):
            base_url = typer.prompt("Base URL (e.g., https://api.example.com/v1)")
        else:
            display_error("Base URL is required for custom provider", title="Configuration Error")
            raise typer.Exit(1)

    # Prompt for missing required parameters
    if not api_key:
        api_key = typer.prompt(f"{provider.upper()} API key")
    
    if not model:
        model = typer.prompt(f"Model name (e.g., {'gpt-4' if provider == 'openai' else 'claude-3-5-sonnet-20241022' if provider == 'anthropic' else 'your-model'})")

    # Test connection if requested
    if test_connection:
        console.print(f"\n[cyan]Testing connection to {provider}...[/cyan]")

        from myagent.providers.utils import check_provider_connection

        result = asyncio.run(
            check_provider_connection(
                provider=provider,
                api_key=api_key,
                model=model,
                base_url=base_url,
            )
        )

        if result["success"]:
            console.print(f"[green]✓[/green] Connection successful!")
            console.print(f"[dim]Provider: {result['provider']}[/dim]")
            console.print(f"[dim]Model: {result['model']}[/dim]")
            console.print(f"[dim]Response preview: {result['response_text']}...[/dim]")
        else:
            display_error(
                f"Connection test failed:\n{result['error']}",
                title="Connection Error",
            )
            if not typer.confirm("\nSave configuration anyway?", default=False):
                raise typer.Exit(1)

    # Save configuration
    if save:
        console.print(f"\n[cyan]Saving configuration to .env...[/cyan]")
        from myagent.providers.utils import save_provider_config

        saved = save_provider_config(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )

        if saved:
            console.print(f"[green]✓[/green] Configuration saved!")
            console.print(f"[dim]Config location: ~/.myagent/.env[/dim]")
            console.print(f"\n[dim]You can now run:[/dim]")
            console.print(f"[cyan]  myagent main[/cyan]")
        else:
            console.print(f"[yellow]⚠[/yellow] Failed to save configuration")
            raise typer.Exit(1)


@provider_app.command("test")
def provider_test(
    provider: Annotated[
        Optional[str],
        typer.Option("--provider", "-p", help="Provider to test (defaults to current)"),
    ] = None,
) -> None:
    """
    Test connection to configured provider.

    Example:
        myagent provider test
        myagent provider test --provider openai
    """
    console = get_console()
    settings = get_settings()

    # Use provided provider or default from settings
    test_provider = provider or settings.get_provider()
    api_key = settings.get_api_key()
    model = settings.get_model()

    if not api_key:
        display_error(
            f"No API key found for provider '{test_provider}'",
            title="Configuration Error",
        )
        raise typer.Exit(1)

    # Get base_url if custom provider
    base_url = None
    if test_provider == "custom":
        import os
        base_url = os.getenv("CUSTOM_BASE_URL")
        if not base_url:
            display_error(
                "CUSTOM_BASE_URL not set for custom provider",
                title="Configuration Error",
            )
            raise typer.Exit(1)

    console.print(f"\n[cyan]Testing connection to {test_provider}...[/cyan]")
    console.print(f"[dim]Model: {model}[/dim]\n")

    from myagent.providers.utils import check_provider_connection

    result = asyncio.run(
        check_provider_connection(
            provider=test_provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
    )

    if result["success"]:
        console.print(f"[green]✓[/green] Connection successful!")
        console.print(f"[dim]Response preview: {result['response_text']}...[/dim]")
    else:
        display_error(
            f"Connection test failed:\n{result['error']}",
            title="Connection Error",
        )
        raise typer.Exit(1)


@provider_app.command("models")
def provider_models(
    provider: Annotated[
        Optional[str],
        typer.Option("--provider", "-p", help="Provider (defaults to current)"),
    ] = None,
) -> None:
    """
    List available models from provider.

    Example:
        myagent provider models
        myagent provider models --provider openai
    """
    console = get_console()
    settings = get_settings()

    # Use provided provider or default from settings
    list_provider = provider or settings.get_provider()
    api_key = settings.get_api_key()

    if not api_key:
        display_error(
            f"No API key found for provider '{list_provider}'",
            title="Configuration Error",
        )
        raise typer.Exit(1)

    # Get base_url if custom provider
    base_url = None
    if list_provider == "custom":
        import os
        base_url = os.getenv("CUSTOM_BASE_URL")

    console.print(f"\n[cyan]Fetching models from {list_provider}...[/cyan]\n")

    from myagent.providers.utils import list_models_from_provider

    result = asyncio.run(
        list_models_from_provider(
            provider=list_provider,
            api_key=api_key,
            base_url=base_url,
        )
    )

    if result["success"]:
        console.print(f"[green]✓[/green] Found {result['count']} models:\n")

        # Display in a table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Model ID", style="white")

        for model_id in result["models"]:
            table.add_row(model_id)

        console.print(table)

        if result.get("note"):
            console.print(f"\n[dim]{result['note']}[/dim]")

    else:
        display_error(
            f"Failed to list models:\n{result['error']}",
            title="Error",
        )
        raise typer.Exit(1)


@provider_app.command("list")
def provider_list() -> None:
    """
    List all available providers.

    Example:
        myagent provider list
    """
    console = get_console()

    console.print("\n[bold cyan]Available Providers:[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Provider", style="white")
    table.add_column("Status", style="green")
    table.add_column("Configuration", style="dim")

    providers = [
        ("openai", "OPENAI_API_KEY", "OpenAI GPT models"),
        ("anthropic", "ANTHROPIC_API_KEY", "Claude models"),
        ("custom", "CUSTOM_API_KEY", "OpenAI-compatible endpoints"),
    ]

    import os

    for provider, env_var, description in providers:
        status = "✓ Configured" if os.getenv(env_var) else "✗ Not configured"
        status_style = "green" if os.getenv(env_var) else "red"
        table.add_row(
            provider,
            f"[{status_style}]{status}[/{status_style}]",
            description,
        )

    console.print(table)

    # Show current provider
    settings = get_settings()
    console.print(f"\n[dim]Current provider: [cyan]{settings.get_provider()}[/cyan][/dim]")


@provider_app.command("switch")
def provider_switch(
    provider: Annotated[
        str,
        typer.Argument(help="Provider to switch to: openai, anthropic, custom"),
    ],
) -> None:
    """
    Switch to a different configured provider.

    Example:
        myagent provider switch custom
        myagent provider switch anthropic
    """
    console = get_console()
    
    # Validate provider
    if provider not in ["openai", "anthropic", "custom"]:
        display_error(f"Invalid provider: {provider}", title="Configuration Error")
        raise typer.Exit(1)
    
    # Check if provider is configured
    import os
    env_var = f"{provider.upper()}_API_KEY"
    
    if not os.getenv(env_var):
        display_error(
            f"Provider '{provider}' is not configured.\n\n"
            f"Please configure it first:\n"
            f"  python -m myagent provider add --provider {provider}",
            title="Provider Not Configured",
        )
        raise typer.Exit(1)
    
    # Update .env file
    from pathlib import Path
    
    env_path = Path(".env")
    if not env_path.exists():
        display_error("No .env file found", title="Configuration Error")
        raise typer.Exit(1)
    
    # Read and update
    lines = env_path.read_text().splitlines()
    updated_lines = []
    
    for line in lines:
        if line.startswith("MYAGENT_PROVIDER="):
            updated_lines.append(f"MYAGENT_PROVIDER={provider}")
        else:
            updated_lines.append(line)
    
    env_path.write_text("\n".join(updated_lines) + "\n")
    
    # Get model for display
    model = os.getenv(f"{provider.upper()}_MODEL", "not set")
    
    console.print(f"\n[green]✓[/green] Switched to provider: [cyan]{provider}[/cyan]")
    console.print(f"[dim]Model: {model}[/dim]")
    console.print(f"\n[dim]You can now run:[/dim]")
    console.print(f"[cyan]  python -m myagent main[/cyan]")


if __name__ == "__main__":
    app()
