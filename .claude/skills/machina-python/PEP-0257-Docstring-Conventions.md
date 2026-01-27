# PEP 257 – Docstring Conventions

**Source**: https://peps.python.org/pep-0257/

## Core Definition
A docstring is a string literal appearing as the first statement in a module, function, class, or method. It becomes the `__doc__` attribute of that object.

## One-Line Docstrings

**Key Rules:**
- Use triple double quotes `"""` even for single-line docstrings
- Closing quotes remain on the same line as opening quotes
- No blank lines before or after the docstring
- Write as a command phrase ending with a period: "Return X" rather than "Returns X"
- Do NOT repeat function signatures or parameters

**Example:**
```python
def kos_root():
    """Return the pathname of the KOS root directory."""
    pass
```

## Multi-Line Docstrings

**Structure:**
- Summary line (fits on one line, like a one-liner)
- Blank line separator
- Detailed description following

**Placement Guidelines:**
- Opening quotes can appear on the first line or the next
- Closing quotes go on their own line (unless entire docstring fits on one line)
- Insert blank line after docstrings documenting classes

**Content Requirements by Type:**

### Modules
List exported classes, exceptions, functions with brief summaries.

### Functions/Methods
Document:
- Behavior
- Arguments
- Return values
- Side effects
- Exceptions raised
- Usage restrictions

### Classes
- Summarize behavior
- List public methods and instance variables
- Note inheritance and method overrides/extensions

### Scripts
Provide usage message with:
- Command-line syntax
- Environment variables
- Files used

## Indentation Handling

Docstring processing tools automatically strip uniform indentation from lines after the first. The algorithm:
1. Removes leading/trailing blank lines
2. Preserves relative indentation of subsequent lines
3. Removes the first line's indentation (it's insignificant)

This standardization ensures consistent formatting regardless of source code indentation levels.

---

**Best Practice**: For this codebase, we prefer concise docstrings that avoid repeating information already clear from type hints. Focus on the "why" rather than the "what".
