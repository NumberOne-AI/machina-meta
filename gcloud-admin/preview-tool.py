#!/usr/bin/env python3
"""preview-tool.py - Utility for managing preview environments, PRs, and deployments

ArgoCD Behavior Note:
When using the ArgoCD CLI to check if an application has been deleted, the command
may return "PermissionDenied" error instead of "NotFound", particularly in ArgoCD
versions 2.6 and later. This is intentional for security reasons to prevent potential
enumeration of existing applications by attackers. Therefore, "PermissionDenied"
errors when querying ArgoCD applications may indicate the app doesn't exist or was
already deleted, not necessarily a permissions issue.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple, List


# ============================================================
# Color and Output Utilities
# ============================================================

class Color:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    GRAY = '\033[0;90m'
    NC = '\033[0m'  # No Color


class Symbol:
    """Unicode symbols for output."""
    CHECK = "✅"
    CROSS = "❌"
    CIRCLE = "⚪"
    WARN = "⚠️"


def print_color(color: str, message: str) -> None:
    """Print colored output."""
    print(f"{color}{message}{Color.NC}")


def print_header(title: str) -> None:
    """Print section header."""
    print()
    print_color(Color.CYAN, "═" * 62)
    print_color(Color.CYAN, title)
    print_color(Color.CYAN, "═" * 62)


def print_kv(key: str, value: str) -> None:
    """Print key-value pair."""
    print(f"  {key:<25} {value}")


def format_timestamp(timestamp: Optional[str]) -> str:
    """Format ISO timestamp to readable format."""
    if not timestamp or timestamp == "null":
        return "N/A"
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return timestamp


# ============================================================
# Configuration
# ============================================================

WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()
DEM2_REPO = WORKSPACE_ROOT / "repos" / "dem2"
WEBUI_REPO = WORKSPACE_ROOT / "repos" / "dem2-webui"
INFRA_REPO = WORKSPACE_ROOT / "repos" / "dem2-infra"
GITHUB_ORG = "NumberOne-AI"


# ============================================================
# Exceptions
# ============================================================

class PreviewToolError(Exception):
    """Base exception for preview tool errors."""
    pass


class CommandNotFoundError(PreviewToolError):
    """Required command not found."""
    pass


class ResolutionError(PreviewToolError):
    """Error resolving identifier to preview ID."""
    pass


# ============================================================
# Data Classes
# ============================================================

class IdentifierType(Enum):
    """Types of identifiers that can resolve to a preview environment."""
    GIT_TAG = "git-tag"
    ARGOCD_APP = "argocd-app"
    GKE_NAMESPACE = "gke-namespace"
    INFRA_BRANCH = "infra-branch"
    PR = "pr"
    GIT_BRANCH = "git-branch"


@dataclass
class TagInfo:
    """Information about a git tag."""
    exists: bool
    commit: Optional[str] = None
    date: Optional[str] = None


@dataclass
class BranchInfo:
    """Information about a git branch."""
    exists: bool
    location: Optional[str] = None  # "LOCAL", "REMOTE", or None


@dataclass
class PRInfo:
    """Information about a GitHub pull request."""
    number: int
    title: str
    state: str
    head_ref: str
    base_ref: str
    url: str
    author: str
    created_at: str
    merged_at: Optional[str] = None
    closed_at: Optional[str] = None


# ============================================================
# Command Utilities
# ============================================================

def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    check: bool = False,
    capture_output: bool = True
) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=check
        )
    except FileNotFoundError:
        raise CommandNotFoundError(f"Command not found: {cmd[0]}")


def check_command_available(cmd: str) -> bool:
    """Check if a command is available in PATH."""
    result = run_command(["which", cmd])
    return result.returncode == 0


# ============================================================
# Git Operations
# ============================================================

def check_git_tag(repo_path: Path, tag: str) -> TagInfo:
    """Check if a git tag exists in a repository."""
    if not repo_path.exists():
        return TagInfo(exists=False)

    result = run_command(["git", "-C", str(repo_path), "rev-parse", tag])
    if result.returncode != 0:
        return TagInfo(exists=False)

    commit = result.stdout.strip()

    result = run_command(["git", "-C", str(repo_path), "log", "-1", "--format=%ai", tag])
    date = result.stdout.strip() if result.returncode == 0 else None

    return TagInfo(exists=True, commit=commit, date=date)


def check_git_branch(repo_path: Path, branch: str) -> BranchInfo:
    """Check if a git branch exists in a repository."""
    if not repo_path.exists():
        return BranchInfo(exists=False)

    # Check local branches
    result = run_command([
        "git", "-C", str(repo_path), "show-ref", "--verify", "--quiet",
        f"refs/heads/{branch}"
    ])
    if result.returncode == 0:
        return BranchInfo(exists=True, location="LOCAL")

    # Check remote branches
    result = run_command([
        "git", "-C", str(repo_path), "show-ref", "--verify", "--quiet",
        f"refs/remotes/origin/{branch}"
    ])
    if result.returncode == 0:
        return BranchInfo(exists=True, location="REMOTE")

    return BranchInfo(exists=False)


def get_remote_preview_branches(repo_path: Path) -> List[str]:
    """Get all remote preview branches from a repository."""
    if not repo_path.exists():
        return []

    result = run_command(["git", "-C", str(repo_path), "branch", "-r"])
    if result.returncode != 0:
        return []

    branches = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if "origin/preview/" in line:
            branch = line.replace("origin/preview/", "")
            branches.append(branch)

    return branches


def get_preview_tags_sorted(repo_path: Path) -> List[str]:
    """Get all preview tags sorted by creation date (newest first)."""
    if not repo_path.exists():
        return []

    result = run_command([
        "git", "-C", str(repo_path), "tag", "-l", "preview-*",
        "--sort=-creatordate"
    ])
    if result.returncode != 0:
        return []

    return [tag.strip() for tag in result.stdout.splitlines() if tag.strip()]


def check_tag_is_ancestor(repo_path: Path, tag: str, branch: str) -> bool:
    """Check if a tag is an ancestor of a branch."""
    result = run_command([
        "git", "-C", str(repo_path), "merge-base", "--is-ancestor",
        tag, branch
    ])
    return result.returncode == 0


# ============================================================
# GitHub Operations
# ============================================================

def get_pr_info(repo: str, pr_number: int) -> Optional[PRInfo]:
    """Get PR information from GitHub using gh CLI."""
    if not check_command_available("gh"):
        return None

    result = run_command([
        "gh", "pr", "view", str(pr_number),
        "--repo", f"{GITHUB_ORG}/{repo}",
        "--json", "number,title,state,headRefName,baseRefName,url,author,createdAt,mergedAt,closedAt"
    ])

    if result.returncode != 0:
        return None

    try:
        data = json.loads(result.stdout)
        return PRInfo(
            number=data["number"],
            title=data["title"],
            state=data["state"],
            head_ref=data["headRefName"],
            base_ref=data["baseRefName"],
            url=data["url"],
            author=data["author"]["login"],
            created_at=data["createdAt"],
            merged_at=data.get("mergedAt"),
            closed_at=data.get("closedAt")
        )
    except (json.JSONDecodeError, KeyError):
        return None


def get_pr_by_branch(repo: str, branch: str) -> Optional[int]:
    """Find PR number for a branch in a repository."""
    if not check_command_available("gh"):
        return None

    result = run_command([
        "gh", "pr", "list",
        "--repo", f"{GITHUB_ORG}/{repo}",
        "--head", branch,
        "--json", "number",
        "--jq", ".[0].number"
    ])

    if result.returncode != 0 or not result.stdout.strip():
        return None

    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


def get_infra_pr_number(preview_id: str) -> Optional[int]:
    """Get the infra PR number for a preview ID."""
    if not check_command_available("gh"):
        return None

    branch = f"preview/{preview_id}"
    result = run_command([
        "gh", "pr", "list",
        "--repo", f"{GITHUB_ORG}/dem2-infra",
        "--head", branch,
        "--json", "number",
        "--jq", ".[0].number"
    ])

    if result.returncode != 0 or not result.stdout.strip():
        return None

    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


def close_pr(repo: str, pr_number: int, comment: str) -> bool:
    """Close a PR with a comment."""
    if not check_command_available("gh"):
        return False

    result = run_command([
        "gh", "pr", "close", str(pr_number),
        "--repo", f"{GITHUB_ORG}/{repo}",
        "--comment", comment
    ])

    return result.returncode == 0


# ============================================================
# Kubernetes Operations
# ============================================================

def get_namespace_annotations(namespace: str) -> Optional[dict]:
    """Get annotations for a Kubernetes namespace."""
    if not check_command_available("kubectl"):
        return None

    result = run_command([
        "kubectl", "get", "namespace", namespace,
        "-o", "json"
    ])

    if result.returncode != 0:
        return None

    try:
        data = json.loads(result.stdout)
        return data.get("metadata", {}).get("annotations", {})
    except (json.JSONDecodeError, KeyError):
        return None


def get_argocd_app_from_namespace(namespace: str) -> Optional[str]:
    """Get ArgoCD application name from namespace annotations."""
    annotations = get_namespace_annotations(namespace)
    if not annotations:
        return None

    # Look for common ArgoCD annotations
    # ArgoCD sets annotations like argocd.argoproj.io/instance or similar
    for key, value in annotations.items():
        if "argocd" in key.lower() and "app" in key.lower():
            return value
        # Also check for common naming patterns in labels
        if key == "app.kubernetes.io/instance":
            return value

    return None


# ============================================================
# ArgoCD Operations
# ============================================================

def get_argocd_app_status(app_name: str) -> Optional[dict]:
    """Get ArgoCD application status."""
    if not check_command_available("argocd"):
        return None

    result = run_command(["argocd", "app", "get", app_name, "-o", "json"])

    if result.returncode != 0:
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def list_argocd_apps() -> Optional[List[dict]]:
    """List all ArgoCD applications."""
    if not check_command_available("argocd"):
        return None

    result = run_command(["argocd", "app", "list", "-o", "json"])

    if result.returncode != 0:
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def get_argocd_app_for_namespace(namespace: str) -> Optional[str]:
    """Find ArgoCD application deploying to a specific namespace."""
    apps = list_argocd_apps()
    if not apps:
        return None

    for app in apps:
        try:
            app_namespace = app.get("spec", {}).get("destination", {}).get("namespace")
            if app_namespace == namespace:
                return app.get("metadata", {}).get("name")
        except (AttributeError, KeyError):
            continue

    return None


def delete_argocd_app(app_name: str) -> bool:
    """Delete an ArgoCD application."""
    if not check_command_available("argocd"):
        return False

    result = run_command(["argocd", "app", "delete", app_name, "--yes"])
    return result.returncode == 0


# ============================================================
# Preview Environment Resolution
# ============================================================

class PreviewEnvironment:
    """Manages preview environment identification and operations."""

    def __init__(self, preview_id: str, id_type: IdentifierType, original_identifier: str):
        self.preview_id = preview_id
        self.id_type = id_type
        self.original_identifier = original_identifier

    @classmethod
    def resolve(cls, id_type: IdentifierType, identifier: str) -> "PreviewEnvironment":
        """Resolve an identifier to a preview environment."""

        if id_type == IdentifierType.GIT_TAG:
            return cls._resolve_git_tag(identifier)
        elif id_type == IdentifierType.ARGOCD_APP:
            return cls._resolve_argocd_app(identifier)
        elif id_type == IdentifierType.GKE_NAMESPACE:
            return cls._resolve_gke_namespace(identifier)
        elif id_type == IdentifierType.INFRA_BRANCH:
            return cls._resolve_infra_branch(identifier)
        elif id_type == IdentifierType.PR:
            return cls._resolve_pr(identifier)
        elif id_type == IdentifierType.GIT_BRANCH:
            return cls._resolve_git_branch(identifier)
        else:
            raise ResolutionError(f"Unknown identifier type: {id_type}")

    @classmethod
    def _resolve_git_tag(cls, identifier: str) -> "PreviewEnvironment":
        """Resolve git tag to preview ID."""
        match = re.match(r"^preview-(.+)$", identifier)
        if not match:
            raise ResolutionError("Git tag must start with 'preview-'")

        preview_id = match.group(1)
        return cls(preview_id, IdentifierType.GIT_TAG, identifier)

    @classmethod
    def _resolve_argocd_app(cls, identifier: str) -> "PreviewEnvironment":
        """Resolve ArgoCD app name to preview ID."""
        match = re.match(r"^preview-pr-(\d+)$", identifier)
        if not match:
            raise ResolutionError("ArgoCD app must be in format 'preview-pr-NUMBER'")

        if not check_command_available("gh"):
            raise CommandNotFoundError("gh CLI required for ArgoCD app resolution")

        infra_pr_num = int(match.group(1))
        pr_info = get_pr_info("dem2-infra", infra_pr_num)

        if not pr_info:
            raise ResolutionError(f"Could not resolve ArgoCD app '{identifier}' to preview ID")

        branch_match = re.match(r"^preview/(.+)$", pr_info.head_ref)
        if not branch_match:
            raise ResolutionError(f"Infra PR #{infra_pr_num} branch is not a preview branch")

        preview_id = branch_match.group(1)
        return cls(preview_id, IdentifierType.ARGOCD_APP, identifier)

    @classmethod
    def _resolve_gke_namespace(cls, identifier: str) -> "PreviewEnvironment":
        """Resolve GKE namespace to preview ID."""
        # Try preview namespace format first: tusdi-preview-NUMBER
        match = re.match(r"^tusdi-preview-(\d+)$", identifier)
        if match:
            infra_pr_num = int(match.group(1))

            if not check_command_available("gh"):
                print_color(Color.YELLOW, "Warning: gh CLI not available, using fallback")
                preview_id = str(infra_pr_num)
            else:
                pr_info = get_pr_info("dem2-infra", infra_pr_num)
                if pr_info:
                    branch_match = re.match(r"^preview/(.+)$", pr_info.head_ref)
                    if branch_match:
                        preview_id = branch_match.group(1)
                    else:
                        preview_id = str(infra_pr_num)
                else:
                    preview_id = str(infra_pr_num)

            return cls(preview_id, IdentifierType.GKE_NAMESPACE, identifier)

        # For any other namespace, try multiple resolution strategies

        # Strategy 1: Check namespace annotations for ArgoCD app
        argocd_app = get_argocd_app_from_namespace(identifier)

        # Strategy 2: List ArgoCD apps and find one deploying to this namespace
        if not argocd_app:
            argocd_app = get_argocd_app_for_namespace(identifier)

        if argocd_app:
            # Try to parse ArgoCD app name to get preview ID
            # Format: preview-pr-NUMBER
            app_match = re.match(r"^preview-pr-(\d+)$", argocd_app)
            if app_match:
                infra_pr_num = int(app_match.group(1))
                if check_command_available("gh"):
                    pr_info = get_pr_info("dem2-infra", infra_pr_num)
                    if pr_info:
                        branch_match = re.match(r"^preview/(.+)$", pr_info.head_ref)
                        if branch_match:
                            preview_id = branch_match.group(1)
                            return cls(preview_id, IdentifierType.GKE_NAMESPACE, identifier)

                preview_id = str(infra_pr_num)
                return cls(preview_id, IdentifierType.GKE_NAMESPACE, identifier)

            # Use ArgoCD app name directly as preview ID
            preview_id = argocd_app
            return cls(preview_id, IdentifierType.GKE_NAMESPACE, identifier)

        # Fallback: use namespace name directly as the preview ID
        preview_id = identifier
        return cls(preview_id, IdentifierType.GKE_NAMESPACE, identifier)

    @classmethod
    def _resolve_infra_branch(cls, identifier: str) -> "PreviewEnvironment":
        """Resolve infra branch to preview ID."""
        match = re.match(r"^preview/(.+)$", identifier)
        if not match:
            raise ResolutionError("Infra branch must start with 'preview/'")

        preview_id = match.group(1)
        return cls(preview_id, IdentifierType.INFRA_BRANCH, identifier)

    @classmethod
    def _resolve_pr(cls, identifier: str) -> "PreviewEnvironment":
        """Resolve PR number to preview ID."""
        if not identifier.isdigit():
            raise ResolutionError("PR number must be numeric")

        if not check_command_available("gh"):
            raise CommandNotFoundError("gh CLI required for PR resolution")

        pr_num = int(identifier)

        # Check dem2-infra first (gives us current preview environment)
        pr_info = get_pr_info("dem2-infra", pr_num)
        if pr_info:
            branch_match = re.match(r"^preview/(.+)$", pr_info.head_ref)
            if branch_match:
                preview_id = branch_match.group(1)
                return cls(preview_id, IdentifierType.PR, identifier)

        # Check dem2 - find LATEST preview tag, not just any ancestor
        pr_info = get_pr_info("dem2", pr_num)
        if not pr_info:
            raise ResolutionError(f"Could not find preview environment for PR #{pr_num}")

        dem2_branch = pr_info.head_ref
        preview_id = None

        # Look for active preview in dem2-infra by searching for the branch name
        preview_branches = get_remote_preview_branches(INFRA_REPO)
        for infra_branch in preview_branches:
            tag = f"preview-{infra_branch}"
            result = run_command(["git", "-C", str(DEM2_REPO), "rev-parse", tag])
            if result.returncode == 0:
                if check_tag_is_ancestor(DEM2_REPO, tag, f"origin/{dem2_branch}"):
                    preview_id = infra_branch
                    break

        # Fallback: look for ANY preview tag on this branch (least preferred)
        if not preview_id:
            tags = get_preview_tags_sorted(DEM2_REPO)
            for tag in tags:
                tag_id = tag.replace("preview-", "")
                if check_tag_is_ancestor(DEM2_REPO, tag, f"origin/{dem2_branch}"):
                    preview_id = tag_id
                    break

        if not preview_id:
            raise ResolutionError(f"Could not find preview environment for PR #{pr_num}")

        return cls(preview_id, IdentifierType.PR, identifier)

    @classmethod
    def _resolve_git_branch(cls, identifier: str) -> "PreviewEnvironment":
        """Resolve git branch to preview ID."""
        if not check_command_available("gh"):
            raise CommandNotFoundError("gh CLI required for git branch resolution")

        # Find PR for this branch in dem2
        pr_num = get_pr_by_branch("dem2", identifier)
        if not pr_num:
            raise ResolutionError(f"Could not find PR for branch '{identifier}'")

        preview_id = None

        # Look for active preview in dem2-infra
        preview_branches = get_remote_preview_branches(INFRA_REPO)
        for infra_branch in preview_branches:
            tag = f"preview-{infra_branch}"
            result = run_command(["git", "-C", str(DEM2_REPO), "rev-parse", tag])
            if result.returncode == 0:
                result = run_command([
                    "git", "-C", str(DEM2_REPO), "rev-parse", "--verify",
                    f"origin/{identifier}"
                ])
                if result.returncode == 0:
                    if check_tag_is_ancestor(DEM2_REPO, tag, f"origin/{identifier}"):
                        preview_id = infra_branch
                        break

        # Fallback: look for ANY preview tag on this branch
        if not preview_id:
            tags = get_preview_tags_sorted(DEM2_REPO)
            for tag in tags:
                tag_id = tag.replace("preview-", "")
                result = run_command([
                    "git", "-C", str(DEM2_REPO), "rev-parse", "--verify",
                    f"origin/{identifier}"
                ])
                if result.returncode == 0:
                    if check_tag_is_ancestor(DEM2_REPO, tag, f"origin/{identifier}"):
                        preview_id = tag_id
                        break

        if not preview_id:
            raise ResolutionError(f"Could not find preview environment for branch '{identifier}'")

        return cls(preview_id, IdentifierType.GIT_BRANCH, identifier)

    def get_argocd_app_name(self) -> Tuple[str, Optional[int]]:
        """Get the ArgoCD application name and infra PR number."""
        infra_pr_num = get_infra_pr_number(self.preview_id)
        if infra_pr_num:
            return f"preview-pr-{infra_pr_num}", infra_pr_num
        else:
            return f"preview-{self.preview_id}", None

    def show_info(self) -> None:
        """Display detailed information about the preview environment."""
        print_header(f"Preview Environment: {self.preview_id}")

        # Show identifier resolution
        print()
        print_color(Color.CYAN, "Identifier Resolution:")
        print_kv("  Input Type", self.id_type.value)
        print_kv("  Input Value", self.original_identifier)
        print_kv("  Resolved Preview ID", self.preview_id)
        print()

        # Extract PR number if in format "pr-XX"
        pr_match = re.match(r"^pr-(\d+)$", self.preview_id)
        pr_number = int(pr_match.group(1)) if pr_match else None

        # Check dem2 repository
        self._show_repo_info("dem2", DEM2_REPO, pr_number)

        # Check dem2-webui repository
        self._show_repo_info("dem2-webui", WEBUI_REPO, pr_number)

        # Check dem2-infra repository
        self._show_infra_info()

        # Check ArgoCD deployment
        self._show_argocd_info()

        # Show summary
        self._show_summary()

    def _show_repo_info(self, repo_name: str, repo_path: Path, pr_number: Optional[int]) -> None:
        """Show information about a repository."""
        print_header(f"{repo_name} ({'Backend' if repo_name == 'dem2' else 'Frontend'})")

        tag_info = check_git_tag(repo_path, f"preview-{self.preview_id}")
        if tag_info.exists:
            print_kv("Preview Tag", f"{Symbol.CHECK} preview-{self.preview_id}")
            if tag_info.commit:
                print_kv("Tag Commit", tag_info.commit[:8])
            if tag_info.date:
                print_kv("Tag Date", tag_info.date)
        else:
            print_kv("Preview Tag", f"{Symbol.CROSS} Not found")

        # Show PR info if we have a number
        if pr_number:
            pr_info = get_pr_info(repo_name, pr_number)
            if pr_info:
                print_kv(f"PR #{pr_number}", pr_info.title)

                if pr_info.state == "OPEN":
                    status = f"{Color.GREEN}{Symbol.CHECK} OPEN{Color.NC}"
                elif pr_info.state == "MERGED":
                    status = f"{Color.BLUE}{Symbol.CHECK} MERGED{Color.NC} ({format_timestamp(pr_info.merged_at)})"
                else:
                    status = f"{Color.RED}{Symbol.CROSS} CLOSED{Color.NC} ({format_timestamp(pr_info.closed_at)})"

                print_kv("Status", status)
                print_kv("Branch", pr_info.head_ref)
                print_kv("Author", pr_info.author)
                print_kv("Created", format_timestamp(pr_info.created_at))
                print_kv("URL", pr_info.url)
            else:
                print_kv(f"PR #{pr_number}", f"{Symbol.CIRCLE} Not found or no access")

    def _show_infra_info(self) -> None:
        """Show information about dem2-infra repository."""
        print_header("dem2-infra (Infrastructure)")

        branch_info = check_git_branch(INFRA_REPO, f"preview/{self.preview_id}")
        print_kv("Preview Branch", f"preview/{self.preview_id}: {branch_info.location if branch_info.exists else 'NOT_FOUND'}")

        # Look for associated PR
        if check_command_available("gh"):
            result = run_command([
                "gh", "pr", "list",
                "--repo", f"{GITHUB_ORG}/dem2-infra",
                "--head", f"preview/{self.preview_id}",
                "--json", "number,title,state,url,author,createdAt,mergedAt,closedAt",
                "--limit", "1"
            ])

            if result.returncode == 0 and result.stdout.strip():
                try:
                    prs = json.loads(result.stdout)
                    if prs:
                        pr_data = prs[0]
                        pr_number = pr_data["number"]
                        pr_state = pr_data["state"]
                        pr_title = pr_data["title"]
                        pr_url = pr_data["url"]
                        pr_author = pr_data["author"]["login"]
                        pr_created = pr_data["createdAt"]
                        pr_merged = pr_data.get("mergedAt")
                        pr_closed = pr_data.get("closedAt")

                        print_kv(f"PR #{pr_number}", pr_title)

                        if pr_state == "OPEN":
                            status = f"{Color.GREEN}{Symbol.CHECK} OPEN{Color.NC}"
                        elif pr_state == "MERGED":
                            status = f"{Color.BLUE}{Symbol.CHECK} MERGED{Color.NC} ({format_timestamp(pr_merged)})"
                        else:
                            status = f"{Color.RED}{Symbol.CROSS} CLOSED{Color.NC} ({format_timestamp(pr_closed)})"

                        print_kv("Status", status)
                        print_kv("Author", pr_author)
                        print_kv("Created", format_timestamp(pr_created))
                        print_kv("URL", pr_url)
                    else:
                        print_kv("Infra PR", f"{Symbol.CIRCLE} Not found")
                except (json.JSONDecodeError, KeyError):
                    print_kv("Infra PR", f"{Symbol.CIRCLE} Error parsing PR info")

    def _show_argocd_info(self) -> None:
        """Show ArgoCD deployment information."""
        print_header("ArgoCD Deployment")

        argocd_app, infra_pr_num = self.get_argocd_app_name()
        argocd_url = f"https://argo.n1-machina.dev/applications/{argocd_app}"

        if infra_pr_num:
            print_kv("Application Name", f"{argocd_app} (based on infra PR #{infra_pr_num})")
        else:
            print_kv("Application Name", f"{argocd_app} (infra PR not found, using fallback)")

        print_kv("ArgoCD URL", argocd_url)

        # Try to get ArgoCD status
        if check_command_available("argocd"):
            app_status = get_argocd_app_status(argocd_app)
            if app_status:
                sync_status = app_status.get("status", {}).get("sync", {}).get("status", "Unknown")
                health_status = app_status.get("status", {}).get("health", {}).get("status", "Unknown")

                print_kv("Sync Status", sync_status)
                print_kv("Health Status", health_status)
            else:
                print_kv("Status", f"{Symbol.CIRCLE} Cannot retrieve (app may not exist)")
        else:
            print_kv("Status", f"{Symbol.CIRCLE} ArgoCD CLI not available")

    def _show_summary(self) -> None:
        """Show summary of preview environment."""
        print_header("Summary")

        dem2_tag = check_git_tag(DEM2_REPO, f"preview-{self.preview_id}")
        webui_tag = check_git_tag(WEBUI_REPO, f"preview-{self.preview_id}")
        infra_branch = check_git_branch(INFRA_REPO, f"preview/{self.preview_id}")

        has_tags = dem2_tag.exists or webui_tag.exists
        has_infra_branch = infra_branch.exists

        # Show artifact summary
        if has_tags or has_infra_branch:
            print()
            print_color(Color.CYAN, "  Preview Environment Artifacts:")

            if dem2_tag.exists:
                print(f"    • dem2 has preview tag: preview-{self.preview_id}")

            if webui_tag.exists:
                print(f"    • dem2-webui has preview tag: preview-{self.preview_id}")

            if has_infra_branch:
                print(f"    • dem2-infra has preview branch: preview/{self.preview_id}")
        else:
            print_color(Color.GREEN, f"  {Symbol.CHECK} No preview artifacts found - environment is clean")

        print()

    def delete(self) -> None:
        """Delete the preview environment (tags, close PR, trigger ArgoCD cleanup)."""
        print_header(f"Deleting Preview Environment: {self.preview_id}")

        # Close PR in dem2-infra (triggers ArgoCD auto-cleanup)
        if check_command_available("gh"):
            print()
            print_color(Color.CYAN, f"Looking up PR for preview/{self.preview_id} branch in dem2-infra...")

            pr_num = get_pr_by_branch("dem2-infra", f"preview/{self.preview_id}")

            if pr_num:
                print_color(Color.CYAN, f"Found PR #{pr_num}")
                print()
                print_color(Color.CYAN, "Closing PR to remove preview environment...")

                if close_pr("dem2-infra", pr_num, f"Closing preview environment: {self.preview_id}"):
                    print_color(Color.GREEN, f"{Symbol.CHECK} Closed PR #{pr_num}")
                else:
                    print_color(Color.YELLOW, f"{Symbol.WARN} Could not close PR #{pr_num} (may already be closed)")
            else:
                print_color(Color.GRAY, f"{Symbol.CIRCLE} No open PR found for preview/{self.preview_id}")
        else:
            print_color(Color.YELLOW, f"{Symbol.WARN} gh CLI not available, skipping PR closure")

        # Remove tags from dem2 and dem2-webui repos
        print()
        print_color(Color.CYAN, "Removing preview tags from application repositories...")

        removed_count = 0
        skipped_count = 0

        for repo_name, repo_path in [("dem2", DEM2_REPO), ("dem2-webui", WEBUI_REPO)]:
            print()
            print_color(Color.CYAN, f"Processing {repo_name}...")

            if not repo_path.exists():
                print_color(Color.YELLOW, f"  {Symbol.WARN} Repository not found: {repo_path}")
                skipped_count += 1
                continue

            tag = f"preview-{self.preview_id}"
            result = run_command(["git", "-C", str(repo_path), "rev-parse", tag])

            if result.returncode == 0:
                # Delete local tag
                result = run_command(["git", "-C", str(repo_path), "tag", "-d", tag])
                if result.returncode == 0:
                    print(f"  {result.stdout.strip()}")

                # Delete remote tag
                result = run_command([
                    "git", "-C", str(repo_path), "push", "origin",
                    f":refs/tags/{tag}"
                ])

                if result.returncode == 0:
                    print(f"  {result.stdout.strip()}")
                    print_color(Color.GREEN, f"  {Symbol.CHECK} Removed {tag} from {repo_name}")
                    removed_count += 1
                else:
                    print_color(Color.YELLOW, f"  {Symbol.WARN} Tag not on remote or already deleted")
                    removed_count += 1
            else:
                print_color(Color.GRAY, f"  {Symbol.CIRCLE} Tag doesn't exist in {repo_name}")
                skipped_count += 1

        # Summary
        print()
        print_header("Summary")

        argocd_app, _ = self.get_argocd_app_name()

        print()
        print_color(Color.GREEN, f"{Symbol.CHECK} Preview environment deletion completed")
        print()
        print(f"  Tags removed: {removed_count}")
        print(f"  Tags skipped: {skipped_count}")
        print()
        print_color(Color.CYAN, "Note: ArgoCD application will auto-delete in 30-60 seconds after PR closure")
        print(f"Monitor: https://argo.n1-machina.dev/applications/{argocd_app}")
        print()
        print(f"When checking deletion status with 'argocd app get {argocd_app}':")
        print("• PermissionDenied error = app was deleted (ArgoCD 2.6+ security feature)")
        print("• Application details shown = app still exists")
        print()



# ============================================================
# CLI Commands
# ============================================================

def cmd_info(args: argparse.Namespace) -> None:
    """Show detailed information about a preview environment."""
    id_type, identifier = _parse_identifier_args(args)

    try:
        env = PreviewEnvironment.resolve(id_type, identifier)
        env.show_info()
    except (ResolutionError, CommandNotFoundError) as e:
        print_color(Color.RED, f"Error: {e}")
        sys.exit(1)


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete preview environment (tags, close PR, trigger ArgoCD cleanup)."""
    id_type, identifier = _parse_identifier_args(args)

    try:
        env = PreviewEnvironment.resolve(id_type, identifier)
        env.delete()
    except (ResolutionError, CommandNotFoundError) as e:
        print_color(Color.RED, f"Error: {e}")
        sys.exit(1)


