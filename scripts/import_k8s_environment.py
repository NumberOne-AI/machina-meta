#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Import and compare Kubernetes environment variables for local development.
>>>>>>> f18d61a (feat(scripts): add graphrag_cli.py using google-genai SDK and APOC)

CRITICALLY IMPORTANT: Development Commands (machina-python standard)
=====================================================================
Run these commands from the workspace root (machina-meta):

1. Type checking (strict mode):
   uv run --with mypy -- mypy --strict scripts/import_k8s_environment.py

2. Linting (curated strict ruleset):
   uvx ruff check --select=E,W,F,B,I,UP,N,S,PL,RUF --line-length 120 scripts/import_k8s_environment.py

3. Auto-fix lint errors:
   uvx ruff check --select=E,W,F,B,I,UP,N,S,PL,RUF --line-length 120 --fix scripts/import_k8s_environment.py

4. Formatting (120 char line length):
   uvx ruff format --line-length 120 scripts/import_k8s_environment.py

IMPORT MODE
-----------
Extract environment variables from a Kubernetes deployment and create a local .env file.

Usage:
    ./scripts/import_k8s_environment.py import -n tusdi-preview-92 -d tusdi-api

The script will:
1. Get the deployment spec from Kubernetes
2. Extract environment variables (direct values, ConfigMap refs, Secret refs)
3. Resolve ConfigMap and Secret values
4. Generate a non-world-readable .env file with export statements

Example output file: .env.tusdi-preview-92.tusdi-api

COMPARE MODE
------------
Compare two .env files and show differences (removed, added, changed, identical).

Usage:
    ./scripts/import_k8s_environment.py compare .env.old .env.new
    ./scripts/import_k8s_environment.py compare .env.old .env.new --json
    ./scripts/import_k8s_environment.py compare .env.old .env.new --no-identical
"""

from __future__ import annotations

import argparse
import base64
import json
import stat
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# ============================================================
# Color and Output Utilities
# ============================================================


class Color:
    """ANSI color codes for terminal output."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"


class Symbol:
    """Unicode symbols for output."""

    CHECK = "✓"
    CROSS = "✗"
    WARN = "⚠"


def print_color(color: str, message: str) -> None:
    """Print colored output."""
    print(f"{color}{message}{Color.NC}")  # noqa: T201


def print_header(title: str) -> None:
    """Print section header."""
    print()  # noqa: T201
    print_color(Color.CYAN, "=" * 60)
    print_color(Color.CYAN, title)
    print_color(Color.CYAN, "=" * 60)


def print_kv(key: str, value: str) -> None:
    """Print key-value pair."""
    print(f"  {key:<30} {value}")  # noqa: T201


# ============================================================
# Configuration
# ============================================================

WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()


# ============================================================
# Exceptions
# ============================================================


class K8sImportError(Exception):
    """Base exception for import errors."""


class KubectlError(K8sImportError):
    """Error running kubectl command."""


class ResourceNotFoundError(K8sImportError):
    """Kubernetes resource not found."""


# ============================================================
# Data Classes
# ============================================================


@dataclass
class EnvVar:
    """Represents an environment variable with its source."""

    name: str
    value: str | None = None
    source: str = "direct"
    source_name: str | None = None
    source_key: str | None = None
    error: str | None = None


@dataclass
class ImportResult:
    """Result of environment import operation."""

    namespace: str
    deployment: str
    container: str
    env_vars: dict[str, EnvVar] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class VarDiff:
    """A single variable difference."""

    name: str
    old_value: str | None
    new_value: str | None


@dataclass(frozen=True)
class CompareResult:
    """Result of comparing two .env files."""

    removed: tuple[VarDiff, ...]
    added: tuple[VarDiff, ...]
    changed: tuple[VarDiff, ...]
    identical: tuple[VarDiff, ...]


# ============================================================
# Kubectl Utilities
# ============================================================


