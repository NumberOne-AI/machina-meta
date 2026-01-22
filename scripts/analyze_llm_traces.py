#!/usr/bin/env python3
"""
Analyze LLM trace files and generate timing report.

Usage:
    python scripts/analyze_llm_traces.py <traces_dir> [--output <output_file>]

Example:
    python scripts/analyze_llm_traces.py logs/llm-traces-20260121 --output docs/SLOW_AGENT_QUERIES_20260121.md
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class LLMCall:
    """Represents a single LLM API call (request/response pair)."""
    agent_name: str
    call_num: int
    model: str
    request_timestamp: float
    response_timestamp: float
    invocation_id: str
    session_id: str
    user_query: Optional[str] = None

    @property
    def duration(self) -> float:
        """Duration of the LLM call in seconds."""
        return self.response_timestamp - self.request_timestamp


@dataclass
class Invocation:
    """Represents a complete agent invocation (may have multiple LLM calls)."""
    invocation_id: str
    session_id: str
    invocation_timestamp: float
    llm_calls: list[LLMCall] = field(default_factory=list)

    @property
    def start_time(self) -> float:
        """Earliest timestamp in this invocation."""
        if not self.llm_calls:
            return self.invocation_timestamp
        return min(self.invocation_timestamp,
                   min(c.request_timestamp for c in self.llm_calls))

    @property
    def end_time(self) -> float:
        """Latest timestamp in this invocation."""
        if not self.llm_calls:
            return self.invocation_timestamp
        return max(c.response_timestamp for c in self.llm_calls)

    @property
    def total_duration(self) -> float:
        """Total wall-clock time for this invocation."""
        return self.end_time - self.start_time

    @property
    def total_llm_time(self) -> float:
        """Sum of all LLM call durations."""
        return sum(c.duration for c in self.llm_calls)

    @property
    def tool_time(self) -> float:
        """Time spent on tools (total - LLM time)."""
        return max(0, self.total_duration - self.total_llm_time)

    @property
    def llm_percentage(self) -> float:
        """Percentage of time spent on LLM calls."""
        if self.total_duration == 0:
            return 0
        return (self.total_llm_time / self.total_duration) * 100

    @property
    def primary_agent(self) -> str:
        """The main agent for this invocation."""
        if not self.llm_calls:
            return "Unknown"
        # Return the agent with the most calls, or first one
        agents = [c.agent_name for c in self.llm_calls]
        return max(set(agents), key=agents.count)

    @property
    def user_query(self) -> Optional[str]:
        """Extract user query from first LLM call."""
        for call in sorted(self.llm_calls, key=lambda c: c.call_num):
            if call.user_query:
                return call.user_query
        return None

    @property
    def datetime(self) -> datetime:
        """Invocation start as datetime."""
        return datetime.fromtimestamp(self.invocation_timestamp)


def parse_trace_file(filepath: Path) -> dict:
    """Parse a single trace JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)
        return {}


def extract_user_query(data: dict) -> Optional[str]:
    """Extract user query text from request data."""
    contents = data.get('contents', [])
    for content in contents:
        if content.get('role') == 'user':
            parts = content.get('parts', [])
            for part in parts:
                text = part.get('text')
                if not text:
                    continue

                # If text is JSON, try to extract 'question' or 'request' field
                if text.startswith('{'):
                    try:
                        json_data = json.loads(text)
                        # Try common field names for user queries
                        for field in ['question', 'request', 'query', 'message', 'prompt']:
                            if field in json_data:
                                query = json_data[field]
                                if isinstance(query, str):
                                    return query
                        # If no known field, skip this JSON
                        continue
                    except json.JSONDecodeError:
                        pass  # Not valid JSON, treat as plain text

                return text  # Return full query
    return None


