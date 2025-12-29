#!/usr/bin/env python3
"""
Codebase Language Scanner

Scans the machina-meta workspace to analyze programming languages,
file types, and generate statistics for LANGUAGES.md report.

Usage:
    python scripts/scan_languages.py [--output OUTPUT] [--verbose]

Output:
    Raw JSON data with file statistics, line counts, and language distribution.
"""

import argparse
import json
import os
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class FileStats:
    """Statistics for a single file."""

    path: str
    extension: str
    language: str
    lines: int
    size_bytes: int
    repo: str
    component: str


@dataclass
class LanguageStats:
    """Aggregated statistics for a language."""

    language: str
    extensions: list[str]
    files: int
    lines: int
    size_bytes: int
    repos: list[str]
    avg_lines_per_file: float


@dataclass
class RepoStats:
    """Statistics for a repository."""

    repo: str
    total_files: int
    total_lines: int
    total_size: int
    languages: dict[str, dict[str, Any]]


@dataclass
class ComponentStats:
    """Statistics for a component within a repository."""

    repo: str
    component: str
    total_files: int
    total_lines: int
    total_size: int
    languages: dict[str, dict[str, Any]]


@dataclass
class ScanResult:
    """Complete scan result."""

    scan_date: str
    repos: list[str]
    total_files: int
    total_lines: int
    total_size: int
    files: list[dict[str, Any]]
    languages: dict[str, dict[str, Any]]
    repos_stats: dict[str, dict[str, Any]]
    components_stats: dict[str, dict[str, Any]]


# Known programming language extensions (whitelist approach)
# Only files with these extensions will be included in the scan
LANGUAGE_MAP = {
    # Python
    ".py": "Python",
    ".pyi": "Python",
    # JavaScript/TypeScript
    ".ts": "TypeScript",
    ".tsx": "TypeScript (JSX)",
    ".js": "JavaScript",
    ".jsx": "JavaScript (JSX)",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    # Data formats
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".xml": "XML",
    ".csv": "CSV",
    # Documentation
    ".md": "Markdown",
    ".rst": "reStructuredText",
    ".txt": "Text",
    ".adoc": "AsciiDoc",
    # Shell scripts
    ".sh": "Shell",
    ".bash": "Bash",
    ".zsh": "Zsh",
    ".fish": "Fish",
    # Configuration
    ".ini": "INI",
    ".cfg": "Config",
    ".conf": "Config",
    ".env": "Environment",
    # Web
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "SASS",
    ".less": "LESS",
    ".svg": "SVG",
    # Frameworks
    ".svelte": "Svelte",
    ".vue": "Vue",
    # Databases
    ".cypher": "Cypher",
    ".cql": "Cypher",
    ".sql": "SQL",
    # Infrastructure
    ".tf": "Terraform",
    ".tfvars": "Terraform",
    ".dockerfile": "Dockerfile",
    # GraphQL
    ".graphql": "GraphQL",
    ".gql": "GraphQL",
    # Protocol Buffers
    ".proto": "Protocol Buffers",
    # Package management
    ".lock": "Lock File",
    # Nix
    ".nix": "Nix",
    # Systems languages
    ".c": "C",
    ".h": "C Header",
    ".cpp": "C++",
    ".cxx": "C++",
    ".cc": "C++",
    ".hpp": "C++ Header",
    ".hxx": "C++ Header",
    ".go": "Go",
    ".rs": "Rust",
    # JVM languages
    ".java": "Java",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".clj": "Clojure",
    ".cljs": "ClojureScript",
    # Ruby
    ".rb": "Ruby",
    ".rake": "Ruby",
    # PHP
    ".php": "PHP",
    # Scripting
    ".lua": "Lua",
    ".pl": "Perl",
    ".pm": "Perl",
    # Data science
    ".r": "R",
    ".jl": "Julia",
    ".ipynb": "Jupyter Notebook",
    # Functional
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".erl": "Erlang",
    ".hs": "Haskell",
    # Swift
    ".swift": "Swift",
    # Objective-C
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    # Dart
    ".dart": "Dart",
    # Other
    ".prisma": "Prisma",
    ".proto": "Protobuf",
}

