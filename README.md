# FastAPI Microservices (SRE Assignment 4)

Проект содержит 5 микросервисов на FastAPI, React-фронтенд и инфраструктуру на Docker Compose:

- auth-service (регистрация, вход, JWT)
- user-service (пользователи)
- product-service (товары)
- order-service (заказы)
- chat-service (чат на Redis, проверка пользователя через user-service)
- frontend (React + Vite SPA)

## Стек

- FastAPI + Uvicorn
- PostgreSQL 17
- Redis 7
- Docker Compose
- React 18 + Vite + React Router DOM v6

## Архитектура (DDD / Clean Architecture)

Каждый сервис разделён на 4 слоя внутри `app/`:

```
app/
  domain/         # Чистые Python dataclass-сущности, абстрактные репозитории (ABC), исключения домена
  application/    # Pydantic-схемы (DTO), use cases (оркестрация)
  infrastructure/ # Конкретные реализации репозиториев (asyncpg / Redis), DB-пул
  interfaces/     # FastAPI APIRouter, Depends-функции для DI
  main.py         # Фабрика приложения с lifespan
```

## Запуск

```bash
docker compose up --build
```

После старта будут доступны:

- **Frontend**: http://localhost:3000
- Auth API: http://localhost:8000/docs
- User API: http://localhost:8001/docs
- Product API: http://localhost:8002/docs
- Order API: http://localhost:8003/docs
- Chat API: http://localhost:8005/docs

## Аутентификация (auth-service)

Пароли хранятся с bcrypt-хешированием. При логине выдаётся JWT-токен.

### Регистрация

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret"}'
```

### Вход (получение JWT)

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret"}'
# Ответ: {"access_token": "...", "token_type": "bearer", "user": {...}}
```

### Проверка токена

```bash
curl "http://localhost:8000/auth/verify?token=<access_token>"
# Ответ: {"user_id": 1, "email": "alice@example.com"}
```

JWT настраивается через переменные окружения: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_HOURS`.

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
