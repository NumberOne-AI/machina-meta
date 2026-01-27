# PEP 8 – Style Guide for Python Code

**Source**: https://peps.python.org/pep-0008/

## Code Layout

### Indentation
Use 4 spaces per indentation level. Continuation lines should align wrapped elements either vertically or using hanging indent. The 4-space rule is optional for continuation lines.

### Tabs or Spaces
"Spaces are the preferred indentation method." Tabs should only be used to maintain consistency with existing tab-indented code. Python disallows mixing tabs and spaces.

### Maximum Line Length
Limit all lines to a maximum of 79 characters. For docstrings or comments, limit to 72 characters. Teams may increase to 99 characters if agreed upon, provided comments remain at 72.

### Binary Operator Line Breaks
Break before binary operators rather than after them. As the guide states, "Following the tradition from mathematics usually results in more readable code."

### Blank Lines
- Surround top-level function and class definitions with two blank lines
- Use single blank lines between method definitions inside classes
- Use blank lines sparingly within functions to indicate logical sections

### Imports
- Place imports at the top of files, after module comments and docstrings
- Organize in groups: standard library, third-party, local application (with blank lines between)
- Use absolute imports; explicit relative imports are acceptable for complex packages
- Avoid wildcard imports (`from module import *`)

## String Quotes
Single and double quotes are equivalent. Consistency matters most. Use the opposite quote type when a string contains quotes to avoid backslashes. For triple-quoted strings, always use double quotes to align with docstring conventions.

## Whitespace in Expressions

### Pet Peeves to Avoid
- Extraneous whitespace inside parentheses, brackets, or braces
- Space before commas, semicolons, or colons
- Space immediately before function call parentheses
- Space before indexing/slicing brackets
- Multiple spaces around operators for alignment

### General Whitespace Rules
- Surround binary operators with single spaces: `=`, `+=`, `-=`, comparisons, Boolean operators
- No spaces around `=` for keyword arguments or unannotated default parameters
- Do use spaces around `=` when combining annotations with defaults

## Trailing Commas
Trailing commas are mandatory for single-element tuples. They're helpful in version-controlled lists expected to grow over time, with each item on its own line and the closing delimiter on a separate line.

## Comments

### Block Comments
Apply to code that follows them, indented to the same level. Each line starts with `#` and a space. Separate paragraphs with a line containing only `#`.

### Inline Comments
Use sparingly. Separate from statements by at least two spaces. Start with `#` and a space. Avoid stating the obvious.

### Docstrings
"Write docstrings for all public modules, functions, classes, and methods." For multiline docstrings, place the closing `"""` on its own line. For one-liners, keep it on the same line.

## Naming Conventions

### Styles Recognized
- `lowercase` and `lower_case_with_underscores`
- `UPPERCASE` and `UPPER_CASE_WITH_UNDERSCORES`
- `CapitalizedWords` (CapWords/CamelCase)
- `mixedCase`

### Special Forms
- `_single_leading_underscore`: weak "internal use" indicator
- `single_trailing_underscore_`: avoids keyword conflicts
- `__double_leading_underscore`: invokes name mangling in classes
- `__double_leading_and_trailing_underscore__`: "magic" attributes only per documentation

### Naming Standards by Type

**Packages and Modules**: Short, all-lowercase names. Underscores acceptable in modules if they improve readability.

**Classes**: Use CapWords convention. When uppercase acronyms appear in names, capitalize all letters (e.g., `HTTPServerError`).

**Functions and Variables**: Lowercase with underscores. `mixedCase` allowed only where that's the prevailing style for backwards compatibility.

**Constants**: All capitals with underscores separating words (e.g., `MAX_OVERFLOW`).

**Function and Method Arguments**:
- Use `self` for instance methods
- Use `cls` for class methods
- Append trailing underscore rather than abbreviate if argument name clashes with keywords

**Method Names and Instance Variables**: Follow function naming rules. Use one leading underscore for non-public items. Use two leading underscores only to avoid name conflicts in subclasses (invokes name mangling).

**Type Variables**: Use CapWords with short names (`T`, `AnyStr`, `Num`). Add `_co` or `_contra` suffixes for covariant or contravariant behavior.

**Exceptions**: Use class naming convention with "Error" suffix for error exceptions.

## Programming Recommendations

### Comparisons and Truthiness
- **Compare to singletons like `None` using `is` or `is not`, never equality operators**
- Use `is not` rather than `not ... is` for readability
- Use `isinstance()` for type checking, not direct type comparison
- Don't compare boolean values to `True` or `False` using `==`

### Sequences
For empty sequences (strings, lists, tuples), leverage the fact that they're falsy:
```python
# Correct
if not seq:
if seq:

# Wrong
if len(seq):
if not len(seq):
```

### String Operations
Use `.startswith()` and `.endswith()` instead of slicing to check prefixes/suffixes.

### Exception Handling
- Derive exceptions from `Exception`, not `BaseException`
- Catch specific exceptions rather than using bare `except:` clauses
- Limit the `try` clause to minimum necessary code
- Use `with` statements for resource management
- Use exception chaining appropriately with `raise X from Y`

### Lambda and Function Definitions
"Always use a def statement instead of an assignment statement that binds a lambda expression directly to an identifier." This preserves function names for tracebacks.

### Return Statements
Be consistent: either all return statements return expressions, or none do. Use explicit `return None` where appropriate.

### Context Managers
Invoke through separate functions/methods when doing more than acquiring and releasing resources.

## Function and Variable Annotations

Function annotations should follow PEP 484 syntax. Type checkers are optional tools—Python interpreters don't enforce annotations by default.

Variable annotations (PEP 526) should have:
- Single space after colons
- No space before colons
- Exactly one space on both sides of `=` when assigning values

---

**Core Philosophy**: "Code is read much more often than it is written." Prioritize readability and consistency, but use judgment—consistency within a module matters most, and backward compatibility shouldn't be broken just to comply with PEP 8.
