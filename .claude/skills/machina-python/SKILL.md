---
name: machina-python
description: World-class Python development expert for machina-meta. Enforces hyper-perfect coding standards, modern Python 3.10+ syntax, strict type hinting, security best practices, and project-specific conventions. Use for ALL Python coding tasks, refactoring, and static analysis.
---

# machina-python Skill

> **⚠️ NOTE: STANDARDS UNDER REVIEW**
>
> The standards in this document are currently **Under Review**. While they represent the target "Hyper-Perfect" state, existing code may not yet conform. Apply these standards rigorously to *new* code, but exercise judgement when refactoring legacy code to avoid massive, disruptive diffs unless explicitly requested.

This skill provides the authoritative standards and workflows for writing "hyper-perfect" world-class Python code in the machina-meta workspace.

## ⚠️ CRITICAL: Core Mandates

1.  **Strict Type Hints**: Every single function, method, parameter, and return value MUST have complete type hints. No exceptions.
    *   **Accept Abstract**: Use `Sequence`, `Iterable`, `Mapping` for arguments.
    *   **Return Concrete**: Use `list`, `dict`, `set` for return values.
2.  **Keyword-Only Arguments**: ALL new functions (even with 1 argument) MUST use `*` to enforce keyword arguments. (e.g., `def foo(*, bar: int):`).
3.  **Modern Syntax (3.10+)**: Use `list[int]` not `List[int]`, `str | None` not `Optional[str]`.
3.  **Strict Static Analysis**: Code must pass strict `mypy` and `ruff` checks.
4.  **Async Correctness**: NEVER block the event loop. Use `async def` for I/O-bound operations. Use `httpx` not `requests`.
5.  **Test Mandate**: No code is "done" without accompanying `pytest` unit tests.
6.  **Security**: No secrets in code. Use env vars. Validate all inputs.

## 🛠️ Development Workflow

### 1. Plan & Design
*   **Consult**: Refer to the "Detailed Python Standards" section below for specific patterns (Naming, Types, Exceptions).
*   **Structure**: Follow the "Service Architecture Style Guide" (API -> Service -> Components -> Infra).
*   **Dependencies**: Ensure imports flow top-down only. No circular dependencies.

### 2. Implementation Rules (The "Hyper-Perfect" Standard)

#### Type Hinting (Non-Negotiable)
*   **Modern Generics**: `list[]`, `dict[]`, `tuple[]`, `set[]`, `type[]` (NOT `List`, `Dict`, etc. from `typing`).
*   **Unions**: Use `|` operator (e.g., `int | str`). NEVER use `Union`.
*   **Optional**: Use `| None` (e.g., `User | None`). NEVER use `Optional`.
*   **No Any**: Avoid `Any` unless absolutely impossible to type.
*   **Dataclasses**: Use `@dataclass(frozen=True)` or Pydantic `BaseModel(frozen=True)` for immutable data structures.

#### Async/Await Standards
*   **I/O Bound**: Must be `async def`.
*   **CPU Bound**: Run in thread pool via `asyncio.to_thread`.
*   **Blocking Calls**: STRICTLY FORBIDDEN in async functions (e.g., `time.sleep`, `requests.get`). Use `asyncio.sleep`, `httpx.get`.
*   **Concurrency**: Use `asyncio.TaskGroup` (Python 3.11+) over `gather`.

#### Control Flow & Logic
*   **None Checks**: ALWAYS use `is None` or `is not None`. NEVER use `== None`.
*   **Fail Fast**: Validate inputs early and return/raise immediately. Avoid deep nesting.
*   **Empty Checks**: Use implicit truthiness (`if not items:`) instead of `len(items) == 0`.
*   **Defaults**: NEVER use mutable default arguments (e.g., `def foo(items: list = []):`). Use `None` and initialize inside.

#### Exception Handling
*   **Chaining**: ALWAYS use `raise NewError("msg") from original_error` to preserve stack traces.
*   **Specifics**: Catch specific exceptions (`ValueError`, `KeyError`). NEVER use bare `except:`.
*   **Custom**: Define custom exceptions in `contracts/exceptions.py`.