def collect_traces(traces_dir: Path) -> dict[str, Invocation]:
    """Collect all trace data from directory."""
    invocations: dict[str, Invocation] = {}

    # Find all JSON files
    for json_file in traces_dir.rglob('*.json'):
        data = parse_trace_file(json_file)
        if not data:
            continue

        inv_id = data.get('invocation_id')
        if not inv_id:
            continue

        inv_ts = float(data.get('invocation_timestamp', 0))
        session_id = data.get('session_id', '')

        # Create invocation if needed
        if inv_id not in invocations:
            invocations[inv_id] = Invocation(
                invocation_id=inv_id,
                session_id=session_id,
                invocation_timestamp=inv_ts
            )

        inv = invocations[inv_id]

        # Parse based on file type
        filename = json_file.name
        timestamp = float(data.get('timestamp', 0))
        agent_name = data.get('agent_name', 'Unknown')
        call_num = int(data.get('call_num', 0))
        model = data.get('model', '')

        # For raw_request files, this is when request was sent
        if '_raw_request.json' in filename:
            # Find or create LLM call
            call = None
            for c in inv.llm_calls:
                if c.agent_name == agent_name and c.call_num == call_num:
                    call = c
                    break

            if not call:
                call = LLMCall(
                    agent_name=agent_name,
                    call_num=call_num,
                    model=model,
                    request_timestamp=timestamp,
                    response_timestamp=timestamp,  # Will be updated
                    invocation_id=inv_id,
                    session_id=session_id,
                    user_query=extract_user_query(data)
                )
                inv.llm_calls.append(call)
            else:
                call.request_timestamp = timestamp
                if not call.user_query:
                    call.user_query = extract_user_query(data)

        # For raw_response files, this is when response was received
        elif '_raw_response.json' in filename:
            for call in inv.llm_calls:
                if call.agent_name == agent_name and call.call_num == call_num:
                    call.response_timestamp = timestamp
                    break
            else:
                # Response without request - create call
                call = LLMCall(
                    agent_name=agent_name,
                    call_num=call_num,
                    model=model,
                    request_timestamp=timestamp,
                    response_timestamp=timestamp,
                    invocation_id=inv_id,
                    session_id=session_id
                )
                inv.llm_calls.append(call)

        # For request.json (not raw), extract user query if available
        elif '_request.json' in filename and '_raw_' not in filename:
            user_query = extract_user_query(data)
            if user_query:
                for call in inv.llm_calls:
                    if call.agent_name == agent_name and call.call_num == call_num:
                        if not call.user_query:
                            call.user_query = user_query
                        break

    return invocations


def calculate_statistics(invocations: list[Invocation]) -> dict:
    """Calculate summary statistics."""
    total_times = [i.total_duration for i in invocations]
    llm_times = [i.total_llm_time for i in invocations]
    tool_times = [i.tool_time for i in invocations]

    def stats(values):
        if not values:
            return {'min': 0, 'max': 0, 'avg': 0, 'median': 0}
        sorted_v = sorted(values)
        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'median': sorted_v[len(sorted_v) // 2]
        }

    return {
        'total_time': stats(total_times),
        'llm_time': stats(llm_times),
        'tool_time': stats(tool_times)
    }


def calculate_agent_stats(invocations: list[Invocation]) -> dict:
    """Calculate per-agent statistics."""
    agent_calls: dict[str, list[float]] = defaultdict(list)

    for inv in invocations:
        for call in inv.llm_calls:
            agent_calls[call.agent_name].append(call.duration)

    result = {}
    for agent, durations in agent_calls.items():
        sorted_d = sorted(durations)
        result[agent] = {
            'calls': len(durations),
            'min': min(durations),
            'max': max(durations),
            'avg': sum(durations) / len(durations),
            'total': sum(durations)
        }

    return result


def calculate_distribution(invocations: list[Invocation]) -> list[dict]:
    """Calculate response time distribution."""
    total_times = [i.total_duration for i in invocations]
    ranges = [(0, 5), (5, 10), (10, 20), (20, 30), (30, 60), (60, float('inf'))]

    result = []
    cumulative = 0
    for low, high in ranges:
        count = len([t for t in total_times if low <= t < high])
        pct = count / len(total_times) * 100 if total_times else 0
        cumulative += pct

        label = f">{low}s" if high == float('inf') else f"{low}-{high}s"
        assessment = {
            (0, 5): "Excellent",
            (5, 10): "Good",
            (10, 20): "Acceptable",
            (20, 30): "Slow",
            (30, 60): "Very Slow",
            (60, float('inf')): "**Critical**"
        }[(low, high)]

        result.append({
            'range': label,
            'count': count,
            'percentage': pct,
            'cumulative': cumulative,
            'assessment': assessment
        })

    return result


