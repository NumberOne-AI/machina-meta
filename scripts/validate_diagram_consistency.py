#!/usr/bin/env python3
"""
Validate that all DATAFLOW_*.dot files use consistent entity definitions.

This ensures that the same entities (FastAPI, PostgreSQL, etc.) are defined
identically across all diagrams for visual consistency.
"""
import re
from pathlib import Path
from collections import defaultdict

# Standard entity definitions that should be used consistently
STANDARD_ENTITIES = {
    "FastAPI": {
        "label": r"FastAPI Backend\\nPort 8000",
        "fillcolor": "lightgreen",
        "shape": "box"
    },
    "NextJS": {
        "label": r"Next\.js Frontend\\nPort 3000",
        "fillcolor": "lightyellow",
        "shape": "box"
    },
    "MedicalCatalog": {
        "label": r"Medical Catalog\\nPort 8001",
        "fillcolor": "lightpink",
        "shape": "box"
    },
    "Postgres": {
        "label": r"PostgreSQL\\n5432",
        "fillcolor": "skyblue",
        "shape": "cylinder"
    },
    "Neo4j": {
        "label": r"Neo4j\\n7474/7687",
        "fillcolor": "skyblue",
        "shape": "cylinder"
    },
    "Redis": {
        "label": r"Redis\\n6379",
        "fillcolor": "skyblue",
        "shape": "cylinder"
    },
    "Qdrant": {
        "label": r"Qdrant\\n6333",
        "fillcolor": "skyblue",
        "shape": "cylinder"
    },
    "Browser": {
        "label": "Web Browser",
        "fillcolor": "lightblue",
        "shape": "box"
    },
    "GeminiAPI": {
        "label": "Google Gemini API",
        "fillcolor": "plum",
        "shape": "cloud"
    },
}


def extract_node_definitions(dot_content):
    """Extract all node definitions from a .dot file."""
    # Pattern: NodeID [label="...", fillcolor=..., shape=...];
    pattern = r'(\w+)\s*\[([^\]]+)\];'
    nodes = {}

    for match in re.finditer(pattern, dot_content):
        node_id = match.group(1)
        attributes = match.group(2)
        nodes[node_id] = attributes

    return nodes


def check_consistency(docs_dir):
    """Check all DATAFLOW_*.dot files for consistent entity definitions."""
    docs_path = Path(docs_dir)
    dot_files = sorted(docs_path.glob("DATAFLOW_*.dot"))

    print(f"Checking {len(dot_files)} diagram files for consistency...")
    print("=" * 70)

    entity_usage = defaultdict(list)
    inconsistencies = []

    for dot_file in dot_files:
        content = dot_file.read_text()
        nodes = extract_node_definitions(content)

        for entity_id in STANDARD_ENTITIES.keys():
            if entity_id in nodes:
                entity_usage[entity_id].append({
                    "file": dot_file.name,
                    "definition": nodes[entity_id]
                })

    # Check for inconsistencies
    for entity_id, expected in STANDARD_ENTITIES.items():
        if entity_id not in entity_usage:
            continue

        usages = entity_usage[entity_id]
        print(f"\n{entity_id}: Found in {len(usages)} diagrams")

        # Check each usage
        for usage in usages:
            issues = []
            attrs = usage["definition"]

            # Check label
            if "label" in expected:
                if expected["label"] not in attrs:
                    issues.append(f"  ⚠️  Label doesn't match standard")

            # Check fillcolor
            if f'fillcolor={expected["fillcolor"]}' not in attrs and \
               f'fillcolor="{expected["fillcolor"]}"' not in attrs:
                issues.append(f"  ⚠️  Color should be {expected['fillcolor']}")

            # Check shape
            if "shape" in expected:
                if f'shape={expected["shape"]}' not in attrs and \
                   f'shape="{expected["shape"]}"' not in attrs:
                    issues.append(f"  ⚠️  Shape should be {expected['shape']}")

            if issues:
                inconsistencies.append({
                    "entity": entity_id,
                    "file": usage["file"],
                    "issues": issues
                })
                print(f"  ✗ {usage['file']}")
                for issue in issues:
                    print(f"    {issue}")
            else:
                print(f"  ✓ {usage['file']}")

    print("\n" + "=" * 70)
    if inconsistencies:
        print(f"⚠️  Found {len(inconsistencies)} inconsistencies")
        print("\nTo fix: Update the entity definitions in the affected files")
        print("to match the standards defined in DATAFLOW_entities.dot")
        return 1
    else:
        print("✓ All entity definitions are consistent!")
        return 0


if __name__ == "__main__":
    docs_dir = Path(__file__).parent.parent / "docs"
    exit(check_consistency(docs_dir))