#### Formatting & Style
*   **Length**: Max 120 characters per line (Modern standard).
*   **Indent**: 4 spaces.
*   **Strings**: Use f-strings everywhere.
*   **Docstrings**:
    *   **Public APIs**: Mandatory.
    *   **Format**: Google style (Args, Returns, Raises).
    *   **Content**: Explain *why*, not *what* (types are already in signature).
    *   **Constraint**: NEVER repeat type info in docstrings.

### 3. Verification (Mandatory)

Run these commands from the project root (`machina-meta`) to verify your code.

**Verification Commands:**
```bash
# Type checking (Strict Mode)
uv run --with mypy -- mypy --strict path/to/file.py

# Linting (Safe Strict Subset)
# Note: --select=ALL is dangerous/conflicting. We use a curated strict set.
# E/W (pycodestyle), F (Pyflakes), B (Bugbear), I (Isort), UP (PyUpgrade), 
# N (Pep8-Naming), S (Bandit), PL (Pylint), RUF (Ruff-specific)
uvx ruff check --select=E,W,F,B,I,UP,N,S,PL,RUF --line-length 120 path/to/file.py

# Auto-fix lint errors
uvx ruff check --select=E,W,F,B,I,UP,N,S,PL,RUF --line-length 120 --fix path/to/file.py

# Formatting (120 char line length)
uvx ruff format --line-length 120 path/to/file.py

# Testing (Mandatory)
# Ensure at least one test covers the changes
uv run pytest path/to/test_file.py
```

## 🏗️ Project-Specific Conventions

### Project Structure (dem2)
*   **Entry Point**: `machina/machina-medical/src/machina_medical/main.py`
*   **Shared**: `shared/` directory for common utilities.
*   **Services**: `services/<package-name>/src/machina/<package_name>`
*   **Tests**: `<package-name>/tests`

### Libraries & Patterns
*   **Logging**: ALWAYS use `structlog`.
*   **Serialization**: Use `machina.shared.utils.serde.json_dumps`.
*   **Database (PostgreSQL)**:
    *   Models inherit from `machina.shared.db.models.BaseSQLModel`.
    *   Access via `machina.shared.db.database.Database`.
*   **Configuration**: Use `config.toml` and `pydantic.BaseModel` for config classes.
*   **Pydantic**: Use v2. Use `.model_validate()` (not `.from_orm()`). Favor `frozen=True`.

### PDF Processing (pdf_tests)
*   **Dev Only**: Use `pdf_tests/Makefile` for development testing.
*   **Commands**: `make process`, `make verify-only`.
*   **Split Files**: Outputs are split to keep files < 25k tokens.

### Standalone Scripts (PEP 723)

For self-contained scripts with dependencies, use **PEP 723 inline script metadata**.

**Full specification**: `PEP-0723-Inline-Script-Metadata.md` (in skill directory)

#### Template

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "httpx>=0.27",
#   "rich>=13.0",
# ]
# ///
"""Script description.

Development Commands (run from workspace root):
===============================================
1. Type checking:
   uv run --with mypy -- mypy --strict scripts/myscript.py

2. Linting:
   uvx ruff check --select=E,W,F,B,I,UP,N,S,PL,RUF --line-length 120 scripts/myscript.py

3. Formatting:
   uvx ruff format --line-length 120 scripts/myscript.py
"""

from __future__ import annotations

# ... imports and code following machina-python standards
```

#### Key Points

| Element | Requirement |
|---------|-------------|
| Shebang | `#!/usr/bin/env -S uv run --quiet --script` |
| Python version | `requires-python = ">=3.12"` (or appropriate) |
| Dependencies | PEP 508 specs with version constraints |
| Code standards | **All machina-python rules still apply** (types, `*` args, etc.) |

#### When to Use

*   ✅ Standalone utility scripts (e.g., `scripts/` directory)
*   ✅ One-off automation tools
*   ✅ Scripts shared outside the package structure
*   ❌ Code within packages (use pyproject.toml)
*   ❌ Libraries or reusable modules

