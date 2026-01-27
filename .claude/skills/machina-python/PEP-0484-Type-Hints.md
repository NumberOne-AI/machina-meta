# PEP 484 – Type Hints

**Source**: https://peps.python.org/pep-0484/

## Core Philosophy

PEP 484 introduces type hints as a standard for Python, emphasizing that **"no type checking happens at runtime."** Instead, type hints serve as a vocabulary for offline type checkers like mypy to analyze code before execution. Importantly: **"Python will remain a dynamically typed language"** with no intention to make type hints mandatory.

## Basic Annotation Syntax

Type hints use PEP 3107 function annotations with the arrow operator for returns:

```python
def greeting(name: str) -> str:
    return 'Hello ' + name
```

The document notes that "expressions whose type is a subtype of a specific argument type are also accepted for that argument."

## Fundamental Types and Constructs

### Basic Types
Built-in classes, user-defined classes, and abstract base classes all work as type hints.

### Type Aliases
Simple variable assignments create type aliases:
```python
Url = str
ConnectionOptions = dict[str, str]
```

### Optional Types
"As a shorthand for `Union[T1, None]` you can write `Optional[T1]`" for values that may be None.

**Modern syntax (Python 3.10+)**:
```python
def foo(arg: str | None) -> int | None:
    ...
```

### Union Types
Allow multiple acceptable types:
```python
Union[Employee, Sequence[Employee]]
# Modern syntax:
Employee | Sequence[Employee]
```

### Any Type
A special type where "every type is consistent with Any." Unannotated parameters default to Any.

## Generics and Type Variables

TypeVar enables generic functions and classes:

```python
from typing import TypeVar, Sequence

T = TypeVar('T')

def first(l: Sequence[T]) -> T:
    return l[0]
```

Constrained type variables limit options:

```python
AnyStr = TypeVar('AnyStr', str, bytes)
```

User-defined generic classes inherit from `Generic[T]`:

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class LoggedVar(Generic[T]):
    def get(self) -> T:
        ...
```

## Advanced Type Concepts

### Callable Types
Express function signatures:
```python
from typing import Callable

def feeder(get_next_item: Callable[[], str]) -> None:
    ...
```

Format: `Callable[[Arg1Type, Arg2Type], ReturnType]`

### Type[C]
References class objects themselves, not instances:
```python
from typing import Type

class User:
    ...

def new_user(user_class: Type[User]) -> User:
    return user_class()
```

### NoReturn
Marks functions that never return normally (raising exceptions instead):
```python
from typing import NoReturn

def stop() -> NoReturn:
    raise RuntimeError('Stopped')
```

### Covariance/Contravariance
Type variables support `covariant=True` or `contravariant=True` for immutable and mutable containers respectively.

## Practical Guidelines

### Forward References
Use string literals for self-referential types to avoid NameError during class definition:

```python
class Tree:
    def __init__(self, left: 'Tree', right: 'Tree'):
        ...
```

Or use `from __future__ import annotations` (Python 3.7+).

### Type Comments
For Python 2.7 compatibility or when annotations aren't feasible:
```python
x = []  # type: List[int]
```

### TYPE_CHECKING Constant
Enables conditional imports only during type checking:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import expensive_mod
```

## Best Practices from the Specification

1. **Keep annotations simple** – "dynamically computed types are unlikely to be understood" by type checkers
2. **Use abstract collection types** (Mapping, Sequence, Iterable) for function arguments rather than concrete types (dict, list)
3. **Capitalize type alias names** since they represent user-defined types
4. **Mark functions that shouldn't be type-checked** with `@no_type_check`
5. **Use `# type: ignore` comments** to suppress specific type errors when necessary
6. **Always add types for all function/method parameters and return values**
7. **Use `list` instead of `List`, `dict` instead of `Dict`** (modern Python 3.9+)
8. **Use `| None` instead of `Optional`** (modern Python 3.10+)

## Type Checker Expectations

Type checkers should "check the body of a checked function for consistency" and attempt inference using decorated methods. Methods without annotations default to `Any` for parameters, except self/cls arguments assume the containing class type.

---

**For this codebase**: We use modern type hints (Python 3.13) with mypy for static type checking. All functions must have complete type annotations.
