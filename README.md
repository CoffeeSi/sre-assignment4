# FastAPI Microservices (SRE Assignment 4)

This project contains 5 FastAPI microservices, a React frontend, and Docker Compose infrastructure:

- auth-service (registration, login, JWT)
- user-service (user management)
- product-service (products)
- order-service (orders)
- chat-service (chat on Redis, user verification via user-service)
- frontend (React + Vite SPA)

## Tech Stack

- FastAPI + Uvicorn
- PostgreSQL 17
- Redis 7
- Docker Compose
- React 18 + Vite + React Router DOM v6

## Architecture

Each service is divided into 4 layers inside `app/`:

```
app/
  domain/         # Clean Python dataclass entities, abstract repositories (ABC), domain exceptions
  application/    # Pydantic schemas (DTO), use cases (orchestration)
  infrastructure/ # Concrete repository implementations (asyncpg / Redis), DB pool
  interfaces/     # FastAPI APIRouter, Depends functions for DI
  main.py         # Application factory with lifespan
```

## Running

### Development (Docker Compose)

```bash
docker swarm init
docker compose build
docker stack deploy -c docker-compose.yaml assignment
```

After startup, the following will be available:

- API Gateway: http://localhost:8080
- Frontend: http://localhost:3000
- Auth API: http://localhost:8000/docs
- User API: http://localhost:8001/docs
- Product API: http://localhost:8002/docs
- Order API: http://localhost:8003/docs
- Chat API: http://localhost:8005/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## API Gateway

All external requests can be routed through a single gateway on port **8080**, which routes them to the appropriate microservice by path prefix:

| Path Prefix          | Upstream              |
|----------------------|-----------------------|
| `/auth/*`            | auth-service:8000     |
| `/users/*`           | user-service:8001     |
| `/products/*`        | product-service:8002  |
| `/orders/*`          | order-service:8003    |
| `/rooms/*`           | chat-service:8005     |

Built-in gateway endpoints: `/health` and `/metrics`.

### Examples via Gateway

```bash
# Register
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret"}'

# Login
curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret"}'

# Create product
curl -X POST http://localhost:8080/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Keyboard","price":99.99}'

# Create order
curl -X POST http://localhost:8080/orders \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'
```

## Authentication (auth-service)

Passwords are stored with bcrypt hashing. Login returns a JWT token.

### Registration

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret"}'
```

### Login (get JWT)

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret"}'
# Response: {"access_token": "...", "token_type": "bearer", "user": {...}}
```

### Verify Token

```bash
curl "http://localhost:8000/auth/verify?token=<access_token>"
# Response: {"user_id": 1, "email": "alice@example.com"}
```

JWT is configured via environment variables: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_HOURS`.

## Example API Requests

1. Create user:

```bash
curl -X POST http://localhost:8001/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com"}'
```

2. Create product:

```bash
curl -X POST http://localhost:8002/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Keyboard","price":99.99}'
```

Get products:

```bash
curl -X GET http://localhost:8002/products \ 
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json"
```

3. Create order:

```bash
curl -X POST http://localhost:8003/orders \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'
```

Get orders:
```bash
curl -X GET http://localhost:8003/orders \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json"
```

4. Send message to chat room:

```bash
curl -X POST http://localhost:8005/rooms/{room_name}/messages \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello team"}'
```

Get messages from chat room:

```bash
curl -X GET http://localhost:8005/rooms/{room_name}/messages \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json"
```

## Deployment Documentation

### Terraform Configuration

The Terraform configuration for this project is defined in the `terraform` directory.
 - `main.tf` – contains the necessary resources to provision an EC2 instance on AWS.
 - `variables.tf` – defines the input variables.
 - `outputs.tf` – specifies the outputs of the Terraform deployment.
 - `terraform.tfvars` – contains the actual values for the variables.

### Run Terraform

1. Initialize Terraform:

Configure your terraform variables in `terraform.tfvars`.

then run the following commands in the terminal:

```bash
cd terraform
# Initialize Terraform
terraform init
# Plan the changes
terraform plan
# Apply the changes
terraform apply
```

### Connect to the Instance

After the instance is running, you can connect to it using SSH.

```bash
ssh -i key.pem <username>@<instance_public_ip>
```

### Clean Up

To destroy the instance run:

```bash
terraform destroy
```

## Monitoring & Observability

### Prometheus & Grafana

Prometheus scrapes all services at `http://localhost:9090` and Grafana visualizes them at `http://localhost:3000`.

### Centralized Logging

Container logs are centralized through Loki and Promtail, while services continue to write structured JSON logs to stdout/stderr.

Use the log inspector to scan recent container logs for common failure patterns:

```bash
python scripts/log_inspector.py
```

It highlights database connection failures and possible restart loops so you can narrow down the root cause faster.

## Horizontal scaling (quick reference)

To scale services in the running Swarm stack use the provided Makefile helpers or the scale script.

Makefile examples:

```bash
# Scale order-service to 10 replicas
make scale-service SERVICE=order-service REPLICAS=10

# Scale using configured environment variable
make make-scale-order
```

Script example:

```bash
# Scale via helper script: ./scripts/scale_service.sh <stack-name> <service-name> <replicas>
./scripts/scale_service.sh assignment4 order-service 10
```

Notes:

- Swarm's internal VIP load-balancing (`endpoint_mode: vip`) distributes traffic across replicas automatically.
- For production-grade load balancing across nodes consider placing an external reverse-proxy/load-balancer in front of the API gateway.