#### Running Scripts

```bash
# Make executable and run directly
chmod +x scripts/myscript.py
./scripts/myscript.py

# Or run via uv
uv run scripts/myscript.py
```

#### Reference Implementation

See `scripts/import_k8s_environment.py` for a production example.

## 🛡️ Security Checklist
*   [ ] No hardcoded secrets (use env vars).
*   [ ] Inputs validated (types, ranges, formats).
*   [ ] SQL queries parameterized (no f-strings in SQL).
*   [ ] Subprocess calls use list arguments (no `shell=True`).
*   [ ] Path traversal prevented (validate against base dir).

---

# Detailed Python Standards

**Reference Documents**: `PEP-0008-Style-Guide.md` | `PEP-0020-Zen-of-Python.md` | `PEP-0257-Docstring-Conventions.md` | `PEP-0484-Type-Hints.md` | `PEP-0723-Inline-Script-Metadata.md` | `Google-Python-Style-Guide.md` (All available in skill directory)

---

## Quick Reference Card

### Critical Rules (Never Violate)

```
✓ All functions MUST have type hints on parameters and return values
✓ Line length MUST be ≤120 characters
✓ Indentation MUST be 4 spaces (never tabs)
✓ None comparisons MUST use `is` or `is not` (never `==`)
✓ Default arguments MUST NOT be mutable objects
✓ Exception chains MUST use `raise ... from err`
✓ Never use bare `except:` without re-raising
✓ Never use `assert` for runtime validation
✓ Async functions MUST NOT contain blocking calls
✓ New functions MUST enforce keyword arguments (`*` separator)
```

### Modern Python Syntax (3.10+)

| Old ❌ | Modern ✓ |
|--------|---------|
| `Optional[str]` | `str | None` |
| `Union[int, str]` | `int | str` |
| `List[int]` | `list[int]` |
| `Dict[str, int]` | `dict[str, int]` |
| `Tuple[int, str]` | `tuple[int, str]` |

---

## Decision Tree: Writing a New Function

```
START
  ├─ Read existing code in module? NO → Read it first
  ├─ Understand requirements? NO → Ask for clarification
  │
  ├─ Define function signature with types
  │   ├─ Parameters: name: type (Prefer Abstract: Sequence, Mapping)
  │   ├─ Use `*` to force keyword-only arguments for clarity
  │   ├─ Return: -> type (Prefer Concrete: list, dict)
  │   └─ Use modern syntax (list not List, | not Union)
  │
  ├─ Write docstring
  │   ├─ Simple function? → One-line docstring
  │   └─ Complex function? → Multi-line with Args/Returns/Raises
  │
  ├─ Implement logic
  │   ├─ Validate inputs at start
  │   ├─ Fail fast (return/raise early)
  │   ├─ Use explicit None checks (is/is not)
  │   └─ Prefer if-else over complex ternaries
  │
  ├─ Handle resources
  │   └─ Files/sockets? → Use `with` or `async with` statement
  │
  ├─ Handle errors
  │   ├─ Catch specific exceptions only
  │   ├─ Use `raise ... from err`
  │   └─ Log before raising
  │
  └─ Format code
      ├─ Lines ≤120 chars
      ├─ Proper spacing
      └─ No trailing whitespace
```

---

## I. Type Hints - Complete Reference

### Rule: Every function must have complete type annotations

**Parameters (Accept Abstract) and Returns (Return Concrete):**
```python
from collections.abc import Sequence, Mapping

# ✓ Correct
def process_data(items: Sequence[str]) -> list[int]:
    return [len(x) for x in items]

# ❌ Wrong - Too specific input type restricts caller
def process_data(items: list[str]) -> list[int]:
    pass
```

**Modern syntax (Python 3.10+) - ALWAYS use these:**

