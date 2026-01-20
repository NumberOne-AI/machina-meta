#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["tabulate"]
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
from dataclasses import dataclass
from pathlib import Path

from tabulate import tabulate


@dataclass
class CheckResult:
    """Result of a single sanity check."""

    name: str
    passed: bool
    message: str
    details: str = ""


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


def get_qdrant_url(workspace_root: Path) -> str | None:
    """Get Qdrant URL from medical-catalog configuration.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        Qdrant REST API URL or None if unable to retrieve
    """
    catalog_path = workspace_root / "repos" / "medical-catalog"
    try:
        result = run_command(
            ["just", "get-qdrant-url"],
            check=False,
            cwd=catalog_path,
        )
        if result.returncode != 0:
            return None
        config = json.loads(result.stdout)
        return config.get("rest_api")
    except Exception:
        return None


def get_qdrant_volume_name(workspace_root: Path) -> str | None:
    """Get the Qdrant storage volume name from docker-compose configuration.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        Volume name or None if unable to determine
    """
    try:
        # Get docker compose config and look for qdrant_storage volume
        result = run_command(
            ["docker", "compose", "config", "--format", "json"],
            check=False,
            cwd=workspace_root,
        )
        if result.returncode != 0:
            return None

        config = json.loads(result.stdout)
        volumes = config.get("volumes", {})

        # Look for qdrant_storage volume and get its full name
        for volume_name, volume_config in volumes.items():
            if "qdrant" in volume_name.lower() and "storage" in volume_name.lower():
                # Docker Compose uses the volume name as defined, potentially with project prefix
                # Get the actual volume name from the config
                return volume_config.get("name", volume_name)

        return None
    except Exception:
        return None


