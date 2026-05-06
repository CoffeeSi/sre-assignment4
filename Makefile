STACK_NAME=assignment4
COMPOSE_FILE=docker-compose.yaml

deploy:
	docker network inspect $(STACK_NAME)_assignment4_network >NUL 2>NUL || docker network create --driver overlay --attachable $(STACK_NAME)_assignment4_network
	python scripts/validate_configuration.py
	docker compose build --no-cache
	docker stack deploy -c $(COMPOSE_FILE) $(STACK_NAME)

validate_config:
	python scripts/validate_configuration.py

rm:
	docker stack rm $(STACK_NAME)

ps:
	docker stack ps $(STACK_NAME)

services_inspect:
	docker stack services $(STACK_NAME)

## Horizontal scaling helpers
## Usage: make scale-service SERVICE=order-service REPLICAS=10
scale-service:
	@echo "Scaling service $(SERVICE) to $(REPLICAS) replicas in stack $(STACK_NAME)"
	docker service scale $(STACK_NAME)_$(SERVICE)=$(REPLICAS)

## Shortcut to scale order-service using env variable ORDER_SERVICE_REPLICAS
make-scale-order:
	@echo "Scaling order-service to $(ORDER_SERVICE_REPLICAS) replicas"
	docker service scale $(STACK_NAME)_order-service=$(ORDER_SERVICE_REPLICAS)

terraform_init:
	cd terraform && terraform init

terraform_plan:
	cd terraform && terraform plan

terraform_apply:
	cd terraform && terraform apply -auto-approve

terraform_destroy:
	cd terraform && terraform destroy -auto-approve

terraform_auto_restart:
	cd terraform && terraform destroy -auto-approve
	cd terraform && terraform init
	cd terraform && terraform plan
	cd terraform && terraform apply -auto-approve

## Auto-scaling targets (creates the shared overlay network if needed)
autoscale-build:
	docker build -t autoscaler:latest -f Dockerfile.autoscaler .

autoscale-deploy: autoscale-build
	docker network inspect $(STACK_NAME)_assignment4_network >NUL 2>NUL || docker network create --driver overlay --attachable $(STACK_NAME)_assignment4_network
	@echo "Deploying autoscaler to Swarm stack..."
	docker stack deploy -c docker-compose.autoscaler.yaml $(STACK_NAME)

autoscale-logs:
	docker service logs $(STACK_NAME)_autoscaler -f

autoscale-stop:
	docker service scale $(STACK_NAME)_autoscaler=0

autoscale-remove:
	docker stack rm $(STACK_NAME)_autoscaler 2>/dev/null || docker service rm $(STACK_NAME)_autoscaler

autoscale-test:
	@echo "Running k6 load test (10 min, 100 VUs) to trigger autoscaling..."
	docker run --network $(STACK_NAME)_assignment4_network -it \
		-e API_GATEWAY_URL=http://api-gateway:8080 \
		grafana/k6:latest run --duration 10m --vus 100 \
		/dev/stdin < scripts/load_test.js

k8s-apply:
	@kubectl config current-context >NUL 2>NUL || (echo Kubernetes context is not configured. Set a current kubectl context before running k8s-apply. & exit /b 1)
	kubectl apply --validate=false -f kubernetes/

k8s-hpa-status:
	kubectl get hpa -n microservices

k8s-hpa-describe:
	kubectl describe hpa -n microservices

k8s-remove:
	kubectl delete -f kubernetes/

k8s-watch-hpa:
	kubectl get hpa -n microservices -w