def _parse_identifier_args(args: argparse.Namespace) -> Tuple[IdentifierType, str]:
    """Parse identifier arguments from argparse namespace."""
    if args.git_tag:
        return IdentifierType.GIT_TAG, args.git_tag
    elif args.argocd_app:
        return IdentifierType.ARGOCD_APP, args.argocd_app
    elif args.gke_namespace:
        return IdentifierType.GKE_NAMESPACE, args.gke_namespace
    elif args.infra_branch:
        return IdentifierType.INFRA_BRANCH, args.infra_branch
    elif args.pr:
        return IdentifierType.PR, args.pr
    elif args.git_branch:
        return IdentifierType.GIT_BRANCH, args.git_branch
    else:
        print_color(Color.RED, "Error: You must specify the type of identifier")
        print()
        print("Use one of:")
        print("  --git-tag <tag>              Git tag (preview-docproc-extraction-pipeline)")
        print("  --argocd-app <app>           ArgoCD app name (preview-pr-91)")
        print("  --gke-namespace <ns>         GKE namespace (tusdi-preview-91)")
        print("  --infra-branch <branch>      dem2-infra branch (preview/docproc-extraction-pipeline)")
        print("  --pr <number>                PR number (421)")
        print("  --git-branch <branch>        Git branch (feature/docproc-extraction-pipeline)")
        sys.exit(1)


