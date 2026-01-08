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

    def collect_info(self) -> dict:
        """Collect all preview environment information into a structured dictionary."""
        data = {
            "preview_id": self.preview_id,
            "identifier": {
                "type": self.id_type.value,
                "value": self.original_identifier
            },
            "repositories": {},
            "argocd": {},
            "summary": {}
        }

        # Extract PR number if in format "pr-XX"
        pr_match = re.match(r"^pr-(\d+)$", self.preview_id)
        pr_number = int(pr_match.group(1)) if pr_match else None

        # Collect dem2 repository info
        data["repositories"]["dem2"] = self._collect_repo_info("dem2", DEM2_REPO, pr_number)

        # Collect dem2-webui repository info
        data["repositories"]["dem2-webui"] = self._collect_repo_info("dem2-webui", WEBUI_REPO, pr_number)

        # Collect dem2-infra repository info
        data["repositories"]["dem2-infra"] = self._collect_infra_info()

        # Collect ArgoCD deployment info
        data["argocd"] = self._collect_argocd_info()

        # Collect summary
        dem2_tag = check_git_tag(DEM2_REPO, f"preview-{self.preview_id}")
        webui_tag = check_git_tag(WEBUI_REPO, f"preview-{self.preview_id}")
        infra_branch = check_git_branch(INFRA_REPO, f"preview/{self.preview_id}")

        data["summary"] = {
            "has_dem2_tag": dem2_tag.exists,
            "has_webui_tag": webui_tag.exists,
            "has_infra_branch": infra_branch.exists,
            "is_clean": not (dem2_tag.exists or webui_tag.exists or infra_branch.exists)
        }

        return data

    def _collect_repo_info(self, repo_name: str, repo_path: Path, pr_number: Optional[int]) -> dict:
        """Collect information about a repository."""
        info = {
            "name": repo_name,
            "tag": {},
            "pr": None
        }

        tag_info = check_git_tag(repo_path, f"preview-{self.preview_id}")
        info["tag"] = {
            "name": f"preview-{self.preview_id}",
            "exists": tag_info.exists,
            "commit": tag_info.commit[:8] if tag_info.commit else None,
            "date": tag_info.date
        }

        # Collect PR info if we have a number
        if pr_number:
            pr_info = get_pr_info(repo_name, pr_number)
            if pr_info:
                info["pr"] = {
                    "number": pr_number,
                    "title": pr_info.title,
                    "state": pr_info.state,
                    "branch": pr_info.head_ref,
                    "author": pr_info.author,
                    "created_at": pr_info.created_at,
                    "merged_at": pr_info.merged_at,
                    "closed_at": pr_info.closed_at,
                    "url": pr_info.url
                }

        return info

    def _collect_infra_info(self) -> dict:
        """Collect information about dem2-infra repository."""
        info = {
            "branch": {
                "name": f"preview/{self.preview_id}",
                "exists": False,
                "location": None
            },
            "pr": None
        }

        branch_info = check_git_branch(INFRA_REPO, f"preview/{self.preview_id}")
        info["branch"]["exists"] = branch_info.exists
        info["branch"]["location"] = branch_info.location if branch_info.exists else None

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
                        info["pr"] = {
                            "number": pr_data["number"],
                            "title": pr_data["title"],
                            "state": pr_data["state"],
                            "author": pr_data["author"]["login"],
                            "created_at": pr_data["createdAt"],
                            "merged_at": pr_data.get("mergedAt"),
                            "closed_at": pr_data.get("closedAt"),
                            "url": pr_data["url"]
                        }
                except (json.JSONDecodeError, KeyError):
                    pass

        return info

    def _collect_argocd_info(self) -> dict:
        """Collect ArgoCD deployment information."""
        argocd_app, infra_pr_num = self.get_argocd_app_name()
        argocd_url = f"https://argo.n1-machina.dev/applications/{argocd_app}"

        info = {
            "app_name": argocd_app,
            "infra_pr_number": infra_pr_num,
            "url": argocd_url,
            "sync_status": None,
            "health_status": None,
            "available": check_command_available("argocd")
        }

        # Try to get ArgoCD status
        if info["available"]:
            app_status = get_argocd_app_status(argocd_app)
            if app_status:
                info["sync_status"] = app_status.get("status", {}).get("sync", {}).get("status", "Unknown")
                info["health_status"] = app_status.get("status", {}).get("health", {}).get("status", "Unknown")

        return info

    def show_info(self, output_format: str = "terminal") -> None:
        """Display detailed information about the preview environment.

        Args:
            output_format: Output format - 'terminal' (default), 'json', or 'markdown'
        """
        data = self.collect_info()

        if output_format == "json":
            self._show_info_json(data)
        elif output_format == "markdown":
            self._show_info_markdown(data)
        else:
            self._show_info_terminal(data)

    def _show_info_json(self, data: dict) -> None:
        """Display information in JSON format."""
        print(json.dumps(data, indent=2))

    def _show_info_markdown(self, data: dict) -> None:
        """Display information in Markdown table format (single giant table)."""
        print(f"# Preview Environment: {data['preview_id']}\n")

        print("| Section | Field | Value |")
        print("|---------|-------|-------|")

        # Identifier Resolution
        print(f"| **Identifier** | Input Type | {data['identifier']['type']} |")
        print(f"| **Identifier** | Input Value | {data['identifier']['value']} |")
        print(f"| **Identifier** | Resolved Preview ID | {data['preview_id']} |")

        # dem2 Repository
        dem2 = data["repositories"]["dem2"]
        print(f"| **dem2 (Backend)** | Preview Tag | {'✅ ' + dem2['tag']['name'] if dem2['tag']['exists'] else '❌ Not found'} |")
        if dem2['tag']['exists']:
            if dem2['tag']['commit']:
                print(f"| **dem2 (Backend)** | Tag Commit | {dem2['tag']['commit']} |")
            if dem2['tag']['date']:
                print(f"| **dem2 (Backend)** | Tag Date | {dem2['tag']['date']} |")
        if dem2['pr']:
            pr = dem2['pr']
            status_emoji = "✅" if pr['state'] == "OPEN" else "🔵" if pr['state'] == "MERGED" else "❌"
            print(f"| **dem2 (Backend)** | PR #{pr['number']} | {pr['title']} |")
            print(f"| **dem2 (Backend)** | PR Status | {status_emoji} {pr['state']} |")
            print(f"| **dem2 (Backend)** | PR Branch | {pr['branch']} |")
            print(f"| **dem2 (Backend)** | PR Author | {pr['author']} |")
            print(f"| **dem2 (Backend)** | PR Created | {format_timestamp(pr['created_at'])} |")
            print(f"| **dem2 (Backend)** | PR URL | {pr['url']} |")

        # dem2-webui Repository
        webui = data["repositories"]["dem2-webui"]
        print(f"| **dem2-webui (Frontend)** | Preview Tag | {'✅ ' + webui['tag']['name'] if webui['tag']['exists'] else '❌ Not found'} |")
        if webui['tag']['exists']:
            if webui['tag']['commit']:
                print(f"| **dem2-webui (Frontend)** | Tag Commit | {webui['tag']['commit']} |")
            if webui['tag']['date']:
                print(f"| **dem2-webui (Frontend)** | Tag Date | {webui['tag']['date']} |")
        if webui['pr']:
            pr = webui['pr']
            status_emoji = "✅" if pr['state'] == "OPEN" else "🔵" if pr['state'] == "MERGED" else "❌"
            print(f"| **dem2-webui (Frontend)** | PR #{pr['number']} | {pr['title']} |")
            print(f"| **dem2-webui (Frontend)** | PR Status | {status_emoji} {pr['state']} |")
            print(f"| **dem2-webui (Frontend)** | PR Branch | {pr['branch']} |")
            print(f"| **dem2-webui (Frontend)** | PR Author | {pr['author']} |")
            print(f"| **dem2-webui (Frontend)** | PR Created | {format_timestamp(pr['created_at'])} |")
            print(f"| **dem2-webui (Frontend)** | PR URL | {pr['url']} |")

        # Infrastructure
        infra = data["repositories"]["dem2-infra"]
        branch_status = f"{infra['branch']['location']}" if infra['branch']['exists'] else "NOT_FOUND"
        print(f"| **dem2-infra (Infrastructure)** | Preview Branch | {infra['branch']['name']}: {branch_status} |")
        if infra['pr']:
            pr = infra['pr']
            status_emoji = "✅" if pr['state'] == "OPEN" else "🔵" if pr['state'] == "MERGED" else "❌"
            print(f"| **dem2-infra (Infrastructure)** | PR #{pr['number']} | {pr['title']} |")
            print(f"| **dem2-infra (Infrastructure)** | PR Status | {status_emoji} {pr['state']} |")
            print(f"| **dem2-infra (Infrastructure)** | PR Author | {pr['author']} |")
            print(f"| **dem2-infra (Infrastructure)** | PR Created | {format_timestamp(pr['created_at'])} |")
            print(f"| **dem2-infra (Infrastructure)** | PR URL | {pr['url']} |")
        else:
            print(f"| **dem2-infra (Infrastructure)** | Infra PR | ⚪ Not found |")

        # ArgoCD Deployment
        argocd = data["argocd"]
        if argocd['infra_pr_number']:
            print(f"| **ArgoCD** | Application Name | {argocd['app_name']} (based on infra PR #{argocd['infra_pr_number']}) |")
        else:
            print(f"| **ArgoCD** | Application Name | {argocd['app_name']} (infra PR not found, using fallback) |")
        print(f"| **ArgoCD** | URL | {argocd['url']} |")
        if argocd['sync_status']:
            print(f"| **ArgoCD** | Sync Status | {argocd['sync_status']} |")
            print(f"| **ArgoCD** | Health Status | {argocd['health_status']} |")
        elif argocd['available']:
            print(f"| **ArgoCD** | Status | ⚪ Cannot retrieve (app may not exist) |")
        else:
            print(f"| **ArgoCD** | Status | ⚪ ArgoCD CLI not available |")

        # Summary
        summary = data["summary"]
        if not summary["is_clean"]:
            artifacts = []
            if summary["has_dem2_tag"]:
                artifacts.append(f"dem2 tag: preview-{data['preview_id']}")
            if summary["has_webui_tag"]:
                artifacts.append(f"webui tag: preview-{data['preview_id']}")
            if summary["has_infra_branch"]:
                artifacts.append(f"infra branch: preview/{data['preview_id']}")
            print(f"| **Summary** | Artifacts | {', '.join(artifacts)} |")
        else:
            print(f"| **Summary** | Status | ✅ No preview artifacts found - environment is clean |")

    def _show_info_terminal(self, data: dict) -> None:
        """Display information in terminal format (original colorized output)."""
        print_header(f"Preview Environment: {data['preview_id']}")

        # Show identifier resolution
        print()
        print_color(Color.CYAN, "Identifier Resolution:")
        print_kv("  Input Type", data['identifier']['type'])
        print_kv("  Input Value", data['identifier']['value'])
        print_kv("  Resolved Preview ID", data['preview_id'])
        print()

        # Show dem2 repository
        self._show_repo_info_terminal(data['repositories']['dem2'], "Backend")

        # Show dem2-webui repository
        self._show_repo_info_terminal(data['repositories']['dem2-webui'], "Frontend")

        # Show dem2-infra repository
        self._show_infra_info_terminal(data['repositories']['dem2-infra'])

        # Show ArgoCD deployment
        self._show_argocd_info_terminal(data['argocd'])

        # Show summary
        self._show_summary_terminal(data['summary'], data['preview_id'])

    def _show_repo_info_terminal(self, repo: dict, label: str) -> None:
        """Show repository information in terminal format."""
        print_header(f"{repo['name']} ({label})")

        tag = repo['tag']
        if tag['exists']:
            print_kv("Preview Tag", f"{Symbol.CHECK} {tag['name']}")
            if tag['commit']:
                print_kv("Tag Commit", tag['commit'])
            if tag['date']:
                print_kv("Tag Date", tag['date'])
        else:
            print_kv("Preview Tag", f"{Symbol.CROSS} Not found")

        # Show PR info if available
        if repo['pr']:
            pr = repo['pr']
            print_kv(f"PR #{pr['number']}", pr['title'])

            if pr['state'] == "OPEN":
                status = f"{Color.GREEN}{Symbol.CHECK} OPEN{Color.NC}"
            elif pr['state'] == "MERGED":
                status = f"{Color.BLUE}{Symbol.CHECK} MERGED{Color.NC} ({format_timestamp(pr['merged_at'])})"
            else:
                status = f"{Color.RED}{Symbol.CROSS} CLOSED{Color.NC} ({format_timestamp(pr['closed_at'])})"

            print_kv("Status", status)
            print_kv("Branch", pr['branch'])
            print_kv("Author", pr['author'])
            print_kv("Created", format_timestamp(pr['created_at']))
            print_kv("URL", pr['url'])

    def _show_infra_info_terminal(self, infra: dict) -> None:
        """Show dem2-infra information in terminal format."""
        print_header("dem2-infra (Infrastructure)")

        branch = infra['branch']
        branch_status = branch['location'] if branch['exists'] else 'NOT_FOUND'
        print_kv("Preview Branch", f"{branch['name']}: {branch_status}")

        # Show PR info if available
        if infra['pr']:
            pr = infra['pr']
            print_kv(f"PR #{pr['number']}", pr['title'])

            if pr['state'] == "OPEN":
                status = f"{Color.GREEN}{Symbol.CHECK} OPEN{Color.NC}"
            elif pr['state'] == "MERGED":
                status = f"{Color.BLUE}{Symbol.CHECK} MERGED{Color.NC} ({format_timestamp(pr['merged_at'])})"
            else:
                status = f"{Color.RED}{Symbol.CROSS} CLOSED{Color.NC} ({format_timestamp(pr['closed_at'])})"

            print_kv("Status", status)
            print_kv("Author", pr['author'])
            print_kv("Created", format_timestamp(pr['created_at']))
            print_kv("URL", pr['url'])
        else:
            print_kv("Infra PR", f"{Symbol.CIRCLE} Not found")

    def _show_argocd_info_terminal(self, argocd: dict) -> None:
        """Show ArgoCD deployment information in terminal format."""
        print_header("ArgoCD Deployment")

        if argocd['infra_pr_number']:
            print_kv("Application Name", f"{argocd['app_name']} (based on infra PR #{argocd['infra_pr_number']})")
        else:
            print_kv("Application Name", f"{argocd['app_name']} (infra PR not found, using fallback)")

        print_kv("ArgoCD URL", argocd['url'])

        # Show ArgoCD status if available
        if argocd['sync_status']:
            print_kv("Sync Status", argocd['sync_status'])
            print_kv("Health Status", argocd['health_status'])
        elif argocd['available']:
            print_kv("Status", f"{Symbol.CIRCLE} Cannot retrieve (app may not exist)")
        else:
            print_kv("Status", f"{Symbol.CIRCLE} ArgoCD CLI not available")

    def _show_summary_terminal(self, summary: dict, preview_id: str) -> None:
        """Show summary of preview environment in terminal format."""
        print_header("Summary")

        # Show artifact summary
        if not summary['is_clean']:
            print()
            print_color(Color.CYAN, "  Preview Environment Artifacts:")

            if summary['has_dem2_tag']:
                print(f"    • dem2 has preview tag: preview-{preview_id}")

            if summary['has_webui_tag']:
                print(f"    • dem2-webui has preview tag: preview-{preview_id}")

            if summary['has_infra_branch']:
                print(f"    • dem2-infra has preview branch: preview/{preview_id}")
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
    output_format = getattr(args, 'format', 'terminal')

    try:
        env = PreviewEnvironment.resolve(id_type, identifier)
        env.show_info(output_format=output_format)
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
    info_parser.add_argument("--format", choices=["terminal", "json", "markdown"], default="markdown",
                            help="Output format (default: markdown)")
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
