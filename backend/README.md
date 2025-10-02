Generic single-database configuration.# Task Management Backend API

A production-ready, high-performance FastAPI backend for a task management application with JWT authentication, role-based access control, and async PostgreSQL support.

## Features

- **FastAPI** with async/await architecture for high performance
- **JWT Authentication** with secure token-based auth
- **Role-Based Access Control (RBAC)** - Admin vs Regular users
- **Async PostgreSQL** with SQLAlchemy 2.0+ and asyncpg
- **Alembic Database Migrations** with async support
- **Pydantic Validation** for robust request/response schemas
- **Service Layer Architecture** for clean separation of concerns
- **Production-Ready** with security best practices
- **Docker Support** for containerized deployment
- **UV Package Management** for fast dependency resolution

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Users (Admin only)

- `GET /api/v1/users/` - List all users
- `GET /api/v1/users/me` - Get current user profile
- `GET /api/v1/users/{user_id}` - Get specific user
- `PATCH /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Tasks

- `GET /api/v1/tasks/` - List tasks (all for admin, own for users)
- `POST /api/v1/tasks/` - Create new task
- `GET /api/v1/tasks/{task_id}` - Get specific task
- `PUT /api/v1/tasks/{task_id}` - Full task update
- `PATCH /api/v1/tasks/{task_id}` - Partial task update
- `DELETE /api/v1/tasks/{task_id}` - Delete task

### Health Check

- `GET /health` - Service health status

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with SQLAlchemy 2.0+
- **Async Driver**: asyncpg
- **Authentication**: JWT with PyJWT
- **Password Hashing**: bcrypt via passlib
- **Migrations**: Alembic with async support
- **Validation**: Pydantic 2.0+
- **Package Manager**: UV
- **API Documentation**: Auto-generated Swagger UI & ReDoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Application configuration
│   ├── database.py            # Database connection setup
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   └── task.py            # Task model
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py            # User request/response schemas
│   │   └── task.py            # Task request/response schemas
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py    # User operations
│   │   └── task_service.py    # Task operations
│   ├── api/                   # API layer
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/     # Route handlers
│   │       │   ├── __init__.py
│   │       │   ├── auth.py    # Authentication routes
│   │       │   ├── users.py   # User management routes
│   │       │   └── tasks.py   # Task management routes
│   │       └── deps.py        # FastAPI dependencies
│   └── auth/                  # Authentication utilities
│       ├── __init__.py
│       ├── jwt.py             # JWT token handling
│       └── security.py        # Password hashing
├── migrations/                # Alembic migration files
│   ├── versions/              # Generated migration scripts
│   └── env.py                 # Alembic configuration
├── tests/                     # Test suite
├── scripts/
│   └── run.sh                 # Application startup script
├── Dockerfile                 # Container configuration
├── pyproject.toml            # Project dependencies and metadata
├── alembic.ini               # Alembic configuration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- UV package manager

### Installation

1. **Clone and setup the project**:

```bash
cd backend
cp .env.example .env
# Edit .env with your database credentials and JWT secret
```

2. **Install dependencies with UV**:

```bash
uv sync
```

3. **Run database migrations**:

```bash
uv run alembic upgrade head
```

4. **Start the development server**:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Using Scripts (Alternative)

Add to `pyproject.toml`:

```toml
[project.scripts]
dev = "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
start = "uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

Then run:

```bash
uv run dev  # Development with auto-reload
uv run start  # Production
```

## Database Setup

### Manual PostgreSQL Setup

1. **Create database and user**:

```sql
CREATE DATABASE taskmanager;
CREATE USER taskuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskuser;
```

2. **Configure environment variables** in `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=taskmanager
DB_USER=taskuser
DB_PASSWORD=yourpassword
```

### Using Docker Compose

Create `docker-compose.db.yml`:

```yaml
version: "3.8"
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: taskmanager
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: yourpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run: `docker-compose -f docker-compose.db.yml up -d`

## Database Migrations

### Creating Migrations

When you modify models, create a new migration:

```bash
uv run alembic revision --autogenerate -m "description_of_changes"
```

### Applying Migrations

```bash
uv run alembic upgrade head
```

### Migration Commands

```bash
# Create new migration
uv run alembic revision --autogenerate -m "message"

# Apply all pending migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Check current migration state
uv run alembic current