```python
# ✓ Correct - modern built-in generics
def process(items: list[str]) -> dict[str, int]:
    pass

# ✓ Correct - union with |
def get_value(key: str) -> int | str | None:
    pass

# ✓ Correct - built-in tuple
def get_point() -> tuple[float, float]:
    pass

# ❌ Wrong - deprecated typing module
from typing import List, Dict, Optional, Union
def process(items: List[str]) -> Dict[str, int]:  # NO
    pass
def get_value(key: str) -> Optional[Union[int, str]]:  # NO
    pass
```

### Type Patterns by Use Case

**Pattern: Collections**
```python
# List - homogeneous elements
numbers: list[int] = [1, 2, 3]
names: list[str] = ["Alice", "Bob"]

# Dict - key and value types
ages: dict[str, int] = {"Alice": 30}
config: dict[str, str | int] = {"host": "localhost", "port": 8000}

# Set - unique elements
tags: set[str] = {"python", "typing"}

# Tuple - fixed structure
point: tuple[float, float] = (10.0, 20.0)
user: tuple[str, int, bool] = ("Alice", 30, True)

# Tuple - variable length
numbers: tuple[int, ...] = (1, 2, 3, 4)
```

**Pattern: Optional (nullable) values**
```python
# ✓ Correct - use | None
def find_user(email: str) -> User | None:
    pass

# ❌ Wrong - don't use Optional
from typing import Optional
def find_user(email: str) -> Optional[User]:  # NO
    pass
```

**Pattern: Union types**
```python
# ✓ Correct - use |
def process(value: int | str | float) -> bool:
    pass

# ❌ Wrong - don't use Union
from typing import Union
def process(value: Union[int, str, float]) -> bool:  # NO
    pass
```

**Pattern: Callable (function) types**
```python
from collections.abc import Callable

# Function taking (int, str) and returning bool
def retry(func: Callable[[int, str], bool], attempts: int) -> bool:
    pass

# Function taking no args and returning str
def run(factory: Callable[[], str]) -> str:
    pass
```

**Pattern: Type aliases for complex types**
```python
from typing import TypeAlias

# ✓ Correct - use TypeAlias for clarity
UserId: TypeAlias = int
UserData: TypeAlias = dict[str, str | int | bool]
JsonDict: TypeAlias = dict[str, Any]

def get_user(user_id: UserId) -> UserData:
    pass
```

**Pattern: Generic types with TypeVar**
```python
from typing import TypeVar
from collections.abc import Sequence

T = TypeVar('T')

def first(items: Sequence[T]) -> T:
    return items[0]

def filter_none(items: list[T | None]) -> list[T]:
    return [x for x in items if x is not None]
```

---

## II. None Handling - Critical Patterns

### Rule: Always use `is` or `is not` for None checks (PEP 8)

**Pattern: None comparison**
```python
# ✓ Correct
if value is None:
    return default

if result is not None:
    process(result)

# ❌ Wrong - never use ==
if value == None:  # NO
    return default
```

**Pattern: Nullable attribute checks**
```python
# ✓ Correct - explicit if-else
if usage is not None and usage.token_count is not None:
    tokens = usage.token_count
else:
    tokens = 0

# ❌ Wrong - complex ternary
tokens = usage.token_count if usage and usage.token_count else 0  # Hard to read
```

**Pattern: Default value for None**
```python
# ✓ Correct - if-else preferred
if config is None:
    config = get_default_config()

# Acceptable for simple cases
config = config or get_default_config()
```

**Pattern: Early return on None**
```python
# ✓ Correct - fail fast
def process(data: dict[str, Any] | None) -> Result:
    if data is None:
        return Result.empty()

    # Continue with non-null data
    return Result(data)
```

---

## III. Naming Conventions - Quick Lookup

### Pattern: Standard naming by type

