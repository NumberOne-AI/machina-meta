#!/usr/bin/env python3
"""
LANGUAGES.md Generator

Analyzes language statistics JSON and generates a comprehensive LANGUAGES.md report.

Usage:
    python scripts/generate_languages_md.py [--input INPUT] [--output OUTPUT]
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def format_number(num: int) -> str:
    """Format number with thousands separator."""
    return f"{num:,}"


def format_percentage(value: float, total: float) -> str:
    """Format percentage."""
    if total == 0:
        return "0.0%"
    pct = (value / total) * 100
    return f"{pct:.1f}%"


def format_size(bytes_val: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"


def get_tech_stack(repo: str) -> str:
    """Get technology stack description for a repository."""
    stacks = {
        "dem2": "Python 3.13, FastAPI, uv, Neo4j, PostgreSQL, Redis, Qdrant",
        "dem2-webui": "Next.js 15, React 19, TypeScript, pnpm, Biome",
        "dem2-infra": "Kubernetes (GKE), ArgoCD, Terraform, Kustomize, GitHub Actions",
        "medical-catalog": "Python, FastAPI, Qdrant, Svelte",
    }
    return stacks.get(repo, "Unknown")


def get_repo_description(repo: str) -> str:
    """Get repository description."""
    descriptions = {
        "dem2": "Backend - Python",
        "dem2-webui": "Frontend - TypeScript/React",
        "dem2-infra": "Infrastructure - Kubernetes/Terraform",
        "medical-catalog": "Catalog Service - Python",
    }
    return descriptions.get(repo, "Unknown")


def get_language_purpose(repo: str, language: str) -> str:
    """Get primary use description for a language in a repo."""
    purposes: dict[str, dict[str, str]] = {
        "dem2": {
            "Python": "Core backend logic, services, API endpoints",
            "YAML": "Configuration, CI/CD, fixtures, data files",
            "JSON": "API schemas, config, test data, fixtures",
            "Cypher": "Neo4j graph database queries",
            "Markdown": "Documentation, guides, architecture docs",
            "Shell": "Deployment scripts, automation, utilities",
            "TOML": "Python project config (pyproject.toml, config files)",
        },
        "dem2-webui": {
            "TypeScript (JSX)": "React components, UI logic, pages",
            "TypeScript": "Type definitions, utilities, hooks, API clients",
            "YAML": "CI/CD, configuration",
            "JSON": "Package config, API schemas, i18n",
            "CSS": "Styling, themes",
            "Markdown": "Documentation, component docs",
        },
        "dem2-infra": {
            "YAML": "Kubernetes manifests, ArgoCD configs, Helm charts",
            "Terraform": "GCP infrastructure as code",
            "Shell": "Deployment automation, setup scripts",
            "TypeScript": "Build scripts, tooling, automation",
            "Markdown": "Infrastructure documentation",
        },
        "medical-catalog": {
            "Python": "Biomarker catalog API, data processing",
            "Svelte": "Admin UI components",
            "YAML": "Configuration, data schemas",
            "JSON": "Biomarker data, catalog schemas",
            "Markdown": "API documentation, usage guides",
        },
    }

    repo_purposes = purposes.get(repo, {})
    return repo_purposes.get(language, "")


def generate_summary_table(data: dict[str, Any]) -> str:
    """Generate summary statistics table."""
    return f"""| Metric | Value |
