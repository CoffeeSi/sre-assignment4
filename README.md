# FastAPI Microservices (SRE Assignment 4)

Проект содержит 5 микросервисов на FastAPI и инфраструктуру на Docker Compose:

- auth-service (регистрация и вход)
- user-service (пользователи)
- product-service (товары)
- order-service (заказы)
- chat-service (чат на Redis, проверка пользователя через user-service)

## Стек

- FastAPI + Uvicorn
- PostgreSQL 17
- Redis 7
- Docker Compose

## Запуск

```bash
docker compose up --build
```

После старта будут доступны:

- Auth API: http://localhost:8000/docs
- User API: http://localhost:8001/docs
- Product API: http://localhost:8002/docs
- Order API: http://localhost:8003/docs
- Chat API: http://localhost:8005/docs

## Примеры запросов

1. Создать пользователя:

```bash
curl -X POST http://localhost:8001/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com"}'
```

2. Создать товар:

```bash
curl -X POST http://localhost:8002/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Keyboard","price":99.99}'
```

3. Создать заказ:

```bash
curl -X POST http://localhost:8003/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"product_id":1,"quantity":2}'
```

4. Отправить сообщение в чат:

```bash
curl -X POST http://localhost:8005/rooms/general/messages \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"text":"Hello team"}'
```
