#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["requests", "pyyaml", "tabulate"]
# ///
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
from tabulate import tabulate


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


def run_cypher_query(query: str, config: dict[str, Any]) -> dict[str, Any]:
    """Execute a Cypher query against Neo4j HTTP API.

    Returns:
        dict with 'columns' (list of column names) and 'data' (list of row data)
    """
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

    result = data.get("results", [{}])[0]
    return {
        "columns": result.get("columns", []),
        "data": result.get("data", [])
    }


def format_results(result: dict[str, Any], output_format: str) -> str:
    """Format query results for display.

    Args:
        result: dict with 'columns' and 'data' keys
        output_format: "json", "rows", "markdown", "neo4j", or "count"

    Returns:
        formatted string output
    """
    columns = result.get("columns", [])
    data = result.get("data", [])

    if output_format == "neo4j":
        # Native Neo4j HTTP API response format
        return json.dumps(result, indent=2)

    elif output_format == "json":
        # Format as JSON array of objects with named fields
        rows = []
        for item in data:
            row_data = item.get("row", [])
            # Create object with column names as keys
            row_obj = {col: val for col, val in zip(columns, row_data)}
            rows.append(row_obj)
        return json.dumps(rows, indent=2)

    elif output_format == "rows":
        if not data:
            return "No results"

        output_lines = []
        for item in data:
            row = item.get("row", [])
            output_lines.append(json.dumps(row))
        return "\n".join(output_lines)

    elif output_format == "markdown":
        if not data:
            return "No results"

        # Extract rows
        rows = [item.get("row", []) for item in data]

        # Use tabulate to format as markdown table (pipe format)
        # Disable number parsing to preserve string values as-is
        return tabulate(rows, headers=columns, tablefmt="pipe", disable_numparse=True)

    elif output_format == "count":
        if data and len(data[0].get("row", [])) == 1:
            return str(data[0]["row"][0])
        return str(len(data))

    else:  # default: table (simple format)
        if not data:
            return "No results"

        # Build simple table
        output_lines = []
        output_lines.append(" | ".join(columns))
        output_lines.append("-|-".join(["-" * len(col) for col in columns]))

        for item in data:
            row = item.get("row", [])
            output_lines.append(" | ".join(str(val) for val in row))

        return "\n".join(output_lines)


def count_biomarkers(config: dict[str, Any]) -> dict[str, int]:
    """Count ObservationTypeNode and ObservationValueNode in Neo4j.

    Args:
        config: Neo4j connection configuration

    Returns:
        dict with 'type_count' and 'value_count'
    """
    type_results = run_cypher_query(
        "MATCH (n:ObservationTypeNode) RETURN count(n) as count", config
    )
    type_count = type_results["data"][0]["row"][0] if type_results["data"] else 0

    value_results = run_cypher_query(
        "MATCH (n:ObservationValueNode) RETURN count(n) as count", config
    )
    value_count = value_results["data"][0]["row"][0] if value_results["data"] else 0

    return {"type_count": type_count, "value_count": value_count}


def list_biomarkers(config: dict[str, Any], output_format: str = "markdown") -> str:
    """List all biomarkers with source documents and reference ranges.

    Returns biomarker data from uploaded documents including:
    - Source document filename
    - Document and observation dates
    - Biomarker name, value, unit
    - Reference range intervals

    Args:
        config: Neo4j connection configuration
        output_format: "json" or "markdown" (default)

    Returns:
        Formatted output string
    """
    query = """
    MATCH (d:DocumentReferenceNode)
    MATCH (ov:ObservationValueNode)
    WHERE ov.source_id = d.uuid
    MATCH (ov)-[:INSTANCE_OF]->(ot:ObservationTypeNode)
    OPTIONAL MATCH (ov)-[:MEASURED_WITH_RANGE]->(rr:ReferenceRangeNode)
    RETURN
      d.document_name AS document_filename,
      d.report_date AS document_date,
      ov.observed_at AS observation_date,
      ot.name AS biomarker_name,
      COALESCE(ov.value_numeric, ov.value_text) AS biomarker_value,
      ov.unit AS unit,
      rr.intervals_json AS reference_range
    ORDER BY d.report_date DESC, ot.name
    """

    result = run_cypher_query(query, config)
    return format_results(result, output_format)


