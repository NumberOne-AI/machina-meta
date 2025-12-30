#!/usr/bin/env python3
"""
Scan API routes from all services in the machina-meta workspace.

This script discovers routes from:
- FastAPI services (dem2, medical-catalog) - Uses OpenAPI JSON
- Next.js App Router pages and API routes (dem2-webui)

Output: routes.json with structured route data for all services.
"""

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


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
    """Scanner for FastAPI routes using OpenAPI JSON specification."""

    def __init__(self, service_name: str, port: int, openapi_url: str):
        self.service_name = service_name
        self.port = port
        self.openapi_url = openapi_url
        self.routes: list[RouteInfo] = []

    def scan(self) -> list[RouteInfo]:
        """Scan FastAPI routes from OpenAPI JSON."""
        print(f"  Fetching OpenAPI spec from {self.openapi_url}...")

        try:
            response = requests.get(self.openapi_url, timeout=5)
            response.raise_for_status()
            openapi_spec = response.json()
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  Could not connect to {self.openapi_url}")
            print(f"  ⚠️  Make sure {self.service_name} is running on port {self.port}")
            print(f"  ⚠️  Start service with: cd repos/{self.service_name} && just run")
            return []
        except requests.exceptions.Timeout:
            print(f"  ⚠️  Timeout connecting to {self.openapi_url}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Error fetching OpenAPI spec: {e}")
            return []
        except json.JSONDecodeError:
            print(f"  ⚠️  Invalid JSON response from {self.openapi_url}")
            return []

        # Parse OpenAPI spec
        paths = openapi_spec.get("paths", {})
        print(f"  Parsing {len(paths)} paths from OpenAPI spec...")

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                # Skip non-HTTP methods
                if method.lower() not in ["get", "post", "put", "patch", "delete", "options", "head"]:
                    continue

                # Extract route information
                summary = operation.get("summary", "")
                description = operation.get("description", summary)
                operation_id = operation.get("operationId", "")

                # Get response model from responses section
                response_model = ""
                responses = operation.get("responses", {})
                success_response = responses.get("200") or responses.get("201") or responses.get("202")
                if success_response and "content" in success_response:
                    content = success_response["content"]
                    if "application/json" in content:
                        schema = content["application/json"].get("schema", {})
                        if "$ref" in schema:
                            # Extract model name from $ref
                            ref = schema["$ref"]
                            response_model = ref.split("/")[-1]
                        elif "title" in schema:
                            response_model = schema["title"]

                # Get parameters
                parameters = []
                for param in operation.get("parameters", []):
                    param_name = param.get("name", "")
                    if param_name:
                        parameters.append(param_name)

                # Get tags (can be used to infer source file/module)
                tags = operation.get("tags", [])
                file_hint = tags[0] if tags else ""

                self.routes.append(
                    RouteInfo(
                        service=self.service_name,
                        port=self.port,
                        path=path,
                        method=method.upper(),
                        description=description or summary,
                        file_path=f"{file_hint}" if file_hint else "(OpenAPI)",
                        line_number=0,
                        handler_name=operation_id,
                        parameters=parameters,
                        response_model=response_model,
                    )
                )

        print(f"  Found {len(self.routes)} routes in {self.service_name}")
        return self.routes


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
            "type": "fastapi",
            "openapi_url": "http://localhost:8000/api/v1/openapi.json",
        },
        {
            "name": "medical-catalog",
            "port": 8001,
            "type": "fastapi",
            "openapi_url": "http://localhost:8001/openapi.json",
        },
        {
            "name": "dem2-webui",
            "port": 3000,
            "type": "nextjs",
            "path": workspace_root / "repos" / "dem2-webui",
        },
    ]

    for service in services:
        print(f"\nScanning {service['name']}...")

        if service["type"] == "fastapi":
            scanner = FastAPIRouteScanner(
                service["name"],
                service["port"],
                service["openapi_url"]
            )
            service_routes = scanner.scan()
            routes.extend(service_routes)

        elif service["type"] == "nextjs":
            if not service["path"].exists():
                print(f"  Warning: {service['path']} does not exist, skipping")
                continue

            scanner = NextJSRouteScanner(
                service["name"],
                service["port"],
                service["path"]
            )
            service_routes = scanner.scan()
            routes.extend(service_routes)

    # Group routes by service
    services_data = {}
    for route in routes:
        if route.service not in services_data:
            services_data[route.service] = {
                "port": route.port,
                "routes": []
            }

        services_data[route.service]["routes"].append({
            "path": route.path,
            "method": route.method,
            "description": route.description,
            "file_path": route.file_path,
            "line_number": route.line_number,
            "handler_name": route.handler_name,
            "parameters": route.parameters,
            "response_model": route.response_model,
        })

    # Sort routes within each service by path
    for service_data in services_data.values():
        service_data["routes"].sort(key=lambda r: r["path"])

    # Build final structure
    routes_data = {
        "scan_date": datetime.now().isoformat(),
        "total_routes": len(routes),
        "services": services_data,
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