# ============================================================
# Main CLI
# ============================================================

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Utility for managing preview environments, PRs, and deployments",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Common identifier arguments for all commands
    def add_identifier_args(subparser: argparse.ArgumentParser) -> None:
        """Add identifier arguments to a subparser."""
        id_group = subparser.add_argument_group("identifier options (one required)")
        id_group.add_argument("--git-tag", metavar="TAG", help="Git tag (preview-docproc-extraction-pipeline)")
        id_group.add_argument("--argocd-app", metavar="APP", help="ArgoCD app name (preview-pr-91)")
        id_group.add_argument("--gke-namespace", metavar="NS", help="GKE namespace (tusdi-preview-91)")
        id_group.add_argument("--infra-branch", metavar="BRANCH", help="dem2-infra branch (preview/docproc-extraction-pipeline)")
        id_group.add_argument("--pr", metavar="NUMBER", help="PR number (421)")
        id_group.add_argument("--git-branch", metavar="BRANCH", help="Git branch (feature/docproc-extraction-pipeline)")

    # info command
    info_parser = subparsers.add_parser("info", help="Show detailed information about a preview environment")
    add_identifier_args(info_parser)
    info_parser.set_defaults(func=cmd_info)

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete preview environment (tags, close PR, trigger ArgoCD cleanup)")
    add_identifier_args(delete_parser)
    delete_parser.set_defaults(func=cmd_delete)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Execute command
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