def export_database(
    config: dict[str, Any],
    output_file: str | None = None,
    format: str = "json"
) -> None:
    """Export entire Neo4j database to stdout or file.

    Exports all nodes and relationships with their properties.
    Format:
    - JSON: {"nodes": [...], "relationships": [...]}
    - Cypher: CREATE statements for nodes and relationships

    Args:
        config: Neo4j connection configuration
        output_file: Output filename (None = stdout, default)
        format: "json" or "cypher" (default: json)
    """
    import time
    start_time = time.time()

    # Send progress to stderr so stdout is clean
    def log(msg: str) -> None:
        if output_file:
            print(msg)
        else:
            print(msg, file=sys.stderr)

    log(f"Exporting database ({format} format)...")
    if not output_file:
        log("Output: stdout")
    else:
        log(f"Output: {output_file}")
    log("This may take several minutes for large databases...")

    # Export nodes
    log("Exporting nodes...")
    nodes_query = """
    MATCH (n)
    RETURN
        id(n) as id,
        labels(n) as labels,
        properties(n) as properties
    """
    nodes_result = run_cypher_query(nodes_query, config)
    nodes = []
    for item in nodes_result["data"]:
        row = item["row"]
        nodes.append({
            "id": row[0],
            "labels": row[1],
            "properties": row[2]
        })

    log(f"  Exported {len(nodes):,} nodes")

    # Export relationships
    log("Exporting relationships...")
    rels_query = """
    MATCH (a)-[r]->(b)
    RETURN
        id(r) as id,
        type(r) as type,
        id(a) as start_id,
        id(b) as end_id,
        properties(r) as properties
    """
    rels_result = run_cypher_query(rels_query, config)
    relationships = []
    for item in rels_result["data"]:
        row = item["row"]
        relationships.append({
            "id": row[0],
            "type": row[1],
            "start_id": row[2],
            "end_id": row[3],
            "properties": row[4]
        })

    log(f"  Exported {len(relationships):,} relationships")

    elapsed = time.time() - start_time

    # Generate output content
    if format == "json":
        export_data = {
            "nodes": nodes,
            "relationships": relationships,
            "metadata": {
                "exported_at": time.time(),
                "node_count": len(nodes),
                "relationship_count": len(relationships),
                "export_time_seconds": elapsed
            }
        }
        content = json.dumps(export_data, indent=2)

    elif format == "cypher":
        # Generate Cypher CREATE statements
        lines = []
        lines.append("// Neo4j Database Export")
        lines.append(f"// Exported at: {time.time()}")
        lines.append(f"// Nodes: {len(nodes):,}, Relationships: {len(relationships):,}")
        lines.append("")

        # Create nodes with a map of internal id -> variable name
        lines.append("// Create nodes")
        for node in nodes:
            labels_str = ":".join(node["labels"])
            props_str = json.dumps(node["properties"])
            lines.append(f"CREATE (n{node['id']}:{labels_str} {props_str});")

        lines.append("")
        lines.append("// Create relationships")
        for rel in relationships:
            props_str = json.dumps(rel["properties"]) if rel["properties"] else "{}"
            lines.append(
                f"MATCH (a), (b) WHERE id(a) = {rel['start_id']} AND id(b) = {rel['end_id']} "
                f"CREATE (a)-[:{rel['type']} {props_str}]->(b);"
            )

        content = "\n".join(lines)

    else:
        raise ValueError(f"Unknown format: {format}. Use 'json' or 'cypher'")

    # Write to stdout or file
    if output_file:
        output_path = Path(output_file)
        output_path.write_text(content)
        file_size = output_path.stat().st_size / (1024 * 1024)  # MB

        log(f"\n✓ Export completed successfully!")
        log(f"  File: {output_path}")
        log(f"  Size: {file_size:.2f} MB")
        log(f"  Nodes: {len(nodes):,}")
        log(f"  Relationships: {len(relationships):,}")
        log(f"  Time: {elapsed:.2f}s")
    else:
        # Output to stdout (progress went to stderr)
        print(content)
        log(f"\n✓ Export completed successfully!")
        log(f"  Nodes: {len(nodes):,}")
        log(f"  Relationships: {len(relationships):,}")
        log(f"  Time: {elapsed:.2f}s")


