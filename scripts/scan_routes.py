#!/usr/bin/env python3
"""
Scan API routes from all services in the machina-meta workspace.

This script discovers routes from:
- FastAPI services (dem2, medical-catalog)
- Next.js App Router pages and API routes (dem2-webui)

Output: routes.json with structured route data for all services.
"""

import ast
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class RouteInfo:
    """Information about a single API route or page."""

    service: str
    port: int
    path: str
    method: str
    description: str
    file_path: str
    line_number: int = 0
    handler_name: str = ""
    parameters: list[str] = field(default_factory=list)
    response_model: str = ""


class FastAPIRouteScanner:
    """Scanner for FastAPI routes in Python files using regex for reliability."""

    HTTP_METHODS = ["get", "post", "put", "patch", "delete", "options", "head", "websocket"]

    def __init__(self, service_name: str, port: int, base_path: Path):
        self.service_name = service_name
        self.port = port
        self.base_path = base_path
        self.routes: list[RouteInfo] = []

    def scan(self) -> list[RouteInfo]:
        """Scan all Python files for FastAPI routes."""
        # Exclude common directories
        exclude_dirs = {
            ".venv",
            "venv",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".git",
            "alembic",
        }

        python_files = []
        for py_file in self.base_path.rglob("*.py"):
            # Skip if any part of the path is in exclude_dirs
            if any(part in exclude_dirs for part in py_file.parts):
                continue
            # Skip test files
            if "test" in py_file.stem.lower() or "test" in py_file.parent.name.lower():
                continue
            python_files.append(py_file)

        print(f"  Scanning {len(python_files)} Python files in {self.service_name}...")

        for py_file in python_files:
            try:
                self._scan_file(py_file)
            except Exception as e:
                print(f"    Warning: Failed to parse {py_file}: {e}")

        print(f"  Found {len(self.routes)} routes in {self.service_name}")
        return self.routes

    def _scan_file(self, file_path: Path) -> None:
        """Scan a single Python file for route definitions using regex."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return

        # Extract router prefix from APIRouter initialization
        router_prefix = self._extract_router_prefix_regex(content)

        # Find all route decorators using regex
        # Pattern matches: @router.METHOD("path", ...optional params...) or @router.METHOD('path', ...)
        for method in self.HTTP_METHODS:
            pattern = rf'@router\.{method}\s*\(\s*["\']([^"\']+)["\']'
            matches = re.finditer(pattern, content, re.MULTILINE)

            for match in matches:
                route_path = match.group(1)
                decorator_start = match.start()

                # Find the function definition after this decorator
                func_pattern = r'\n\s*(?:async\s+)?def\s+(\w+)\s*\('
                func_match = re.search(func_pattern, content[decorator_start:])

                if not func_match:
                    continue

                handler_name = func_match.group(1)
                func_start = decorator_start + func_match.start()

                # Extract docstring if present
                description = self._extract_docstring(content, func_start)

                # Extract response_model from decorator if present
                response_model = self._extract_response_model(content, decorator_start, func_start)

                # Combine router prefix with route path
                full_path = router_prefix + route_path if router_prefix else route_path
                full_path = full_path.replace("//", "/")

                # Get line number
                line_number = content[:decorator_start].count('\n') + 1

                relative_file = file_path.relative_to(self.base_path)

                self.routes.append(
                    RouteInfo(
                        service=self.service_name,
                        port=self.port,
                        path=full_path,
                        method=method.upper() if method != "websocket" else "WS",
                        description=description,
                        file_path=str(relative_file),
                        line_number=line_number,
                        handler_name=handler_name,
                        response_model=response_model,
                    )
                )

    def _extract_router_prefix_regex(self, content: str) -> str:
        """Extract router prefix using regex."""
        # Pattern: router = APIRouter(prefix="/api/v1/xxx", ...)
        patterns = [
            r'router\s*=\s*APIRouter\s*\(\s*prefix\s*=\s*["\']([^"\']+)["\']',
            r'router\s*=\s*APIRouter\s*\([^)]*prefix\s*=\s*["\']([^"\']+)["\']',
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)

        return ""

    def _extract_docstring(self, content: str, func_start: int) -> str:
        """Extract first line of docstring from function."""
        # Look for docstring after function definition
        # Pattern: def func(): """docstring"""
        docstring_pattern = r'def\s+\w+[^:]*:\s*(?:"""([^"]+)"""|\'\'\'([^\']+)\'\'\')'
        match = re.search(docstring_pattern, content[func_start:func_start + 500])

        if match:
            docstring = match.group(1) or match.group(2)
            # Take only first line
            return docstring.split('\n')[0].strip()

        return ""

    def _extract_response_model(self, content: str, decorator_start: int, func_start: int) -> str:
        """Extract response_model from decorator."""
        decorator_text = content[decorator_start:func_start]

        # Pattern: response_model=SomeModel or response_model = SomeModel
        pattern = r'response_model\s*=\s*([A-Za-z_][\w\[\],\s]*)'
        match = re.search(pattern, decorator_text)

        if match:
            model = match.group(1).strip()
            # Clean up (remove trailing commas, spaces, etc.)
            model = re.sub(r'[,\s)]+$', '', model)
            return model

        return ""


class NextJSRouteScanner:
    """Scanner for Next.js App Router pages and API routes."""

    def __init__(self, service_name: str, port: int, base_path: Path):
        self.service_name = service_name
        self.port = port
        self.base_path = base_path
        self.app_dir = base_path / "src" / "app"
        self.routes: list[RouteInfo] = []

    def scan(self) -> list[RouteInfo]:
        """Scan Next.js app directory for routes."""
        if not self.app_dir.exists():
            print(f"  Warning: {self.app_dir} does not exist")
            return []

        print(f"  Scanning Next.js routes in {self.service_name}...")

        # Scan API routes (route.ts/tsx files)
        self._scan_api_routes()

        # Scan page routes (page.tsx files)
        self._scan_page_routes()

        print(f"  Found {len(self.routes)} routes in {self.service_name}")
        return self.routes

    def _scan_api_routes(self) -> None:
        """Scan App Router API routes (route.ts/tsx files)."""
        route_files = list(self.app_dir.glob("**/route.ts")) + list(
            self.app_dir.glob("**/route.tsx")
        )

        for route_file in route_files:
            try:
                content = route_file.read_text(encoding="utf-8")
                self._extract_api_route_handlers(route_file, content)
            except Exception as e:
                print(f"    Warning: Failed to parse {route_file}: {e}")

    def _extract_api_route_handlers(self, file_path: Path, content: str) -> None:
        """Extract HTTP method handlers from API route file."""
        # Convert file path to URL path
        relative_path = file_path.relative_to(self.app_dir)
        url_path = "/" + str(relative_path.parent).replace("\\", "/")

        # Remove route groups (folders in parentheses)
        url_path = re.sub(r'/\([^)]+\)', '', url_path)

        # Clean up path
        if url_path == "/.":
            url_path = "/"

        # Find exported HTTP method handlers
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
        for method in methods:
            # Match: export async function GET() or export function POST()
            pattern = rf'export\s+(?:async\s+)?function\s+{method}\s*\('
            if re.search(pattern, content):
                # Try to extract description from comments or JSDoc
                description = self._extract_description(content, method)

                relative_file = file_path.relative_to(self.base_path)
                self.routes.append(
                    RouteInfo(
                        service=self.service_name,
                        port=self.port,
                        path=url_path,
                        method=method,
                        description=description,
                        file_path=str(relative_file),
                        handler_name=method,
                    )
                )

    def _scan_page_routes(self) -> None:
        """Scan App Router page routes (page.tsx files)."""
        page_files = list(self.app_dir.glob("**/page.tsx"))

        for page_file in page_files:
            try:
                content = page_file.read_text(encoding="utf-8")
                self._extract_page_route(page_file, content)
            except Exception as e:
                print(f"    Warning: Failed to parse {page_file}: {e}")

    def _extract_page_route(self, file_path: Path, content: str) -> None:
        """Extract page route information."""
        # Convert file path to URL path
        relative_path = file_path.relative_to(self.app_dir)
        url_path = "/" + str(relative_path.parent).replace("\\", "/")

        # Remove route groups (folders in parentheses)
        url_path = re.sub(r'/\([^)]+\)', '', url_path)

        # Clean up path
        if url_path == "/.":
            url_path = "/"

        # Extract description from metadata or comments
        description = self._extract_page_description(content)

        # Determine if it's a client or server component
        is_client = '"use client"' in content or "'use client'" in content

        component_type = "Client Component" if is_client else "Server Component"
        description = f"{description} ({component_type})" if description else component_type

        relative_file = file_path.relative_to(self.base_path)
        self.routes.append(
            RouteInfo(
                service=self.service_name,
                port=self.port,
                path=url_path,
                method="PAGE",
                description=description,
                file_path=str(relative_file),
            )
        )

    def _extract_description(self, content: str, method: str) -> str:
        """Extract description from JSDoc comment before method handler."""
        # Look for JSDoc comment before the function
        pattern = rf'/\*\*\s*\n\s*\*\s*([^\n]+)\s*\n\s*\*/\s*export\s+(?:async\s+)?function\s+{method}'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()

        # Look for single-line comment
        pattern = rf'//\s*([^\n]+)\s*\nexport\s+(?:async\s+)?function\s+{method}'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()

        return ""

    def _extract_page_description(self, content: str) -> str:
        """Extract description from page metadata or default export."""
        # Look for metadata title
        match = re.search(r'title:\s*[\'"`]([^\'"`]+)[\'"`]', content)
        if match:
            return match.group(1).strip()

        # Look for component name in default export
        match = re.search(r'export\s+default\s+function\s+(\w+)', content)
        if match:
            component_name = match.group(1)
            # Convert PascalCase to words
            name_words = re.sub(r'([A-Z])', r' \1', component_name).strip()
            return name_words

        return ""


def scan_all_services(workspace_root: Path) -> dict[str, Any]:
    """Scan all services in the workspace for routes."""
    routes: list[RouteInfo] = []

    # Service definitions
    services = [
        {
            "name": "dem2",
            "port": 8000,
            "path": workspace_root / "repos" / "dem2",
            "scanner": FastAPIRouteScanner,
        },
        {
            "name": "medical-catalog",
            "port": 8001,
            "path": workspace_root / "repos" / "medical-catalog",
            "scanner": FastAPIRouteScanner,
        },
        {
            "name": "dem2-webui",
            "port": 3000,
            "path": workspace_root / "repos" / "dem2-webui",
            "scanner": NextJSRouteScanner,
        },
    ]

    for service in services:
        print(f"\nScanning {service['name']}...")
        if not service["path"].exists():
            print(f"  Warning: {service['path']} does not exist, skipping")
            continue

        scanner = service["scanner"](service["name"], service["port"], service["path"])
        service_routes = scanner.scan()
        routes.extend(service_routes)

    # Sort routes by service, then by path
    routes.sort(key=lambda r: (r.service, r.path))

    # Convert to dict format
    routes_data = {
        "scan_date": datetime.now().isoformat(),
        "total_routes": len(routes),
        "services": list({r.service for r in routes}),
        "routes": [
            {
                "service": r.service,
                "port": r.port,
                "path": r.path,
                "method": r.method,
                "description": r.description,
                "file_path": r.file_path,
                "line_number": r.line_number,
                "handler_name": r.handler_name,
                "parameters": r.parameters,
                "response_model": r.response_model,
            }
            for r in routes
        ],
    }

    return routes_data


def main() -> None:
    """Main entry point."""
    # Determine workspace root (parent of scripts/)
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent

    print(f"Workspace root: {workspace_root}")
    print("=" * 80)

    # Scan all services
    routes_data = scan_all_services(workspace_root)

    # Write JSON output
    output_file = workspace_root / "routes.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(routes_data, f, indent=2)

    print("\n" + "=" * 80)
    print(f"✓ Scan complete!")
    print(f"  Total routes: {routes_data['total_routes']}")
    print(f"  Services: {', '.join(routes_data['services'])}")
    print(f"  Output: {output_file}")


if __name__ == "__main__":
    main()
