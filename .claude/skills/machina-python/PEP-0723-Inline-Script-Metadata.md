# PEP 723 - Inline Script Metadata

> **Status:** Final (January 8, 2024)
> **Replaces:** PEP 722
> **Reference:** https://peps.python.org/pep-0723/

## Overview

PEP 723 defines a format for embedding metadata directly in single-file Python scripts. This allows scripts to declare their own dependencies and Python version requirements without external files.

## Format Specification

### Block Structure

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "rich>=13.0",
# ]
# ///
```

**Rules:**
- Opening line: `# /// script` (exactly this format)
- Closing line: `# ///`
- Content lines: Each starts with `#` followed by a space (or just `#` for empty lines)
- Content is TOML format (similar to pyproject.toml)
- Block must appear before any code (after shebang/encoding declarations)

### Supported Keys

| Key | Type | Description |
|-----|------|-------------|
| `requires-python` | String | PEP 440 version specifier (e.g., `">=3.11"`) |
| `dependencies` | Array | List of PEP 508 dependency specs |
| `[tool]` | Table | Tool-specific configuration (mirrors pyproject.toml) |

### Dependency Specification (PEP 508)

```python
# /// script
# dependencies = [
#   "requests>=2.28",           # Version constraint
#   "numpy>=1.24,<2.0",         # Version range
#   "pandas[excel]",            # With extras
#   "mypackage @ git+https://github.com/user/repo.git",  # Git URL
# ]
# ///
```

## Usage with uv

### Shebang Pattern (Recommended)

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx", "rich"]
# ///

import httpx
import rich
# ... script code
```

**Make executable and run:**
```bash
chmod +x script.py
./script.py
```

### Manual Execution

```bash
# Run script with dependencies
uv run script.py

# Run with additional inline dependencies
uv run --with pandas script.py
```

## Tool Support

| Tool | Support | Notes |
|------|---------|-------|
| **uv** | Full | Since v0.2.0 (April 2024) |
| **PDM** | Full | Native support |
| **Hatch** | Full | Native support |
| **pip** | Planned | [Feature request open](https://github.com/pypa/pip/issues/12891) |
| **Pylance** | Planned | [Feature request open](https://github.com/microsoft/pylance-release/issues/6853) |

## When to Use PEP 723

**Use for:**
- Standalone utility scripts
- One-off automation tools
- Scripts shared outside a package structure
- Quick prototypes with external dependencies
- DevOps/infrastructure scripts

**Don't use for:**
- Code within a package (use pyproject.toml)
- Libraries or reusable modules
- Scripts that are part of a larger project structure

## Complete Example

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "httpx>=0.27",
#   "rich>=13.0",
# ]
# ///
"""Fetch and display GitHub user information.

Development Commands (run from workspace root):
===============================================
1. Type checking:
   uv run --with mypy -- mypy --strict scripts/github_user.py

2. Linting:
   uvx ruff check --select=E,W,F,B,I,UP,N,S,PL,RUF --line-length 120 scripts/github_user.py

3. Formatting:
   uvx ruff format --line-length 120 scripts/github_user.py
"""

from __future__ import annotations

import sys

import httpx
from rich.console import Console
from rich.table import Table


def fetch_user(*, username: str) -> dict[str, object]:
    """Fetch GitHub user data."""
    response = httpx.get(f"https://api.github.com/users/{username}")
    response.raise_for_status()
    return response.json()


def display_user(*, user: dict[str, object]) -> None:
    """Display user information in a table."""
    console = Console()
    table = Table(title=f"GitHub User: {user.get('login', 'Unknown')}")

    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    for field in ["name", "company", "location", "public_repos", "followers"]:
        value = user.get(field)
        if value is not None:
            table.add_row(field, str(value))

    console.print(table)


def main() -> None:
    """Entry point."""
    if len(sys.argv) != 2:
        print("Usage: ./github_user.py <username>", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]
    user = fetch_user(username=username)
    display_user(user=user)


if __name__ == "__main__":
    main()
```

## Validation Regex

The canonical regex for parsing PEP 723 blocks:

```regex
(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$
```

## Best Practices

1. **Place metadata block early** - After shebang and encoding, before imports
2. **Pin major versions** - Use `>=3.12` not `>=3` for Python version
3. **Specify version constraints** - Use `package>=1.0` not just `package`
4. **Include development instructions** - Add verification commands in docstring
5. **Follow machina-python standards** - Type hints, modern syntax, etc. still apply
6. **Use keyword-only arguments** - As per machina-python mandate

## Reference Implementation

See `scripts/import_k8s_environment.py` in machina-meta for a production example demonstrating:
- PEP 723 metadata block
- uv shebang pattern
- Full machina-python standards compliance
- Development command documentation