def run_kubectl(
    args: Sequence[str],
    namespace: str | None = None,
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a kubectl command and return the result."""
    cmd: list[str] = ["kubectl"]
    if namespace:
        cmd.extend(["-n", namespace])
    cmd.extend(args)

    try:
        result = subprocess.run(  # noqa: S603
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as err:
        msg = "kubectl not found in PATH"
        raise KubectlError(msg) from err

    if check and result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip()
        if "not found" in error_msg.lower() or "NotFound" in error_msg:
            raise ResourceNotFoundError(error_msg)
        msg = f"kubectl failed: {error_msg}"
        raise KubectlError(msg)

    return result


def get_deployment(namespace: str, deployment: str) -> dict[str, object]:
    """Get deployment spec from Kubernetes."""
    result = run_kubectl(
        ["get", "deployment", deployment, "-o", "json"],
        namespace=namespace,
    )
    return json.loads(result.stdout)  # type: ignore[no-any-return]


def get_configmap(namespace: str, name: str) -> dict[str, object] | None:
    """Get ConfigMap data from Kubernetes."""
    try:
        result = run_kubectl(
            ["get", "configmap", name, "-o", "json"],
            namespace=namespace,
        )
        return json.loads(result.stdout)  # type: ignore[no-any-return]
    except ResourceNotFoundError:
        return None


def get_secret(namespace: str, name: str) -> dict[str, object] | None:
    """Get Secret data from Kubernetes (base64 decoded)."""
    try:
        result = run_kubectl(
            ["get", "secret", name, "-o", "json"],
            namespace=namespace,
        )
    except ResourceNotFoundError:
        return None

    secret: dict[str, object] = json.loads(result.stdout)

    # Decode base64 values
    data = secret.get("data")
    if isinstance(data, dict):
        decoded: dict[str, str] = {}
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    decoded[key] = base64.b64decode(value).decode("utf-8")
                except (ValueError, UnicodeDecodeError):
                    decoded[key] = value
        secret["data"] = decoded

    return secret


# ============================================================
# Environment Variable Resolution
# ============================================================


def resolve_configmap_ref(
    name: str,
    value_from: dict[str, object],
    namespace: str,
    configmap_cache: dict[str, dict[str, object] | None],
) -> EnvVar:
    """Resolve configMapKeyRef."""
    ref = value_from.get("configMapKeyRef")
    if not isinstance(ref, dict):
        return EnvVar(name=name, source="configmap", error="Invalid ref")

    cm_name = ref.get("name", "")
    cm_key = ref.get("key", "")
    optional = ref.get("optional", False)

    if not isinstance(cm_name, str) or not isinstance(cm_key, str):
        return EnvVar(name=name, source="configmap", error="Invalid ref keys")

    if cm_name not in configmap_cache:
        configmap_cache[cm_name] = get_configmap(namespace, cm_name)

    cm = configmap_cache[cm_name]
    if cm is None:
        error = f"ConfigMap '{cm_name}' not found"
        if optional:
            error += " (optional)"
        return EnvVar(
            name=name,
            source="configmap",
            source_name=cm_name,
            source_key=cm_key,
            error=error,
        )

    cm_data = cm.get("data", {})
    if not isinstance(cm_data, dict) or cm_key not in cm_data:
        error = f"Key '{cm_key}' not found in ConfigMap '{cm_name}'"
        if optional:
            error += " (optional)"
        return EnvVar(
            name=name,
            source="configmap",
            source_name=cm_name,
            source_key=cm_key,
            error=error,
        )

    value = cm_data[cm_key]
    return EnvVar(
        name=name,
        value=str(value) if value is not None else None,
        source="configmap",
        source_name=cm_name,
        source_key=cm_key,
    )


def resolve_secret_ref(
    name: str,
    value_from: dict[str, object],
    namespace: str,
    secret_cache: dict[str, dict[str, object] | None],
) -> EnvVar:
    """Resolve secretKeyRef."""
    ref = value_from.get("secretKeyRef")
    if not isinstance(ref, dict):
        return EnvVar(name=name, source="secret", error="Invalid ref")

    secret_name = ref.get("name", "")
    secret_key = ref.get("key", "")
    optional = ref.get("optional", False)

    if not isinstance(secret_name, str) or not isinstance(secret_key, str):
        return EnvVar(name=name, source="secret", error="Invalid ref keys")

    if secret_name not in secret_cache:
        secret_cache[secret_name] = get_secret(namespace, secret_name)

    secret = secret_cache[secret_name]
    if secret is None:
        error = f"Secret '{secret_name}' not found"
        if optional:
            error += " (optional)"
        return EnvVar(
            name=name,
            source="secret",
            source_name=secret_name,
            source_key=secret_key,
            error=error,
        )

    secret_data = secret.get("data", {})
    if not isinstance(secret_data, dict) or secret_key not in secret_data:
        error = f"Key '{secret_key}' not found in Secret '{secret_name}'"
        if optional:
            error += " (optional)"
        return EnvVar(
            name=name,
            source="secret",
            source_name=secret_name,
            source_key=secret_key,
            error=error,
        )

    value = secret_data[secret_key]
    return EnvVar(
        name=name,
        value=str(value) if value is not None else None,
        source="secret",
        source_name=secret_name,
        source_key=secret_key,
    )


def resolve_field_ref(name: str, value_from: dict[str, object]) -> EnvVar:
    """Resolve fieldRef (pod metadata)."""
    field_ref = value_from.get("fieldRef")
    field_path = ""
    if isinstance(field_ref, dict):
        fp = field_ref.get("fieldPath", "")
        field_path = str(fp) if fp else ""
    return EnvVar(
        name=name,
        source="fieldref",
        source_name=field_path,
        error=f"FieldRef '{field_path}' cannot be resolved locally",
    )


def resolve_resource_field_ref(
    name: str,
    value_from: dict[str, object],
) -> EnvVar:
    """Resolve resourceFieldRef (container resources)."""
    resource_ref = value_from.get("resourceFieldRef")
    resource = ""
    if isinstance(resource_ref, dict):
        r = resource_ref.get("resource", "")
        resource = str(r) if r else ""
    return EnvVar(
        name=name,
        source="resourcefieldref",
        source_name=resource,
        error=f"ResourceFieldRef '{resource}' cannot be resolved locally",
    )


def resolve_value_from(
    name: str,
    value_from: dict[str, object],
    namespace: str,
    configmap_cache: dict[str, dict[str, object] | None],
    secret_cache: dict[str, dict[str, object] | None],
) -> EnvVar:
    """Resolve a valueFrom reference."""
    if "configMapKeyRef" in value_from:
        return resolve_configmap_ref(
            name,
            value_from,
            namespace,
            configmap_cache,
        )

    if "secretKeyRef" in value_from:
        return resolve_secret_ref(
            name,
            value_from,
            namespace,
            secret_cache,
        )

    if "fieldRef" in value_from:
        return resolve_field_ref(name, value_from)

    if "resourceFieldRef" in value_from:
        return resolve_resource_field_ref(name, value_from)

    return EnvVar(name=name, source="unknown", error="Unknown valueFrom type")


def resolve_env_var(
    env_spec: dict[str, object],
    namespace: str,
    configmap_cache: dict[str, dict[str, object] | None],
    secret_cache: dict[str, dict[str, object] | None],
) -> EnvVar:
    """Resolve a single environment variable specification."""
    name = env_spec.get("name", "")
    if not isinstance(name, str):
        name = ""

    # Direct value
    if "value" in env_spec:
        value = env_spec["value"]
        return EnvVar(
            name=name,
            value=str(value) if value is not None else None,
            source="direct",
        )

    # ValueFrom reference
    value_from = env_spec.get("valueFrom", {})
    if not isinstance(value_from, dict):
        return EnvVar(name=name, source="unknown", error="Invalid valueFrom")

    return resolve_value_from(
        name,
        value_from,
        namespace,
        configmap_cache,
        secret_cache,
    )


def resolve_env_from_configmap(
    ref: dict[str, object],
    prefix: str,
    namespace: str,
    configmap_cache: dict[str, dict[str, object] | None],
) -> tuple[dict[str, EnvVar], list[str]]:
    """Resolve configMapRef from envFrom."""
    env_vars: dict[str, EnvVar] = {}
    errors: list[str] = []

    cm_name_raw = ref.get("name", "")
    cm_name = str(cm_name_raw) if cm_name_raw else ""
    optional = ref.get("optional", False)

    if cm_name not in configmap_cache:
        configmap_cache[cm_name] = get_configmap(namespace, cm_name)

    cm = configmap_cache[cm_name]
    if cm is None:
        if not optional:
            errors.append(f"ConfigMap '{cm_name}' not found (envFrom)")
        return env_vars, errors

    cm_data = cm.get("data", {})
    if isinstance(cm_data, dict):
        for key, value in cm_data.items():
            env_name = f"{prefix}{key}"
            env_vars[env_name] = EnvVar(
                name=env_name,
                value=str(value) if value is not None else None,
                source="configmap",
                source_name=cm_name,
                source_key=key,
            )

    return env_vars, errors


def resolve_env_from_secret(
    ref: dict[str, object],
    prefix: str,
    namespace: str,
    secret_cache: dict[str, dict[str, object] | None],
) -> tuple[dict[str, EnvVar], list[str]]:
    """Resolve secretRef from envFrom."""
    env_vars: dict[str, EnvVar] = {}
    errors: list[str] = []

    secret_name_raw = ref.get("name", "")
    secret_name = str(secret_name_raw) if secret_name_raw else ""
    optional = ref.get("optional", False)

    if secret_name not in secret_cache:
        secret_cache[secret_name] = get_secret(namespace, secret_name)

    secret = secret_cache[secret_name]
    if secret is None:
        if not optional:
            errors.append(f"Secret '{secret_name}' not found (envFrom)")
        return env_vars, errors

    secret_data = secret.get("data", {})
    if isinstance(secret_data, dict):
        for key, value in secret_data.items():
            env_name = f"{prefix}{key}"
            env_vars[env_name] = EnvVar(
                name=env_name,
                value=str(value) if value is not None else None,
                source="secret",
                source_name=secret_name,
                source_key=key,
            )

    return env_vars, errors


def resolve_env_from(
    env_from_spec: dict[str, object],
    namespace: str,
    configmap_cache: dict[str, dict[str, object] | None],
    secret_cache: dict[str, dict[str, object] | None],
) -> tuple[dict[str, EnvVar], list[str]]:
    """Resolve envFrom specification (entire ConfigMap or Secret)."""
    env_vars: dict[str, EnvVar] = {}
    errors: list[str] = []
    prefix_raw = env_from_spec.get("prefix", "")
    prefix = str(prefix_raw) if prefix_raw else ""

    # ConfigMapRef
    if "configMapRef" in env_from_spec:
        ref = env_from_spec["configMapRef"]
        if isinstance(ref, dict):
            cm_vars, cm_errors = resolve_env_from_configmap(
                ref,
                prefix,
                namespace,
                configmap_cache,
            )
            env_vars.update(cm_vars)
            errors.extend(cm_errors)

    # SecretRef
    if "secretRef" in env_from_spec:
        ref = env_from_spec["secretRef"]
        if isinstance(ref, dict):
            secret_vars, secret_errors = resolve_env_from_secret(
                ref,
                prefix,
                namespace,
                secret_cache,
            )
            env_vars.update(secret_vars)
            errors.extend(secret_errors)

    return env_vars, errors


def get_containers_from_deployment(
    deploy: dict[str, object],
) -> tuple[list[object], str | None]:
    """Extract containers list from deployment. Returns (containers, error)."""
    spec = deploy.get("spec", {})
    if not isinstance(spec, dict):
        return [], "Invalid deployment spec"

    template = spec.get("template", {})
    if not isinstance(template, dict):
        return [], "Invalid deployment template"

    pod_spec = template.get("spec", {})
    if not isinstance(pod_spec, dict):
        return [], "Invalid pod spec"

    containers = pod_spec.get("containers", [])
    if not isinstance(containers, list) or not containers:
        return [], "No containers found in deployment"

    return containers, None


def select_container(
    containers: list[object],
    container_name: str | None,
) -> tuple[dict[str, object] | None, str | None, str | None]:
    """Select container from list. Returns (container_spec, error, warning)."""
    if container_name:
        for c in containers:
            if isinstance(c, dict) and c.get("name") == container_name:
                return c, None, None
        available = [str(c.get("name", "unnamed")) for c in containers if isinstance(c, dict)]
        return (
            None,
            (f"Container '{container_name}' not found. Available: {', '.join(available)}"),
            None,
        )

    first = containers[0]
    if not isinstance(first, dict):
        return None, "Invalid container spec", None

    warning = None
    if len(containers) > 1:
        cname = first.get("name", "unnamed")
        warning = f"Multiple containers found, using first: '{cname}'"

    return first, None, warning


def process_container_env(
    container_spec: dict[str, object],
    namespace: str,
    result: ImportResult,
) -> None:
    """Process environment variables from a container spec."""
    configmap_cache: dict[str, dict[str, object] | None] = {}
    secret_cache: dict[str, dict[str, object] | None] = {}

    # Process envFrom first (lower priority, can be overridden by env)
    env_from_list = container_spec.get("envFrom", [])
    if isinstance(env_from_list, list):
        for env_from_spec in env_from_list:
            if isinstance(env_from_spec, dict):
                vars_dict, errors = resolve_env_from(
                    env_from_spec,
                    namespace,
                    configmap_cache,
                    secret_cache,
                )
                result.env_vars.update(vars_dict)
                result.errors.extend(errors)

    # Process individual env vars (higher priority)
    env_list = container_spec.get("env", [])
    if isinstance(env_list, list):
        for env_spec in env_list:
            if isinstance(env_spec, dict):
                env_var = resolve_env_var(
                    env_spec,
                    namespace,
                    configmap_cache,
                    secret_cache,
                )
                result.env_vars[env_var.name] = env_var
                if env_var.error:
                    if "optional" not in env_var.error.lower():
                        result.errors.append(f"{env_var.name}: {env_var.error}")
                    else:
                        result.warnings.append(
                            f"{env_var.name}: {env_var.error}",
                        )


def import_environment(
    namespace: str,
    deployment: str,
    container: str | None = None,
) -> ImportResult:
    """Import environment variables from a Kubernetes deployment."""
    result = ImportResult(
        namespace=namespace,
        deployment=deployment,
        container="",
    )

    # Get deployment spec
    try:
        deploy = get_deployment(namespace, deployment)
    except ResourceNotFoundError:
        result.errors.append(
            f"Deployment '{deployment}' not found in namespace '{namespace}'",
        )
        return result
    except KubectlError as e:
        result.errors.append(str(e))
        return result

    # Extract containers
    containers, error = get_containers_from_deployment(deploy)
    if error:
        result.errors.append(error)
        return result

    # Select container
    container_spec, error, warning = select_container(containers, container)
    if error:
        result.errors.append(error)
        return result
    if warning:
        result.warnings.append(warning)

    # Should not happen after select_container validation
    if container_spec is None:
        result.errors.append("Failed to select container")
        return result

    cname_raw = container_spec.get("name", "unnamed")
    result.container = str(cname_raw) if cname_raw else "unnamed"

    # Process environment variables
    process_container_env(container_spec, namespace, result)

    return result


# ============================================================
# File Generation
# ============================================================


def escape_shell_value(value: str) -> str:
    """Escape a value for shell export statement."""
    if "'" not in value:
        return f"'{value}'"
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"$'{escaped}'"


def generate_metadata_header(
    result: ImportResult,
    output_path: Path,
) -> list[str]:
    """Generate metadata header lines for .env file."""
    now = datetime.now(tz=timezone.utc).isoformat()
    lines = [
        "# Environment variables imported from Kubernetes",
        f"# Namespace: {result.namespace}",
        f"# Deployment: {result.deployment}",
        f"# Container: {result.container}",
        f"# Generated: {now}",
        "#",
        f"# Usage: source {output_path.name}",
        "#",
    ]

    if result.warnings:
        lines.append("# Warnings:")
        lines.extend(f"#   - {w}" for w in result.warnings)
        lines.append("#")

    if result.errors:
        lines.append("# Errors (some variables may be missing):")
        lines.extend(f"#   - {e}" for e in result.errors)
        lines.append("#")

    lines.append("")
    return lines


def group_env_vars_by_source(
    env_vars: dict[str, EnvVar],
) -> dict[str, list[EnvVar]]:
    """Group environment variables by their source."""
    sources: dict[str, list[EnvVar]] = {}
    for env_var in sorted(env_vars.values(), key=lambda v: v.name):
        source_key = env_var.source
        if env_var.source in ("configmap", "secret") and env_var.source_name:
            source_key = f"{env_var.source}:{env_var.source_name}"
        if source_key not in sources:
            sources[source_key] = []
        sources[source_key].append(env_var)
    return sources


def get_source_comment(source_key: str) -> str:
    """Get comment for a source key."""
    if source_key == "direct":
        return "# Direct values"
    if source_key.startswith("configmap:"):
        cm_name = source_key.split(":", 1)[1]
        return f"# From ConfigMap: {cm_name}"
    if source_key.startswith("secret:"):
        secret_name = source_key.split(":", 1)[1]
        return f"# From Secret: {secret_name}"
    return f"# Source: {source_key}"


def generate_env_lines(
    sources: dict[str, list[EnvVar]],
    *,
    include_comments: bool,
) -> list[str]:
    """Generate environment variable export lines."""
    lines: list[str] = []
    for source_key in sorted(sources.keys()):
        env_vars = sources[source_key]

        if include_comments:
            lines.append(get_source_comment(source_key))

        for env_var in env_vars:
            if env_var.value is not None:
                escaped_value = escape_shell_value(env_var.value)
                lines.append(f"export {env_var.name}={escaped_value}")
            elif include_comments:
                error = env_var.error or "Unknown error"
                lines.append(f"# export {env_var.name}=  # Error: {error}")

        lines.append("")
    return lines


def generate_env_file(
    result: ImportResult,
    output_path: Path,
    *,
    include_comments: bool = True,
    include_metadata: bool = True,
) -> None:
    """Generate .env file from import result."""
    lines: list[str] = []

    if include_metadata:
        lines.extend(generate_metadata_header(result, output_path))

    sources = group_env_vars_by_source(result.env_vars)
    lines.extend(generate_env_lines(sources, include_comments=include_comments))

    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))

    # Set permissions to 600 (owner read/write only) - non-world-readable
    output_path.chmod(stat.S_IRUSR | stat.S_IWUSR)


# ============================================================
# Environment File Parsing (for comparison)
# ============================================================


def parse_env_line(line: str) -> tuple[str, str] | None:
    """Parse a single .env line. Returns (name, value) or None if not a variable."""
    stripped = line.strip()

    # Skip empty lines and comments
    if not stripped or stripped.startswith("#"):
        return None

    # Handle 'export NAME=value' format
    if stripped.startswith("export "):
        stripped = stripped[7:]  # Remove 'export '

    # Find the first '=' sign
    eq_pos = stripped.find("=")
    if eq_pos == -1:
        return None

    name = stripped[:eq_pos].strip()
    raw_value = stripped[eq_pos + 1 :]

    # Validate variable name
    if not name or not name.replace("_", "").isalnum():
        return None

    # Parse the value (handle quoting)
    value = parse_quoted_value(raw_value)
    return (name, value)


def parse_quoted_value(raw_value: str) -> str:
    """Parse a potentially quoted value from .env file."""
    raw_value = raw_value.strip()

    if not raw_value:
        return ""

    # Single-quoted: 'value'
    if raw_value.startswith("'") and raw_value.endswith("'") and len(raw_value) >= 2:
        return raw_value[1:-1]

    # Double-quoted: "value"
    if raw_value.startswith('"') and raw_value.endswith('"') and len(raw_value) >= 2:
        # Handle escape sequences in double quotes
        inner = raw_value[1:-1]
        return inner.replace('\\"', '"').replace("\\\\", "\\")

    # ANSI-C quoting: $'value'
    if raw_value.startswith("$'") and raw_value.endswith("'") and len(raw_value) >= 3:
        inner = raw_value[2:-1]
        return inner.replace("\\'", "'").replace("\\\\", "\\")

    # Unquoted value
    return raw_value


def parse_env_file(file_path: Path) -> dict[str, str]:
    """Parse a .env file and return dict of name -> value."""
    env_vars: dict[str, str] = {}

    if not file_path.exists():
        msg = f"File not found: {file_path}"
        raise FileNotFoundError(msg)

    content = file_path.read_text(encoding="utf-8")

    for line in content.splitlines():
        parsed = parse_env_line(line)
        if parsed is not None:
            name, value = parsed
            env_vars[name] = value

    return env_vars


def compare_env_files(*, old_path: Path, new_path: Path) -> CompareResult:
    """Compare two .env files and return categorized differences."""
    old_vars = parse_env_file(old_path)
    new_vars = parse_env_file(new_path)

    old_names = set(old_vars.keys())
    new_names = set(new_vars.keys())

    removed: list[VarDiff] = []
    added: list[VarDiff] = []
    changed: list[VarDiff] = []
    identical: list[VarDiff] = []

    # Removed: in old but not in new
    for name in sorted(old_names - new_names):
        removed.append(VarDiff(name=name, old_value=old_vars[name], new_value=None))

    # Added: in new but not in old
    for name in sorted(new_names - old_names):
        added.append(VarDiff(name=name, old_value=None, new_value=new_vars[name]))

    # Check common variables
    for name in sorted(old_names & new_names):
        old_val = old_vars[name]
        new_val = new_vars[name]
        if old_val == new_val:
            identical.append(VarDiff(name=name, old_value=old_val, new_value=new_val))
        else:
            changed.append(VarDiff(name=name, old_value=old_val, new_value=new_val))

    return CompareResult(
        removed=tuple(removed),
        added=tuple(added),
        changed=tuple(changed),
        identical=tuple(identical),
    )


# ============================================================
# Compare Output
# ============================================================


def truncate_value(value: str | None, *, max_length: int = 50) -> str:
    """Truncate a value for display, handling None."""
    if value is None:
        return "(none)"
    if len(value) <= max_length:
        return repr(value)
    return repr(value[: max_length - 3] + "...")


def print_compare_section(
    *,
    title: str,
    color: str,
    items: tuple[VarDiff, ...],
    show_old: bool = False,
    show_new: bool = False,
    show_both: bool = False,
) -> None:
    """Print a section of comparison results."""
    if not items:
        return

    print()  # noqa: T201
    print_color(color, f"{title} ({len(items)}):")

    for diff in items:
        if show_both:
            print(f"  {diff.name}")  # noqa: T201
            print(f"    old: {truncate_value(diff.old_value)}")  # noqa: T201
            print(f"    new: {truncate_value(diff.new_value)}")  # noqa: T201
        elif show_old:
            print(f"  {diff.name} = {truncate_value(diff.old_value)}")  # noqa: T201
        elif show_new:
            print(f"  {diff.name} = {truncate_value(diff.new_value)}")  # noqa: T201
        else:
            print(f"  {diff.name}")  # noqa: T201


def print_compare_result(result: CompareResult, *, show_identical: bool = True) -> None:
    """Print comparison result in human-readable format."""
    print_header("Environment Comparison")

    total = len(result.removed) + len(result.added) + len(result.changed) + len(result.identical)
    print()  # noqa: T201
    print(f"  Total variables: {total}")  # noqa: T201
    print(f"    Removed:   {len(result.removed)}")  # noqa: T201
    print(f"    Added:     {len(result.added)}")  # noqa: T201
    print(f"    Changed:   {len(result.changed)}")  # noqa: T201
    print(f"    Identical: {len(result.identical)}")  # noqa: T201

    print_compare_section(title="REMOVED", color=Color.RED, items=result.removed, show_old=True)
    print_compare_section(title="ADDED", color=Color.GREEN, items=result.added, show_new=True)
    print_compare_section(title="CHANGED", color=Color.YELLOW, items=result.changed, show_both=True)

    if show_identical:
        print_compare_section(title="IDENTICAL", color=Color.CYAN, items=result.identical)

    print()  # noqa: T201


def output_compare_as_json(result: CompareResult) -> None:
    """Output comparison result as JSON."""
    output_data = {
        "removed": [{"name": d.name, "old_value": d.old_value} for d in result.removed],
        "added": [{"name": d.name, "new_value": d.new_value} for d in result.added],
        "changed": [{"name": d.name, "old_value": d.old_value, "new_value": d.new_value} for d in result.changed],
        "identical": [{"name": d.name, "value": d.old_value} for d in result.identical],
        "summary": {
            "removed": len(result.removed),
            "added": len(result.added),
            "changed": len(result.changed),
            "identical": len(result.identical),
        },
    }
    print(json.dumps(output_data, indent=2))  # noqa: T201


# ============================================================
# CLI
# ============================================================


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Import Kubernetes environment variables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -n tusdi-preview-92 -d tusdi-api
  %(prog)s -n tusdi-dev -d tusdi-api -c api
  %(prog)s -n tusdi-preview-92 -d tusdi-api -o .env.preview

The script creates .env.<namespace>.<deployment> by default.
File permissions are set to 600 (owner read/write only).
""",
    )

    parser.add_argument(
        "-n",
        "--namespace",
        required=True,
        help="Kubernetes namespace",
    )
    parser.add_argument(
        "-d",
        "--deployment",
        required=True,
        help="Deployment name",
    )
    parser.add_argument(
        "-c",
        "--container",
        help="Container name (default: first container)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: .env.<namespace>.<deployment>)",
    )
    parser.add_argument(
        "--no-comments",
        action="store_true",
        help="Omit comments from output file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of .env file",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    return parser.parse_args()


def print_import_header(args: argparse.Namespace, output_path: Path) -> None:
    """Print import operation header."""
    print_header("Importing Kubernetes Environment")
    print()  # noqa: T201
    print_kv("Namespace", args.namespace)
    print_kv("Deployment", args.deployment)
    if args.container:
        print_kv("Container", args.container)
    print_kv("Output", str(output_path))
    print()  # noqa: T201


def print_import_summary(result: ImportResult) -> None:
    """Print import result summary."""
    print_kv("Container used", result.container)
    print_kv("Variables found", str(len(result.env_vars)))

    source_counts: dict[str, int] = {}
    for env_var in result.env_vars.values():
        source = env_var.source
        source_counts[source] = source_counts.get(source, 0) + 1

    for source, count in sorted(source_counts.items()):
        print_kv(f"  - {source}", str(count))


def print_warnings_and_errors(result: ImportResult) -> None:
    """Print warnings and errors from result."""
    if result.warnings:
        print()  # noqa: T201
        print_color(Color.YELLOW, f"{Symbol.WARN} Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")  # noqa: T201

    if result.errors:
        print()  # noqa: T201
        print_color(Color.YELLOW, f"{Symbol.WARN} Errors (some vars missing):")
        for error in result.errors:
            print(f"  - {error}")  # noqa: T201


def output_as_json(result: ImportResult) -> None:
    """Output result as JSON."""
    output_data = {
        "namespace": result.namespace,
        "deployment": result.deployment,
        "container": result.container,
        "variables": {
            name: {
                "value": var.value,
                "source": var.source,
                "source_name": var.source_name,
                "source_key": var.source_key,
                "error": var.error,
            }
            for name, var in sorted(result.env_vars.items())
        },
        "warnings": result.warnings,
        "errors": result.errors,
    }
    print(json.dumps(output_data, indent=2))  # noqa: T201


def output_env_file(
    result: ImportResult,
    output_path: Path,
    *,
    include_comments: bool,
    quiet: bool,
) -> None:
    """Generate and output .env file."""
    if not quiet:
        print()  # noqa: T201
        print_color(Color.CYAN, "Generating environment file...")

    generate_env_file(result, output_path, include_comments=include_comments)

    if not quiet:
        print()  # noqa: T201
        print_color(
            Color.GREEN,
            f"{Symbol.CHECK} Environment file created: {output_path}",
        )
        print()  # noqa: T201
        print("  File permissions: 600 (owner read/write only)")  # noqa: T201
        print()  # noqa: T201
        print("  Usage:")  # noqa: T201
        print(f"    source {output_path}")  # noqa: T201
        print()  # noqa: T201

        resolved = sum(1 for v in result.env_vars.values() if v.value is not None)
        unresolved = len(result.env_vars) - resolved

        if unresolved > 0:
            print_color(
                Color.YELLOW,
                f"  Note: {unresolved} variable(s) could not be resolved",
            )


def main() -> None:
    """Entry point for the script."""
    args = parse_args()

    # Determine output path
    output_path = Path(args.output) if args.output else WORKSPACE_ROOT / f".env.{args.namespace}.{args.deployment}"

    if not args.quiet:
        print_import_header(args, output_path)
        print_color(Color.CYAN, "Fetching deployment spec...")

    result = import_environment(
        namespace=args.namespace,
        deployment=args.deployment,
        container=args.container,
    )

    # Check for fatal errors
    if not result.env_vars and result.errors:
        print_color(Color.RED, f"\n{Symbol.CROSS} Import failed:")
        for error in result.errors:
            print(f"  - {error}")  # noqa: T201
        sys.exit(1)

    if not args.quiet:
        print_import_summary(result)
        print_warnings_and_errors(result)

    # Output
    if args.json:
        output_as_json(result)
    else:
        output_env_file(
            result,
            output_path,
            include_comments=not args.no_comments,
            quiet=args.quiet,
        )


if __name__ == "__main__":
    main()