|--------|-------|
| **Total Files** | {format_number(data['total_files'])} |
| **Total Lines of Code** | {format_number(data['total_lines'])} |
| **Programming Languages** | {len(data['languages'])}+ |
| **Repositories** | {len(data['repos'])} |"""


def generate_language_distribution_table(data: dict[str, Any]) -> str:
    """Generate language distribution table."""
    total_lines = data["total_lines"]
    languages = data["languages"]

    # Sort by lines descending
    sorted_langs = sorted(
        languages.items(),
        key=lambda x: x[1]["lines"],
        reverse=True,
    )

    # Take top 20 languages
    top_languages = sorted_langs[:20]

    lines = ["| Language | Files | Lines | % of Total | Repos | Extensions |"]
    lines.append("|----------|-------|-------|------------|-------|------------|")

    for lang, stats in top_languages:
        name = f"**{lang}**" if stats["lines"] > 10000 else lang
        files = format_number(stats["files"])
        loc = format_number(stats["lines"])
        pct = format_percentage(stats["lines"], total_lines)
        repos = ", ".join(stats["repos"])
        exts = ", ".join(f"`{e}`" for e in stats["extensions"][:3])  # Limit to 3

        lines.append(f"| {name} | {files} | {loc} | {pct} | {repos} | {exts} |")

    return "\n".join(lines)


def generate_repo_section(
    repo: str, repo_stats: dict[str, Any], data: dict[str, Any]
) -> str:
    """Generate repository language usage section."""
    desc = get_repo_description(repo)
    tech_stack = get_tech_stack(repo)

    # Sort languages by lines in this repo
    languages = repo_stats["languages"]
    sorted_langs = sorted(
        languages.items(),
        key=lambda x: x[1]["lines"],
        reverse=True,
    )

    # Take top 10 languages for each repo
    top_langs = sorted_langs[:10]

    lines = [f"### {repo} ({desc})"]
    lines.append("| Language | Files | Lines | Primary Use |")
    lines.append("|----------|-------|-------|-------------|")

    for lang, stats in top_langs:
        files = format_number(stats["files"])
        loc = format_number(stats["lines"])
        purpose = get_language_purpose(repo, lang)

        lines.append(f"| {lang} | {files} | {loc} | {purpose} |")

    lines.append("")
    lines.append(f"**Tech Stack:** {tech_stack}")

    return "\n".join(lines)


def generate_component_table(data: dict[str, Any]) -> str:
    """Generate component-level breakdown table with separate row per language."""
    components_stats = data["components_stats"]

    # Flatten to (repo, component, language, stats) tuples
    rows: list[tuple[str, str, str, dict[str, Any]]] = []

    for key, stats in components_stats.items():
        repo = stats["repo"]
        component = stats["component"]
        languages = stats["languages"]

        for lang, lang_stats in languages.items():
            rows.append((repo, component, lang, lang_stats))

    # Sort by lines descending (largest first)
    sorted_rows = sorted(
        rows,
        key=lambda x: -x[3]["lines"],
    )

    lines = [
        "| Repository | Component | Language | Files | Lines |",
        "|------------|-----------|----------|-------|-------|",
    ]

    for repo, component, lang, lang_stats in sorted_rows:
        files = format_number(lang_stats["files"])
        loc = format_number(lang_stats["lines"])

        lines.append(f"| {repo} | {component} | {lang} | {files} | {loc} |")

    return "\n".join(lines)


def generate_language_repo_sections(data: dict[str, Any]) -> str:
    """Generate per-language per-repo breakdown grouped by repository."""
    components_stats = data["components_stats"]

    # Group by (repo, language) and collect components
    repo_lang_data: dict[tuple[str, str], list[tuple[str, int, int]]] = {}

    for key, stats in components_stats.items():
        repo = stats["repo"]
        component = stats["component"]
        languages = stats["languages"]

        for lang, lang_stats in languages.items():
            key_tuple = (repo, lang)
            if key_tuple not in repo_lang_data:
                repo_lang_data[key_tuple] = []

            repo_lang_data[key_tuple].append(
                (component, lang_stats["files"], lang_stats["lines"])
            )

    # Group by repo
    repo_data: dict[str, list[tuple[str, int, int, list[tuple[str, int, int]]]]] = {}

    for (repo, lang), components in repo_lang_data.items():
        if repo not in repo_data:
            repo_data[repo] = []

        total_files = sum(c[1] for c in components)
        total_lines = sum(c[2] for c in components)
        repo_data[repo].append((lang, total_files, total_lines, components))

    # Sort repos by total lines (descending)
    sorted_repos = []
    for repo, languages in repo_data.items():
        repo_total = sum(lang[2] for lang in languages)
        sorted_repos.append((repo, repo_total, languages))

    sorted_repos.sort(key=lambda x: -x[1])

    # Generate hierarchical sections
    sections = []

    for repo, repo_total, languages in sorted_repos:
        # Repo header (h3)
        sections.append(f"### {repo}\n")

        # Sort languages within repo by lines descending
        sorted_langs = sorted(languages, key=lambda x: -x[2])

        for lang, total_files, total_lines, components in sorted_langs:
            # Language header (h4)
            sections.append(
                f"#### {lang} ({format_number(total_files)} files, {format_number(total_lines)} lines)\n"
            )

            # Sort components by lines descending
            sorted_components = sorted(components, key=lambda x: -x[2])

            # Component table
            sections.append("| Component | Files | Lines |")
            sections.append("|-----------|-------|-------|")

            for component, files, lines in sorted_components:
                sections.append(
                    f"| {component} | {format_number(files)} | {format_number(lines)} |"
                )

            sections.append("")  # Empty line between language sections

    return "\n".join(sections)


def calculate_category_stats(languages: dict[str, Any]) -> dict[str, int]:
    """Calculate lines by category."""
    categories: dict[str, list[str]] = {
        "Source Code": [
            "Python",
            "TypeScript",
            "TypeScript (JSX)",
            "JavaScript",
            "JavaScript (JSX)",
            "Svelte",
            "Vue",
            "Shell",
            "Bash",
            "Go",
            "Rust",
            "C",
            "C++",
            "Java",
        ],
        "Configuration": [
            "JSON",
            "YAML",
            "TOML",
            "INI",
            "Config",
            "Environment",
        ],
        "Documentation": [
            "Markdown",
            "Text",
        ],
        "Infrastructure": [
            "Dockerfile",
            "Terraform",
            "Makefile",
            "Just",
        ],
        "Database": [
            "Cypher",
            "SQL",
            "GraphQL",
        ],
        "Styling": [
            "CSS",
            "SCSS",
            "SASS",
        ],
        "Data": [
            "Lock File",
        ],
    }

    category_lines: dict[str, int] = defaultdict(int)

    for lang, stats in languages.items():
        lines = stats["lines"]
        categorized = False

        for category, lang_list in categories.items():
            if lang in lang_list:
                category_lines[category] += lines
                categorized = True
                break

        if not categorized:
            category_lines["Other"] += lines

    return dict(category_lines)


def generate_markdown(data: dict[str, Any]) -> str:
    """Generate the complete LANGUAGES.md content."""
    scan_date = data["scan_date"]
    repos = ", ".join(data["repos"])

    # Calculate category statistics
    category_stats = calculate_category_stats(data["languages"])
    total_lines = data["total_lines"]

    md = f"""# Programming Languages Analysis

