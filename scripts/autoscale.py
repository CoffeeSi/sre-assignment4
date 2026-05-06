#!/usr/bin/env python3
"""
Metric-based auto-scaling controller for Docker Swarm services.

Monitors Prometheus metrics (CPU, memory, RPS, error rate) and automatically
scales services based on thresholds.
"""

import os
import sys
import time
import logging
from dataclasses import dataclass
from typing import Optional
import requests
import docker

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ScalingPolicy:
    """Auto-scaling policy configuration."""

    service_name: str
    min_replicas: int = 1
    max_replicas: int = 10

    # CPU thresholds
    cpu_scale_up_threshold: float = 70.0  # % CPU
    cpu_scale_down_threshold: float = 20.0  # % CPU

    # Memory thresholds
    memory_scale_up_threshold: float = 80.0  # % Memory
    memory_scale_down_threshold: float = 30.0  # % Memory

    # Request rate thresholds (requests per second)
    rps_scale_up_threshold: float = 1000.0
    rps_scale_down_threshold: float = 100.0

    # Error rate thresholds (%)
    error_rate_threshold: float = 5.0

    # Cooldown period (seconds) to prevent rapid scaling
    cooldown_period: int = 300


class PrometheusClient:
    """Client for querying Prometheus metrics."""

    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus_url = prometheus_url
        self.session = requests.Session()

    def query(self, query_expr: str) -> Optional[float]:
        """Execute instant query and return single value."""
        try:
            response = self.session.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": query_expr},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()

            if data["status"] == "success" and data["data"]["result"]:
                return float(data["data"]["result"][0]["value"][1])
            return None
        except Exception as e:
            logger.error(f"Prometheus query failed: {e}")
            return None

    def get_avg_cpu_usage(self, service_name: str) -> Optional[float]:
        """Get average CPU usage for service (%)."""
        query = (
            f"avg(rate(container_cpu_usage_seconds_total"
            f'{{label_com_docker_swarm_service_name="{service_name}"}}[1m])) * 100'
        )
        return self.query(query)

    def get_avg_memory_usage(self, service_name: str) -> Optional[float]:
        """Get average memory usage percentage for service."""
        query = (
            f"avg(container_memory_usage_bytes"
            f'{{label_com_docker_swarm_service_name="{service_name}"}}'
            f"/ container_spec_memory_limit_bytes) * 100"
        )
        return self.query(query)

    def get_rps(self, service_name: str) -> Optional[float]:
        """Get requests per second for service."""
        query = (
            f"sum(rate(api_gateway_requests_total" f'{{service="{service_name}"}}[1m]))'
        )
        return self.query(query)

    def get_error_rate(self, service_name: str) -> Optional[float]:
        """Get error rate percentage for service."""
        query = (
            f"100 * sum(rate(api_gateway_requests_total"
            f'{{service="{service_name}",status_code=~"[45].."}}[1m]))'
            f"/ sum(rate(api_gateway_requests_total"
            f'{{service="{service_name}"}}[1m]))'
        )
        return self.query(query)


class DockerSwarmScaler:
    """Docker Swarm service scaler."""

    def __init__(self):
        self.client = docker.from_env()

    def get_current_replicas(self, service_name: str) -> int:
        """Get current replica count for service."""
        try:
            services = self.client.services.list(filters={"name": service_name})
            if services:
                service = services[0]
                mode = service.attrs.get("Spec", {}).get("Mode", {})
                if "Replicated" in mode:
                    return mode["Replicated"]["Replicas"]
            return 0
        except Exception as e:
            logger.error(f"Failed to get replicas for {service_name}: {e}")
            return 0

    def scale_service(self, service_name: str, replicas: int) -> bool:
        """Scale service to specified replica count."""
        try:
            services = self.client.services.list(filters={"name": service_name})
            if services:
                service = services[0]
                service.scale(replicas)
                logger.info(f"Scaled {service_name} to {replicas} replicas")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to scale {service_name}: {e}")
            return False


