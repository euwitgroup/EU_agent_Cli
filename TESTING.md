# MyAgent Testing Documentation

## Test Coverage Summary

MyAgent has comprehensive test coverage across all core components with **128 passing tests**.

## Test Organization

### Configuration Tests (`test_config.py` - 7 tests)
- Settings initialization and defaults
- Provider/model selection and overrides
- API key retrieval for different providers
- Singleton pattern and reset functionality

### Agent Core Tests (`test_agent.py` - 21 tests)
- **AgentState**: Message management, tool call tracking, file changes, iteration limits
- **ContextManager**: Project detection, system prompts, user messages, tool result formatting
- **AgentLoop**: Initialization, tool execution, task completion, iteration limits

### Provider Tests (`test_providers.py` - 28 tests)
- **Base Models**: Message, ToolCall, ToolDefinition, GenerateResponse creation
- **OpenAI Provider**: Initialization, configuration validation, message/tool conversion
- **Anthropic Provider**: Initialization, configuration validation, message/tool conversion
- **Custom Provider**: Initialization with base URL, validation
- **ProviderRouter**: Provider creation, configuration validation, error handling

### Provider Utilities Tests (`test_provider_utils.py` - 12 tests)
- **Connection Testing**: Test provider connectivity, successful/failed connections
- **Model Listing**: Fetch available models from OpenAI, Anthropic, custom providers
- **Configuration Saving**: Save provider configs to .env, update existing configs
- **Error Handling**: Invalid providers, API errors, file system errors

### Permission Tests (`test_permissions.py` - 25 tests)
- Policy enums and categories
- Permission manager initialization and policies
- Permission checking (ALWAYS/ASK/NEVER policies)
- Command permission for safe/dangerous commands
- Path access control and traversal protection
- Caching and statistics
- Global manager singleton

### Tool Tests (`test_tools.py` - 35 tests)
- **ToolRegistry**: Registration, listing, execution
- **FilesystemTools**: Read/write/edit files, line ranges, binary files, path traversal protection
- **SearchTools**: Content search, case sensitivity, file finding
- **TerminalTools**: Command execution, success/failure, dangerous command detection
- **GitTools**: Initialization, git availability, repository checks
- **TestRunner**: Framework detection, command generation, output parsing (pytest, jest, etc.)
- **Tool Registration**: Complete registration and provider integration

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_agent.py
pytest tests/test_providers.py
pytest tests/test_provider_utils.py
pytest tests/test_tools.py
pytest tests/test_permissions.py
pytest tests/test_config.py
```

### Run With Coverage
```bash
pytest --cov=myagent tests/
```

### Run With Verbose Output
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_agent.py::TestAgentLoop::test_run_simple_task -v
pytest tests/test_provider_utils.py::TestProviderConnection -v
```

## Test Structure

Tests are organized by component:

```
tests/
├── __init__.py
├── test_agent.py          # Agent core tests
├── test_config.py         # Configuration tests  
├── test_permissions.py    # Permission system tests
├── test_providers.py      # Provider system tests
├── test_provider_utils.py # Provider management utilities tests
└── test_tools.py          # Tool system tests
```

## Test Fixtures

Common fixtures used across tests:
- `temp_workspace`: Temporary workspace directory for isolated testing
- `reset_settings`: Resets global settings before each test
- `reset_tool_registry`: Resets tool registry before each test
- `reset_permission_manager`: Resets permission manager before each test

## Mocking Strategy

- **Providers**: Mocked in agent tests to avoid requiring real API keys
- **External Commands**: Git and test runner tests handle both available and unavailable scenarios
- **File System**: Uses temporary directories for safe testing

## Test Quality Standards

All tests follow these principles:
1. **Isolation**: Each test is independent and doesn't affect others
2. **Clarity**: Test names clearly describe what is being tested
3. **Coverage**: Both happy paths and error cases are tested
4. **No External Dependencies**: Tests don't require API keys or external services
5. **Fast Execution**: Full test suite runs in ~12 seconds

## Continuous Testing

During development:
```bash
# Watch mode (if using pytest-watch)
ptw tests/

# Quick test run
pytest tests/ -q

# Test specific module during development
pytest tests/test_tools.py -v -k "filesystem"
```

## Test Categories

- **Unit Tests**: Test individual components in isolation (majority of tests)
- **Integration Tests**: Test component interactions (e.g., tool registration, agent loop with tools)
- **Mock Tests**: Tests using mocked dependencies (e.g., agent with mocked providers)

## Adding New Tests

When adding new functionality:

1. Add tests in the appropriate test file
2. Follow existing naming conventions: `test_<functionality>`
3. Use fixtures for common setup
4. Test both success and failure cases
5. Mock external dependencies
6. Run full test suite before committing

## Current Test Status

✅ **All 128 tests passing**
- Configuration: 7/7 ✓
- Agent Core: 21/21 ✓
- Providers: 28/28 ✓
- Provider Utils: 12/12 ✓
- Permissions: 25/25 ✓
- Tools: 35/35 ✓

## Future Testing Enhancements

Potential improvements:
- Add integration tests with real API calls (optional, requires API keys)
- Add performance benchmarks
- Add load testing for concurrent operations
- Add fuzzing tests for input validation
- Increase code coverage to 95%+