```python
# Module/package names
user_service.py
data_processing/

# Class names - CapWords
class UserAccount:
    pass

class HTTPClient:
    pass

# Exception names - CapWords + Error suffix
class ValidationError(Exception):
    pass

class NotFoundError(Exception):
    pass

# Function names - lower_with_under
def calculate_total(items: list[Item]) -> float:
    pass

def fetch_user_data(user_id: int) -> UserData:
    pass

# Constants - CAPS_WITH_UNDER
MAX_RETRIES = 3
API_TIMEOUT = 30
DEFAULT_CONFIG = {"host": "localhost"}

# Variables - lower_with_under
user_count = 0
total_price = 99.99
is_valid = True

# Private/internal - prefix with _
class MyClass:
    _internal_cache: dict[str, Any] = {}

    def _private_method(self) -> None:
        pass

# Type variables
T = TypeVar('T')
AnyStr = TypeVar('AnyStr', str, bytes)
```

### Pattern: Method ordering in classes

```python
class Service:
    # 1. Public instance methods
    def public_method(self) -> None:
        pass

    # 2. Public class methods
    @classmethod
    def from_config(cls, config: Config) -> Self:
        pass

    # 3. Public static methods
    @staticmethod
    def public_static() -> None:
        pass

    # 4. Private instance methods
    def _private_method(self) -> None:
        pass

    # 5. Private class methods
    @classmethod
    def _private_class_method(cls) -> None:
        pass

    # 6. Private static methods
    @staticmethod
    def _private_static() -> None:
        pass
```

---

## IV. Formatting Rules - Exact Specifications

### Rule: Line length maximum 120 characters

```python
# ✓ Correct - fits in 120 chars
def short_function(param: int) -> str:
    return f"Value: {param}"

# ✓ Correct - break long lines
def long_function(
    first_parameter: str,
    second_parameter: int,
    third_parameter: bool,
) -> dict[str, Any]:
    return {
        "first": first_parameter,
        "second": second_parameter,
        "third": third_parameter,
    }

# ✓ Correct - break long expressions
result = (
    very_long_variable_name
    + another_long_variable
    + yet_another_variable
)
```

### Rule: Indentation is 4 spaces (never tabs)

```python
# ✓ Correct - 4 spaces
def function():
    if condition:
        do_something()
    else:
        do_other()

# ❌ Wrong - tabs or 2 spaces
def function():
  if condition:  # 2 spaces - NO
        do_something()
```

### Rule: Blank lines for separation

```python
# ✓ Correct - 2 blank lines between top-level definitions
def first_function():
    pass


def second_function():
    pass


class MyClass:
    pass


# ✓ Correct - 1 blank line between methods
class Service:
    def first_method(self):
        pass

    def second_method(self):
        pass
```

### Rule: Whitespace patterns

```python
# ✓ Correct spacing
result = function(arg1, arg2, arg3)
value = x + y
items[1:5]
{"key": "value"}

# ❌ Wrong spacing
result = function( arg1 , arg2 , arg3 )  # Extra spaces inside parens
value = x+y  # No spaces around operator
items[ 1 : 5 ]  # Spaces inside brackets
{"key":"value"}  # No space after colon
```

### Rule: Import organization

```python
# ✓ Correct - grouped and sorted
# 1. Standard library
import os
import sys
from pathlib import Path

# 2. Third-party
import numpy as np
import pandas as pd

# 3. Local application
from myapp.core import Service
from myapp.utils import helper

# ❌ Wrong - mixed up
from myapp.core import Service
import numpy as np
import os
```

---

## V. Docstrings - Template Patterns

### Pattern: One-line docstring (simple functions)

```python
def get_user_id(email: str) -> int:
    """Return the user ID for the given email address."""
    pass
```

**Rules for one-liners:**
- Triple quotes `"""` even for one line
- Closing quotes on same line
- Imperative mood: "Return" not "Returns"
- End with period
- No blank lines

### Pattern: Multi-line docstring (complex functions)

```python
def process_user_data(
    user_id: int,
    include_history: bool = False,
) -> dict[str, Any]:
    """Process and return user data with optional history.

    Detailed description goes here. Explain what the function does
    in more detail, covering edge cases and important behavior.

    Args:
        user_id: Unique identifier for the user
        include_history: Whether to include transaction history

    Returns:
        Dictionary containing user data and optional history

    Raises:
        UserNotFoundError: If user_id does not exist
        DatabaseError: If database connection fails
    """
    pass
```

