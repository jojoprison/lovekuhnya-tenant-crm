# LoveKuhnya Tenant CRM

[🇷🇺 Русский](#русский) | [🇬🇧 English](#english)

---

<a name="русский"></a>

## 🇷🇺 Русский

Мультитенантный CRM-бэкенд с ролевым доступом и аналитикой.

**Стек:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, Pydantic v2, JWT, uv.

### Быстрый старт

```bash
cp .env.example .env
```

```bash
make upb
```

```bash
make smoke
```

- **Admin:** http://localhost:8007/admin
- **API Docs:** http://localhost:8007/docs

Опционально — демо-данные (логин: `admin@example.com` / `admin`):

```bash
make demo
```

### Для разработки

Локальные линтеры и pre-commit хуки требуют установки зависимостей:

```bash
make install
```

После этого доступны:

```bash
make lint
make lint-fix
make pre-commit
```

### Команды

| Команда         | Описание                    |
|-----------------|-----------------------------|
| `make install`  | Установить зависимости      |
| `make up`       | Запустить сервисы           |
| `make upb`      | Собрать и запустить         |
| `make down`     | Остановить                  |
| `make clean`    | Остановить и удалить данные |
| `make demo`     | Демо-данные (опционально)   |
| `make test`     | Запустить тесты             |
| `make smoke`    | Smoke-тест API (curl)       |
| `make lint`      | Проверка кода (CI)          |
| `make lint-fix`  | Автоисправление             |
| `make pre-commit`| Установить git hooks        |

### Особенности

- **In-memory кэш** аналитики с TTL (60 сек)
- **Health check** с версией, uptime, статусом БД
- **Pre-commit hooks** (ruff + mypy)
- **Type hints** везде + mypy strict

### Архитектура

```
src/
├── domain/           # Бизнес-правила, перечисления
├── application/      # Сервисы, порты репозиториев
├── interface/        # HTTP API (FastAPI)
├── infrastructure/   # БД, конфиг, безопасность
├── api/v1/           # Роутеры API
├── services/         # Бизнес-логика
├── repositories/     # Доступ к данным
├── models/           # ORM-модели
└── schemas/          # Pydantic DTO
```

### API Endpoints

| Группа        | Эндпоинты                                                       |
|---------------|-----------------------------------------------------------------|
| Auth          | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh` |
| Organizations | `GET /organizations/me`                                         |
| Contacts      | `GET/POST /contacts`, `GET/PATCH/DELETE /contacts/{id}`         |
| Deals         | `GET/POST /deals`, `GET/PATCH/DELETE /deals/{id}`               |
| Tasks         | `GET/POST /tasks`, `GET/PATCH/DELETE /tasks/{id}`               |
| Activities    | `GET/POST /deals/{id}/activities`                               |
| Analytics     | `GET /analytics/deals/summary`, `GET /analytics/deals/funnel`   |

### Бизнес-правила

1. Нельзя закрыть сделку как «выиграна» с суммой ≤ 0
2. Нельзя удалить контакт, если есть связанные сделки
3. Участники могут управлять только своими сущностями
4. Срок задачи не может быть в прошлом
5. Откат стадии сделки — только для admin/owner
6. Изменения статуса/стадии создают записи в Activity

### Роли

| Роль    | Своё | Всё | Настройки орг. |
|---------|------|-----|----------------|
| owner   | ✅    | ✅   | ✅              |
| admin   | ✅    | ✅   | ✅              |
| manager | ✅    | ✅   | ❌              |
| member  | ✅    | ❌   | ❌              |

[↑ English version](#english)

---

<a name="english"></a>

## 🇬🇧 English

Multi-tenant CRM backend with role-based access control and analytics.

**Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, Pydantic v2, JWT, uv.

### Quick Start

```bash
cp .env.example .env
```

```bash
make upb
```

```bash
make smoke
```

- **Admin:** http://localhost:8007/admin
- **API Docs:** http://localhost:8007/docs

Optional — demo data (login: `admin@example.com` / `admin`):

```bash
make demo
```

### For Development

Local linters and pre-commit hooks require installing dependencies:

```bash
make install
```

After that, the following are available:

```bash
make lint
make lint-fix
make pre-commit
```

### Commands

| Command         | Description           |
|-----------------|-----------------------|
| `make install`  | Install dependencies  |
| `make up`       | Start services        |
| `make upb`      | Build and start       |
| `make down`     | Stop services         |
| `make clean`    | Stop and remove data  |
| `make demo`     | Demo data (optional)  |
| `make test`     | Run tests             |
| `make smoke`    | API smoke test (curl) |
| `make lint`      | Check code (CI)       |
| `make lint-fix`  | Auto-fix code         |
| `make pre-commit`| Install git hooks     |

### Features

- **In-memory cache** for analytics with TTL (60 sec)
- **Health check** with version, uptime, DB status
- **Pre-commit hooks** (ruff + mypy)
- **Type hints** everywhere + mypy strict

### Architecture

```
src/
├── domain/           # Business rules, enums
├── application/      # Services, repository ports
├── interface/        # HTTP API (FastAPI)
├── infrastructure/   # DB, config, security
├── api/v1/           # API routers
├── services/         # Business logic
├── repositories/     # Data access
├── models/           # ORM models
└── schemas/          # Pydantic DTOs
```

### API Endpoints

| Group         | Endpoints                                                       |
|---------------|-----------------------------------------------------------------|
| Auth          | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh` |
| Organizations | `GET /organizations/me`                                         |
| Contacts      | `GET/POST /contacts`, `GET/PATCH/DELETE /contacts/{id}`         |
| Deals         | `GET/POST /deals`, `GET/PATCH/DELETE /deals/{id}`               |
| Tasks         | `GET/POST /tasks`, `GET/PATCH/DELETE /tasks/{id}`               |
| Activities    | `GET/POST /deals/{id}/activities`                               |
| Analytics     | `GET /analytics/deals/summary`, `GET /analytics/deals/funnel`   |

### Business Rules

1. Cannot close deal as "won" with amount ≤ 0
2. Cannot delete contact with linked deals
3. Members can only manage their own entities
4. Task due date cannot be in the past
5. Stage rollback only for admin/owner
6. Status/stage changes create Activity records

### Roles

| Role    | Own | All | Org settings |
|---------|-----|-----|--------------|
| owner   | ✅   | ✅   | ✅            |
| admin   | ✅   | ✅   | ✅            |
| manager | ✅   | ✅   | ❌            |
| member  | ✅   | ❌   | ❌            |

[↑ Русская версия](#русский)
