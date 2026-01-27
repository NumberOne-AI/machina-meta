#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "neo4j>=5.18.0",
#     "neo4j-graphrag[google]>=0.1.0",
#     "pyyaml",
#     "tabulate",
#     "google-genai>=0.2.0",
# ]
# ///
"""
Neo4j GraphRAG CLI - Run natural language queries against Neo4j using Gemini.

Uses neo4j-graphrag to translate natural language to Cypher queries via Google Vertex AI.

Usage:
    ./scripts/graphrag_cli.py "How many patients have high cholesterol?"
    ./scripts/graphrag_cli.py --model gemini-1.5-pro "List all biomarkers for patient X"
"""

import argparse
import json
import os
import re
import sys
import yaml
from pathlib import Path
from typing import Any, Optional

from neo4j import GraphDatabase

try:
    from google import genai
    from google.genai import types
    from neo4j_graphrag.llm import LLMInterface
    from neo4j_graphrag.llm.types import LLMResponse
    from neo4j_graphrag.retrievers import Text2CypherRetriever
except ImportError:
    print(
        "Error: Dependencies not found. Run with uv run or install dependencies.",
        file=sys.stderr,
    )
    sys.exit(1)


class GoogleGenAILLM(LLMInterface):
    """LLM Interface using the modern Google Gen AI SDK (google-genai)."""

    def __init__(
        self,
        model_name: str,
        project_id: str,
        location: str,
        model_params: Optional[dict[str, Any]] = None,
    ):
        super().__init__(model_name, model_params)
        self.client = genai.Client(vertexai=True, project=project_id, location=location)

    def invoke(
        self,
        input: str,
        message_history: Optional[Any] = None,
        system_instruction: Optional[str] = None,
    ) -> LLMResponse:
        # Simple invoke implementation for Text2Cypher
        config = None
        if self.model_params:
            # Map params if needed, or pass directly if compatible
            # simple mapping for temperature
            config = types.GenerateContentConfig(
                temperature=self.model_params.get("temperature", 0.0)
            )

        response = self.client.models.generate_content(
            model=self.model_name, contents=input, config=config
        )
        return LLMResponse(content=response.text)

    async def ainvoke(
        self,
        input: str,
        message_history: Optional[Any] = None,
        system_instruction: Optional[str] = None,
    ) -> LLMResponse:
        config = None
        if self.model_params:
            config = types.GenerateContentConfig(
                temperature=self.model_params.get("temperature", 0.0)
            )

        response = await self.client.aio.models.generate_content(
            model=self.model_name, contents=input, config=config
        )
        return LLMResponse(content=response.text)


def find_workspace_root() -> Optional[Path]:
    """Find the machina-meta workspace root directory."""
    current = Path.cwd()
    try:
        while current != current.parent:
            if (current / "docker-compose.yaml").exists():
                return current
            current = current.parent
        # Fallback to script location if run from somewhere else
        script_path = Path(__file__).resolve()
        if (script_path.parent.parent / "docker-compose.yaml").exists():
            return script_path.parent.parent
    except Exception:
        pass

    # In K8s/Docker, we might just be at /app
    if Path("/app").exists():
        return Path("/app")

    return None


def load_env_variable(var_name: str, env_file: str = ".env") -> Optional[str]:
    """Load environment variable from env file or environment.

    Priority:
    1. Environment variable (if set)
    2. .env file in current directory
    3. .env file in workspace root
    """
    # Check environment variable first (highest priority)
    value = os.getenv(var_name)
    if value:
        return value

    # Try .env in current working directory and workspace root
    try:
        workspace_root = find_workspace_root()
        env_paths = [Path.cwd() / env_file]
        if workspace_root:
            env_paths.append(workspace_root / env_file)

        for env_path in env_paths:
            if env_path.exists():
                try:
                    with open(env_path) as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("#"):
                                continue
                            # Match: VAR_NAME=value
                            match = re.match(rf"^{re.escape(var_name)}=(.*)$", line)
                            if match:
                                return match.group(1).strip().strip('"').strip("'")
                except OSError:
                    continue
    except Exception:
        pass

    return None