**Structure:**
1. Summary line (≤120 chars, ends with period)
2. Blank line
3. Detailed description (optional)
4. Blank line
5. Args: List each parameter with description
6. Returns: Describe return value
7. Raises: List exceptions

**For this codebase:**
- Don't repeat type information (it's in type hints)
- Focus on "why" not "what"
- Only document public APIs and complex logic

---

## VI. Exception Handling - Standard Patterns

### Pattern: Catch specific exceptions

```python
# ✓ Correct - specific exceptions
try:
    result = risky_operation()
except ValueError as e:
    logger.error("Invalid value", exc_info=e)
    raise ValidationError("Invalid input") from e
except KeyError as e:
    logger.error("Missing key", exc_info=e)
    raise DataError("Required field missing") from e

# ❌ Wrong - catch-all
try:
    result = risky_operation()
except:  # Never use bare except
    handle_error()

# ❌ Wrong - too broad
try:
    result = risky_operation()
except Exception:  # Too broad unless re-raising
    handle_error()
```

### Pattern: Exception chaining with `from`

```python
# ✓ Correct - preserve exception chain
try:
    data = parse_json(text)
except json.JSONDecodeError as e:
    raise ValidationError("Invalid JSON format") from e

# ❌ Wrong - lose original exception
try:
    data = parse_json(text)
except json.JSONDecodeError:
    raise ValidationError("Invalid JSON format")  # Original error lost
```

### Pattern: Minimize try block

```python
# ✓ Correct - minimal try block
data = prepare_data()
try:
    result = risky_operation(data)
except ValueError as e:
    raise ProcessingError() from e
finally:
    cleanup()

# ❌ Wrong - too much in try
try:
    data = prepare_data()  # These don't need try
    result = risky_operation(data)
    processed = transform(result)  # These don't need try
except ValueError as e:
    raise ProcessingError() from e
```

### Rule: Never use `assert` for runtime validation

```python
# ✓ Correct - explicit check
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Divisor cannot be zero")
    return a / b

# ❌ Wrong - assert can be disabled with -O flag
def divide(a: int, b: int) -> float:
    assert b != 0, "Divisor cannot be zero"  # NO
    return a / b
```

---

## VII. Common Patterns and Anti-Patterns

### Pattern: Checking empty sequences

```python
# ✓ Correct - implicit false
if not users:
    return []

if items:
    process(items)

# ❌ Wrong - explicit length check
if len(users) == 0:  # Verbose
    return []

if len(items) > 0:  # Verbose
    process(items)
```

### Pattern: Boolean checks

```python
# ✓ Correct - implicit check
if is_valid:
    proceed()

if not is_active:
    return

# ❌ Wrong - explicit comparison
if is_valid == True:  # Redundant
    proceed()

if is_active == False:  # Redundant
    return
```

### Pattern: Default arguments (no mutables!)

```python
# ✓ Correct - None default, create inside
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items

# ❌ Wrong - mutable default
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)  # BUG: same list reused!
    return items
```

### Pattern: String formatting

```python
# ✓ Correct - f-strings
name = "Alice"
age = 30
message = f"User {name} is {age} years old"

# ✓ Correct - logging with %
logger.info("User %s logged in", username)  # Lazy evaluation

# ❌ Wrong - string concatenation
message = "User " + name + " is " + str(age) + " years old"
```

### Pattern: String accumulation

```python
# ✓ Correct - list + join
parts: list[str] = []
for item in items:
    parts.append(f"Item: {item}")
result = "\n".join(parts)

# ❌ Wrong - += in loop (O(n²) complexity)
result = ""
for item in items:
    result += f"Item: {item}\n"
```

### Pattern: File handling

```python
# ✓ Correct - context manager
with open("data.txt") as f:
    data = f.read()

# ✓ Correct - multiple files
with (
    open("input.txt") as infile,
    open("output.txt", "w") as outfile,
):
    outfile.write(infile.read())

# ❌ Wrong - manual close
f = open("data.txt")
data = f.read()
f.close()  # Can be skipped if exception occurs
```

