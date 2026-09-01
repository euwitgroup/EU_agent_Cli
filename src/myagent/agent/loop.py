"""Agent loop implementation."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from myagent.agent.context import ContextManager
from myagent.agent.state import AgentState
from myagent.config import get_settings
from myagent.providers import Message, ProviderRouter, ToolCall, ToolDefinition
from myagent.tools import register_all_tools
from myagent.ui import display_error, display_status, display_tool_call, display_tool_result, get_enhanced_display

logger = logging.getLogger(__name__)


class AgentLoop:
    """Main agent loop for executing tasks."""

    def __init__(self, workspace_dir: Path, use_enhanced_display: bool = True):
        """
        Initialize the agent loop.

        Args:
            workspace_dir: Workspace root directory
            use_enhanced_display: Whether to use enhanced display (default: True)
        """
        self.workspace_dir = workspace_dir
        self.use_enhanced_display = use_enhanced_display
        settings = get_settings()

        # Initialize state
        self.state = AgentState(
            workspace_dir=workspace_dir,
            provider=settings.get_provider(),
            model=settings.get_model(),
            max_iterations=settings.myagent_max_iterations,
        )

        # Initialize components
        self.context_manager = ContextManager(workspace_dir)
        self.tool_registry = register_all_tools(workspace_dir)
        
        # Get display instance
        if use_enhanced_display:
            self.display = get_enhanced_display()
        else:
            self.display = None
        
        try:
            self.provider = ProviderRouter.create_provider()
        except Exception as e:
            logger.error(f"Failed to create provider: {e}")
            raise

        logger.info(f"Agent loop initialized: {self.state.provider} / {self.state.model}")

    def run(self, task: str, stream: bool = True) -> Dict[str, Any]:
        """
        Execute a task.

        Args:
            task: Task description from user
            stream: Whether to stream responses (for interactive mode)

        Returns:
            Dict with execution results
        """
        logger.info(f"Starting task: {task[:100]}...")

        try:
            # Build initial messages
            system_prompt = self.context_manager.build_system_context()
            user_message = self.context_manager.build_user_message(
                task, include_project_summary=True
            )

            # Add to state
            self.state.add_message("system", system_prompt)
            self.state.add_message("user", user_message)

            # Get tool definitions
            tool_definitions = [
                ToolDefinition(
                    name=td["name"],
                    description=td["description"],
                    parameters=td["parameters"],
                )
                for td in self.tool_registry.get_definitions()
            ]

            # Main agent loop
            while not self.state.has_reached_limit():
                self.state.increment_iteration()
                logger.debug(f"Iteration {self.state.iteration_count}/{self.state.max_iterations}")

                # Convert state messages to provider format
                messages = []
                for msg in self.state.messages:
                    # Handle messages stored as dicts
                    if isinstance(msg, dict):
                        role = msg.get("role")
                        content = msg.get("content")
                        tool_calls = msg.get("tool_calls")
                        tool_call_id = msg.get("tool_call_id")
                        
                        # Convert tool_calls if present
                        tc_list = None
                        if tool_calls:
                            tc_list = [
                                ToolCall(id=tc["id"], name=tc["name"], arguments=tc["arguments"])
                                if isinstance(tc, dict) else tc
                                for tc in tool_calls
                            ]
                        
                        messages.append(
                            Message(
                                role=role,
                                content=content,
                                tool_calls=tc_list,
                                tool_call_id=tool_call_id,
                            )
                        )
                    else:
                        # Already a Message object
                        messages.append(msg)

                # Show thinking indicator
                if self.display:
                    self.display.show_thinking()

                # Generate response
                try:
                    response = self.provider.generate(
                        messages=messages,
                        tools=tool_definitions,
                        temperature=0.7,
                        stream=False,
                    )
                    
                    # Clear thinking indicator
                    if self.display:
                        self.display.clear_thinking()
                        
                except Exception as e:
                    logger.error(f"Provider error: {e}")
                    if self.display:
                        self.display.clear_thinking()
                        self.display.show_error_flash(f"AI provider error: {e}")
                    else:
                        display_error(f"AI provider error: {e}")
                    return {
                        "success": False,
                        "error": f"Provider error: {e}",
                        "state": self.state.get_summary(),
                    }

                # Check finish reason
                if response.finish_reason == "stop":
                    # Task completed
                    if response.content:
                        self.state.add_message("assistant", response.content)
                        logger.info("Task completed successfully")
                    
                    return {
                        "success": True,
                        "message": response.content,
                        "state": self.state.get_summary(),
                    }

                elif response.finish_reason == "tool_calls" or response.tool_calls:
                    # Execute tool calls
                    tool_results = self._execute_tools(response.tool_calls)

                    # Add assistant message with tool calls
                    self.state.add_message("assistant", {
                        "content": response.content,
                        "tool_calls": [tc.model_dump() for tc in response.tool_calls],
                    })

                    # Add tool results as user messages
                    for tool_call, result in zip(response.tool_calls, tool_results):
                        formatted_result = self.context_manager.format_tool_result(
                            tool_call.name, result
                        )
                        
                        self.state.add_message("user", {
                            "content": formatted_result,
                            "tool_call_id": tool_call.id,
                        })

                    # Continue loop for next iteration
                    continue

                elif response.finish_reason == "length":
                    # Context limit reached
                    logger.warning("Response truncated due to length")
                    display_error("Response truncated. Context limit reached.")
                    return {
                        "success": False,
                        "error": "Context length limit reached",
                        "state": self.state.get_summary(),
                    }

                else:
                    # Unknown finish reason
                    logger.warning(f"Unknown finish reason: {response.finish_reason}")
                    return {
                        "success": False,
                        "error": f"Unexpected finish reason: {response.finish_reason}",
                        "state": self.state.get_summary(),
                    }

            # Reached iteration limit
            logger.warning(f"Reached iteration limit: {self.state.max_iterations}")
            display_error(
                f"Reached maximum iteration limit ({self.state.max_iterations}). Task may be incomplete."
            )
            
            return {
                "success": False,
                "error": "Iteration limit reached",
                "state": self.state.get_summary(),
            }

        except KeyboardInterrupt:
            logger.info("Task interrupted by user")
            return {
                "success": False,
                "error": "Interrupted by user",
                "state": self.state.get_summary(),
            }
        except Exception as e:
            logger.exception("Unexpected error in agent loop")
            display_error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": str(e),
                "state": self.state.get_summary(),
            }

    def _execute_tools(self, tool_calls: List[ToolCall]) -> List[Any]:
        """
        Execute a list of tool calls.

        Args:
            tool_calls: List of tool calls from the model

        Returns:
            List of tool execution results
        """
        results = []

        for tool_call in tool_calls:
            # Use enhanced display if available
            if self.display:
                self.display.show_tool_call(tool_call.name, tool_call.arguments)
            else:
                display_tool_call(tool_call.name, tool_call.arguments)

            try:
                # Execute tool
                result = self.tool_registry.execute(tool_call.name, **tool_call.arguments)

                # Record in state
                self.state.add_tool_call(tool_call.name, tool_call.arguments, result)

                # Track file changes
                if tool_call.name in ["write_file", "edit_file"]:
                    if isinstance(result, dict) and result.get("success"):
                        path = result.get("path", "")
                        action = result.get("action", "modified")
                        if action == "created":
                            self.state.record_file_change(path, "created")
                        else:
                            self.state.record_file_change(path, "modified")

                # Track commands
                if tool_call.name == "run_command":
                    if isinstance(result, dict):
                        cmd = result.get("command", "")
                        if cmd:
                            self.state.record_command(cmd)

                        # Track test results if it looks like a test command
                        if any(test_word in cmd.lower() for test_word in ["test", "pytest", "npm test"]):
                            if result.get("success"):
                                self.state.last_test_result = {"status": "passed"}
                            else:
                                self.state.last_test_result = {"status": "failed"}

                # Show result (only errors in enhanced mode)
                if isinstance(result, dict) and "success" in result:
                    success = result.get("success", False)
                    msg = result.get("error") if not success else result.get("message")
                    
                    if self.display:
                        self.display.show_tool_result(success, msg)
                    else:
                        display_tool_result(success, msg)
                else:
                    if not self.display:
                        display_tool_result(True)

                results.append(result)

            except Exception as e:
                logger.error(f"Tool execution error: {tool_call.name} - {e}")
                error_result = {
                    "success": False,
                    "error": str(e),
                }
                
                if self.display:
                    self.display.show_tool_result(False, str(e))
                else:
                    display_tool_result(False, str(e))
                    
                results.append(error_result)

        return results