# Special filename mappings
SPECIAL_FILES = {
    "Dockerfile": "Dockerfile",
    "Makefile": "Makefile",
    "makefile": "Makefile",
    "justfile": "Just",
    "Justfile": "Just",
    ".gitignore": "Gitignore",
    ".dockerignore": "Dockerignore",
    ".env": "Environment",
    ".env.example": "Environment",
}

# Note: No exclusion lists needed - we use git ls-files which automatically
# excludes .gitignore'd files, .venv, node_modules, etc.


def infer_component(repo: str, relative_path: Path) -> str:
    """Infer component name from file path within a repository."""
    parts = relative_path.parts

    if len(parts) == 1:
        # Root-level files
        return "root"

    # Repository-specific component inference
    if repo == "dem2":
        first_dir = parts[0]

        # Services (microservices architecture)
        if first_dir == "services" and len(parts) > 1:
            return f"services/{parts[1]}"

        # Shared code
        if first_dir == "shared":
            return "shared"

        # Packages
        if first_dir == "packages" and len(parts) > 1:
            return f"packages/{parts[1]}"

        # Infrastructure
        if first_dir == "infrastructure":
            return "infrastructure"

        # Tests
        if first_dir == "pdf_tests":
            return "pdf_tests"

        # Datasets
        if first_dir == "datasets":
            return "datasets"

        # Scripts
        if first_dir == "scripts":
            return "scripts"

        # Nix
        if first_dir == "nix":
            return "nix"

        return first_dir

    elif repo == "dem2-webui":
        first_dir = parts[0]

        # Source code
        if first_dir == "src" and len(parts) > 1:
            second_dir = parts[1]
            # App router structure
            if second_dir == "app":
                return "src/app"
            # Components
            if second_dir == "components":
                return "src/components"
            # Hooks
            if second_dir == "hooks":
                return "src/hooks"
            # Types
            if second_dir == "types":
                return "src/types"
            # Utils
            if second_dir == "utils":
                return "src/utils"
            # Lib
            if second_dir == "lib":
                return "src/lib"
            # Other src subdirs
            return f"src/{second_dir}"

        # Public assets
        if first_dir == "public":
            return "public"

        # Tests
        if first_dir == "tests" or first_dir == "test":
            return "tests"

        # Config
        if first_dir == "config":
            return "config"

        return first_dir

    elif repo == "dem2-infra":
        first_dir = parts[0]

        # Kubernetes/Helm
        if first_dir == "k8s" or first_dir == "kubernetes":
            return "k8s"

        # Helm charts
        if first_dir == "charts":
            return "charts"

        # Terraform
        if first_dir == "terraform":
            return "terraform"

        # Scripts
        if first_dir == "scripts":
            return "scripts"

        # ArgoCD
        if first_dir == "argocd":
            return "argocd"

        # Environments
        if first_dir == "environments" and len(parts) > 1:
            return f"environments/{parts[1]}"

        return first_dir

    elif repo == "medical-catalog":
        first_dir = parts[0]

        # Source code
        if first_dir == "src":
            return "src"

        # Tests
        if first_dir == "tests" or first_dir == "test":
            return "tests"

        # Data
        if first_dir == "data":
            return "data"

        # Scripts
        if first_dir == "scripts":
            return "scripts"

        return first_dir

    # Default: use first directory
    return parts[0] if parts else "root"


def get_language(path: Path) -> str | None:
    """Determine language from file path. Returns None for unknown/binary files."""
    # Check special filenames first
    if path.name in SPECIAL_FILES:
        return SPECIAL_FILES[path.name]

    # Check extension
    ext = path.suffix.lower()
    if ext in LANGUAGE_MAP:
        return LANGUAGE_MAP[ext]

    # Unknown extension - skip this file
    return None