### Pattern: Lambda functions

```python
# ✓ Correct - simple one-liner
sorted_items = sorted(items, key=lambda x: x.priority)

# ✓ Correct - use operator module
from operator import attrgetter
sorted_items = sorted(items, key=attrgetter('priority'))

# ❌ Wrong - complex lambda (>60-80 chars)
result = map(
    lambda x: x.value ** 2 if x.value > 0 else 0,
    items
)

# ✓ Better - named function
def square_positive(item: Item) -> int:
    return item.value ** 2 if item.value > 0 else 0

result = map(square_positive, items)
```

### Pattern: Fail fast (early return/raise)

```python
# ✓ Correct - fail fast
def process(data: dict[str, Any] | None) -> Result:
    if data is None:
        return Result.empty()

    if not data.get("valid"):
        raise ValidationError("Invalid data")

    if "required_field" not in data:
        raise ValueError("Missing required field")

    # Happy path at lowest indentation
    return Result(data)

# ❌ Wrong - deeply nested
def process(data: dict[str, Any] | None) -> Result:
    if data is not None:
        if data.get("valid"):
            if "required_field" in data:
                return Result(data)
            else:
                raise ValueError("Missing required field")
        else:
            raise ValidationError("Invalid data")
    else:
        return Result.empty()
```

---

## VIII. Security Patterns

### Pattern: Input validation

```python
# ✓ Correct - validate all inputs
def get_user(user_id: str) -> User:
    if not user_id or not user_id.isdigit():
        raise ValueError("Invalid user_id format")

    uid = int(user_id)
    if uid <= 0:
        raise ValueError("user_id must be positive")

    return fetch_user(uid)
```

### Pattern: SQL queries (prevent injection)

```python
# ✓ Correct - parameterized query
cursor.execute(
    "SELECT * FROM users WHERE email = ?",
    (email,)
)

# ❌ Wrong - string formatting (SQL injection!)
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### Pattern: Subprocess calls (prevent command injection)

```python
import subprocess

# ✓ Correct - list arguments
subprocess.run(["ls", "-l", directory], check=True)

# ❌ Wrong - shell=True (command injection!)
subprocess.run(f"ls -l {directory}", shell=True)
```

### Pattern: Path validation (prevent traversal)

```python
from pathlib import Path

# ✓ Correct - validate path stays in bounds
def read_user_file(filename: str) -> str:
    base_dir = Path("/var/data/users")
    file_path = (base_dir / filename).resolve()

    if not file_path.is_relative_to(base_dir):
        raise ValueError("Invalid file path")

    return file_path.read_text()
```

### Pattern: Secrets management

```python
import os

# ✓ Correct - environment variables
api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError("API_KEY not set")

# ❌ Wrong - hardcoded
api_key = "sk-1234567890"  # Never commit secrets!
```

---

## IX. Code Quality Checklist

Use this before marking code complete:

```
Type Safety:
  ☐ All parameters have type hints (Prefer Abstract: Sequence/Mapping)
  ☐ All returns have type hints (Prefer Concrete: list/dict)
  ☐ Use modern syntax (list not List, | not Union)
  ☐ No use of Any unless absolutely necessary
  ☐ Complex types use TypeAlias

Style:
  ☐ Lines ≤120 characters
  ☐ 4-space indentation
  ☐ 2 blank lines between top-level definitions
  ☐ 1 blank line between methods
  ☐ Imports grouped and sorted
  ☐ No trailing whitespace

Naming:
  ☐ Functions: lower_with_under
  ☐ Classes: CapWords
  ☐ Constants: CAPS_WITH_UNDER
  ☐ Private: _prefix

Correctness:
  ☐ No mutable default arguments
  ☐ None checks use is/is not
  ☐ Specific exception handling
  ☐ Exception chains use `from`
  ☐ Resources use context managers (with/async with)
  ☐ String accumulation uses list + join
  ☐ No bare except:
  ☐ No assert for validation
  ☐ Async: No blocking calls in async functions

