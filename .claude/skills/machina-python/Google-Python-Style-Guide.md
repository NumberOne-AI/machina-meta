# Google Python Style Guide

**Source**: https://google.github.io/styleguide/pyguide.html

This document is a comprehensive guide to Python coding style used at Google. It emphasizes readability, consistency, and best practices for writing maintainable Python code.

## Table of Contents

1. [Python Language Rules](#python-language-rules)
2. [Python Style Rules](#python-style-rules)
3. [Parting Words](#parting-words)

---

## Python Language Rules

### 2.1 Lint

Run `pylint` over code using the provided pylintrc configuration. Suppress warnings with line-level comments when inappropriate, using `pylint: disable` format (not the deprecated `pylint: disable-msg`).

### 2.2 Imports

**Rules:**
- Use `import x` for packages and modules only
- Use `from x import y` where x is package prefix, y is module name
- Use `from x import y as z` when:
  - Modules named y conflict
  - y conflicts with current module names
  - y conflicts with common parameter names
  - y is inconveniently long
  - y is too generic
- Use `import y as z` only when z is a standard abbreviation (e.g., `import numpy as np`)
- **Do not use relative imports**, even within the same package

### 2.3 Packages

Import each module using full pathname location. All new code should use complete package names in imports.

### 2.4 Exceptions

**Best Practices:**
- Use built-in exception classes when appropriate (e.g., `ValueError` for precondition violations)
- **Do not use `assert` statements** for critical application logic validation
- **Never use catch-all `except:` statements** unless re-raising or creating isolation points
- Minimize code within `try`/`except` blocks
- Use `finally` clause for cleanup operations

### 2.5 Mutable Global State

Avoid mutable global state. When necessary, declare at module level or as class attribute with `_` prefix. Module-level constants are permitted and encouraged (format: `_MAX_CONSTANT` or `PUBLIC_CONSTANT`).

### 2.6 Nested/Local/Inner Classes and Functions

Acceptable when closing over local variables. Avoid nesting just to hide from module users; use `_` prefix instead.

### 2.7 Comprehensions & Generator Expressions

Allowed for simple cases. Multiple `for` clauses or filter expressions not permitted. Optimize for readability over conciseness.

### 2.8 Default Iterators and Operators

Use default iterators for types supporting them (lists, dictionaries, files). Prefer methods that use defaults over methods returning lists.

### 2.9 Generators

Fine to use. Use "Yields:" rather than "Returns:" in docstrings. Manage expensive resources; wrap with context manager (PEP-0533).

### 2.10 Lambda Functions

**Guidelines:**
- Okay for one-liners
- Prefer generator expressions over `map()` or `filter()` with lambda
- **If spanning multiple lines or exceeding 60-80 characters, use nested function instead**
- Use `operator` module functions instead of lambda for common operations

### 2.11 Conditional Expressions

Okay for simple cases. Each portion must fit on one line. Use complete `if` statement for complex scenarios.

### 2.12 Default Argument Values

**Rules:**
- Okay in most cases
- **Do not use mutable objects (list, dictionary) as defaults**
- Use `None` as default, then initialize inside function

**Example:**
```python
# Correct
def foo(a, b=None):
    if b is None:
        b = []

# Wrong
def foo(a, b=[]):  # Mutable default!
    pass
```

### 2.13 Properties

Use `@property` decorator for controlling attribute access or trivial calculations. Match expectations of typical attribute access. Avoid hiding side-effects. Do not implement computations subclasses may override.

### 2.14 True/False Evaluations

**Best Practices:**
- Use implicit false: `if foo:` rather than `if foo != []:`
- **Always use `if foo is None:` for None checks**
- Use `if not x:` instead of comparing boolean to False
- For sequences, use `if seq:` rather than `if len(seq):`
- For integers, may compare against `0` when value known to be integer
- Note: `'0'` (string) evaluates to true
- For Numpy arrays, prefer `.size` attribute check

### 2.16 Lexical Scoping

Acceptable to use. Nested functions can refer to enclosing scope variables but cannot assign to them.

### 2.17 Function and Method Decorators

Use judiciously when clear advantage exists. Avoid `staticmethod`; use module-level function instead. Use `classmethod` only for named constructors or class-specific routines modifying global state. Decorators execute at object definition time (import time for module-level). Write unit tests for decorators. Avoid external dependencies in decorator code.

### 2.18 Threading

Do not rely on built-in type atomicity. Use `queue.Queue` for thread communication. Prefer condition variables and `threading.Condition` over lower-level locks.

### 2.19 Power Features

**Avoid:**
- Custom metaclasses
- Bytecode access
- Dynamic inheritance
- Import hacks
- Reflection
- System internals modification
- `__del__` methods

Standard library use (e.g., `abc.ABCMeta`, `dataclasses`, `enum`) is acceptable.

### 2.20 Modern Python: from __future__ imports

Use `from __future__ import` statements encouraged. For code supporting Python 3.5+, import: `from __future__ import generator_stop`. Remove only when confident code runs sufficiently modern environment.

### 2.21 Type Annotated Code

Annotate with type hints; check at build time with tools like pytype. Annotations in source files or stub `.pyi` files for third-party modules. Strongly encouraged when updating code. Include type annotations for public APIs.

---

## Python Style Rules

### 3.1 Semicolons

**Do not terminate lines with semicolons. Do not use semicolons for multiple statements on one line.**

### 3.2 Line Length

**Maximum: 80 characters**

**Exceptions:**
- Long imports
- URLs/pathnames in comments
- Long module-level string constants
- pylint disable comments

**Guidelines:**
- No backslash for explicit line continuation; use implicit joining within parentheses/brackets/braces
- Docstring summary lines must stay within 80 characters
- Lines exceeding 80 may be allowed if Black/Pyink formatter cannot reduce below limit

### 3.3 Parentheses

Use parentheses sparingly. Not required around tuples except for clarity or 1-item tuples. Omit from return statements and conditionals unless for line continuation or tuples.

### 3.4 Indentation

**Indent code blocks with 4 spaces. Never use tabs.**

**Implied line continuation:**
- Align with opening delimiter, OR
- Use hanging 4-space indent

Closing brackets may end line or separate line, indented same as opening bracket line.

#### 3.4.1 Trailing Commas

Recommended when closing container token doesn't appear on same line as final element. For single-element tuples. Signals auto-formatter to format one item per line.

### 3.5 Blank Lines

**Rules:**
- **Two blank lines between top-level definitions** (functions/classes)
- **One blank line between method definitions**
- One blank line between class docstring and first method
- No blank line after `def` line
- Single blank lines within functions as appropriate

### 3.6 Whitespace

**Guidelines:**
- No whitespace inside parentheses, brackets, or braces
- No whitespace before comma, semicolon, or colon
- Whitespace after comma, semicolon, or colon (except line end)
- No whitespace before argument list parentheses or indexing brackets
- No trailing whitespace
- Single space around binary operators: `=`, comparisons, Boolean operators
- Use judgment for arithmetic operators
- No spaces around `=` in keyword arguments or default parameters (except with type annotation: use spaces)
- No vertical alignment of tokens across consecutive lines

### 3.7 Shebang Line

Most `.py` files don't need shebang. Main program file: `#!/usr/bin/env python3` or `#!/usr/bin/python3` (per PEP-394).

### 3.8 Comments and Docstrings

#### 3.8.1 Docstrings

**Format:**
- Use three-double-quote `"""` format (per PEP 257)
- **One-line summary (≤80 chars)** terminated by period, question mark, or exclamation
- Multi-line: blank line after summary, rest starts at same position as first quote

#### 3.8.2 Modules

Include license boilerplate appropriate to project. Start with module docstring describing contents and usage.

#### 3.8.2.1 Test Modules

Module-level docstrings not required unless additional context provided. Avoid docstrings providing no new information.

#### 3.8.3 Functions and Methods

**Requirements:**
A function must have a docstring, unless it meets all of the following criteria:
- Not externally visible
- Very short
- Obvious

Should provide calling syntax and semantics without reading implementation.

**Style:**
- Descriptive style (`"""Fetches rows."""`) or imperative style (`"""Fetch rows."""`) - be consistent
- Prefer descriptive form

**Special sections:**
- **Args**: list parameter names with description, include types if not annotated
- **Returns**: describe semantics and type; omit if only returns None
- **Yields**: document object returned by `next()`
- **Raises**: list exceptions relevant to interface

#### 3.8.3.1 Overridden Methods

If decorated with `@override` (typing_extensions or typing), docstring optional unless behavior materially refines base or details needed. Without `@override`, docstring required.

#### 3.8.4 Classes

Docstring below class definition. Document public attributes (excluding properties) in Attributes section. One-line summary describing what instance represents. Exception subclasses: describe exception, not context. Avoid repeating that entity is a class.

#### 3.8.5 Block and Inline Comments

**For tricky code sections:**
- Block comments: few lines before operations
- **Inline comments: at least 2 spaces from code**, `#` followed by space
- Never describe code; assume reader knows Python
- Assume reader understands implementation intent better than you

#### 3.8.6 Punctuation, Spelling, Grammar

Pay attention to punctuation, spelling, grammar. Maintain high clarity and readability. Complete sentences preferred but short comments may be less formal. Be consistent.

### 3.10 Strings

**Formatting:**
- Use f-strings, `%` operator, or `.format()` for formatting
- Single `+` join acceptable; do not format with `+`
- **Do not use `+` or `+=` to accumulate strings in loops** (quadratic complexity)
- Add substrings to list, then `''.join()` after loop

**Quotes:**
- Be consistent with quote character (`'` or `"`) within file
- Use other quote character to avoid backslash-escaping within string
- Prefer `"""` for multi-line strings over `'''`

If embedded space problematic, use concatenated single-line strings or `textwrap.dedent()`.

#### 3.10.1 Logging

For logging functions expecting pattern-string as first argument: use string literal (not f-string) as first argument with pattern-parameters as subsequent arguments. Prevents rendering messages no logger outputs.

#### 3.10.2 Error Messages

Match actual error condition precisely. Interpolated pieces clearly identifiable. Allow simple automated processing (e.g., grepping).

### 3.11 Files, Sockets, and Similar Stateful Resources

**Explicitly close files and sockets when done.**

**Use `with` statement for file-like objects:**
```python
with open("hello.txt") as hello_file:
    for line in hello_file:
        print(line)
```

Use `contextlib.closing()` for objects not supporting `with`. Clear resource-lifetime management documentation if context-based management infeasible.

### 3.12 TODO Comments

**Format:**
Begin with `TODO:` (all caps), colon, link to resource/bug reference. Follow with hyphen and explanatory string. Avoid referring to individual or team as context. For future-date TODOs: include specific date or event.

**Example:**
```python
# TODO: crbug.com/192795 - Investigate cpufreq optimizations.
```

### 3.13 Imports Formatting

**Rules:**
- Separate lines per import (exceptions: `typing` and `collections.abc` imports)
- Top of file after module comments/docstrings, before globals/constants

**Group from most to least generic:**
1. `__future__` imports
2. Standard library imports
3. Third-party imports
4. Repository sub-package imports
5. (Deprecated) application-specific same-package imports

Within groups: sort lexicographically (ignoring case) by full package path. Optional blank lines between import sections.

### 3.14 Statements

Generally one statement per line. Result of test on same line allowed only if entire statement fits and no `else`. `if` acceptable without `else` on same line; `try`/`except` not acceptable.

### 3.15 Getters and Setters

Use when: getting/setting is complex or costly currently or reasonably in future. Should not be used if simply reading/writing internal attribute. Follow naming guidelines: `get_foo()`, `set_foo()`. Breaking old property access intentional to signal behavior change.

### 3.16 Naming

**Format:**
- `module_name`, `package_name`
- `ClassName`, `ExceptionName`
- `method_name`, `function_name`
- `GLOBAL_CONSTANT_NAME`
- `global_var_name`, `instance_var_name`
- `function_parameter_name`, `local_var_name`

**Guidelines:**
- Be descriptive; avoid ambiguous abbreviations
- Use `.py` extension; never use dashes in filenames

#### 3.16.1 Names to Avoid

- Single characters except: counters/iterators (i, j, k, v), exception identifier (e), file handle (f), private type variables without constraints (_T, _P), established notation names
- Dashes in package/module names
- `__double_leading_and_trailing_underscore__` names
- Offensive terms
- Type-inclusive names (e.g., id_to_name_dict)

#### 3.16.2 Naming Conventions

**Single underscore (`_`):**
- Module variables/functions protection
- Unit tests may access protected constants

**Double underscore (`__`):**
- Discouraged; impacts readability/testability
- Not truly private

**Organization:**
- Related classes/functions: group in module (no single-class-per-module requirement like Java)
- Classes: CapWords; modules: lower_with_under.py (not CapWords.py)
- Unit test files: PEP 8 compliant lower_with_under methods; e.g., `test_<method_under_test>_<state>`

#### 3.16.3 File Naming

`.py` extension required. No dashes in filenames (allows import and unittest). Executable without extension: use symbolic link or bash wrapper with `exec "$0.py" "$@"`.

#### 3.16.4 Naming Guidelines (Guido's Recommendations)

| Type | Public | Internal |
|------|--------|----------|
| Packages | `lower_with_under` | |
| Modules | `lower_with_under` | `_lower_with_under` |
| Classes | `CapWords` | `_CapWords` |
| Exceptions | `CapWords` | |
| Functions | `lower_with_under()` | `_lower_with_under()` |
| Global/Class Constants | `CAPS_WITH_UNDER` | `_CAPS_WITH_UNDER` |
| Global/Class Variables | `lower_with_under` | `_lower_with_under` |
| Instance Variables | `lower_with_under` | `_lower_with_under` |
| Method Names | `lower_with_under()` | `_lower_with_under()` |
| Function/Method Parameters | `lower_with_under` | |
| Local Variables | `lower_with_under` | |

#### 3.16.5 Mathematical Notation

Short variable names acceptable when matching established notation. Cite source in comment or docstring; link to academic resource preferred. Prefer PEP8-compliant descriptive names for public APIs. Use narrowly-scoped `pylint: disable=invalid-name` directive.

### 3.17 Main

Main functionality in `main()` function. Always check `if __name__ == '__main__'` before executing main program. Modules must remain importable. With absl: use `app.run(main)`. Avoid top-level code execution on import.

### 3.18 Function Length

**Prefer small, focused functions. No hard limit; reconsider if exceeding ~40 lines.** Break up if difficult to modify, debug, or reuse portions.

### 3.19 Type Annotations

#### 3.19.1 General Rules

Familiarize with type hints. Annotating `self`/`cls` generally unnecessary; use `Self` if needed for type information. Do not annotate `__init__` return (always None). Use `Any` for variables/returns not expressible. Not required to annotate all functions; at least annotate public APIs. Annotate code prone to type errors, hard to understand, or stable from types perspective.

#### 3.19.2 Line Breaking

Follow existing indentation rules. One parameter per line after annotation. Comma after last parameter ensures return type on own line. Prefer breaking between variables, not variable/type. If function name + last parameter + return type too long: indent 4 in new line. Preferred: each parameter and return type on own lines, closing parenthesis aligned with `def`. Optional: return type on same line as last parameter. Prefer not to break types; break only if necessary (keep sub-types unbroken). If single name + type too long: use alias or break after colon with 4-space indent.

#### 3.19.3 Forward Declarations

Use `from __future__ import annotations` or string class name if class used before definition. Allows class references within same class declaration or before definition.

#### 3.19.4 Default Values

**Use spaces around `=` only for arguments with both type annotation and default value.**

```python
def func(x: int = 0) -> int:
    return x
```

#### 3.19.5 NoneType

`None` is alias for NoneType in type system. If argument can be None, declare explicitly. **Use `X | None` (recommended in Python 3.10+)** or `Optional[X]`/`Union[X, None]`. Avoid implicit `a: str = None`.

#### 3.19.6 Type Aliases

CapWorded names; `_Private` if module-only. **Use `: TypeAlias` annotation (Python 3.10+).**

```python
_LossAndGradient: TypeAlias = tuple[tf.Tensor, tf.Tensor]
```

#### 3.19.7 Ignoring Types

Use `# type: ignore` line comment to disable type checking. Use `# pytype: disable=error-name` for specific errors.

#### 3.19.8 Typing Variables

Annotated assignments: colon + type between name and value (like function arguments with defaults). Type comments (`# type: <type>` at line end) discouraged; don't add new uses.

#### 3.19.9 Tuples vs Lists

**Typed lists: single type only. Typed tuples: single repeated type or set number of different-type elements.**

```python
# List with single type
def process_items(items: list[int]) -> None:
    pass

# Tuple with multiple types
def get_user() -> tuple[str, int, bool]:
    return ("Alice", 30, True)

# Tuple with variable length
def get_numbers() -> tuple[int, ...]:
    return (1, 2, 3, 4)
```

#### 3.19.10 Type Variables

Common use: `TypeVar`, `ParamSpec`. TypeVar constraints syntax: `TypeVar("Name", type1, type2, ...)`. Predefined `AnyStr` for bytes or str (must be same type throughout). Descriptive names required unless: not externally visible AND not constrained.

#### 3.19.11 String Types

**Use `str` for string/text data. Use `bytes` for binary data.** Do not use `typing.Text` (Python 2/3 compatibility only). Use `AnyStr` if all string types in function always same.

#### 3.19.12 Imports For Typing

**Import symbols themselves from `typing` or `collections.abc` (not wildcard).** Multiple specific symbols acceptable on one line from these modules. Treat typing/collections.abc names like keywords; don't redefine. Collision: use `import x as y`. Prefer abstract types (e.g., `collections.abc.Sequence`) over concrete (e.g., `list`). For concrete types, prefer built-ins (e.g., `tuple`) over parametric aliases (e.g., `typing.Tuple`).

#### 3.19.13 Conditional Imports

Discouraged; prefer refactoring for top-level imports. Use `if TYPE_CHECKING:` block for type-checking-only imports. Conditionally imported types: reference as strings. Only type-only entities in block. Block immediately after normal imports. No empty lines in typing imports list. Sort as regular imports list.

#### 3.19.14 Circular Dependencies

Code smell; candidate for refactoring. Replace circular imports with `Any`. Set alias with meaningful name. Alias definitions separated from last import by one line.

#### 3.19.15 Generics

Specify type parameters in parameter list for generic types. Otherwise assumed to be `Any`. Explicit `Any` acceptable if appropriate; consider `TypeVar` instead.

---

## Parting Words

**Be consistent.** Consider code style surrounding additions. Local style important; global vocabulary important. Consistency should not justify old styles when new styles offer benefits. Tendency toward newer styles over time acceptable.

---

**For this codebase**: We follow Google Python Style Guide with Python 3.13+ features. All functions must have type annotations. Use modern syntax (`|` for unions, built-in generics). Prioritize readability and maintainability.