def generate_markdown_report(invocations: list[Invocation], namespace: str, pod: str) -> str:
    """Generate markdown report from invocations."""
    lines = []

    # Sort by timestamp
    invocations = sorted(invocations, key=lambda i: i.invocation_timestamp)

    total_calls = sum(len(i.llm_calls) for i in invocations)
    stats = calculate_statistics(invocations)
    agent_stats = calculate_agent_stats(invocations)
    distribution = calculate_distribution(invocations)

    # Header
    lines.append("# LLM Trace Timing Analysis Report")
    lines.append("")
    lines.append(f"**Environment:** {namespace} (GKE)")
    lines.append(f"**Pod:** {pod}")
    lines.append(f"**Report Date:** {datetime.now().strftime('%Y-%m-%d')}")
    if invocations:
        start = invocations[0].datetime.strftime('%Y-%m-%d %H:%M')
        end = invocations[-1].datetime.strftime('%H:%M')
        lines.append(f"**Analysis Period:** {start} - {end} UTC")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")

    critical_count = len([i for i in invocations if i.total_duration > 60])
    critical_pct = critical_count / len(invocations) * 100 if invocations else 0
    fast_count = len([i for i in invocations if i.total_duration < 10])
    fast_pct = fast_count / len(invocations) * 100 if invocations else 0
    max_time = max(i.total_duration for i in invocations) if invocations else 0

    lines.append(f"Analysis of {total_calls} LLM trace files across {len(invocations)} agent invocations reveals significant performance variability. "
                 f"While {fast_pct:.0f}% of requests complete in under 10 seconds, {critical_pct:.0f}% exceed 60 seconds, "
                 f"with the worst case reaching **{max_time:.0f} seconds ({max_time/60:.1f} minutes)**.")
    lines.append("")

    lines.append("| Metric                          | Value        |")
    lines.append("|---------------------------------|--------------|")
    lines.append(f"| Total Invocations Analyzed      | {len(invocations)}           |")
    lines.append(f"| Total LLM API Calls             | {total_calls}          |")
    lines.append(f"| Median Response Time            | {stats['total_time']['median']:.2f}s       |")
    lines.append(f"| Average Response Time           | {stats['total_time']['avg']:.2f}s       |")
    lines.append(f"| Requests Exceeding 60s          | {critical_count} ({critical_pct:.1f}%)   |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary Statistics
    lines.append("## Summary Statistics")
    lines.append("")
    lines.append("| Metric                              |    Min |     Max |    Avg | Median |")
    lines.append("|-------------------------------------|-------:|--------:|-------:|-------:|")
    lines.append(f"| Total Invocation Time               | {stats['total_time']['min']:6.2f}s | {stats['total_time']['max']:7.2f}s | {stats['total_time']['avg']:6.2f}s | {stats['total_time']['median']:6.2f}s |")
    lines.append(f"| LLM Call Time (Gemini API)          | {stats['llm_time']['min']:6.2f}s | {stats['llm_time']['max']:7.2f}s | {stats['llm_time']['avg']:6.2f}s | {stats['llm_time']['median']:6.2f}s |")
    lines.append(f"| Processing Time (tools/graph)       | {stats['tool_time']['min']:6.2f}s | {stats['tool_time']['max']:7.2f}s | {stats['tool_time']['avg']:6.2f}s | {stats['tool_time']['median']:6.2f}s |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Agent Performance Summary
    lines.append("## Agent Performance Summary")
    lines.append("")
    lines.append("| Agent                    | LLM Calls |    Min |     Max |    Avg |   Total |")
    lines.append("|--------------------------|----------:|-------:|--------:|-------:|--------:|")
    for agent in sorted(agent_stats.keys()):
        s = agent_stats[agent]
        lines.append(f"| {agent:<24} | {s['calls']:9} | {s['min']:6.2f}s | {s['max']:7.2f}s | {s['avg']:6.2f}s | {s['total']:7.1f}s |")
    lines.append("")

    lines.append("**Column Definitions:**")
    lines.append("- **LLM Calls**: Number of round-trips to the Gemini API per invocation. Multiple calls occur due to the **agent loop pattern**:")
    lines.append("  1. Agent sends query to LLM → LLM requests a tool (e.g., `query_graph`)")
    lines.append("  2. Tool executes → result returned to LLM → LLM may request another tool")
    lines.append("  3. Loop continues until LLM produces final response without tool calls")
    lines.append("")
    lines.append("  Example: 3 LLM calls = initial request + 2 tool-use cycles before final answer.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Response Time Distribution
    lines.append("## Response Time Distribution")
    lines.append("")
    lines.append("| Duration Range | Count | Percentage | Cumulative | Assessment       |")
    lines.append("|----------------|------:|-----------:|-----------:|------------------|")
    for d in distribution:
        lines.append(f"| {d['range']:<14} | {d['count']:5} | {d['percentage']:10.1f}% | {d['cumulative']:10.1f}% | {d['assessment']:<16} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Detailed Invocation Timing
    lines.append("## Detailed Invocation Timing")
    lines.append("")
    lines.append("| #  | Time (UTC) | Invocation ID              | Agent(s)                | LLM Calls | Total    |  LLM    | Tools   | LLM % |")
    lines.append("|---:|:-----------|:---------------------------|:------------------------|----------:|---------:|--------:|--------:|------:|")

    for i, inv in enumerate(invocations, 1):
        time_str = inv.datetime.strftime('%H:%M:%S')
        inv_id = f"`{inv.invocation_id[:24]}...`"
        agent = inv.primary_agent
        llm_calls = len(inv.llm_calls)
        total = inv.total_duration
        llm = inv.total_llm_time
        tools = inv.tool_time
        llm_pct = inv.llm_percentage

        lines.append(f"| {i:2} | {time_str} | {inv_id:<26} | {agent:<23} | {llm_calls:9} | {total:8.2f}s | {llm:7.2f}s | {tools:7.2f}s | {llm_pct:5.0f}% |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Critical Slow Queries
    slow_invocations = sorted([i for i in invocations if i.total_duration > 100],
                               key=lambda i: i.total_duration, reverse=True)

    if slow_invocations:
        lines.append("## Critical Slow Queries (>100s)")
        lines.append("")
        lines.append("| Rank | Timestamp  | Invocation ID                          |   Total |     LLM |   Tools | User Query Summary                                              |")
        lines.append("|-----:|:-----------|:---------------------------------------|--------:|--------:|--------:|:----------------------------------------------------------------|")

        for rank, inv in enumerate(slow_invocations[:10], 1):
            time_str = inv.datetime.strftime('%H:%M:%S')
            query = inv.user_query or "(query not extracted)"
            # Replace newlines with spaces to keep table intact
            query = ' '.join(query.split())

            lines.append(f"| {rank:4} | {time_str}   | `{inv.invocation_id}` | {inv.total_duration:7.2f}s | {inv.total_llm_time:7.2f}s | {inv.tool_time:7.2f}s | {query} |")

        lines.append("")
        lines.append("---")
        lines.append("")

    # LLM Call Breakdown (Sample)
    lines.append("## LLM Call Breakdown (Sample of First 30 Calls)")
    lines.append("")
    lines.append("| Invocation       | Agent                   | Call # | Duration | Time Range (UTC)      |")
    lines.append("|:-----------------|:------------------------|-------:|---------:|:----------------------|")

    call_count = 0
    for inv in invocations:
        for call in sorted(inv.llm_calls, key=lambda c: c.call_num):
            if call_count >= 30:
                break

            inv_short = f"`{inv.invocation_id[:12]}...`"
            req_time = datetime.fromtimestamp(call.request_timestamp).strftime('%H:%M:%S')
            resp_time = datetime.fromtimestamp(call.response_timestamp).strftime('%H:%M:%S')

            lines.append(f"| {inv_short:<16} | {call.agent_name:<23} | {call.call_num:6} | {call.duration:8.2f}s | {req_time} - {resp_time}   |")
            call_count += 1

        if call_count >= 30:
            break

    lines.append("")
    lines.append(f"*(Showing first 30 of {total_calls} calls)*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Footer
    lines.append(f"**Report generated:** {datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("**Analyzed by:** analyze_llm_traces.py")
    lines.append(f"**Trace files:** {total_calls * 2}")  # request + response per call
    lines.append(f"**Invocations:** {len(invocations)}")
    lines.append("")

    return '\n'.join(lines)


def get_trace_date(invocations: list[Invocation]) -> str:
    """Extract date from trace timestamps in YYYYMMDD format."""
    if not invocations:
        return datetime.now().strftime('%Y%m%d')

    # Use the earliest invocation timestamp
    earliest = min(inv.invocation_timestamp for inv in invocations)
    return datetime.fromtimestamp(earliest).strftime('%Y%m%d')


def main():
    parser = argparse.ArgumentParser(description='Analyze LLM trace files and generate timing report.')
    parser.add_argument('traces_dir', type=Path, help='Directory containing LLM trace files')
    parser.add_argument('--output', '-o', type=Path, help='Output markdown file (auto-generated if not specified)')
    parser.add_argument('--output-dir', type=Path, default=Path('docs'), help='Output directory for auto-generated filename')
    parser.add_argument('--namespace', default='tusdi-preview-92', help='Kubernetes namespace')
    parser.add_argument('--pod', default='tusdi-api-*', help='Pod name')

    args = parser.parse_args()

    if not args.traces_dir.exists():
        print(f"Error: Directory {args.traces_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"Collecting traces from {args.traces_dir}...", file=sys.stderr)
    invocations = collect_traces(args.traces_dir)
    print(f"Found {len(invocations)} invocations", file=sys.stderr)

    # Convert to list
    invocation_list = list(invocations.values())

    # Auto-generate output filename if not specified
    if args.output:
        output_path = args.output
    else:
        trace_date = get_trace_date(invocation_list)
        # Sanitize namespace for filename (replace non-alphanumeric with dash)
        safe_namespace = ''.join(c if c.isalnum() or c == '-' else '-' for c in args.namespace)
        filename = f"MEDICAL_AGENT_QUERIES_{safe_namespace}_{trace_date}.md"
        output_path = args.output_dir / filename

    # Generate report
    report = generate_markdown_report(invocation_list, args.namespace, args.pod)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(report)
    print(f"Report written to {output_path}", file=sys.stderr)

    # Print the output path for use by calling scripts
    print(output_path)


if __name__ == '__main__':
    main()