# Show migration history
uv run alembic history --verbose
```

## Authentication

### User Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "is_admin": false
  }'
```

### User Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword"
```

### Using JWT Tokens

Add the token to requests:

```bash
curl -H "Authorization: Bearer <your_jwt_token>" \
  "http://localhost:8000/api/v1/users/me"
```

## User Roles

### Regular Users

- Can manage their own tasks
- Can view their own profile
- Cannot access other users' data

### Admin Users

- Can manage all tasks (create, read, update, delete any task)
- Can manage all users (create, read, update, delete any user)
- Have access to all API endpoints

## Docker Deployment

### Build and Run

```bash
docker build -t task-management-backend .
docker run -p 8000:8000 \
  -e DB_HOST=localhost \
  -e DB_PASSWORD=secret \
  -e JWT_SECRET_KEY=supersecret \
  task-management-backend
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: "3.8"
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgres
      - DB_NAME=taskmanager
      - DB_USER=taskuser
      - DB_PASSWORD=yourpassword
      - JWT_SECRET_KEY=your-jwt-secret-key
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: taskmanager
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: yourpassword
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run: `docker-compose up -d`

## Configuration

### Environment Variables

| Variable                      | Description       | Default       |
| ----------------------------- | ----------------- | ------------- |
| `DB_HOST`                     | PostgreSQL host   | `localhost`   |
| `DB_PORT`                     | PostgreSQL port   | `5432`        |
| `DB_NAME`                     | Database name     | `taskmanager` |
| `DB_USER`                     | Database user     | `postgres`    |
| `DB_PASSWORD`                 | Database password | -             |
| `JWT_SECRET_KEY`              | JWT signing key   | -             |
| `JWT_ALGORITHM`               | JWT algorithm     | `HS256`       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration  | `30`          |
| `DEBUG`                       | Debug mode        | `False`       |

### Production Configuration

For production, set environment variables through:

- **AWS ECS**: Use Secrets Manager and Parameter Store
- **Kubernetes**: Use Kubernetes Secrets
- **Docker**: Use `-e` flags or env files
- **Traditional**: Set in deployment scripts

## Testing

### Running Tests

```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio httpx

# Run tests
uv run pytest
```

### Test Structure

- `tests/test_auth.py` - Authentication tests
- `tests/test_users.py` - User management tests
- `tests/test_tasks.py` - Task management tests

## API Documentation

### Auto-generated Docs

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Example API Usage

1. **Register a new user**:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "email": "admin@example.com",
        "password": "admin123",
        "is_admin": True
    }
)
```

2. **Create a task**:

```python
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/api/v1/tasks/",
    headers=headers,
    json={
        "title": "Complete project",
        "description": "Finish the backend implementation",
        "status": "todo"
    }
)
```

## Security Features

- **JWT Token Authentication** with expiration
- **Password Hashing** using bcrypt
- **SQL Injection Prevention** through SQLAlchemy
- **CORS Protection** configurable origins
- **Input Validation** with Pydantic schemas
- **Role-Based Access Control** (RBAC)
- **Environment Variable Security** no hardcoded secrets

## Deployment

### AWS ECS Deployment

1. Build and push Docker image to ECR
2. Create ECS task definition with environment variables
3. Configure Application Load Balancer
4. Set up Secrets Manager for sensitive data

### Kubernetes Deployment

1. Create Kubernetes deployment and service
2. Configure secrets and config maps
3. Set up ingress controller
4. Configure health checks

## Troubleshooting

### Common Issues

1. **Database Connection Errors**

   - Check PostgreSQL is running
   - Verify credentials in `.env`
   - Ensure database exists

2. **Migration Issues**

   - Run `alembic current` to check state
   - Use `alembic history` to see migration chain
   - Check `migrations/env.py` configuration

3. **JWT Errors**
   - Verify `JWT_SECRET_KEY` is set
   - Check token expiration
   - Validate token in Authorization header

### Logs

Enable debug logging by setting `DEBUG=True` in environment variables.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run test suite
5. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:

- Check API documentation at `/docs`
- Review migration files in `migrations/versions/`
- Examine test cases for usage examples

---

**Development Server**: `http://localhost:8000`  
**API Documentation**: `http://localhost:8000/docs`  
**Health Check**: `http://localhost:8000/health`