This document provides a comprehensive analysis of programming languages and file types used across the MachinaMed (machina-meta) workspace.

**Analysis Date:** {scan_date}
**Repositories Analyzed:** {repos}

## Summary Statistics

{generate_summary_table(data)}

## Language Distribution by Lines of Code

{generate_language_distribution_table(data)}

## Language Usage by Repository

"""

    # Add repository sections
    for repo in sorted(data["repos"]):
        repo_stats = data["repos_stats"][repo]
        md += "\n" + generate_repo_section(repo, repo_stats, data) + "\n"

    # Add language-repo breakdown
    md += """
## Language Usage by Repository (Detailed)

This section shows each language used in each repository, with all components using that language.

"""
    md += generate_language_repo_sections(data) + "\n"

    # Add component breakdown
    md += """
## Component Breakdown (All Components)

This section provides a complete breakdown of every language in every component, sorted by lines of code.

"""
    md += generate_component_table(data) + "\n"

    md += """
## Key Insights

### Language Breakdown
"""

    # Top 3 languages
    sorted_langs = sorted(
        data["languages"].items(),
        key=lambda x: x[1]["lines"],
        reverse=True,
    )[:3]

    for i, (lang, stats) in enumerate(sorted_langs, 1):
        lines = stats["lines"]
        pct = format_percentage(lines, total_lines)
        md += f'{i}. **{lang}** with {format_number(lines)} lines ({pct})\n'

    # Calculate config lines (JSON + YAML)
    json_lines = data["languages"].get("JSON", {}).get("lines", 0)
    yaml_lines = data["languages"].get("YAML", {}).get("lines", 0)
    config_lines = json_lines + yaml_lines
    config_pct = format_percentage(config_lines, total_lines)

    # TypeScript total (TS + TSX)
    ts_lines = data["languages"].get("TypeScript", {}).get("lines", 0)
    tsx_lines = data["languages"].get("TypeScript (JSX)", {}).get("lines", 0)
    total_ts = ts_lines + tsx_lines
    ts_pct = format_percentage(total_ts, total_lines)

    md += f"\n**Configuration as Code** (JSON + YAML): {format_number(config_lines)} lines ({config_pct})\n"
    md += f"**TypeScript** (TS + TSX): {format_number(total_ts)} lines ({ts_pct})\n"

    md += """
