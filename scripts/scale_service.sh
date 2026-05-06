#!/usr/bin/env bash
# Helper to scale a service in the swarm stack used by this project.
# Usage: ./scripts/scale_service.sh <service-name> <replicas>
set -euo pipefail
STACK_NAME=${1:-assignment4}
SERVICE=${2:-order-service}
REPLICAS=${3:-5}

if [ -z "$STACK_NAME" ] || [ -z "$SERVICE" ] || [ -z "$REPLICAS" ]; then
  echo "Usage: $0 <stack-name> <service-name> <replicas>"
  exit 2
fi

FULL_NAME="$STACK_NAME"_"$SERVICE"

echo "Scaling $FULL_NAME to $REPLICAS replicas..."
docker service scale "$FULL_NAME"="$REPLICAS"

echo "Done."