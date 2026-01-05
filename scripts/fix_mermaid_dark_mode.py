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

    # Pattern to match mermaid blocks without theme configuration or with old theme config
    # Match: ```mermaid\n followed by diagram type (graph, sequenceDiagram, etc.)
    # Or match old theme config without background
    pattern1 = r'(```mermaid)\n((?!%%\{init:)(graph |sequenceDiagram|classDiagram|flowchart ))'
    pattern2 = r"%%\{init: \{'theme':'neutral'\}\}%%"

    # Replace with theme configuration including background
    replacement1 = r"\1\n%%{init: {'theme':'neutral', 'themeVariables': {'background':'#f5f5f5'}}}%%\n\2"
    replacement2 = r"%%{init: {'theme':'neutral', 'themeVariables': {'background':'#f5f5f5'}}}%%"

    # Perform replacements
    new_content = re.sub(pattern1, replacement1, content)
    new_content = re.sub(pattern2, replacement2, new_content)

    # Count replacements
    original_blocks = len(re.findall(r'```mermaid', content))
    themed_blocks = len(re.findall(r"%%\{init: \{'theme':'neutral', 'themeVariables': \{'background':'#f5f5f5'\}\}\}%%", new_content))

    if new_content != content:
        file_path.write_text(new_content)
        print(f"Updated {file_path}")
        print(f"  Total Mermaid blocks: {original_blocks}")
        print(f"  Blocks with theme: {themed_blocks}")
        old_themed = len(re.findall(r'%%\{init:', content))
        print(f"  Blocks updated: {themed_blocks - old_themed if themed_blocks >= old_themed else 'all (updated existing configs)'}")
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