def get_project_config() -> tuple[Optional[str], str]:
    """Get Google Cloud project ID and region from unified dot-environ state."""
    # Priority:
    # 1. Standard Google env vars (GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_REGION)
    # 2. Cloud SDK env vars from .env (CLOUDSDK_CORE_PROJECT, CLOUDSDK_COMPUTE_REGION)
    # 3. Fallbacks (GCP_PROJECT, defaults)

    project_id = (
        load_env_variable("GOOGLE_CLOUD_PROJECT")
        or load_env_variable("CLOUDSDK_CORE_PROJECT")
        or load_env_variable("GCP_PROJECT")
    )

    location = (
        load_env_variable("GOOGLE_CLOUD_REGION")
        or load_env_variable("CLOUDSDK_COMPUTE_REGION")
        or "global"
    )

    if not project_id:
        try:
            import google.auth

            _, detected_project = google.auth.default()
            if detected_project:
                project_id = detected_project
        except Exception:
            pass

    return project_id, location


def get_neo4j_auth() -> tuple[str, str, str]:
    """Get Neo4j connection details (uri, user, password)."""
    # Defaults
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "neo4j"  # fallback

    # Track if we found explicit configuration to avoid fallback overrides
    found_explicit_config = False

    # 1. Try env vars first (Cloud/K8s friendly)
    env_host = load_env_variable("DYNACONF_NEO4J_DB__HOST")
    env_port = load_env_variable("DYNACONF_NEO4J_DB__PORT")
    env_user = load_env_variable("DYNACONF_NEO4J_DB__USER")
    env_pass = load_env_variable("DYNACONF_NEO4J_DB__PASSWORD")
    env_http_port = load_env_variable("DYNACONF_NEO4J_DB__HTTP_PORT")

    # If host is just a hostname (e.g. 'neo4j'), assume standard port if not set
    # Note: K8s services often use simple names
    if env_host:
        port = env_port or "7687"
        uri = f"neo4j://{env_host}:{port}"
        found_explicit_config = True
    elif env_http_port:
        # Heuristic: If HTTP port is explicitly set (e.g. for tunneling) but Host/Bolt isn't,
        # assume localhost and infer Bolt port (standard offset is +213: 7474->7687)
        try:
            bolt_port = int(env_http_port) + 213
            uri = f"neo4j://localhost:{bolt_port}"
            found_explicit_config = True
        except ValueError:
            pass

    if env_user:
        user = env_user
    if env_pass:
        password = env_pass

    # 2. Try docker-compose if available (Local dev override)
    # Only if we haven't found explicit configuration in env vars
    workspace_root = find_workspace_root()
    if workspace_root and not found_explicit_config:
        compose_file = workspace_root / "docker-compose.yaml"
        if compose_file.exists():
            try:
                with open(compose_file) as f:
                    compose_data = yaml.safe_load(f)

                neo4j_service = compose_data.get("services", {}).get("neo4j", {})
                environment = neo4j_service.get("environment", [])

                # Extract auth from docker-compose environment list
                env_dict = {}
                for item in environment:
                    if isinstance(item, str) and "=" in item:
                        k, v = item.split("=", 1)
                        env_dict[k] = v

                auth_str = env_dict.get("NEO4J_AUTH", "neo4j/neo4j")
                if "/" in auth_str:
                    # Only override if we are using localhost (meaning we are outside containers)
                    # If we already found a remote host via env vars, keep it
                    if "localhost" in uri:
                        c_user, c_pass = auth_str.split("/", 1)
                        user = c_user
                        password = c_pass

                # Check port mapping for Bolt (7687) if we are on localhost
                if "localhost" in uri:
                    ports = neo4j_service.get("ports", [])
                    for p in ports:
                        if "7687" in p:
                            host_port = p.split(":")[0]
                            uri = f"neo4j://localhost:{host_port}"
                            break
            except Exception as e:
                print(
                    f"Warning: Could not parse docker-compose.yaml: {e}",
                    file=sys.stderr,
                )

    return uri, user, password


