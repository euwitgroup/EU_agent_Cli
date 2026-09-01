"""Interactive menu with arrow key and mouse support."""

from typing import Any, Callable, Dict, List, Optional, Tuple

import inquirer
from inquirer import errors
from inquirer.themes import GreenPassion


class InteractiveMenu:
    """Interactive menu system with arrow keys and mouse support."""

    def __init__(self):
        """Initialize interactive menu."""
        self.theme = GreenPassion()

    def show_main_menu(self) -> str:
        """
        Show main menu and return selected action.

        Returns:
            Selected action code
        """
        questions = [
            inquirer.List(
                "action",
                message="What would you like to do?",
                choices=[
                    ("💬 Chat with Agent", "chat"),
                    ("📋 Execute Task", "task"),
                    ("📊 View Status", "status"),
                    ("🔧 Configure Settings", "settings"),
                    ("📁 File Operations", "files"),
                    ("🔄 Git Operations", "git"),
                    ("❓ Help", "help"),
                    ("🚪 Exit", "exit"),
                ],
            ),
        ]

        answers = inquirer.prompt(questions, theme=self.theme)
        return answers["action"] if answers else "exit"

    def show_settings_menu(self) -> str:
        """
        Show settings menu.

        Returns:
            Selected setting action
        """
        questions = [
            inquirer.List(
                "setting",
                message="Settings",
                choices=[
                    ("🔄 Change Provider", "provider"),
                    ("🤖 Change Model", "model"),
                    ("📊 View Configuration", "view"),
                    ("⬅️  Back to Main Menu", "back"),
                ],
            ),
        ]

        answers = inquirer.prompt(questions, theme=self.theme)
        return answers["setting"] if answers else "back"

    def show_provider_menu(self, current_provider: str) -> Optional[str]:
        """
        Show provider selection menu.

        Args:
            current_provider: Currently selected provider

        Returns:
            Selected provider or None if cancelled
        """
        questions = [
            inquirer.List(
                "provider",
                message=f"Select AI Provider (current: {current_provider})",
                choices=[
                    ("OpenAI (GPT-4, GPT-3.5)", "openai"),
                    ("Anthropic (Claude)", "anthropic"),
                    ("Custom (OpenAI-compatible)", "custom"),
                    ("Cancel", None),
                ],
            ),
        ]

        answers = inquirer.prompt(questions, theme=self.theme)
        return answers["provider"] if answers else None

    def show_model_input(self, current_model: str, provider: str) -> Optional[str]:
        """
        Show model input prompt.

        Args:
            current_model: Current model
            provider: Provider name

        Returns:
            Model name or None if cancelled
        """
        # Suggest models based on provider
        suggestions = {
            "openai": ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            "anthropic": [
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
            ],
            "custom": ["model-name"],
        }

        choices = suggestions.get(provider, ["model-name"])
        choices.append("Enter custom model name")
        choices.append("Cancel")

        questions = [
            inquirer.List(
                "model_choice",
                message=f"Select Model (current: {current_model})",
                choices=choices,
            ),
        ]

        answers = inquirer.prompt(questions, theme=self.theme)
        
        if not answers or answers["model_choice"] == "Cancel":
            return None
        
        if answers["model_choice"] == "Enter custom model name":
            custom_questions = [
                inquirer.Text(
                    "model",
                    message="Enter model name",
                    default=current_model,
                ),
            ]
            custom_answers = inquirer.prompt(custom_questions, theme=self.theme)
            return custom_answers["model"] if custom_answers else None
        
        return answers["model_choice"]

    def show_file_operations_menu(self) -> str:
        """
        Show file operations menu.

        Returns:
            Selected operation
        """
        questions = [
            inquirer.List(
                "operation",
                message="File Operations",
                choices=[
                    ("📄 View File", "view"),
                    ("✏️  Edit File", "edit"),
                    ("🔍 Search Files", "search"),
                    ("📊 Show Changes", "changes"),
                    ("⬅️  Back to Main Menu", "back"),
                ],
            ),
        ]

        answers = inquirer.prompt(questions, theme=self.theme)
        return answers["operation"] if answers else "back"

    def show_git_operations_menu(self) -> str:
        """
        Show git operations menu.

        Returns:
            Selected operation
        """
        questions = [
            inquirer.List(
                "operation",
                message="Git Operations",
                choices=[
                    ("📊 Status", "status"),
                    ("📝 Diff", "diff"),
                    ("📜 Log", "log"),
                    ("➕ Stage Changes", "add"),
                    ("💾 Commit", "commit"),
                    ("⬅️  Back to Main Menu", "back"),
                ],
            ),
        ]

        answers = inquirer.prompt(questions, theme=self.theme)
        return answers["operation"] if answers else "back"

    def confirm(self, message: str, default: bool = True) -> bool:
        """
        Show confirmation dialog.

        Args:
            message: Confirmation message
            default: Default value

        Returns:
            User's choice
        """
        questions = [
            inquirer.Confirm(
                "confirmed",
                message=message,
                default=default,
            ),
        ]

        answers = inquirer.prompt(questions, theme=self.theme)
        return answers["confirmed"] if answers else False

    def text_input(self, message: str, default: str = "") -> Optional[str]:
        """
        Show text input prompt.

        Args:
            message: Input message
            default: Default value

        Returns:
            User input or None if cancelled
        """
        questions = [
            inquirer.Text(
                "input",
                message=message,
                default=default,
            ),
        ]

        answers = inquirer.prompt(questions, theme=self.theme)
        return answers["input"] if answers else None

    def multiline_input(self, message: str) -> Optional[str]:
        """
        Show multiline text input.

        Args:
            message: Input message

        Returns:
            User input or None if cancelled
        """
        questions = [
            inquirer.Editor(
                "input",
                message=message,
            ),
        ]

        answers = inquirer.prompt(questions, theme=self.theme)
        return answers["input"] if answers else None

    def list_select(
        self,
        message: str,
        choices: List[Tuple[str, Any]],
        default: Optional[Any] = None,
    ) -> Optional[Any]:
        """
        Show list selection menu.

        Args:
            message: Selection message
            choices: List of (display_name, value) tuples
            default: Default selection

        Returns:
            Selected value or None if cancelled
        """
        questions = [
            inquirer.List(
                "selection",
                message=message,
                choices=choices,
                default=default,
            ),
        ]

        answers = inquirer.prompt(questions, theme=self.theme)
        return answers["selection"] if answers else None

    def checkbox_select(
        self,
        message: str,
        choices: List[Tuple[str, Any]],
    ) -> List[Any]:
        """
        Show checkbox selection menu.

        Args:
            message: Selection message
            choices: List of (display_name, value) tuples

        Returns:
            List of selected values
        """
        questions = [
            inquirer.Checkbox(
                "selections",
                message=message,
                choices=choices,
            ),
        ]

        answers = inquirer.prompt(questions, theme=self.theme)
        return answers["selections"] if answers else []


# Global menu instance
_menu: Optional[InteractiveMenu] = None


def get_menu() -> InteractiveMenu:
    """Get or create the global menu instance."""
    global _menu
    if _menu is None:
        _menu = InteractiveMenu()
    return _menu
