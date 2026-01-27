#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["tabulate"]
# ///
"""
Format Markdown tables in files using the `tabulate` library.
Usage: ./scripts/format_md_tables.py <file1.md> [file2.md ...]
"""

import argparse
import sys
import re
from tabulate import tabulate


def parse_table_block(lines: list[str]) -> tuple[list[list[str]], bool]:
    """Parse a block of lines into a list of rows. Returns (rows, has_header)."""
    rows = []
    for line in lines:
        # Split by pipe, strip whitespace
        # Note: simplistic splitting, doesn't handle escaped pipes inside cells
        cells = [c.strip() for c in line.strip().split("|")]

        # Remove empty first/last elements if line starts/ends with pipe
        if line.strip().startswith("|"):
            cells = cells[1:]
        if line.strip().endswith("|"):
            cells = cells[:-1]

        rows.append(cells)

    # Check for separator line (---|---|---)
    if len(rows) > 1:
        # Heuristic: separator line usually contains only -, :, |
        sep_row = lines[1].strip()
        if re.match(r"^\|?[\s\-:|]+\|?$", sep_row):
            # Remove separator row from data
            rows.pop(1)
            return rows, True

    return rows, False


def format_file(filepath: str):
    print(f"Processing: {filepath}")
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    new_lines = []
    in_table = False
    table_buffer = []

    # Regex to detect table lines (must start with |)
    table_line_re = re.compile(r"^\s*\|")

    for i, line in enumerate(lines):
        is_table_line = bool(table_line_re.match(line))

        if is_table_line:
            in_table = True
            table_buffer.append(line)
        else:
            if in_table:
                # End of table, process buffer
                rows, has_header = parse_table_block(table_buffer)
                if rows:
                    try:
                        # Format using tabulate
                        # "github" format is standard Markdown (pipes)
                        formatted = tabulate(
                            rows,
                            headers="firstrow" if has_header else [],
                            tablefmt="github",
                        )
                        new_lines.append(formatted + "\n")
                    except Exception as e:
                        print(f"Error formatting table: {e}")
                        new_lines.extend(table_buffer)
                else:
                    new_lines.extend(table_buffer)

                table_buffer = []
                in_table = False

            new_lines.append(line)

    # Flush pending table at EOF
    if in_table and table_buffer:
        rows, has_header = parse_table_block(table_buffer)
        if rows:
            formatted = tabulate(
                rows, headers="firstrow" if has_header else [], tablefmt="github"
            )
            new_lines.append(formatted + "\n")
        else:
            new_lines.extend(table_buffer)

    # Write back
    with open(filepath, "w") as f:
        f.writelines(new_lines)
    print(f"  Done: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Format Markdown tables")
    parser.add_argument("files", nargs="+", help="Markdown files to format")
    args = parser.parse_args()

    for f in args.files:
        format_file(f)


if __name__ == "__main__":
    main()
