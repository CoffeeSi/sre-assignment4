#!/usr/bin/env python3
"""Inspect Docker Compose logs for common troubleshooting patterns.

This script helps identify:
- Database connection failures in service logs
- Service restart loops from container restart counts

It reads centralized container logs from `docker compose logs` and inspects
container state via `docker inspect`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable


DB_FAILURE_PATTERNS = [
    re.compile(r"connection refused", re.IGNORECASE),
    re.compile(r"could not connect", re.IGNORECASE),
    re.compile(r"database not ready", re.IGNORECASE),
    re.compile(r"db not ready", re.IGNORECASE),
    re.compile(r"authentication failed", re.IGNORECASE),
    re.compile(r"password authentication failed", re.IGNORECASE),
    re.compile(r"timeout.*database", re.IGNORECASE),
    re.compile(r"asyncpg.*(cannotconnectnowerror|connectiondoesnotexisterror)", re.IGNORECASE),
]


RESTART_LOOP_THRESHOLD = 3


@dataclass
class Finding:
    service: str
    category: str
    evidence: list[str]


def run_command(args: list[str]) -> str:
    completed = subprocess.run(
        args,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout


def parse_compose_logs(raw_logs: str, services_filter: set[str] | None) -> dict[str, list[str]]:
    logs_by_service: dict[str, list[str]] = defaultdict(list)
    for line in raw_logs.splitlines():
        match = re.match(r"^(?P<service>[^|]+)\|\s?(?P<message>.*)$", line)
        if not match:
            continue
        service = match.group("service").strip()
        message = match.group("message").strip()
        if services_filter and service not in services_filter:
            continue
        logs_by_service[service].append(message)
    return logs_by_service


def detect_db_failures(lines: Iterable[str]) -> list[str]:
    matches: list[str] = []
    for line in lines:
        if any(pattern.search(line) for pattern in DB_FAILURE_PATTERNS):
            matches.append(line)
    return matches


def get_compose_containers(services_filter: set[str] | None) -> list[tuple[str, str]]:
    output = run_command(["docker", "compose", "ps", "-q"])
    container_ids = [line.strip() for line in output.splitlines() if line.strip()]
    containers: list[tuple[str, str]] = []

    for container_id in container_ids:
        inspect_output = run_command(
            [
                "docker",
                "inspect",
                container_id,
                "--format",
                "{{ index .Config.Labels \"com.docker.compose.service\" }}",
            ]
        ).strip()
        if services_filter and inspect_output not in services_filter:
            continue
        containers.append((container_id, inspect_output))

    return containers


def inspect_restart_loops(containers: list[tuple[str, str]]) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = defaultdict(list)
    for container_id, service in containers:
        inspect_output = run_command(
            [
                "docker",
                "inspect",
                container_id,
                "--format",
                "{{ json .State }}",
            ]
        ).strip()
        state = json.loads(inspect_output)
        restart_count = int(state.get("RestartCount", 0))
        restarting = bool(state.get("Restarting", False))
        exit_code = state.get("ExitCode")
        status = state.get("Status", "unknown")

        if restarting or restart_count >= RESTART_LOOP_THRESHOLD:
            findings[service].append(
                f"restart_count={restart_count}, status={status}, restarting={restarting}, exit_code={exit_code}"
            )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect docker compose logs for database failures and restart loops."
    )
    parser.add_argument(
        "--services",
        nargs="*",
        help="Optional list of service names to inspect.",
    )
    parser.add_argument(
        "--tail",
        type=int,
        default=400,
        help="Number of log lines to fetch from docker compose logs.",
    )
    args = parser.parse_args()

    services_filter = set(args.services) if args.services else None

    compose_args = ["docker", "compose", "logs", "--no-color", f"--tail={args.tail}"]
    if args.services:
        compose_args.extend(args.services)

    raw_logs = run_command(compose_args)
    logs_by_service = parse_compose_logs(raw_logs, services_filter)

    containers = get_compose_containers(services_filter)
    restart_findings = inspect_restart_loops(containers)

    findings: list[Finding] = []

    for service, lines in logs_by_service.items():
        db_matches = detect_db_failures(lines)
        if db_matches:
            findings.append(
                Finding(
                    service=service,
                    category="database-connection-failure",
                    evidence=db_matches[:5],
                )
            )

    for service, evidence in restart_findings.items():
        findings.append(
            Finding(
                service=service,
                category="restart-loop-suspected",
                evidence=evidence,
            )
        )

    if not findings:
        print("No known failure patterns detected in recent compose logs.")
        return 0

    print("Troubleshooting findings:\n")
    for finding in findings:
        print(f"[{finding.category}] {finding.service}")
        for evidence in finding.evidence:
            print(f"  - {evidence}")
        print()

    print("Suggested next checks:")
    print("- Verify dependent services and database credentials in .env")
    print("- Inspect recent restarts with: docker compose ps")
    print("- Review full logs for the affected service with: docker compose logs <service>")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
