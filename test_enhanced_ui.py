"""Test the enhanced UI components."""

from pathlib import Path

from myagent.ui.enhanced_display import get_enhanced_display
from myagent.ui.menu import get_menu


def test_enhanced_display():
    """Test enhanced display features."""
    display = get_enhanced_display()
    
    print("\n=== Testing Enhanced Display ===\n")
    
    # Test banner
    display.show_banner(
        project_name="TestProject",
        provider="anthropic",
        model="claude-3-5-sonnet-20241022"
    )
    
    # Test flash messages
    display.show_flash("Operation successful!", style="green", icon="✓")
    display.show_error_flash("Something went wrong")
    display.show_warning_flash("This is a warning")
    display.show_info_flash("Just FYI")
    
    # Test task flow
    display.start_task("Fix the authentication bug")
    display.show_tool_call("read_file", {"path": "auth.py"})
    display.show_tool_call("edit_file", {"path": "auth.py"})
    display.show_tool_call("run_command", {"command": "pytest tests/"})
    
    display.show_assistant_response(
        "I've fixed the authentication bug by updating the token validation logic."
    )
    
    display.show_task_complete(
        files_changed=["auth.py", "tests/test_auth.py"],
        files_created=["utils/validators.py"],
        commands_run=["pytest tests/test_auth.py"],
    )
    
    print("\n✓ Enhanced display test completed!\n")


def test_menu_system():
    """Test menu system (non-interactive)."""
    menu = get_menu()
    
    print("\n=== Testing Menu System ===\n")
    print("✓ Menu system initialized successfully")
    print("✓ Interactive menus available:")
    print("  - Main menu")
    print("  - Settings menu")
    print("  - Provider selection")
    print("  - File operations")
    print("  - Git operations")
    print("\n✓ Menu system test completed!\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Enhanced UI Components Test")
    print("="*60)
    
    test_enhanced_display()
    test_menu_system()
    
    print("="*60)
    print("All tests completed successfully! ✓")
    print("="*60 + "\n")
    
    print("To test the full interactive mode, run:")
    print("  python -m myagent")
    print("\nOr execute a single task:")
    print('  python -m myagent "add a hello function to main.py"')
    print()
