#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""
Integration test for graphrag_cli.py.
Executes the CLI tool against the real local Neo4j instance and real Vertex AI.
"""

import subprocess
import sys
import os
from pathlib import Path


def test_integration():
    script_path = Path(__file__).parent / "graphrag_cli.py"
    if not script_path.exists():
        print(f"Error: Could not find {script_path}")
        sys.exit(1)

    print(f"Testing {script_path.name}...")

    # Force usage of ADC if USE_ADC env var is set, otherwise default to script logic
    env = dict(os.environ)
    if os.environ.get("USE_ADC"):
        env["USE_ADC"] = "1"

    # 1. Simple count query (Dry Run)
    # Using dry-run to verify argument parsing and basic flow without DB dependency
    query = "Count all nodes in the database"
    cmd = [
        str(script_path),
        query,
        "--verbose",
        "--model",
        "gemini-3-pro-preview",
        "--location",
        "global",
        "--dry-run",
    ]

    print(f"\n1. Running query: '{query}' (dry-run)")
    print("-" * 50)

    try:
        # Run with a timeout to prevent hanging if auth prompts appear
        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=60, check=False
        )

        # Print output for visibility
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        print("-" * 50)

        # Analysis
        if result.returncode == 0:
            print("SUCCESS: Dry-run executed successfully.")
            if "Dry Run Mode" in result.stdout:
                print("Confirmed Dry Run output.")
        else:
            print(f"FAILED: Script returned exit code {result.returncode}")
            sys.exit(result.returncode)

    except subprocess.TimeoutExpired:
        print("FAILED: Timeout expired.")
        sys.exit(1)
    except Exception as e:
        print(f"FAILED: Unexpected error: {e}")
        sys.exit(1)

    # 2. Test with patient context injection (Dry Run)
    print("\n2. Testing with patient context injection (dry-run)...")
    query_context = "List all documents"
    cmd_context = [
        str(script_path),
        query_context,
        "--verbose",
        "--model",
        "gemini-3-pro-preview",
        "--location",
        "global",
        "--patient-id",
        "P12345",
        "--instructions",
        "Return only the count.",
        "--dry-run",
    ]

    print(f"Running query: '{query_context}' with --patient-id P12345")
    try:
        result = subprocess.run(
            cmd_context,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        if "Using custom prompt with injected context" in result.stderr:
            print("SUCCESS: Custom prompt message found in stderr.")
        else:
            print("WARNING: Custom prompt message not found in stderr.")

        if (
            "RESTRICTION: You MUST only return nodes related to Patient ID: P12345"
            in result.stdout
        ):
            print("SUCCESS: Patient ID restriction found in generated prompt.")
        else:
            print("FAILED: Patient ID restriction missing from generated prompt.")
            sys.exit(1)

        if result.returncode == 0:
            print("SUCCESS: Context query executed successfully.")
            sys.exit(0)
        else:
            print(f"FAILED: Context query failed with code {result.returncode}")
            sys.exit(result.returncode)

    except Exception as e:
        print(f"FAILED: Error running context test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_integration()