def import_database(
    config: dict[str, Any],
    input_file: str = "neo4j_export.json",
    format: str = "json"
) -> None:
    """Import Neo4j database from file.

    Supports JSON and Cypher formats:
    - JSON: Import from JSON export (default)
    - Cypher: Import from Cypher script (runs CREATE statements)

    WARNING: This will add data to the current database. Clear the database first
    if you want a clean import.

    Args:
        config: Neo4j connection configuration
        input_file: Input filename (from current directory)
        format: "json" or "cypher" (default: json)
    """
    import time
    start_time = time.time()

    input_path = Path(input_file)
    if not input_path.exists():
        print(f"✗ Error: File not found: {input_file}")
        return

    print(f"Importing database from {input_file} ({format} format)...")
    print("WARNING: This adds to existing data. Clear database first for clean import.")
    print("This may take several minutes for large databases...")

    try:
        if format == "json":
            # Load JSON file
            data = json.loads(input_path.read_text())
            nodes = data.get("nodes", [])
            relationships = data.get("relationships", [])

            print(f"Loading {len(nodes):,} nodes and {len(relationships):,} relationships...")

            # Import nodes in batches
            batch_size = 1000
            id_mapping = {}  # Map old internal IDs to new UUIDs

            print("Importing nodes...")
            for i in range(0, len(nodes), batch_size):
                batch = nodes[i:i + batch_size]
                for node in batch:
                    labels_str = ":".join(node["labels"])
                    props_json = json.dumps(node["properties"])

                    # Create node and get its new internal ID
                    query = f"""
                    CREATE (n:{labels_str})
                    SET n = {props_json}
                    RETURN id(n) as new_id
                    """
                    result = run_cypher_query(query, config)
                    if result["data"]:
                        new_id = result["data"][0]["row"][0]
                        id_mapping[node["id"]] = new_id

                print(f"  Imported {min(i + batch_size, len(nodes)):,} / {len(nodes):,} nodes")

            print("Importing relationships...")
            for i in range(0, len(relationships), batch_size):
                batch = relationships[i:i + batch_size]
                for rel in batch:
                    start_new_id = id_mapping.get(rel["start_id"])
                    end_new_id = id_mapping.get(rel["end_id"])

                    if start_new_id is None or end_new_id is None:
                        continue  # Skip if nodes not found

                    props_json = json.dumps(rel["properties"]) if rel["properties"] else "{}"

                    query = f"""
                    MATCH (a), (b)
                    WHERE id(a) = {start_new_id} AND id(b) = {end_new_id}
                    CREATE (a)-[:{rel['type']} {props_json}]->(b)
                    """
                    run_cypher_query(query, config)

                print(f"  Imported {min(i + batch_size, len(relationships)):,} / {len(relationships):,} relationships")

            elapsed = time.time() - start_time
            print(f"\n✓ Import completed successfully!")
            print(f"  Nodes imported: {len(nodes):,}")
            print(f"  Relationships imported: {len(relationships):,}")
            print(f"  Time: {elapsed:.2f}s")

        elif format == "cypher":
            # Read Cypher file and execute line by line
            lines = input_path.read_text().split("\n")
            statements = [line.strip() for line in lines if line.strip() and not line.strip().startswith("//")]

            print(f"Executing {len(statements):,} Cypher statements...")

            for i, statement in enumerate(statements):
                if statement:
                    run_cypher_query(statement, config)

                if (i + 1) % 100 == 0:
                    print(f"  Executed {i + 1:,} / {len(statements):,} statements")

            elapsed = time.time() - start_time
            print(f"\n✓ Import completed successfully!")
            print(f"  Statements executed: {len(statements):,}")
            print(f"  Time: {elapsed:.2f}s")

        else:
            raise ValueError(f"Unknown format: {format}. Use 'json' or 'cypher'")

    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        raise


def clear_biomarkers(config: dict[str, Any]) -> dict[str, int]:
    """Clear all ObservationTypeNode and ObservationValueNode from Neo4j.

    This is commonly used when re-processing documents to validate extraction performance,
    ensuring a clean slate for testing biomarker extraction against the medical catalog.

    Args:
        config: Neo4j connection configuration

    Returns:
        dict with 'type_count' and 'value_count' of deleted nodes
    """
    # Count before deletion
    print("Counting ObservationTypeNode...")
    counts = count_biomarkers(config)
    type_count = counts["type_count"]
    value_count = counts["value_count"]

    print(f"Found {type_count} ObservationTypeNode nodes")
    print(f"Found {value_count} ObservationValueNode nodes")

    # Delete nodes
    if type_count > 0 or value_count > 0:
        print("Deleting ObservationTypeNode nodes...")
        run_cypher_query("MATCH (n:ObservationTypeNode) DETACH DELETE n", config)

        print("Deleting ObservationValueNode nodes...")
        run_cypher_query("MATCH (n:ObservationValueNode) DETACH DELETE n", config)

        print("Done! All observation nodes cleared.")
    else:
        print("No observation nodes to delete.")

    return {"type_count": type_count, "value_count": value_count}


