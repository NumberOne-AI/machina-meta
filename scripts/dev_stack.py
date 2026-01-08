#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""Development stack management script.

Manages the development environment with docker compose.
Supports modes: up (full stack), down (stop all), status (check services).
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def run_command(
    cmd: list[str],
    check: bool = True,
    cwd: Path | None = None,
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a shell command and return the result.

    Args:
        cmd: Command to execute as list of strings
        check: Whether to raise exception on non-zero exit code
        cwd: Working directory for command execution
        capture_output: Whether to capture stdout/stderr

    Returns:
        CompletedProcess with stdout/stderr captured as text
    """
    return subprocess.run(  # noqa: S603
        cmd,
        check=check,
        text=True,
        capture_output=capture_output,
        cwd=cwd,
    )


def check_service_status(
    workspace_root: Path, wait_for_health_complete: bool = False
) -> tuple[bool, str, list[str]]:
    """Check if any services are unhealthy or exited.

    Args:
        workspace_root: Path to workspace root directory
        wait_for_health_complete: If True, also consider "(health: starting)" as not ready

    Returns:
        Tuple of (all_healthy, status_output, failed_services)
    """
    result = run_command(
        ["docker", "compose", "ps"],
        check=False,
        cwd=workspace_root,
    )
    output = result.stdout

    # Check for unhealthy or exited services and extract their names
    failed_services = []
    for line in output.split("\n"):
        is_unhealthy = "Exit" in line or "unhealthy" in line
        is_starting = wait_for_health_complete and "(health: starting)" in line

        if is_unhealthy or is_starting:
            # Extract service name (first column before whitespace)
            parts = line.split()
            if parts:
                service_name = parts[0].replace("machina-meta-", "").replace("-1", "")
                failed_services.append(service_name)

    has_issues = len(failed_services) > 0

    return (not has_issues, output, failed_services)


def get_service_logs(
    workspace_root: Path, service_names: list[str] | None = None, tail: int = 50
) -> str:
    """Get logs for specific services or all services.

    Args:
        workspace_root: Path to workspace root directory
        service_names: List of service names to get logs for (None = all)
        tail: Number of lines to show per service

    Returns:
        Combined log output
    """
    cmd = ["docker", "compose", "logs", f"--tail={tail}"]
    if service_names:
        cmd.extend(service_names)

    result = run_command(cmd, check=False, cwd=workspace_root)
    return result.stdout


def analyze_logs(logs: str) -> str:
    """Analyze logs and provide troubleshooting guidance.

    Args:
        logs: Docker compose logs output

    Returns:
        Analysis message with troubleshooting steps
    """
    lines = logs.split("\n")

    # Extract unique error patterns
    errors = []
    for line in lines:
        lower = line.lower()
        if any(
            keyword in lower
            for keyword in ["error:", "failed", "exception", "fatal", "cannot"]
        ):
            # Clean up container prefix and extract meaningful error
            if "|" in line:
                error_msg = line.split("|", 1)[1].strip()
                if error_msg and error_msg not in errors:
                    errors.append(error_msg)

    if not errors:
        return "No specific errors found in logs. Check full logs with: docker compose logs <service>"

    # Build analysis message
    msg = ["🔍 Error Analysis:", ""]
    for i, error in enumerate(errors[:5], 1):  # Show first 5 unique errors
        msg.append(f"{i}. {error}")

    msg.append("")
    msg.append("💡 Troubleshooting tips:")
    msg.append("  • View full logs: docker compose logs <service-name>")
    msg.append("  • Check .env files exist and have required values")
    msg.append("  • Restart from clean state: docker compose down && docker compose up")

    return "\n".join(msg)


def wait_for_health_checks(workspace_root: Path, max_wait: int = 60) -> bool:
    """Wait for all service health checks to complete.

    Args:
        workspace_root: Path to workspace root directory
        max_wait: Maximum seconds to wait

    Returns:
        True if all services are healthy
    """
    print(f"Waiting for health checks to complete (max {max_wait}s)...")
    start_time = time.time()

    while time.time() - start_time < max_wait:
        # Check with wait_for_health_complete=True to wait for all health checks to finish
        all_healthy, _, failed_services = check_service_status(
            workspace_root, wait_for_health_complete=True
        )

        if all_healthy:
            elapsed = int(time.time() - start_time)
            print(f"✅ All services healthy after {elapsed}s")
            return True

        # Wait a bit before checking again
        time.sleep(3)

    return False


def dev_up(workspace_root: Path) -> int:
    """Start full stack in production mode (databases + frontend + backend).

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print("Starting full stack in production mode...")
    print()

    # Start all services with prod profile (quiet by default)
    result = run_command(
        ["docker", "compose", "--profile", "prod", "up", "-d", "--build"],
        check=False,
        cwd=workspace_root,
    )

    # Show docker output if command failed
    if result.returncode != 0:
        print("❌ ERROR: docker compose up failed")
        print()
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return 1

    # Wait 15 seconds for services to initialize
    print("Waiting for services to initialize...")
    time.sleep(15)

    # Wait for health checks with timeout (90s to allow for start_period + retries)
    if not wait_for_health_checks(workspace_root, max_wait=90):
        # Health checks timed out or failed
        all_healthy, status_output, failed_services = check_service_status(
            workspace_root
        )

        print()
        print(f"❌ ERROR: {len(failed_services)} service(s) failed to start")
        print()
        print("Service Status:")
        print(status_output)
        print()

        # Get logs for failed services
        print(f"Analyzing logs for failed services: {', '.join(failed_services)}")
        print()
        logs = get_service_logs(workspace_root, failed_services, tail=100)
        print(logs)
        print()

        # Analyze and provide guidance
        analysis = analyze_logs(logs)
        print(analysis)
        return 1

    print()
    print("Services:")
    print("  • Frontend:  http://localhost:3000")
    print("  • Backend:   http://localhost:8000")
    print("  • Neo4j:     http://localhost:7474")
    print("  • Qdrant:    http://localhost:6333")
    print()
    print("Run 'just dev-status' to check service health")

    return 0


def dev_down(workspace_root: Path) -> int:
    """Stop all development services.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print("Stopping all services...")

    # Stop all services with prod profile
    result = run_command(
        ["docker", "compose", "--profile", "prod", "down"],
        check=False,
        cwd=workspace_root,
    )

    if result.returncode != 0:
        print("Error stopping services:")
        print(result.stderr)
        return 1

    print("Stopping any legacy services...")

    # Stop legacy machina-med project (ignore errors)
    run_command(
        ["docker", "compose", "-p", "machina-med", "down"],
        check=False,
        cwd=workspace_root,
    )

    return 0


def check_http_endpoint(url: str, timeout: float = 2.0) -> bool:
    """Check if an HTTP endpoint is responding.

    Args:
        url: URL to check
        timeout: Request timeout in seconds

    Returns:
        True if endpoint responds with 2xx or 3xx status
    """
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return 200 <= response.status < 400
    except Exception:
        return False


def check_docker_container(name_pattern: str) -> bool:
    """Check if a docker container is running.

    Args:
        name_pattern: Pattern to match container name

    Returns:
        True if container is running
    """
    result = run_command(
        ["docker", "ps", "--format", "{{.Names}}"],
        check=False,
    )
    return name_pattern in result.stdout


def get_service_status(workspace_root: Path) -> list[dict]:
    """Get status of all development services.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        List of service status dictionaries
    """
    services = []

    # Frontend
    services.append(
        {
            "category": "Frontend",
            "service": "Frontend",
            "type": "Next.js",
            "ports": "3000",
            "running": check_http_endpoint("http://localhost:3000"),
            "url": "http://localhost:3000",
        }
    )

    # Backend API
    services.append(
        {
            "category": "Backend",
            "service": "Backend API",
            "type": "FastAPI",
            "ports": "8000",
            "running": check_http_endpoint("http://localhost:8000/docs"),
            "url": "http://localhost:8000",
        }
    )

    # Medical Catalog
    services.append(
        {
            "category": "Backend",
            "service": "Medical Catalog",
            "type": "FastAPI",
            "ports": "8001",
            "running": check_http_endpoint("http://localhost:8001/health"),
            "url": "http://localhost:8001",
        }
    )

    # PostgreSQL
    services.append(
        {
            "category": "Database",
            "service": "PostgreSQL",
            "type": "Relational",
            "ports": "5432",
            "running": check_docker_container("postgres"),
            "url": "localhost:5432",
        }
    )

    # Neo4j
    services.append(
        {
            "category": "Database",
            "service": "Neo4j",
            "type": "Graph",
            "ports": "7474, 7687",
            "running": check_docker_container("neo4j"),
            "url": "http://localhost:7474",
        }
    )

    # Redis
    services.append(
        {
            "category": "Infrastructure",
            "service": "Redis",
            "type": "Cache/Pub-Sub",
            "ports": "6379",
            "running": check_docker_container("redis"),
            "url": "localhost:6379",
        }
    )

    # Qdrant
    services.append(
        {
            "category": "Infrastructure",
            "service": "Qdrant",
            "type": "Vector Search",
            "ports": "6333",
            "running": check_docker_container("qdrant"),
            "url": "http://localhost:6333",
        }
    )

    # RedisInsight (optional)
    services.append(
        {
            "category": "Dev Tools",
            "service": "RedisInsight",
            "type": "Redis UI",
            "ports": "5540",
            "running": check_docker_container("redisinsight"),
            "url": "http://localhost:5540",
            "optional": True,
        }
    )

    return services


def format_status_markdown(services: list[dict]) -> str:
    """Format service status as markdown table.

    Args:
        services: List of service status dictionaries

    Returns:
        Markdown table string
    """
    lines = [
        "# Development Stack Status",
        "",
        "| Category | Service | Type | Port(s) | Status | URL |",
        "|----------|---------|------|---------|--------|-----|",
    ]

    for svc in services:
        is_optional = svc.get("optional", False)
        if is_optional and not svc["running"]:
            status = "⚪ Optional"
            url = "-"
        elif svc["running"]:
            status = "✅ Running"
            url = svc["url"]
        else:
            status = "❌ Stopped"
            url = "-"

        lines.append(
            f"| {svc['category']} | {svc['service']} | {svc['type']} | "
            f"{svc['ports']} | {status} | {url} |"
        )

    return "\n".join(lines)


def format_status_json(services: list[dict]) -> str:
    """Format service status as JSON.

    Args:
        services: List of service status dictionaries

    Returns:
        JSON string
    """
    return json.dumps(services, indent=2)


def dev_status(workspace_root: Path, output_format: str = "markdown") -> int:
    """Check status of all development services.

    Args:
        workspace_root: Path to workspace root directory
        output_format: Output format (markdown or json)

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    services = get_service_status(workspace_root)

    if output_format == "json":
        print(format_status_json(services))
    else:  # markdown
        print(format_status_markdown(services))

    # Return non-zero if any required service is down
    required_down = any(
        not svc["running"] and not svc.get("optional", False) for svc in services
    )
    return 1 if required_down else 0


def main() -> int:
    """Main entry point for dev stack management."""
    parser = argparse.ArgumentParser(
        description="Development stack management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start full stack (production mode)
  %(prog)s up

  # Stop all services
  %(prog)s down

  # Check service status (markdown table)
  %(prog)s status

  # Check service status (JSON output)
  %(prog)s status --format json
        """,
    )

    parser.add_argument(
        "command",
        choices=["up", "down", "status"],
        help="Command to execute: up (full stack), down (stop all), status (check services)",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format for status command (default: markdown)",
    )

    args = parser.parse_args()

    # Get workspace root (script is in scripts/ subdirectory)
    workspace_root = Path(__file__).parent.parent

    # Execute requested command
    if args.command == "up":
        return dev_up(workspace_root)
    elif args.command == "down":
        return dev_down(workspace_root)
    elif args.command == "status":
        return dev_status(workspace_root, args.format)
    else:
        parser.error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
