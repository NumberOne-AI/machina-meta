#!/usr/bin/env python3
"""
Generate ROUTES.md from routes.json data.

This script reads the routes.json file and generates a comprehensive
markdown documentation file showing all API routes across all services.
"""

import json
from pathlib import Path
from typing import Any


def generate_routes_table(routes: list[dict[str, Any]]) -> str:
    """Generate markdown table from routes data."""
    lines = []

    # Table header
    lines.append("| Service | Port | Method | Path | Description | Example |")
    lines.append("|---------|------|--------|------|-------------|---------|")

    for route in routes:
        service = route["service"]
        port = route["port"]
        method = route["method"]
        path = route["path"]
        description = route["description"] or "(No description)"

        # Generate example based on method and port
        example = generate_example(service, port, method, path)

        # Escape pipe characters in description
        description = description.replace("|", "\\|")

        # Format table row
        lines.append(f"| {service} | {port} | {method} | {path} | {description} | {example} |")

    return "\n".join(lines)


def generate_example(service: str, port: int, method: str, path: str) -> str:
    """Generate example query for a route."""
    # For PAGE routes (Next.js pages), return browser example
    if method == "PAGE":
        return f"`http://localhost:{port}{path}`"

    # For API routes, generate curl example
    # Simplify path by removing parameters for example
    example_path = path

    # Replace path parameters with example values
    example_path = example_path.replace("{session_id}", "abc123")
    example_path = example_path.replace("{patient_id}", "pat-123")
    example_path = example_path.replace("{bookmark_id}", "bmk-456")
    example_path = example_path.replace("{allergy_id}", "alg-789")
    example_path = example_path.replace("{path:path}", "collections/info")

    if method in ["GET", "DELETE", "OPTIONS", "HEAD"]:
        return f"`curl http://localhost:{port}{example_path}`"
    elif method == "POST":
        return f"`curl -X POST http://localhost:{port}{example_path} -d '{{}}'`"
    elif method in ["PUT", "PATCH"]:
        return f"`curl -X {method} http://localhost:{port}{example_path} -d '{{}}'`"
    elif method == "WS":
        return f"`ws://localhost:{port}{example_path}`"
    else:
        return f"`curl http://localhost:{port}{example_path}`"


def generate_service_section(
    service_name: str, service_data: dict[str, Any]
) -> str:
    """Generate markdown section for a single service."""
    lines = []

    port = service_data["port"]
    files = service_data["files"]

    # Flatten routes from all files
    service_routes = []
    for file_path, file_data in files.items():
        for route in file_data["routes"]:
            service_routes.append({
                **route,
                "service": service_name,
                "port": port,
                "file_path": file_path
            })

    if not service_routes:
        return ""

    lines.append(f"## {service_name}")
    lines.append("")
    lines.append(f"**Port**: {port}")
    lines.append(f"**Total Routes**: {len(service_routes)}")
    lines.append("")

    # Group routes by type
    api_routes = [r for r in service_routes if r["method"] != "PAGE"]
    page_routes = [r for r in service_routes if r["method"] == "PAGE"]

    if api_routes:
        lines.append("### API Routes")
        lines.append("")
        lines.append(generate_routes_table(api_routes))
        lines.append("")

    if page_routes:
        lines.append("### Pages")
        lines.append("")
        lines.append(generate_routes_table(page_routes))
        lines.append("")

    return "\n".join(lines)


def generate_routes_md(data: dict[str, Any]) -> str:
    """Generate complete ROUTES.md content."""
    lines = []

    services = data["services"]
    service_names = sorted(services.keys())

    # Header
    lines.append("# API Routes Documentation")
    lines.append("")
    lines.append("Comprehensive listing of all API routes and pages across all services in the machina-meta workspace.")
    lines.append("")
    lines.append(f"**Generated**: {data['scan_date']}")
    lines.append(f"**Total Routes**: {data['total_routes']}")
    lines.append(f"**Services**: {', '.join(service_names)}")
    lines.append("")

    # Table of Contents
    lines.append("## Table of Contents")
    lines.append("")
    for service in service_names:
        lines.append(f"- [{service}](#{service})")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Service sections
    for service_name in service_names:
        service_data = services[service_name]
        section = generate_service_section(service_name, service_data)
        if section:
            lines.append(section)
            lines.append("---")
            lines.append("")

    # Statistics section
    lines.append("## Statistics")
    lines.append("")
    lines.append(f"- **Total Routes**: {data['total_routes']}")
    lines.append("")

    # Route counts by service
    lines.append("### Routes by Service")
    lines.append("")
    lines.append("| Service | Routes |")
    lines.append("|---------|--------|")

    for service_name in service_names:
        files = services[service_name]["files"]
        count = sum(len(file_data["routes"]) for file_data in files.values())
        lines.append(f"| {service_name} | {count} |")

    lines.append("")

    # Method distribution
    lines.append("### Routes by Method")
    lines.append("")
    lines.append("| Method | Count |")
    lines.append("|--------|-------|")

    method_counts = {}
    for service_data in services.values():
        for file_data in service_data["files"].values():
            for route in file_data["routes"]:
                method = route["method"]
                method_counts[method] = method_counts.get(method, 0) + 1

    for method in sorted(method_counts.keys()):
        count = method_counts[method]
        lines.append(f"| {method} | {count} |")

    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    # Determine workspace root (parent of scripts/)
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent

    # Read routes.json
    routes_json = workspace_root / "routes.json"
    if not routes_json.exists():
        print(f"Error: {routes_json} does not exist")
        print("Run scripts/scan_routes.py first to generate routes.json")
        return

    print(f"Reading {routes_json}...")
    with open(routes_json, encoding="utf-8") as f:
        data = json.load(f)

    print(f"Generating ROUTES.md from {data['total_routes']} routes...")

    # Generate markdown
    markdown = generate_routes_md(data)

    # Write ROUTES.md
    output_file = workspace_root / "ROUTES.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"✓ Generated {output_file}")
    print(f"  Total routes: {data['total_routes']}")
    print(f"  Services: {', '.join(sorted(data['services'].keys()))}")


if __name__ == "__main__":
    main()
