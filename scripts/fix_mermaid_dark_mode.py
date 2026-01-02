#!/usr/bin/env python3
"""
Add neutral theme to all Mermaid diagrams for dark mode compatibility.
"""
import re
import sys
from pathlib import Path

def fix_mermaid_diagrams(file_path: Path) -> None:
    """Add theme configuration to Mermaid diagrams that don't have it."""

    content = file_path.read_text()

    # Pattern to match mermaid blocks without theme configuration
    # Match: ```mermaid\n followed by diagram type (graph, sequenceDiagram, etc.)
    # But NOT if already has %%{init:
    pattern = r'(```mermaid)\n((?!%%\{init:)(graph |sequenceDiagram|classDiagram|flowchart ))'

    # Replace with theme configuration
    replacement = r"\1\n%%{init: {'theme':'neutral'}}%%\n\2"

    # Perform replacement
    new_content = re.sub(pattern, replacement, content)

    # Count replacements
    original_blocks = len(re.findall(r'```mermaid', content))
    themed_blocks = len(re.findall(r'%%\{init:', new_content))

    if new_content != content:
        file_path.write_text(new_content)
        print(f"Updated {file_path}")
        print(f"  Total Mermaid blocks: {original_blocks}")
        print(f"  Blocks with theme: {themed_blocks}")
        print(f"  Blocks updated: {themed_blocks - len(re.findall(r'%%{init:', content))}")
    else:
        print(f"No changes needed for {file_path}")

def main():
    dataflow_md = Path("/home/dbeal/repos/NumberOne-AI/machina-meta/docs/DATAFLOW.md")

    if not dataflow_md.exists():
        print(f"Error: {dataflow_md} not found")
        sys.exit(1)

    fix_mermaid_diagrams(dataflow_md)
    print("\nDone!")

if __name__ == "__main__":
    main()
