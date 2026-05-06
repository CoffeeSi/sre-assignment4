#!/usr/bin/env python3
"""Validate deployment configuration before starting the stack.

Checks:
- Required variables are present in the active environment file or environment
- Database connection strings use the expected PostgreSQL/asyncpg format
- Service endpoints are valid URLs with a host and port
- Template-based configuration files define the expected variables
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / ".env.example"
DEFAULT_ENV = ROOT / ".env"

REQUIRED_VARIABLES = {
    "DATABASE_URL",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "REDIS_URL",
    "JWT_SECRET_KEY",
    "JWT_ALGORITHM",
    "JWT_EXPIRE_HOURS",
    "AUTH_SERVICE_URL",
    "USER_SERVICE_URL",
    "PRODUCT_SERVICE_URL",
    "ORDER_SERVICE_URL",
    "CHAT_SERVICE_URL",
    "API_GATEWAY_URL",
    "INSTANCE_IP",
    "ENVIRONMENT",
    "LOG_LEVEL",
    "JSON_LOGGING",
    "PROMETHEUS_PORT",
    "GRAFANA_PORT",
    "UPSTREAM_TIMEOUT",
    "REQUEST_TIMEOUT",
    "DB_POOL_SIZE",
    "DB_MAX_OVERFLOW",
    "REDIS_POOL_SIZE",
    "HEALTH_CHECK_INTERVAL",
    "HEALTH_CHECK_TIMEOUT",
    "HEALTH_CHECK_RETRIES",
    "HEALTH_CHECK_START_PERIOD",
    "RESTART_POLICY",
    "RESTART_DELAY",
    "RESTART_MAX_ATTEMPTS",
    "SERVICE_REPLICAS",
}

SERVICE_URL_VARIABLES = [
    "AUTH_SERVICE_URL",
    "USER_SERVICE_URL",
    "PRODUCT_SERVICE_URL",
    "ORDER_SERVICE_URL",
    "CHAT_SERVICE_URL",
    "API_GATEWAY_URL",
]

DATABASE_URL_PATTERN = re.compile(
    r"^postgresql\+asyncpg://[^\s/]+:[^\s/]+@[^\s/]+/[^\s/]+$"
)


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def validate_template(template_values: dict[str, str]) -> list[str]:
    missing = sorted(REQUIRED_VARIABLES - template_values.keys())
    return [f"Template is missing required variable: {name}" for name in missing]


def validate_database_url(value: str) -> list[str]:
    errors: list[str] = []
    if not DATABASE_URL_PATTERN.match(value):
        errors.append(
            "DATABASE_URL must use postgresql+asyncpg://user:password@host:port/database format"
        )
        return errors

    parsed = urlparse(value)
    if parsed.scheme != "postgresql+asyncpg":
        errors.append("DATABASE_URL must start with postgresql+asyncpg://")
    if not parsed.hostname:
        errors.append("DATABASE_URL must include a hostname")
    if parsed.port is None:
        errors.append("DATABASE_URL must include a port")
    if not parsed.path or parsed.path == "/":
        errors.append("DATABASE_URL must include a database name")
    if not parsed.username:
        errors.append("DATABASE_URL must include a username")
    if parsed.password is None:
        errors.append("DATABASE_URL must include a password")
    return errors


def validate_service_url(name: str, value: str) -> list[str]:
    errors: list[str] = []
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        errors.append(f"{name} must use http:// or https://")
    if not parsed.hostname:
        errors.append(f"{name} must include a hostname")
    if parsed.port is None:
        errors.append(f"{name} must include an explicit port")
    if parsed.path not in {"", "/"}:
        errors.append(f"{name} should point to the service root without a path suffix")
    return errors


def validate_env_values(values: dict[str, str]) -> list[str]:
    errors: list[str] = []

    missing_runtime = [name for name in REQUIRED_VARIABLES if not values.get(name)]
    errors.extend(
        f"Missing required variable: {name}" for name in sorted(missing_runtime)
    )

    database_url = values.get("DATABASE_URL", "")
    if database_url:
        errors.extend(validate_database_url(database_url))

    for name in SERVICE_URL_VARIABLES:
        service_value = values.get(name, "")
        if service_value:
            errors.extend(validate_service_url(name, service_value))

    return errors


def print_report(errors: Iterable[str]) -> int:
    error_list = list(errors)
    if not error_list:
        print("Configuration validation passed.")
        return 0

    print("Configuration validation failed:\n")
    for error in error_list:
        print(f"- {error}")
    print()
    print("Fix the issues above before deploying the stack.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate environment configuration before deployment."
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV,
        help="Path to the environment file to validate.",
    )
    parser.add_argument(
        "--template-file",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="Path to the .env.example template to compare against.",
    )
    args = parser.parse_args()

    template_values = parse_env_file(args.template_file)
    runtime_values = {**template_values, **parse_env_file(args.env_file), **os.environ}

    errors = []
    errors.extend(validate_template(template_values))
    errors.extend(validate_env_values(runtime_values))

    return print_report(errors)


if __name__ == "__main__":
    raise SystemExit(main())