def count_lines(file_path: Path) -> int:
    """Count lines in a file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        # Binary file or read error
        return 0


def get_git_tracked_files(repo_dir: Path) -> list[Path]:
    """Get list of git-tracked files in a repository."""
    import subprocess

    try:
        # Run git ls-files to get tracked files
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse output into list of paths
        files = []
        for line in result.stdout.strip().split("\n"):
            if line:
                file_path = repo_dir / line
                if file_path.is_file():
                    files.append(file_path)

        return files

    except subprocess.CalledProcessError:
        # Not a git repo or git not available, fall back to directory walking
        print(f"  Warning: Could not get git-tracked files for {repo_dir.name}, using directory scan")
        return list(repo_dir.rglob("*"))


def scan_directory(root_dir: Path, repo_name: str, verbose: bool = False) -> list[FileStats]:
    """Scan a directory and collect file statistics (git-tracked files only)."""
    stats: list[FileStats] = []

    # Get git-tracked files only
    git_files = get_git_tracked_files(root_dir)

    for path in git_files:
        if not path.is_file():
            continue

        language = get_language(path)

        # Skip files with unknown extensions (binary files, etc.)
        if language is None:
            continue

        lines = count_lines(path)
        size = path.stat().st_size

        relative_path = path.relative_to(root_dir)

        # Infer component from path
        component = infer_component(repo_name, relative_path)

        file_stat = FileStats(
            path=str(relative_path),
            extension=path.suffix.lower() or path.name,
            language=language,
            lines=lines,
            size_bytes=size,
            repo=repo_name,
            component=component,
        )

        stats.append(file_stat)

        if verbose and len(stats) % 100 == 0:
            print(f"  Scanned {len(stats)} files in {repo_name}...")

    return stats


def aggregate_by_language(files: list[FileStats]) -> dict[str, LanguageStats]:
    """Aggregate file stats by language."""
    lang_data: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "extensions": set(),
            "files": 0,
            "lines": 0,
            "size_bytes": 0,
            "repos": set(),
        }
    )

    for file in files:
        data = lang_data[file.language]
        data["extensions"].add(file.extension)
        data["files"] += 1
        data["lines"] += file.lines
        data["size_bytes"] += file.size_bytes
        data["repos"].add(file.repo)

    # Convert to LanguageStats objects
    result: dict[str, LanguageStats] = {}
    for lang, data in lang_data.items():
        avg_lines = data["lines"] / data["files"] if data["files"] > 0 else 0
        result[lang] = LanguageStats(
            language=lang,
            extensions=sorted(data["extensions"]),
            files=data["files"],
            lines=data["lines"],
            size_bytes=data["size_bytes"],
            repos=sorted(data["repos"]),
            avg_lines_per_file=round(avg_lines, 1),
        )

    return result


def aggregate_by_repo(files: list[FileStats]) -> dict[str, RepoStats]:
    """Aggregate file stats by repository."""
    repo_data: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "total_files": 0,
            "total_lines": 0,
            "total_size": 0,
            "languages": defaultdict(lambda: {"files": 0, "lines": 0, "size_bytes": 0}),
        }
    )

    for file in files:
        data = repo_data[file.repo]
        data["total_files"] += 1
        data["total_lines"] += file.lines
        data["total_size"] += file.size_bytes

        lang_data = data["languages"][file.language]
        lang_data["files"] += 1
        lang_data["lines"] += file.lines
        lang_data["size_bytes"] += file.size_bytes

    # Convert to RepoStats objects
    result: dict[str, RepoStats] = {}
    for repo, data in repo_data.items():
        # Convert defaultdict to regular dict for JSON serialization
        languages = {lang: dict(stats) for lang, stats in data["languages"].items()}

        result[repo] = RepoStats(
            repo=repo,
            total_files=data["total_files"],
            total_lines=data["total_lines"],
            total_size=data["total_size"],
            languages=languages,
        )

    return result


def aggregate_by_component(files: list[FileStats]) -> dict[str, ComponentStats]:
    """Aggregate file stats by component."""
    component_data: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "repo": "",
            "component": "",
            "total_files": 0,
            "total_lines": 0,
            "total_size": 0,
            "languages": defaultdict(lambda: {"files": 0, "lines": 0, "size_bytes": 0}),
        }
    )

    for file in files:
        # Create unique key for repo+component
        key = f"{file.repo}::{file.component}"

        data = component_data[key]
        data["repo"] = file.repo
        data["component"] = file.component
        data["total_files"] += 1
        data["total_lines"] += file.lines
        data["total_size"] += file.size_bytes

        lang_data = data["languages"][file.language]
        lang_data["files"] += 1
        lang_data["lines"] += file.lines
        lang_data["size_bytes"] += file.size_bytes

    # Convert to ComponentStats objects
    result: dict[str, ComponentStats] = {}
    for key, data in component_data.items():
        # Convert defaultdict to regular dict for JSON serialization
        languages = {lang: dict(stats) for lang, stats in data["languages"].items()}

        result[key] = ComponentStats(
            repo=data["repo"],
            component=data["component"],
            total_files=data["total_files"],
            total_lines=data["total_lines"],
            total_size=data["total_size"],
            languages=languages,
        )

    return result


def scan_workspace(workspace_dir: Path, verbose: bool = False) -> ScanResult:
    """Scan the entire workspace."""
    repos_dir = workspace_dir / "repos"
    if not repos_dir.exists():
        raise FileNotFoundError(f"Repos directory not found: {repos_dir}")

    all_files: list[FileStats] = []
    repo_names: list[str] = []

    # Scan each repository
    for repo_dir in sorted(repos_dir.iterdir()):
        if not repo_dir.is_dir() or repo_dir.name.startswith("."):
            continue

        repo_name = repo_dir.name
        repo_names.append(repo_name)

        if verbose:
            print(f"Scanning {repo_name}...")

        repo_files = scan_directory(repo_dir, repo_name, verbose)
        all_files.extend(repo_files)

        if verbose:
            total_lines = sum(f.lines for f in repo_files)
            print(f"  {repo_name}: {len(repo_files)} files, {total_lines:,} lines")

    # Aggregate statistics
    languages = aggregate_by_language(all_files)
    repos_stats = aggregate_by_repo(all_files)
    components_stats = aggregate_by_component(all_files)

    total_lines = sum(f.lines for f in all_files)
    total_size = sum(f.size_bytes for f in all_files)

    return ScanResult(
        scan_date=datetime.now().strftime("%Y-%m-%d"),
        repos=repo_names,
        total_files=len(all_files),
        total_lines=total_lines,
        total_size=total_size,
        files=[asdict(f) for f in all_files],
        languages={lang: asdict(stats) for lang, stats in languages.items()},
        repos_stats={repo: asdict(stats) for repo, stats in repos_stats.items()},
        components_stats={key: asdict(stats) for key, stats in components_stats.items()},
    )


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Scan codebase for language statistics")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="language_stats.json",
        help="Output JSON file path (default: language_stats.json)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    workspace_dir = Path(__file__).parent.parent
    output_path = workspace_dir / args.output

    if args.verbose:
        print(f"Scanning workspace: {workspace_dir}")
        print(f"Output file: {output_path}")
        print()

    result = scan_workspace(workspace_dir, verbose=args.verbose)

    # Write JSON output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, indent=2, sort_keys=True)

    print()
    print("=" * 60)
    print("SCAN COMPLETE")
    print("=" * 60)
    print(f"Total Files: {result.total_files:,}")
    print(f"Total Lines: {result.total_lines:,}")
    print(f"Total Size: {result.total_size / 1024 / 1024:.1f} MB")
    print(f"Languages: {len(result.languages)}")
    print(f"Repositories: {len(result.repos)}")
    print()
    print(f"Results written to: {output_path}")


if __name__ == "__main__":
    main()