### Code Organization
- **Microservices Architecture**: Each repo is independently deployable
- **Type Safety**: Heavy use of Python type hints, TypeScript, Pydantic schemas
- **Configuration**: Extensive YAML for configs, CI/CD, fixtures
- **Documentation**: Comprehensive Markdown documentation

### Technology Patterns
- **Backend**: Python 3.13 + FastAPI (async/await patterns)
- **Frontend**: Next.js 15 + React 19 (App Router, Server Components)
- **Database**: Neo4j (Cypher), PostgreSQL, Qdrant (vector)
- **DevOps**: Kubernetes, ArgoCD, GitHub Actions
- **Package Management**: uv (Python), pnpm (Node.js)
- **Task Runners**: just, make

"""

    # Notable technologies
    notable = []
    if "Cypher" in data["languages"]:
        stats = data["languages"]["Cypher"]
        notable.append(
            f"| **Cypher** | Neo4j graph queries | {stats['files']} files, {format_number(stats['lines'])} lines |"
        )
    if "Terraform" in data["languages"]:
        stats = data["languages"]["Terraform"]
        notable.append(
            f"| **Terraform** | GCP infrastructure | {stats['files']} files, {format_number(stats['lines'])} lines |"
        )
    if "Svelte" in data["languages"]:
        stats = data["languages"]["Svelte"]
        notable.append(
            f"| **Svelte** | Catalog admin UI | {stats['files']} files, {format_number(stats['lines'])} lines |"
        )
    if "Nix" in data["languages"]:
        stats = data["languages"]["Nix"]
        notable.append(
            f"| **Nix** | Reproducible dev environments | {stats['files']} files, {format_number(stats['lines'])} lines |"
        )

    if notable:
        md += """### Notable Technologies
| Technology | Purpose | Files |
|------------|---------|-------|
"""
        md += "\n".join(notable) + "\n\n"

    md += """## File Type Distribution

"""

    # Sort categories by lines
    sorted_categories = sorted(
        category_stats.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    for category, lines in sorted_categories:
        pct = format_percentage(lines, total_lines)
        md += f"### {category} ({pct} of lines)\n"

        # List languages in this category
        cat_langs = []
        for lang, stats in data["languages"].items():
            # Check if this language belongs to this category
            # This is a simplified check - you might want to make it more robust
            if category == "Source Code" and lang in [
                "Python",
                "TypeScript",
                "TypeScript (JSX)",
                "JavaScript",
                "Svelte",
                "Shell",
            ]:
                cat_langs.append((lang, stats["lines"]))
            elif category == "Configuration" and lang in ["JSON", "YAML", "TOML"]:
                cat_langs.append((lang, stats["lines"]))
            elif category == "Documentation" and lang in ["Markdown", "Text"]:
                cat_langs.append((lang, stats["lines"]))
            elif category == "Infrastructure" and lang in [
                "Dockerfile",
                "Terraform",
                "Makefile",
                "Just",
            ]:
                cat_langs.append((lang, stats["lines"]))
            elif category == "Database" and lang in ["Cypher", "SQL"]:
                cat_langs.append((lang, stats["lines"]))
            elif category == "Styling" and lang in ["CSS", "SCSS"]:
                cat_langs.append((lang, stats["lines"]))

        for lang, lang_lines in sorted(cat_langs, key=lambda x: x[1], reverse=True):
            md += f"- {lang}: {format_number(lang_lines)} lines\n"

        md += "\n"

    md += """## Development Tools

### Build & Task Runners
- **just** - Modern task runner (justfiles)
- **make** - Traditional build tool (Makefiles)
- **pnpm** - Fast Node.js package manager
- **uv** - Fast Python package manager

### Linting & Formatting
- **Python**: ruff (linting), mypy (type checking)
- **TypeScript**: biome (linting + formatting)

### Testing
- **Python**: pytest
- **TypeScript**: Jest, Vitest

### CI/CD
- **GitHub Actions** - Primary CI/CD platform
- **ArgoCD** - GitOps continuous delivery