def setup_google_credentials() -> None:
    """Configures Google Cloud credentials.

    1. Checks GOOGLE_APPLICATION_CREDENTIALS env var.
    2. Checks .env files for GOOGLE_APPLICATION_CREDENTIALS.
    3. Falls back to ADC (Application Default Credentials).
    """
    if os.environ.get("USE_ADC"):
        # Force ADC
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        return

    # 1. & 2. Check env var and .env files
    creds_path = load_env_variable("GOOGLE_APPLICATION_CREDENTIALS")

    if creds_path:
        # Resolve relative paths relative to workspace root
        path_obj = Path(creds_path)
        if not path_obj.is_absolute():
            try:
                workspace_root = find_workspace_root()
                path_obj = workspace_root / creds_path
            except Exception:
                pass

        if path_obj.exists():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(path_obj)
            # print(f"Using Google Credentials: {path_obj}", file=sys.stderr)
            return
        else:
            print(
                f"Warning: GOOGLE_APPLICATION_CREDENTIALS points to missing file: {path_obj}",
                file=sys.stderr,
            )

    # 3. Fallback to ADC
    # The Google client libraries automatically look for ADC if the env var is not set.
    # We just inform the user.
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        # Check if ADC is configured via gcloud
        adc_path = Path.home() / ".config/gcloud/application_default_credentials.json"
        if not adc_path.exists():
            print(
                "Note: No explicit credentials found in .env and no ADC file found at default location.",
                file=sys.stderr,
            )
            print(
                "If authentication fails, run: gcloud auth application-default login",
                file=sys.stderr,
            )
    """Get Google Cloud project ID and region from unified dot-environ state."""
    # Priority:
    # 1. Standard Google env vars (GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_REGION)
    # 2. Cloud SDK env vars from .env (CLOUDSDK_CORE_PROJECT, CLOUDSDK_COMPUTE_REGION)
    # 3. Fallbacks (GCP_PROJECT, defaults)

    project_id = (
        load_env_variable("GOOGLE_CLOUD_PROJECT")
        or load_env_variable("CLOUDSDK_CORE_PROJECT")
        or load_env_variable("GCP_PROJECT")
    )

    location = (
        load_env_variable("GOOGLE_CLOUD_REGION")
        or load_env_variable("CLOUDSDK_COMPUTE_REGION")
        or "us-central1"
    )

    return project_id, location


def probe_working_model(project_id: str, location: str) -> Optional[str]:
    """Probe specific models to see if they work (fallback when listing fails)."""
    candidates = [
        "gemini-3-pro-preview",  # Preview model, often global
        "gemini-1.5-flash",  # Current stable alias
        "gemini-1.5-pro",
        "gemini-1.5-flash-001",
        "gemini-1.0-pro",
    ]

    print(f"Probing models in {location}...", file=sys.stderr)

    try:
        client = genai.Client(vertexai=True, project=project_id, location=location)
    except Exception:
        return None

    for model_name in candidates:
        try:
            # Try to generate a single token
            client.models.generate_content(model=model_name, contents="Hi")
            print(f"Probe successful: {model_name}", file=sys.stderr)
            return model_name
        except Exception:
            continue

    return None


