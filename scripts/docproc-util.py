#!/usr/bin/env python3
"""Document processing utility for test documents.

This script helps manage test documents for the medical-data-engine:
- List all test documents in pdf_tests/medical_records
- Upload all test documents
- Process all uploaded documents
- Wait for processing completion
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Backend API base URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")

# Patient context defaults
PATIENT_FIRST_NAME = os.getenv("PATIENT_FIRST_NAME", "Stuart")
PATIENT_LAST_NAME = os.getenv("PATIENT_LAST_NAME", "McClure")
PATIENT_DATE_OF_BIRTH = os.getenv("PATIENT_DATE_OF_BIRTH", "1969-03-03")
AUTH_EMAIL = os.getenv("AUTH_EMAIL", "dbeal@numberone.ai")


def get_workspace_root() -> Path:
    """Get the workspace root directory."""
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent
    return workspace_root


def get_test_docs_dir() -> Path:
    """Get the test documents directory."""
    workspace_root = get_workspace_root()
    return workspace_root / "repos" / "dem2" / "pdf_tests" / "medical_records"


def list_test_docs() -> list[str]:
    """List all test documents in pdf_tests/medical_records.

    Returns:
        List of relative paths (relative to repos/dem2)
    """
    test_docs_dir = get_test_docs_dir()

    if not test_docs_dir.exists():
        print(f"ERROR: Test documents directory not found: {test_docs_dir}", file=sys.stderr)
        return []

    # Find all PDF files
    pdf_files = sorted(test_docs_dir.rglob("*.pdf")) + sorted(test_docs_dir.rglob("*.PDF"))

    # Convert to relative paths (relative to repos/dem2)
    dem2_root = get_workspace_root() / "repos" / "dem2"
    relative_paths = [str(pdf.relative_to(dem2_root)) for pdf in pdf_files]

    return relative_paths


def call_curl_api(function: str, **kwargs: Any) -> dict[str, Any]:
    """Call curl_api.sh function using justfile.

    Args:
        function: The function name to call
        **kwargs: Additional arguments to pass to the function

    Returns:
        Parsed JSON response
    """
    workspace_root = get_workspace_root()
    dem2_dir = workspace_root / "repos" / "dem2"

    # Build JSON payload
    payload = {"function": function}
    payload.update(kwargs)
    json_str = json.dumps(payload)

    # Call just curl_api from dem2 directory
    cmd = ["just", "curl_api", json_str]

    try:
        result = subprocess.run(
            cmd,
            cwd=dem2_dir,
            capture_output=True,
            text=True,
            check=True
        )

        # Parse JSON response from stdout
        # The output format is: JSON\nbash command echo
        # We need to extract just the JSON part (everything before the bash command line)
        lines = result.stdout.strip().split("\n")

        # Collect all lines that are part of the JSON
        json_lines = []
        for line in lines:
            # Stop when we hit the bash command echo (starts with "bash -c")
            if line.startswith("bash -c"):
                break
            json_lines.append(line)

        # Join the JSON lines and parse
        json_text = "\n".join(json_lines).strip()
        if json_text:
            try:
                return json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse JSON: {e}", file=sys.stderr)
                print(f"JSON text: {json_text}", file=sys.stderr)
                return {}

        # If no JSON found, return empty dict
        return {}

    except subprocess.CalledProcessError as e:
        print(f"ERROR: curl_api failed: {e}", file=sys.stderr)
        print(f"stdout: {e.stdout}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        raise


def upload_document(doc_path: str) -> str | None:
    """Upload a document.

    Args:
        doc_path: Path to document relative to repos/dem2

    Returns:
        File ID if successful, None otherwise
    """
    try:
        response = call_curl_api("upload_file", path=doc_path)
        file_id = response.get("id")
        if file_id:
            print(f"✅ Uploaded: {doc_path} -> {file_id}")
            return file_id
        else:
            print(f"❌ Failed to upload: {doc_path} (no ID in response)")
            return None
    except Exception as e:
        print(f"❌ Failed to upload: {doc_path} - {e}")
        return None


def process_document(file_id: str) -> str | None:
    """Process a document.

    Args:
        file_id: File ID to process

    Returns:
        Task ID if successful, None otherwise
    """
    try:
        response = call_curl_api("process_document", file_id=file_id)
        task_id = response.get("task_id") or response.get("id")
        if task_id:
            print(f"✅ Processing started: {file_id} -> task {task_id}")
            return task_id
        else:
            print(f"❌ Failed to process: {file_id} (no task ID in response)")
            return None
    except Exception as e:
        print(f"❌ Failed to process: {file_id} - {e}")
        return None


def get_task_status(task_id: str) -> dict[str, Any]:
    """Get task status.

    Args:
        task_id: Task ID to check

    Returns:
        Task status dict
    """
    try:
        return call_curl_api("get_task", task_id=task_id)
    except Exception as e:
        print(f"❌ Failed to get task status: {task_id} - {e}")
        return {}


def wait_for_tasks(task_ids: list[str], poll_interval: int = 5, timeout: int = 600) -> None:
    """Wait for all tasks to complete.

    Args:
        task_ids: List of task IDs to wait for
        poll_interval: Seconds between status checks
        timeout: Maximum seconds to wait
    """
    print(f"\n=== Waiting for {len(task_ids)} tasks to complete ===")

    start_time = time.time()
    pending_tasks = set(task_ids)

    while pending_tasks and (time.time() - start_time) < timeout:
        for task_id in list(pending_tasks):
            status = get_task_status(task_id)
            task_status = status.get("status", "unknown")

            if task_status in ("completed", "failed", "error"):
                print(f"✅ Task {task_id}: {task_status}")
                pending_tasks.remove(task_id)
            else:
                print(f"⏳ Task {task_id}: {task_status}")

        if pending_tasks:
            print(f"Waiting {poll_interval}s... ({len(pending_tasks)} tasks remaining)")
            time.sleep(poll_interval)

    if pending_tasks:
        print(f"\n⚠️  Timeout reached. {len(pending_tasks)} tasks still pending.")
    else:
        print(f"\n✅ All tasks completed in {time.time() - start_time:.1f}s")


def cmd_list() -> None:
    """List all test documents."""
    docs = list_test_docs()
    print(json.dumps(docs, indent=2))


def cmd_upload_all() -> None:
    """Upload all test documents."""
    docs = list_test_docs()
    print(f"=== Found {len(docs)} test documents ===\n")

    file_ids = []
    for doc_path in docs:
        file_id = upload_document(doc_path)
        if file_id:
            file_ids.append(file_id)

    print(f"\n=== Summary: Uploaded {len(file_ids)}/{len(docs)} documents ===")

    # Save file IDs to a temp file for process-all command
    temp_file = Path("/tmp/docproc_file_ids.json")
    temp_file.write_text(json.dumps(file_ids))
    print(f"File IDs saved to: {temp_file}")


def cmd_process_all() -> None:
    """Process all uploaded documents (reads file IDs from temp file)."""
    temp_file = Path("/tmp/docproc_file_ids.json")

    if not temp_file.exists():
        print("ERROR: No file IDs found. Run 'upload-all' first.", file=sys.stderr)
        sys.exit(1)

    file_ids = json.loads(temp_file.read_text())
    print(f"=== Processing {len(file_ids)} documents ===\n")

    task_ids = []
    for file_id in file_ids:
        task_id = process_document(file_id)
        if task_id:
            task_ids.append(task_id)

    print(f"\n=== Summary: Started processing {len(task_ids)}/{len(file_ids)} documents ===")

    # Save task IDs to temp file for wait command
    temp_file = Path("/tmp/docproc_task_ids.json")
    temp_file.write_text(json.dumps(task_ids))
    print(f"Task IDs saved to: {temp_file}")


def cmd_wait() -> None:
    """Wait for all processing tasks to complete."""
    temp_file = Path("/tmp/docproc_task_ids.json")

    if not temp_file.exists():
        print("ERROR: No task IDs found. Run 'process-all' first.", file=sys.stderr)
        sys.exit(1)

    task_ids = json.loads(temp_file.read_text())
    wait_for_tasks(task_ids)


def cmd_full() -> None:
    """Run full pipeline: upload all, process all, wait for completion."""
    print("=== STEP 1: Upload all documents ===\n")
    cmd_upload_all()

    print("\n=== STEP 2: Process all documents ===\n")
    cmd_process_all()

    print("\n=== STEP 3: Wait for completion ===\n")
    cmd_wait()

    print("\n✅ Full pipeline complete!")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: docproc-util.py <command>")
        print("\nCommands:")
        print("  list         - List all test documents")
        print("  upload-all   - Upload all test documents")
        print("  process-all  - Process all uploaded documents")
        print("  wait         - Wait for all tasks to complete")
        print("  full         - Run full pipeline (upload + process + wait)")
        sys.exit(1)

    command = sys.argv[1]

    commands = {
        "list": cmd_list,
        "upload-all": cmd_upload_all,
        "process-all": cmd_process_all,
        "wait": cmd_wait,
        "full": cmd_full,
    }

    if command not in commands:
        print(f"ERROR: Unknown command: {command}", file=sys.stderr)
        sys.exit(1)

    commands[command]()


if __name__ == "__main__":
    main()