## Repository Health

### Code Quality Indicators
✅ **Extensive Type Coverage**
- Python: Type hints + Pydantic models
- TypeScript: Strict mode enabled

✅ **Comprehensive Documentation**
- Markdown documentation throughout
- Per-repo CLAUDE.md for AI assistant guidance
- API documentation (OpenAPI/Swagger)

✅ **Modern Tooling**
- Fast package managers (uv, pnpm)
- Modern linters (ruff, biome)
- Container-based development

✅ **Infrastructure as Code**
- Kubernetes manifests
- Terraform for cloud resources
- Docker for containerization

### Areas of Focus
- **Backend**: Python microservices with FastAPI
- **Frontend**: Next.js with TypeScript and React 19
- **Data**: Neo4j graph database with Cypher queries
- **DevOps**: Kubernetes with ArgoCD GitOps

## File Size Analysis
"""

    # Calculate average file sizes
    python_stats = data["languages"].get("Python", {})
    ts_stats = data["languages"].get("TypeScript", {})
    tsx_stats = data["languages"].get("TypeScript (JSX)", {})

    if python_stats and python_stats.get("files", 0) > 0:
        py_avg = python_stats["lines"] / python_stats["files"]
        md += f"- **Python files**: Average {py_avg:.0f} lines per file\n"

    if ts_stats and ts_stats.get("files", 0) > 0:
        ts_avg = ts_stats["lines"] / ts_stats["files"]
        md += f"- **TypeScript files**: Average {ts_avg:.0f} lines per file\n"

    if tsx_stats and tsx_stats.get("files", 0) > 0:
        tsx_avg = tsx_stats["lines"] / tsx_stats["files"]
        md += f"- **TypeScript (JSX) files**: Average {tsx_avg:.0f} lines per file\n"

    md += f"""
## Comparison to Industry Standards

| Metric | machina-meta | Industry Typical |
|--------|-------------|------------------|
| Backend Language | Python 3.13 | ✅ Modern (Python 3.10+) |
| Frontend Language | TypeScript | ✅ Industry standard |
| Frontend Framework | Next.js 15 | ✅ Cutting edge |
| Database | Neo4j + PostgreSQL | ✅ Multi-model approach |
| Container Orchestration | Kubernetes | ✅ Industry standard |
| CI/CD | GitHub Actions + ArgoCD | ✅ Modern GitOps |
| Package Management | uv + pnpm | ✅ Fast modern tools |
| Lines per Python file | {python_stats.get('avg_lines_per_file', 0):.0f} avg | ✅ Good (200-400 typical) |
| Lines per TS file | {ts_stats.get('avg_lines_per_file', 0):.0f} avg | ✅ Excellent (<200 ideal) |

## Conclusion

The MachinaMed codebase demonstrates:
- ✅ **Modern Technology Stack** - Latest versions of Python, TypeScript, Next.js
- ✅ **Strong Type Safety** - Extensive use of type systems
- ✅ **Cloud-Native Architecture** - Kubernetes, microservices, containers
- ✅ **Comprehensive Documentation** - Extensive Markdown documentation
- ✅ **Infrastructure as Code** - Declarative configs for reproducibility
- ✅ **Developer Experience** - Fast tooling (uv, pnpm), clear organization

**Total Codebase Size:** {format_number(total_lines)} lines across {format_number(data['total_files'])} files in {len(data['repos'])} repositories.
"""

    return md


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate LANGUAGES.md from scan data")
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default="language_stats.json",
        help="Input JSON file path (default: language_stats.json)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="LANGUAGES.md",
        help="Output markdown file path (default: LANGUAGES.md)",
    )

    args = parser.parse_args()

    workspace_dir = Path(__file__).parent.parent
    input_path = workspace_dir / args.input
    output_path = workspace_dir / args.output

    # Load JSON data
    print(f"Reading data from: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Generate markdown
    print(f"Generating LANGUAGES.md...")
    markdown = generate_markdown(data)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"LANGUAGES.md written to: {output_path}")
    print()
    print("Summary:")
    print(f"  Files: {data['total_files']:,}")
    print(f"  Lines: {data['total_lines']:,}")
    print(f"  Languages: {len(data['languages'])}")


if __name__ == "__main__":
    main()