def find_working_model(project_id: str | None, location: str) -> str:
    """Find the best available Gemini model by probing."""

    if not project_id:
        print("Warning: No project ID found. Cannot probe models.", file=sys.stderr)
        return "gemini-1.5-flash-001"

    print("Auto-selecting best available model...", file=sys.stderr)

    # 1. Probe models directly
    probed = probe_working_model(project_id, location)
    if probed:
        return probed

    # 2. Smart Fallback: If location was NOT global, try global
    if location != "global":
        print(
            f"Warning: Probing failed in {location}. Trying 'global' location...",
            file=sys.stderr,
        )
        try:
            probed = probe_working_model(project_id, "global")
            if probed:
                print(
                    "Switching to global location for subsequent calls.",
                    file=sys.stderr,
                )
                return probed
        except Exception:
            pass

    # 3. Last Resort
    print(
        "Warning: Could not verify any model. Defaulting to gemini-1.5-flash-001",
        file=sys.stderr,
    )
    return "gemini-1.5-flash-001"

    print("Auto-selecting best available model...", file=sys.stderr)

    # 1. Try to list available models from API
    available = list_available_models(project_id, location)

    if available:
        # Preference order
        preferences = [
            "gemini-3-pro-preview",
            "gemini-1.5-pro-001",
            "gemini-1.5-flash-001",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro",
        ]

        # Find first preference that exists in available list AND works
        for pref in preferences:
            if pref in available:
                # Verify it actually works (listing might be optimistic)
                if probe_working_model(project_id, location) == pref:
                    # probe_working_model checks the whole list, which is inefficient here
                    # Let's check this specific model
                    try:
                        client = genai.Client(
                            vertexai=True, project=project_id, location=location
                        )
                        client.models.generate_content(model=pref, contents="Hi")
                        print(f"Selected model: {pref}", file=sys.stderr)
                        return pref
                    except Exception:
                        print(
                            f"Model {pref} listed but failed probing.", file=sys.stderr
                        )
                        continue

        # If no preferred model found/working, pick the first gemini one that works
        for model_id in available:
            try:
                client = genai.Client(
                    vertexai=True, project=project_id, location=location
                )
                client.models.generate_content(model=model_id, contents="Hi")
                print(f"Selected model: {model_id}", file=sys.stderr)
                return model_id
            except Exception:
                continue

    # 2. Fallback: Probe models directly if listing failed or returned nothing
    print(
        "Warning: listing models failed/empty. Probing candidates...", file=sys.stderr
    )
    probed = probe_working_model(project_id, location)
    if probed:
        return probed

    # 3. Smart Fallback: If location was NOT global, try global
    if location != "global":
        print(
            f"Warning: Probing failed in {location}. Trying 'global' location...",
            file=sys.stderr,
        )
        try:
            probed = probe_working_model(project_id, "global")
            if probed:
                print(
                    "Switching to global location for subsequent calls.",
                    file=sys.stderr,
                )
                return probed
        except Exception:
            pass

    # 4. Last Resort
    print(
        "Warning: Could not verify any model. Defaulting to gemini-1.5-flash-001",
        file=sys.stderr,
    )
    return "gemini-1.5-flash-001"


