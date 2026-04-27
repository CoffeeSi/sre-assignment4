STACK_NAME=assignment4
COMPOSE_FILE=docker-compose.yaml

deploy:
	docker compose build --no-cache
	docker stack deploy -c $(COMPOSE_FILE) $(STACK_NAME)

rm:
	docker stack rm $(STACK_NAME)

ps:
	docker stack ps $(STACK_NAME)

services_inspect:
	docker stack services $(STACK_NAME)