def clear_all_data(config: dict[str, Any]) -> int:
    """Clear ALL nodes and relationships from Neo4j database.

    WARNING: This deletes EVERYTHING in the database. Use with caution!

    Args:
        config: Neo4j connection configuration

    Returns:
        Number of nodes deleted
    """
    print("WARNING: This will delete ALL data from the database!")
    print("Counting nodes...")

    count_result = run_cypher_query("MATCH (n) RETURN count(n) as count", config)
    total_count = count_result["data"][0]["row"][0] if count_result["data"] else 0

    print(f"Found {total_count:,} nodes")

    if total_count > 0:
        print("Deleting all nodes and relationships...")
        run_cypher_query("MATCH (n) DETACH DELETE n", config)
        print(f"✓ Deleted {total_count:,} nodes and all relationships")
    else:
        print("Database is already empty")

    return total_count


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

  # Output as JSON (array of objects with named fields)
  %(prog)s --format json "MATCH (n) RETURN n LIMIT 5"

  # Output as native Neo4j format
  %(prog)s --format neo4j "MATCH (n) RETURN n LIMIT 5"

  # Clear biomarkers (for testing/re-processing)
  %(prog)s --clear-biomarkers

  # Count biomarkers
  %(prog)s --count-biomarkers

  # List all biomarkers with source documents
  %(prog)s --list-biomarkers
  %(prog)s --list-biomarkers --format json

  # Export database (backup)
  %(prog)s --export-database  # outputs to stdout
  %(prog)s --export-database > backup.json  # redirect stdout to file
  %(prog)s --export-database --export-file backup.json  # write directly to file
  %(prog)s --export-database --export-format cypher > backup.cypher  # cypher format

  # Import database (restore)
  %(prog)s --import-database --import-file backup.json
  %(prog)s --import-database --import-file backup.json --import-format json

  # Clear all data
  %(prog)s --clear-all-data
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
        choices=["table", "rows", "json", "markdown", "neo4j", "count"],
        default="rows",
        help="Output format (default: rows)",
    )
    parser.add_argument(
        "--clear-biomarkers",
        action="store_true",
        help="Clear all ObservationTypeNode and ObservationValueNode (for testing)",
    )
    parser.add_argument(
        "--count-biomarkers",
        action="store_true",
        help="Count ObservationTypeNode and ObservationValueNode",
    )
    parser.add_argument(
        "--list-biomarkers",
        action="store_true",
        help="List all biomarkers with source documents and reference ranges",
    )
    parser.add_argument(
        "--export-database",
        action="store_true",
        help="Export entire database to file (backup)",
    )
    parser.add_argument(
        "--export-file",
        type=str,
        default=None,
        help="Export output filename (default: stdout)",
    )
    parser.add_argument(
        "--export-format",
        choices=["json", "cypher"],
        default="json",
        help="Export format: json or cypher (default: json)",
    )
    parser.add_argument(
        "--import-database",
        action="store_true",
        help="Import database from file (restore)",
    )
    parser.add_argument(
        "--import-file",
        type=str,
        default="neo4j_export.json",
        help="Import input filename (default: neo4j_export.json)",
    )
    parser.add_argument(
        "--import-format",
        choices=["json", "cypher"],
        default="json",
        help="Import format: json or cypher (default: json)",
    )
    parser.add_argument(
        "--clear-all-data",
        action="store_true",
        help="Clear ALL nodes and relationships (WARNING: deletes everything!)",
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_neo4j_config()

        # Handle count-biomarkers command
        if args.count_biomarkers:
            result = count_biomarkers(config)
            print(f"ObservationTypeNode: {result['type_count']}")
            print(f"ObservationValueNode: {result['value_count']}")
            return

        # Handle list-biomarkers command
        if args.list_biomarkers:
            output = list_biomarkers(config, args.format)
            print(output)
            return

        # Handle export-database command
        if args.export_database:
            export_database(config, args.export_file, args.export_format)
            return

        # Handle import-database command
        if args.import_database:
            import_database(config, args.import_file, args.import_format)
            return

        # Handle clear-all-data command
        if args.clear_all_data:
            clear_all_data(config)
            return

        # Handle clear-biomarkers command
        if args.clear_biomarkers:
            result = clear_biomarkers(config)
            print(
                f"\nDeleted {result['type_count']} type nodes and {result['value_count']} value nodes"
            )
            return

        # Get query from args or file
        if args.file:
            query = args.file.read_text().strip()
        elif args.query:
            query = args.query
        else:
            parser.error(
                "Either query, --file, --list-biomarkers, --count-biomarkers, "
                "--clear-biomarkers, --export-database, --import-database, "
                "or --clear-all-data must be provided"
            )

        # Run query
        result = run_cypher_query(query, config)

        # Format and print results
        output = format_results(result, args.format)
        print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
