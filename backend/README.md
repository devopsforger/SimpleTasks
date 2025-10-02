## FastAPI Backend for Task Management

A high-performance FastAPI backend with PostgreSQL, async/await architecture, and comprehensive authentication system.

## 🚀 Features

- **FastAPI** with async/await support
- **PostgreSQL** with SQLAlchemy 2.0+ and asyncpg
- **JWT Authentication** with token-based security
- **Role-Based Access Control** (Admin vs Regular users)
- **Alembic Database Migrations**
- **Pydantic Validation** for robust API schemas
- **Service Layer Architecture** for clean separation
- **Docker Support** for containerized deployment

## 📋 API Endpoints

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

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- UV package manager

### Local Development

1. **Navigate to backend directory**

   ```bash
   cd backend
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Install dependencies with UV**

   ```bash
   uv sync
   ```

4. **Run database migrations**

   ```bash
   uv run alembic upgrade head
   ```

5. **Start development server**
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up backend

# Or build individually
docker build -t task-management-backend .
docker run -p 8000:8000 task-management-backend
```

## 📊 Database Setup

### Manual PostgreSQL Setup

```sql
CREATE DATABASE taskmanager;
CREATE USER taskuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskuser;
```

### Environment Variables

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=taskmanager
DB_USER=postgres
DB_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your_super_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True
```

## 🔄 Database Migrations

### Creating Migrations

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

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Check current state
uv run alembic current
```

## 🧪 Testing

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

## 📚 API Documentation

When the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker Development

### Development with Hot-Reload

```bash
docker-compose up backend
```

### Production Build

```bash
docker build -t task-management-backend .
```

## 🔒 Security Features

- JWT token authentication with expiration
- Password hashing using bcrypt
- SQL injection prevention via SQLAlchemy
- Input validation with Pydantic schemas
- Role-based access control
- CORS protection

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic layer
│   ├── api/                 # API routes and endpoints
│   └── auth/                # Authentication utilities
├── migrations/              # Alembic migration files
├── tests/                   # Test suite
└── scripts/                 # Utility scripts
```

## 🚀 Deployment

The application is containerized and can be deployed to any container orchestration platform. The Dockerfile includes:

- Non-root user execution
- Health checks
- Database connection waiting
- Automatic migrations