class AutoScaler:
    """Main auto-scaling controller."""

    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus = PrometheusClient(prometheus_url)
        self.scaler = DockerSwarmScaler()
        self.policies: dict[str, ScalingPolicy] = {}
        self.last_scale_time: dict[str, float] = {}

    def register_policy(self, policy: ScalingPolicy):
        """Register a scaling policy."""
        self.policies[policy.service_name] = policy
        self.last_scale_time[policy.service_name] = 0

    def evaluate_and_scale(self, policy: ScalingPolicy):
        """Evaluate metrics and scale service if needed."""
        service_name = policy.service_name

        # Check cooldown period
        now = time.time()
        if now - self.last_scale_time.get(service_name, 0) < policy.cooldown_period:
            logger.debug(f"Skipping {service_name} - in cooldown period")
            return

        current_replicas = self.scaler.get_current_replicas(service_name)
        if current_replicas == 0:
            logger.warning(f"Service {service_name} has 0 replicas")
            return

        # Get metrics
        cpu_usage = self.prometheus.get_avg_cpu_usage(service_name)
        memory_usage = self.prometheus.get_avg_memory_usage(service_name)
        rps = self.prometheus.get_rps(service_name)
        error_rate = self.prometheus.get_error_rate(service_name)

        logger.info(
            f"{service_name}: CPU={cpu_usage}%, MEM={memory_usage}%, "
            f"RPS={rps}/s, ErrorRate={error_rate}%"
        )

        decision = self._make_scaling_decision(
            policy, current_replicas, cpu_usage, memory_usage, rps, error_rate
        )

        if decision != current_replicas:
            logger.warning(
                f"Scaling {service_name} from {current_replicas} to {decision} replicas"
            )
            if self.scaler.scale_service(service_name, decision):
                self.last_scale_time[service_name] = now

    def _make_scaling_decision(
        self,
        policy: ScalingPolicy,
        current_replicas: int,
        cpu_usage: Optional[float],
        memory_usage: Optional[float],
        rps: Optional[float],
        error_rate: Optional[float],
    ) -> int:
        """Determine target replica count based on metrics."""
        target = current_replicas

        # Scale up if metrics exceed upper thresholds
        if cpu_usage and cpu_usage > policy.cpu_scale_up_threshold:
            target = min(current_replicas + 1, policy.max_replicas)
            logger.info(
                f"Scale up due to CPU: {cpu_usage}% > {policy.cpu_scale_up_threshold}%"
            )

        if memory_usage and memory_usage > policy.memory_scale_up_threshold:
            target = min(current_replicas + 1, policy.max_replicas)
            logger.info(
                f"Scale up due to memory: {memory_usage}% > {policy.memory_scale_up_threshold}%"
            )

        if rps and rps > policy.rps_scale_up_threshold:
            target = min(current_replicas + 1, policy.max_replicas)
            logger.info(f"Scale up due to RPS: {rps} > {policy.rps_scale_up_threshold}")

        if error_rate and error_rate > policy.error_rate_threshold:
            target = min(current_replicas + 1, policy.max_replicas)
            logger.warning(
                f"Scale up due to error rate: {error_rate}% > {policy.error_rate_threshold}%"
            )

        # Scale down if metrics below lower thresholds (all must be low)
        if (
            (cpu_usage is None or cpu_usage < policy.cpu_scale_down_threshold)
            and (
                memory_usage is None
                or memory_usage < policy.memory_scale_down_threshold
            )
            and (rps is None or rps < policy.rps_scale_down_threshold)
            and (error_rate is None or error_rate < policy.error_rate_threshold / 2)
        ):
            target = max(current_replicas - 1, policy.min_replicas)
            if target < current_replicas:
                logger.info("Scale down - all metrics below thresholds")

        return target

    def run(self, interval: int = 60):
        """Run auto-scaling loop."""
        logger.info(f"Starting auto-scaler (interval={interval}s)")

        while True:
            try:
                for policy in self.policies.values():
                    self.evaluate_and_scale(policy)
            except Exception as e:
                logger.error(f"Error in scaling loop: {e}")

            time.sleep(interval)


def load_policies_from_env() -> list[ScalingPolicy]:
    """Load scaling policies from environment variables."""
    policies = []

    # Example: Define policies via environment
    # SERVICES=order-service,product-service
    # ORDER_SERVICE_MIN=1
    # ORDER_SERVICE_MAX=10
    # ORDER_SERVICE_CPU_UP=70
    # ORDER_SERVICE_CPU_DOWN=20

    services = os.getenv("SERVICES", "order-service,product-service").split(",")

    for service in services:
        service = service.strip()
        env_prefix = service.upper().replace("-", "_")

        policy = ScalingPolicy(
            service_name=service,
            min_replicas=int(os.getenv(f"{env_prefix}_MIN_REPLICAS", "1")),
            max_replicas=int(os.getenv(f"{env_prefix}_MAX_REPLICAS", "10")),
            cpu_scale_up_threshold=float(os.getenv(f"{env_prefix}_CPU_UP", "70")),
            cpu_scale_down_threshold=float(os.getenv(f"{env_prefix}_CPU_DOWN", "20")),
            memory_scale_up_threshold=float(os.getenv(f"{env_prefix}_MEMORY_UP", "80")),
            memory_scale_down_threshold=float(
                os.getenv(f"{env_prefix}_MEMORY_DOWN", "30")
            ),
            rps_scale_up_threshold=float(os.getenv(f"{env_prefix}_RPS_UP", "1000")),
            rps_scale_down_threshold=float(os.getenv(f"{env_prefix}_RPS_DOWN", "100")),
            error_rate_threshold=float(os.getenv(f"{env_prefix}_ERROR_RATE", "5")),
            cooldown_period=int(os.getenv(f"{env_prefix}_COOLDOWN", "300")),
        )
        policies.append(policy)

    return policies


if __name__ == "__main__":
    prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
    interval = int(os.getenv("SCALING_INTERVAL", "60"))

    scaler = AutoScaler(prometheus_url)

    # Register policies
    policies = load_policies_from_env()
    for policy in policies:
        scaler.register_policy(policy)
        logger.info(f"Registered policy for {policy.service_name}")

    # Run auto-scaler
    scaler.run(interval)
