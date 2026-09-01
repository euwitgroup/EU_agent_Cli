"""Test runner tools."""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class TestRunner:
    """Test execution and result parsing."""

    def __init__(self, workspace_dir: Path):
        """
        Initialize test runner.

        Args:
            workspace_dir: Root directory for test operations
        """
        self.workspace_dir = workspace_dir.resolve()
        self.detected_framework = self._detect_test_framework()
        logger.info(f"Test runner initialized: framework={self.detected_framework}")

    def _detect_test_framework(self) -> Optional[str]:
        """
        Detect test framework based on project files.

        Returns:
            Framework name or None
        """
        # Python test frameworks
        if (self.workspace_dir / "pytest.ini").exists() or \
           (self.workspace_dir / "pyproject.toml").exists():
            # Check if pytest is likely used
            pyproject = self.workspace_dir / "pyproject.toml"
            if pyproject.exists():
                content = pyproject.read_text()
                if "pytest" in content.lower():
                    return "pytest"

        # Node.js test frameworks
        package_json = self.workspace_dir / "package.json"
        if package_json.exists():
            try:
                import json
                content = json.loads(package_json.read_text())
                scripts = content.get("scripts", {})
                test_script = scripts.get("test", "")

                if "jest" in test_script.lower():
                    return "jest"
                elif "vitest" in test_script.lower():
                    return "vitest"
                elif "mocha" in test_script.lower():
                    return "mocha"
                else:
                    return "npm"  # Generic npm test
            except Exception:
                pass

        # PHP test framework
        if (self.workspace_dir / "phpunit.xml").exists() or \
           (self.workspace_dir / "phpunit.xml.dist").exists():
            return "phpunit"

        # Go test
        if list(self.workspace_dir.glob("*_test.go")):
            return "go"

        # Rust test
        if (self.workspace_dir / "Cargo.toml").exists():
            return "cargo"

        # Ruby test
        if (self.workspace_dir / "Rakefile").exists():
            return "rake"

        # Default fallback
        return None

    def get_test_command(self, specific_test: Optional[str] = None) -> Optional[str]:
        """
        Get the appropriate test command for the detected framework.

        Args:
            specific_test: Optional specific test file or pattern

        Returns:
            Test command string or None
        """
        if not self.detected_framework:
            return None

        if self.detected_framework == "pytest":
            cmd = "pytest"
            if specific_test:
                cmd += f" {specific_test}"
            return cmd

        elif self.detected_framework == "jest":
            cmd = "npm test"
            if specific_test:
                cmd += f" -- {specific_test}"
            return cmd

        elif self.detected_framework == "vitest":
            cmd = "npm test"
            if specific_test:
                cmd += f" {specific_test}"
            return cmd

        elif self.detected_framework == "mocha":
            cmd = "npm test"
            if specific_test:
                cmd += f" {specific_test}"
            return cmd

        elif self.detected_framework == "npm":
            return "npm test"

        elif self.detected_framework == "phpunit":
            cmd = "vendor/bin/phpunit"
            if specific_test:
                cmd += f" {specific_test}"
            return cmd

        elif self.detected_framework == "go":
            cmd = "go test"
            if specific_test:
                cmd += f" {specific_test}"
            else:
                cmd += " ./..."
            return cmd

        elif self.detected_framework == "cargo":
            cmd = "cargo test"
            if specific_test:
                cmd += f" {specific_test}"
            return cmd

        elif self.detected_framework == "rake":
            return "rake test"

        return None

    def parse_test_results(self, output: str, framework: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse test output to extract results.

        Args:
            output: Test command output
            framework: Test framework (uses detected if not specified)

        Returns:
            Dict with parsed test results
        """
        framework = framework or self.detected_framework

        if framework == "pytest":
            return self._parse_pytest_output(output)
        elif framework in ["jest", "vitest"]:
            return self._parse_jest_output(output)
        elif framework == "go":
            return self._parse_go_test_output(output)
        elif framework == "cargo":
            return self._parse_cargo_test_output(output)
        else:
            return self._parse_generic_output(output)

    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest output."""
        result = {
            "framework": "pytest",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
            "duration": None,
            "failures": [],
        }

        # Look for summary line like: "5 passed, 2 failed in 1.23s"
        summary_pattern = r"(\d+)\s+passed|(\d+)\s+failed|(\d+)\s+skipped|(\d+)\s+error"
        for match in re.finditer(summary_pattern, output):
            if match.group(1):
                result["passed"] = int(match.group(1))
            elif match.group(2):
                result["failed"] = int(match.group(2))
            elif match.group(3):
                result["skipped"] = int(match.group(3))
            elif match.group(4):
                result["errors"] = int(match.group(4))

        result["total"] = result["passed"] + result["failed"] + result["skipped"]

        # Extract duration
        duration_match = re.search(r"in\s+([\d.]+)s", output)
        if duration_match:
            result["duration"] = float(duration_match.group(1))

        # Extract failures
        if result["failed"] > 0:
            failure_pattern = r"FAILED\s+([\w/\.\:]+)"
            result["failures"] = re.findall(failure_pattern, output)

        return result

    def _parse_jest_output(self, output: str) -> Dict[str, Any]:
        """Parse Jest/Vitest output."""
        result = {
            "framework": "jest",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "duration": None,
            "failures": [],
        }

        # Look for summary like: "Tests: 2 failed, 8 passed, 10 total"
        passed_match = re.search(r"(\d+)\s+passed", output)
        failed_match = re.search(r"(\d+)\s+failed", output)
        total_match = re.search(r"(\d+)\s+total", output)

        if passed_match:
            result["passed"] = int(passed_match.group(1))
        if failed_match:
            result["failed"] = int(failed_match.group(1))
        if total_match:
            result["total"] = int(total_match.group(1))

        # Extract duration
        duration_match = re.search(r"Time:\s+([\d.]+)\s*s", output)
        if duration_match:
            result["duration"] = float(duration_match.group(1))

        return result

    def _parse_go_test_output(self, output: str) -> Dict[str, Any]:
        """Parse Go test output."""
        result = {
            "framework": "go",
            "passed": 0,
            "failed": 0,
            "total": 0,
            "duration": None,
            "failures": [],
        }

        # Count PASS and FAIL lines
        result["passed"] = len(re.findall(r"^PASS", output, re.MULTILINE))
        result["failed"] = len(re.findall(r"^FAIL", output, re.MULTILINE))
        result["total"] = result["passed"] + result["failed"]

        # Check for overall result
        if "FAIL" in output:
            result["failed"] = max(result["failed"], 1)

        return result

    def _parse_cargo_test_output(self, output: str) -> Dict[str, Any]:
        """Parse Cargo test output."""
        result = {
            "framework": "cargo",
            "passed": 0,
            "failed": 0,
            "total": 0,
            "duration": None,
            "failures": [],
        }

        # Look for summary like: "test result: ok. 5 passed; 0 failed"
        summary_match = re.search(r"(\d+)\s+passed;\s+(\d+)\s+failed", output)
        if summary_match:
            result["passed"] = int(summary_match.group(1))
            result["failed"] = int(summary_match.group(2))
            result["total"] = result["passed"] + result["failed"]

        return result

    def _parse_generic_output(self, output: str) -> Dict[str, Any]:
        """Parse generic test output."""
        result = {
            "framework": "generic",
            "passed": 0,
            "failed": 0,
            "total": 0,
            "duration": None,
        }

        # Try to find any numbers that might indicate test counts
        numbers = re.findall(r"\d+", output)
        if numbers:
            # Very basic heuristic
            result["total"] = int(numbers[0]) if numbers else 0

        # Check for common success/failure indicators
        if any(word in output.lower() for word in ["fail", "error", "failed"]):
            result["failed"] = 1
        elif any(word in output.lower() for word in ["pass", "ok", "success"]):
            result["passed"] = 1

        return result

    def format_test_results(self, results: Dict[str, Any]) -> str:
        """
        Format test results for display.

        Args:
            results: Parsed test results

        Returns:
            Formatted string
        """
        lines = []
        lines.append(f"Framework: {results.get('framework', 'unknown')}")

        passed = results.get("passed", 0)
        failed = results.get("failed", 0)
        skipped = results.get("skipped", 0)
        total = results.get("total", 0)

        if total > 0:
            lines.append(f"Total: {total} tests")

        if passed > 0:
            lines.append(f"✓ Passed: {passed}")
        if failed > 0:
            lines.append(f"✗ Failed: {failed}")
        if skipped > 0:
            lines.append(f"⊘ Skipped: {skipped}")

        duration = results.get("duration")
        if duration:
            lines.append(f"Duration: {duration}s")

        failures = results.get("failures", [])
        if failures:
            lines.append("\nFailed tests:")
            for failure in failures[:10]:  # Limit display
                lines.append(f"  - {failure}")
            if len(failures) > 10:
                lines.append(f"  ... and {len(failures) - 10} more")

        return "\n".join(lines)
