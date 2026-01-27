#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pydantic>=2.0"]
# ///
"""Kubernetes port forwarding helper with async process management.

CRITICALLY IMPORTANT: Development Commands
==========================================
Run these commands from the workspace root (machina-meta):

1. Type checking (strict mode):
   uv run --with pydantic --with mypy -- mypy --strict scripts/port_forward_service.py

2. Linting (all rules):
   uvx ruff check --select=ALL scripts/port_forward_service.py

3. Auto-fix lint errors:
   uvx ruff check --select=ALL --fix scripts/port_forward_service.py

4. Formatting:
   uvx ruff format scripts/port_forward_service.py

Forwards multiple Kubernetes services simultaneously using kubectl port-forward,
with automatic restart on failure.

Origin: Adapted from Wethos-AI/wethos-meeting-ai-assistant/port_forward_service.py
"""

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from asyncio import Task, as_completed, create_subprocess_shell, create_task, run
from asyncio.queues import Queue
from collections.abc import Coroutine
from json import dumps, loads
from shlex import quote
from subprocess import PIPE
from typing import Any, NoReturn

from pydantic import BaseModel, ConfigDict


class PortForwardTarget(BaseModel):
    """A single service to port-forward."""

    model_config = ConfigDict(strict=True)

    namespace: str
    service_name: str


class PortForwardConfig(BaseModel):
    """JSON config for port forwarding multiple services."""

    model_config = ConfigDict(strict=True)

    port_forward: list[PortForwardTarget]


def get_task_runner() -> tuple[
    Coroutine[Any, Any, None],
    Queue[Coroutine[Any, Any, NoReturn] | None],
]:
    """Create a task runner and its input queue.

    Returns a tuple of (task_runner coroutine, queue for submitting coroutines).
    """
    coroq: Queue[Coroutine[Any, Any, NoReturn] | None] = Queue()

    async def task_runner() -> None:
        tasks: set[Task[NoReturn]] = set()

        def track_task(coro: Coroutine[Any, Any, NoReturn]) -> None:
            task = create_task(coro, name=coro.__name__)
            tasks.add(task)
            task.add_done_callback(tasks.discard)

        async def task_queue() -> None:
            coro = await coroq.get()
            if coro is not None:
                track_task(coro)

        def get_task_info() -> str:
            return dumps(
                sorted(task.get_name() for task in tasks),
                indent=2,
            )

        _ = get_task_info  # Silence unused warning; kept for debugging

        await task_queue()

        while tasks:
            for i, task in enumerate(tasks):
                print(f"task {i + 1}: {task.get_name()}")  # noqa: T201
            for future in as_completed((create_task(task_queue()), *tasks)):
                await future
                break

    return (task_runner(), coroq)


def start_port_forward(
    *,
    service_namespace: str,
    service_name: str,
    service_port: int,
    host_port: int,
) -> Coroutine[Any, Any, NoReturn]:
    """Create a coroutine that runs kubectl port-forward in a loop."""
    service_namespace_sh = quote(service_namespace)
    service_name_sh = quote(service_name)
    cmd = (
        f"kubectl port-forward -n {service_namespace_sh} "
        f"services/{service_name_sh} {host_port}:{service_port}"
    )

    async def coro() -> NoReturn:
        while True:
            proc = await create_subprocess_shell(cmd)
            print(f"spawned: {cmd=}: {proc.pid=}")  # noqa: T201
            returncode = await proc.wait()
            print(f"exited: {cmd=}: {returncode=}")  # noqa: T201

    coro.__name__ = cmd
    return coro()


async def amain(*, config: PortForwardConfig) -> None:
    """Port forward services specified in config."""
    (task_runner, coroq) = get_task_runner()
    proc = await create_subprocess_shell(
        "kubectl get services -A -o json",
        stdout=PIPE,
    )
    (js, _) = await proc.communicate()
    returncode = await proc.wait()
    if returncode != 0:
        msg = f"kubectl get services failed with exit code {returncode}"
        raise RuntimeError(msg)
    services = loads(js)

    # Build lookup: (namespace, service_name) -> True
    config_targets = {(t.namespace, t.service_name): True for t in config.port_forward}

    for service in services["items"]:
        service_name: str = service["metadata"]["name"]
        service_namespace: str = service["metadata"]["namespace"]

        if (service_namespace, service_name) in config_targets:
            for service_port_info in service["spec"]["ports"]:
                print(f"{service_port_info=}")  # noqa: T201
                service_port: int = service_port_info["port"]
                host_port: int = service_port_info["targetPort"]
                coro = start_port_forward(
                    service_namespace=service_namespace,
                    service_name=service_name,
                    service_port=service_port,
                    host_port=host_port,
                )
                await coroq.put(coro)
    await task_runner


_EXAMPLE_CONFIG = """{
  "port_forward": [
    {"namespace": "tusdi-staging", "service_name": "neo4j"},
    {"namespace": "tusdi-staging", "service_name": "postgres"},
    {"namespace": "tusdi-staging", "service_name": "qdrant"},
    {"namespace": "tusdi-staging", "service_name": "redis"},
    {"namespace": "tusdi-staging", "service_name": "redisinsight"},
    {"namespace": "tusdi-staging", "service_name": "tusdi-api"},
    {"namespace": "tusdi-staging", "service_name": "tusdi-webui"}
  ]
}"""


def parse_args() -> Namespace:
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description="Kubernetes Port Forward Helper",
        epilog=(
            "Example (forward all tusdi-staging services):\n"
            f"%(prog)s '{_EXAMPLE_CONFIG}'"
        ),
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "config_json",
        nargs="?",
        type=str,
        help=(
            "JSON config, e.g.: "
            '{"port_forward": [{"namespace": "ns", "service_name": "svc"}]}'
        ),
    )
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Output JSON schema (OpenAPI format) for config and exit",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the script."""
    args = parse_args()

    if args.schema:
        schema = PortForwardConfig.model_json_schema()
        print(dumps(schema, indent=2))  # noqa: T201
        raise SystemExit(0)

    if not args.config_json:
        msg = "config_json is required (or use --schema)"
        raise SystemExit(msg)

    config = PortForwardConfig.model_validate_json(args.config_json)
    print(f"{config=}")  # noqa: T201
    run(amain(config=config))


if __name__ == "__main__":
    main()