Documentation:
  ☐ Public functions have docstrings
  ☐ Complex logic has comments
  ☐ Docstrings don't repeat type info
  ☐ Focus on "why" not "what"

Security:
  ☐ Input validation
  ☐ No hardcoded secrets
  ☐ Parameterized queries
  ☐ No shell=True
  ☐ Path validation
```

---

## X. Complete Example - Reference Implementation

```python
"""User file processing module.

This module provides functions for processing user-uploaded files
with validation and size limits.
"""

from collections.abc import Sequence
from pathlib import Path


class FileSizeError(Exception):
    """Raised when a file exceeds the maximum size limit."""


def process_user_files(
    user_id: int,
    file_paths: Sequence[Path],
    max_size_mb: int = 10,
) -> dict[str, list[str]]:
    """Process multiple user files and return extracted text.

    Reads and validates user-uploaded files, extracting text content
    while enforcing size limits to prevent resource exhaustion.

    Args:
        user_id: Unique identifier for the user (must be positive)
        file_paths: Paths to files to process
        max_size_mb: Maximum file size in megabytes (default: 10)

    Returns:
        Dictionary mapping filenames to lists of non-empty text lines

    Raises:
        ValueError: If user_id is invalid
        FileSizeError: If any file exceeds size limit
        FileNotFoundError: If any file path doesn't exist
    """
    # Validate inputs early (fail fast)
    if user_id <= 0:
        raise ValueError(f"Invalid user_id: {user_id}")

    if not file_paths:
        return {}

    max_size_bytes = max_size_mb * 1024 * 1024
    results: dict[str, list[str]] = {}

    for file_path in file_paths:
        # Check existence
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check size
        if file_path.stat().st_size > max_size_bytes:
            raise FileSizeError(
                f"File {file_path.name} exceeds {max_size_mb}MB limit"
            )

        # Process file with context manager
        with file_path.open() as f:
            lines = [line.strip() for line in f if line.strip()]
            results[file_path.name] = lines

    return results
```

**This example demonstrates:**
- ✓ Complete type annotations (modern syntax)
- ✓ Clear, descriptive naming
- ✓ Module and function docstrings
- ✓ Input validation (fail fast)
- ✓ Custom exception class
- ✓ Context manager for file handling
- ✓ Proper formatting (≤120 chars, 4 spaces)
- ✓ Security (file size limit)
- ✓ No mutable defaults
- ✓ Explicit None handling in checks

---

## XI. LLM Decision Guide

### When should I use `is None` vs truthiness check?

```
if x:              Use when: checking if collection/string is non-empty
if not x:          Use when: checking if collection/string is empty
if x is None:      Use when: specifically checking for None value
if x is not None:  Use when: checking value exists (not None)
```

### When should I use a docstring?

```
YES - Always:
  - Public functions/methods
  - Complex logic
  - Public classes
  - Modules

NO - Skip:
  - Private functions with obvious behavior
  - Very short functions (<3 lines, obvious)
  - Overridden methods with @override decorator
```

### When should I use TypeAlias?

```
YES - Use TypeAlias when:
  - Type appears 3+ times
  - Type is complex (nested dict/tuple)
  - Type has business meaning (UserId, UserData)

NO - Don't use when:
  - Type appears only 1-2 times
  - Type is simple (str, int, list[str])
```

### When should I break a long line?

```
Line length > 120 chars
  ├─ Function signature? → Break after each parameter
  ├─ Long expression? → Break at operators
  ├─ Long string? → Use implicit string concatenation or f-strings
  └─ Long import? → OK to exceed for imports
```

### When should I use `list` vs `Sequence` in parameters?

```
Parameter needs:
  ├─ Read-only access? → Use Sequence (more flexible)
  ├─ Need to modify? → Use list (or MutableSequence)
  └─ Need to iterate once? → Use Iterable (most flexible)

Return value:
  └─ Always use concrete type (list, dict, etc.)
```