def main():
    parser = argparse.ArgumentParser(
        description="Run natural language queries on Neo4j using Gemini"
    )
    parser.add_argument("query", help="Natural language query")
    parser.add_argument(
        "--model",
        required=True,
        help="Gemini model to use (e.g. gemini-1.5-flash)",
    )
    parser.add_argument("--project-id", help="Google Cloud Project ID")
    # Default to None so we can fall back to env/global logic
    parser.add_argument("--location", help="Google Cloud Region (default: global)")
    parser.add_argument(
        "--verbose", action="store_true", help="Show generated Cypher query"
    )
    # Customization arguments
    parser.add_argument("--patient-id", help="Filter by Patient ID")
    parser.add_argument("--user-id", help="Filter by User ID")
    parser.add_argument("--instructions", help="Additional instructions for the LLM")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompt and exit without connecting to DB",
    )

    args = parser.parse_args()

    # 1. Setup Environment
    setup_google_credentials()

    # Get project and location from env (with improved logic)
    env_project, env_location = get_project_config()

    # CLI args override env
    project_id = args.project_id or env_project
    location = args.location or env_location

    # Construct custom prompt if needed
    custom_prompt = None
    if args.patient_id or args.user_id or args.instructions:
        # Base template structure matching standard neo4j-graphrag default
        base_template = """Task: Generate a Cypher statement for querying a Neo4j graph database from a user input.

Schema:
{schema}

Examples (optional):
{examples}

Input:
{query_text}

"""
        footer = """
Do not use any properties or relationships not included in the schema.
Do not include triple backticks ``` or any additional text except the generated Cypher statement in your response.

Cypher query:"""

        # Build context section
        context_lines = ["Context and Restrictions:"]
        if args.patient_id:
            context_lines.append(
                f"- RESTRICTION: You MUST only return nodes related to Patient ID: {args.patient_id}"
            )
            context_lines.append(
                f"- Ensure all match clauses filter by patient_id='{args.patient_id}' where applicable."
            )

        if args.user_id:
            context_lines.append(f"- Context: Current User ID is {args.user_id}")

        if args.instructions:
            context_lines.append(f"- Additional Instructions: {args.instructions}")

        custom_prompt = base_template + "\n".join(context_lines) + "\n" + footer

        if args.verbose:
            print("Using custom prompt with injected context.", file=sys.stderr)

    if args.dry_run:
        print("--- Dry Run Mode ---")
        if custom_prompt:
            print(f"Custom Prompt:\n{custom_prompt}")
        else:
            print("No custom prompt generated (using default).")
        sys.exit(0)

    # 2. Connect to Neo4j
    uri, user, password = get_neo4j_auth()
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
    except Exception as e:
        print(f"Error connecting to Neo4j at {uri}: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Initialize Gemini LLM
    try:
        llm = GoogleGenAILLM(
            model_name=args.model,
            project_id=project_id,
            location=location,
            model_params={"temperature": 0.0},
        )
    except Exception as e:
        print(f"Error initializing Google Gen AI: {e}", file=sys.stderr)
        if not project_id:
            print(
                "Hint: Try setting GOOGLE_CLOUD_PROJECT in .env or passing --project-id",
                file=sys.stderr,
            )
        sys.exit(1)

    # 4. Initialize Retriever
    if args.verbose:
        print("Fetching database schema...", file=sys.stderr)

    try:
        # Use built-in schema introspection (relies on APOC)
        retriever = Text2CypherRetriever(
            driver=driver, llm=llm, custom_prompt=custom_prompt
        )
    except Exception as e:
        print(f"Error initializing retriever: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # 5. Execute Query

        if args.verbose:
            print(f"Analyzing query: '{args.query}'", file=sys.stderr)

        result = retriever.search(query_text=args.query)

        # 6. Display Results
        if not result.items:
            print("No results found.")
            return

        # Handle different return types (Neo4j driver records vs Pydantic models vs dicts)
        # result.items is a list of RetrieverResultItem (usually)
        print(f"Found {len(result.items)} results:\n")

        from tabulate import tabulate

        # Convert records to list of dicts for tabulate
        data = []
        if result.items:
            first = result.items[0]
            # Check if it's a Neo4j Record (has .data() method)
            if hasattr(first, "data"):
                data = [dict(record) for record in result.items]
            # Check if it's a Pydantic model (has .content or similar)
            elif hasattr(first, "content"):
                # neo4j-graphrag RetrieverResultItem usually has 'content' and 'metadata'
                data = [
                    {"content": item.content, **(item.metadata or {})}
                    for item in result.items
                ]
            # Fallback: assume it's already a dict or try to cast
            else:
                try:
                    data = [dict(item) for item in result.items]
                except (ValueError, TypeError):
                    # Last resort: string representation
                    data = [{"result": str(item)} for item in result.items]

        if data:
            print(tabulate(data, headers="keys", tablefmt="simple_grid"))

        if args.verbose and result.metadata:
            print("\nMetadata:")
            # Filter out some metadata if needed, but for now show all
            if "cypher" in result.metadata:
                print(f"\nGenerated Cypher:\n{result.metadata['cypher']}")
            else:
                print(result.metadata)

    except Exception as e:
        print(f"Error executing query: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