def check_qdrant_volume_exists(workspace_root: Path) -> bool:
    """Check if the Qdrant storage volume already exists.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        True if volume exists, False if it needs to be created
    """
    volume_name = get_qdrant_volume_name(workspace_root)
    if not volume_name:
        return False

    try:
        result = run_command(
            ["docker", "volume", "inspect", volume_name],
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def restore_qdrant_snapshots(workspace_root: Path) -> bool:
    """Restore Qdrant snapshots if catalog is empty.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        True if restore was successful or not needed
    """
    catalog_path = workspace_root / "repos" / "medical-catalog"
    snapshots_path = catalog_path / "snapshots"

    # Check if snapshots directory exists
    if not snapshots_path.exists():
        print("⚠️  No snapshots directory found, skipping restore")
        return True

    # Check if there are any snapshot files
    snapshot_files = list(snapshots_path.glob("*.snapshot"))
    if not snapshot_files:
        print("⚠️  No snapshot files found, skipping restore")
        return True

    print(f"Found {len(snapshot_files)} snapshot files, restoring...")

    # Run snapshot-restore-all via justfile
    result = run_command(
        ["just", "snapshot-restore-all"],
        check=False,
        cwd=catalog_path,
        capture_output=False,  # Show output to user
    )

    if result.returncode != 0:
        print("❌ Failed to restore snapshots")
        return False

    print("✅ Snapshots restored successfully")
    return True


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


# =============================================================================
# Sanity Check Functions
# =============================================================================


def check_service_status_test(workspace_root: Path) -> CheckResult:
    """Check 1: Service status via dev_stack.py status logic.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        CheckResult with service status summary
    """
    services = get_service_status(workspace_root)
    running = sum(1 for s in services if s["running"])
    total = len(services)
    optional_count = sum(1 for s in services if s.get("optional", False))
    required_running = sum(
        1 for s in services if s["running"] and not s.get("optional", False)
    )
    required_total = total - optional_count

    all_required_running = required_running == required_total
    passed = all_required_running

    # Build details showing each service
    details_lines = []
    for svc in services:
        status_icon = "✅" if svc["running"] else "❌"
        optional_tag = " (optional)" if svc.get("optional", False) else ""
        details_lines.append(f"  {status_icon} {svc['service']}{optional_tag}")

    return CheckResult(
        name="Service Status",
        passed=passed,
        message=f"{running}/{total} services running ({required_running}/{required_total} required)",
        details="\n".join(details_lines),
    )


def check_container_status(workspace_root: Path) -> CheckResult:
    """Check 2: Container status via docker compose ps.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        CheckResult with container status summary
    """
    result = run_command(
        ["docker", "compose", "ps", "--format", "json"],
        check=False,
        cwd=workspace_root,
    )

    if result.returncode != 0:
        return CheckResult(
            name="Container Status",
            passed=False,
            message="Failed to query containers",
            details=result.stderr or "docker compose ps failed",
        )

    # Parse JSON output (one JSON object per line)
    containers = []
    for line in result.stdout.strip().split("\n"):
        if line:
            try:
                containers.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    if not containers:
        return CheckResult(
            name="Container Status",
            passed=False,
            message="No containers found",
            details="No machina-meta containers are running",
        )

    running = sum(1 for c in containers if c.get("State") == "running")
    total = len(containers)
    passed = running == total

    details_lines = []
    for c in containers:
        name = c.get("Name", "unknown")
        state = c.get("State", "unknown")
        status = c.get("Status", "")
        icon = "✅" if state == "running" else "❌"
        details_lines.append(f"  {icon} {name}: {status}")

    return CheckResult(
        name="Container Status",
        passed=passed,
        message=f"{running}/{total} containers running",
        details="\n".join(details_lines),
    )


def check_health_checks(workspace_root: Path) -> CheckResult:
    """Check 3: Docker health check status for all containers.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        CheckResult with health check summary
    """
    # Get container IDs for machina-meta containers
    result = run_command(
        ["docker", "ps", "-q", "--filter", "name=machina-meta"],
        check=False,
    )

    if result.returncode != 0 or not result.stdout.strip():
        return CheckResult(
            name="Health Checks",
            passed=False,
            message="No containers found",
            details="No machina-meta containers are running",
        )

    container_ids = result.stdout.strip().split("\n")

    # Inspect each container for health status
    health_results = []
    for cid in container_ids:
        inspect_result = run_command(
            [
                "docker",
                "inspect",
                "--format",
                "{{.Name}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}",
                cid,
            ],
            check=False,
        )
        if inspect_result.returncode == 0:
            output = inspect_result.stdout.strip()
            if "|" in output:
                name, status = output.split("|", 1)
                name = name.lstrip("/")
                health_results.append((name, status))

    healthy = sum(1 for _, status in health_results if status in ("healthy", "no-healthcheck"))
    total = len(health_results)
    passed = healthy == total

    details_lines = []
    for name, status in health_results:
        if status == "healthy":
            icon = "✅"
        elif status == "no-healthcheck":
            icon = "⚪"
        else:
            icon = "❌"
        details_lines.append(f"  {icon} {name}: {status}")

    return CheckResult(
        name="Health Checks",
        passed=passed,
        message=f"{healthy}/{total} healthy",
        details="\n".join(details_lines),
    )


def check_resource_usage(workspace_root: Path) -> CheckResult:
    """Check 4: Resource usage via docker stats.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        CheckResult with resource usage summary
    """
    result = run_command(
        [
            "docker",
            "stats",
            "--no-stream",
            "--format",
            "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}",
        ],
        check=False,
    )

    if result.returncode != 0:
        return CheckResult(
            name="Resource Usage",
            passed=False,
            message="Failed to query stats",
            details=result.stderr or "docker stats failed",
        )

    # Parse stats output and filter for machina containers
    stats = []
    for line in result.stdout.strip().split("\n"):
        if "machina" in line.lower():
            parts = line.split("|")
            if len(parts) == 3:
                stats.append(
                    {"name": parts[0], "cpu": parts[1], "memory": parts[2]}
                )

    if not stats:
        return CheckResult(
            name="Resource Usage",
            passed=True,
            message="No machina containers found",
            details="No containers to report",
        )

    # Calculate totals (just informational, always passes if we got stats)
    details_lines = []
    for s in stats:
        details_lines.append(f"  {s['name']}: CPU {s['cpu']}, Mem {s['memory']}")

    return CheckResult(
        name="Resource Usage",
        passed=True,
        message=f"{len(stats)} containers monitored",
        details="\n".join(details_lines),
    )


def check_volume_status(workspace_root: Path) -> CheckResult:
    """Check 5: Docker volume status.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        CheckResult with volume status summary
    """
    result = run_command(
        ["docker", "volume", "ls", "--format", "{{.Name}}"],
        check=False,
    )

    if result.returncode != 0:
        return CheckResult(
            name="Volume Status",
            passed=False,
            message="Failed to query volumes",
            details=result.stderr or "docker volume ls failed",
        )

    # Filter for machina volumes
    volumes = [v for v in result.stdout.strip().split("\n") if "machina" in v.lower()]

    if not volumes:
        return CheckResult(
            name="Volume Status",
            passed=False,
            message="No machina volumes found",
            details="Expected volumes for postgres, neo4j, redis, qdrant",
        )

    # Check for expected volumes
    expected_patterns = ["postgres", "neo4j", "redis", "qdrant"]
    found_patterns = []
    for pattern in expected_patterns:
        if any(pattern in v.lower() for v in volumes):
            found_patterns.append(pattern)

    passed = len(found_patterns) >= 3  # Allow some flexibility

    details_lines = [f"  • {v}" for v in volumes[:10]]  # Show first 10
    if len(volumes) > 10:
        details_lines.append(f"  ... and {len(volumes) - 10} more")

    return CheckResult(
        name="Volume Status",
        passed=passed,
        message=f"{len(volumes)} volumes found",
        details="\n".join(details_lines),
    )


def check_endpoint_health(workspace_root: Path) -> CheckResult:
    """Check 6: HTTP endpoint health checks.

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        CheckResult with endpoint health summary
    """
    endpoints = [
        ("Backend API", "http://localhost:8000/api/v1/health"),
        ("Medical Catalog", "http://localhost:8001/health"),
        ("Qdrant", "http://localhost:6333/healthz"),
        ("Frontend", "http://localhost:3000"),
    ]

    results = []
    for name, url in endpoints:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as response:
                healthy = 200 <= response.status < 400
                results.append((name, healthy, f"HTTP {response.status}"))
        except urllib.error.URLError as e:
            results.append((name, False, str(e.reason)[:30]))
        except Exception as e:
            results.append((name, False, str(e)[:30]))

    healthy = sum(1 for _, h, _ in results if h)
    total = len(results)
    passed = healthy == total

    details_lines = []
    for name, is_healthy, msg in results:
        icon = "✅" if is_healthy else "❌"
        details_lines.append(f"  {icon} {name}: {msg}")

    return CheckResult(
        name="Endpoint Health",
        passed=passed,
        message=f"{healthy}/{total} endpoints healthy",
        details="\n".join(details_lines),
    )


def format_check_results_markdown(results: list[CheckResult]) -> str:
    """Format check results as a markdown table.

    Args:
        results: List of CheckResult objects

    Returns:
        Markdown table string
    """
    headers = ["#", "Check", "Status", "Result"]
    rows = []

    for i, result in enumerate(results, 1):
        status_icon = "✅ PASS" if result.passed else "❌ FAIL"
        rows.append([i, result.name, status_icon, result.message])

    table = tabulate(rows, headers=headers, tablefmt="pipe")

    # Calculate summary
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    summary_icon = "✅" if passed == total else "❌"

    output = [
        "# Docker Sanity Check Results",
        "",
        table,
        "",
        f"**Summary:** {summary_icon} {passed}/{total} checks passed",
    ]

    return "\n".join(output)


def format_check_results_json(results: list[CheckResult]) -> str:
    """Format check results as JSON.

    Args:
        results: List of CheckResult objects

    Returns:
        JSON string
    """
    data = {
        "checks": [
            {
                "name": r.name,
                "passed": r.passed,
                "message": r.message,
                "details": r.details,
            }
            for r in results
        ],
        "summary": {
            "passed": sum(1 for r in results if r.passed),
            "total": len(results),
            "all_passed": all(r.passed for r in results),
        },
    }
    return json.dumps(data, indent=2)


def dev_check(workspace_root: Path, output_format: str = "markdown", verbose: bool = False) -> int:
    """Run comprehensive sanity checks on the development stack.

    Performs 6 non-destructive verification tests:
    1. Service Status - Check if services are running
    2. Container Status - Docker compose container state
    3. Health Checks - Docker healthcheck status
    4. Resource Usage - CPU/memory consumption
    5. Volume Status - Data persistence volumes
    6. Endpoint Health - HTTP endpoint accessibility

    Args:
        workspace_root: Path to workspace root directory
        output_format: Output format (markdown or json)
        verbose: Show detailed output for each check

    Returns:
        Exit code (0 = all checks passed, 1 = some checks failed)
    """
    results: list[CheckResult] = []

    # Run all checks
    results.append(check_service_status_test(workspace_root))
    results.append(check_container_status(workspace_root))
    results.append(check_health_checks(workspace_root))
    results.append(check_resource_usage(workspace_root))
    results.append(check_volume_status(workspace_root))
    results.append(check_endpoint_health(workspace_root))

    # Format output
    if output_format == "json":
        print(format_check_results_json(results))
    else:
        print(format_check_results_markdown(results))

        # Show details if verbose
        if verbose:
            print("\n## Details\n")
            for result in results:
                status = "✅" if result.passed else "❌"
                print(f"### {status} {result.name}")
                print(f"{result.message}\n")
                if result.details:
                    print(f"```\n{result.details}\n```\n")

    # Return exit code
    all_passed = all(r.passed for r in results)
    return 0 if all_passed else 1


def dev_up(workspace_root: Path) -> int:
    """Start full stack in production mode (databases + frontend + backend).

    Args:
        workspace_root: Path to workspace root directory

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print("Starting full stack in production mode...")
    print()

    # Check if Qdrant volume exists before starting services
    volume_existed = check_qdrant_volume_exists(workspace_root)
    needs_snapshot_restore = not volume_existed

    if needs_snapshot_restore:
        print("📦 Qdrant volume does not exist - snapshots will be restored")
    else:
        print("✅ Qdrant volume exists - using existing data")

    # Start all services with dev profile (quiet by default)
    result = run_command(
        ["docker", "compose", "--profile", "dev", "up", "-d", "--build"],
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

    # Restore snapshots if this is a fresh Qdrant volume
    if needs_snapshot_restore:
        # Get Qdrant URL from configuration
        qdrant_url = get_qdrant_url(workspace_root)
        if not qdrant_url:
            print("⚠️  Could not get Qdrant URL from configuration, skipping snapshot restore")
        else:
            # Wait for Qdrant to be ready
            print("Waiting for Qdrant to be ready...")
            qdrant_ready = False
            for _ in range(30):  # Wait up to 30 seconds
                if check_http_endpoint(qdrant_url):
                    qdrant_ready = True
                    break
                time.sleep(1)

            if not qdrant_ready:
                print("⚠️  Qdrant did not become ready, skipping snapshot restore")
            else:
                print("📦 Restoring Qdrant snapshots...")
                if not restore_qdrant_snapshots(workspace_root):
                    print("❌ Failed to restore snapshots, continuing anyway...")
                else:
                    print("✅ Snapshots restored successfully")

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

    # Stop all services with dev profile
    result = run_command(
        ["docker", "compose", "--profile", "dev", "down"],
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
        Markdown table string with aligned columns
    """
    # Prepare table data
    headers = ["Category", "Service", "Type", "Port(s)", "Status", "URL"]
    rows = []

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

        rows.append([
            svc["category"],
            svc["service"],
            svc["type"],
            svc["ports"],
            status,
            url,
        ])

    # Format as markdown table with pipe format
    table = tabulate(rows, headers=headers, tablefmt="pipe")

    return f"# Development Stack Status\n\n{table}"


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

  # Run sanity checks (markdown table)
  %(prog)s check

  # Run sanity checks with verbose details
  %(prog)s check --verbose

  # Run sanity checks (JSON output)
  %(prog)s check --format json
        """,
    )

    parser.add_argument(
        "command",
        choices=["up", "down", "status", "check"],
        help="Command to execute: up (full stack), down (stop all), status (check services), check (sanity tests)",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format for status/check commands (default: markdown)",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for check command",
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
    elif args.command == "check":
        return dev_check(workspace_root, args.format, args.verbose)
    else:
        parser.error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
