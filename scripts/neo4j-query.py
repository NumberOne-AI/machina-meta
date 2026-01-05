#!/usr/bin/env python3
"""
Neo4j Query Tool - Run Cypher queries against local Neo4j instance.

Automatically reads connection details from docker-compose.yaml and .env files.

Usage:
    ./scripts/neo4j-query.py "MATCH (n) RETURN count(n) LIMIT 10"
    ./scripts/neo4j-query.py --file query.cypher
    just neo4j-query "MATCH (o:ObservationValue) RETURN count(o)"
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests
import yaml


def find_workspace_root() -> Path:
    """Find the machina-meta workspace root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "docker-compose.yaml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find machina-meta workspace root")


def parse_neo4j_auth(auth_string: str) -> tuple[str, str]:
    """Parse NEO4J_AUTH environment variable (format: username/password)."""
    if "/" in auth_string:
        username, password = auth_string.split("/", 1)
        return username, password
    return "neo4j", auth_string


def load_neo4j_config() -> dict[str, Any]:
    """Load Neo4j connection details from docker-compose.yaml."""
    workspace_root = find_workspace_root()
    compose_file = workspace_root / "docker-compose.yaml"

    with open(compose_file) as f:
        compose_data = yaml.safe_load(f)

    neo4j_service = compose_data.get("services", {}).get("neo4j", {})
    environment = neo4j_service.get("environment", [])

    # Parse environment variables
    env_dict = {}
    for item in environment:
        if isinstance(item, str) and "=" in item:
            key, value = item.split("=", 1)
            env_dict[key] = value
        elif isinstance(item, dict):
            env_dict.update(item)

    # Extract auth credentials
    neo4j_auth = env_dict.get("NEO4J_AUTH", "neo4j/neo4j")
    username, password = parse_neo4j_auth(neo4j_auth)

    # Extract ports
    ports = neo4j_service.get("ports", [])
    http_port = 7474  # default
    for port_mapping in ports:
        if isinstance(port_mapping, str):
            if "7474" in port_mapping:
                host_port = port_mapping.split(":")[0]
                http_port = int(host_port)
                break

    return {
        "host": "localhost",
        "http_port": http_port,
        "username": username,
        "password": password,
    }


def run_cypher_query(query: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    """Execute a Cypher query against Neo4j HTTP API."""
    url = f"http://{config['host']}:{config['http_port']}/db/neo4j/tx/commit"

    payload = {
        "statements": [
            {
                "statement": query,
                "resultDataContents": ["row", "graph"],
            }
        ]
    }

    response = requests.post(
        url,
        auth=(config["username"], config["password"]),
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )

    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        sys.exit(1)

    data = response.json()

    # Check for Neo4j errors
    if data.get("errors"):
        for error in data["errors"]:
            print(f"Neo4j Error: {error.get('message')}", file=sys.stderr)
        sys.exit(1)

    return data.get("results", [{}])[0].get("data", [])


def format_results(results: list[dict[str, Any]], output_format: str) -> str:
    """Format query results for display."""
    if output_format == "json":
        return json.dumps(results, indent=2)

    elif output_format == "rows":
        if not results:
            return "No results"

        output_lines = []
        for item in results:
            row = item.get("row", [])
            output_lines.append(json.dumps(row))
        return "\n".join(output_lines)

    elif output_format == "count":
        if results and len(results[0].get("row", [])) == 1:
            return str(results[0]["row"][0])
        return str(len(results))

    else:  # table
        if not results:
            return "No results"

        # Extract column headers from first result's metadata
        first_result = results[0]
        columns = [f"col{i}" for i in range(len(first_result.get("row", [])))]

        # Build table
        output_lines = []
        output_lines.append(" | ".join(columns))
        output_lines.append("-|-".join(["-" * len(col) for col in columns]))

        for item in results:
            row = item.get("row", [])
            output_lines.append(" | ".join(str(val) for val in row))

        return "\n".join(output_lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Cypher queries against local Neo4j instance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Count all nodes
  %(prog)s "MATCH (n) RETURN count(n)"

  # Count ObservationValue nodes
  %(prog)s "MATCH (o:ObservationValue) RETURN count(o) as count"

  # Get first 10 observation types
  %(prog)s "MATCH (t:ObservationType) RETURN t.name LIMIT 10"

  # Read query from file
  %(prog)s --file query.cypher

  # Output as JSON
  %(prog)s --format json "MATCH (n) RETURN n LIMIT 5"
        """,
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Cypher query to execute",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        help="Read query from file",
    )
    parser.add_argument(
        "--format",
        choices=["table", "rows", "json", "count"],
        default="rows",
        help="Output format (default: rows)",
    )

    args = parser.parse_args()

    # Get query from args or file
    if args.file:
        query = args.file.read_text().strip()
    elif args.query:
        query = args.query
    else:
        parser.error("Either query or --file must be provided")

    try:
        # Load configuration
        config = load_neo4j_config()

        # Run query
        results = run_cypher_query(query, config)

        # Format and print results
        output = format_results(results, args.format)
        print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
