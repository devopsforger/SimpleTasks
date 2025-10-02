# Task Management Application

A production-realistic monorepo application with a FastAPI backend and Next.js frontend, designed for testing AWS ECS (EC2 launch type) infrastructure with secure authentication, RBAC, and CI/CD.

### Structure

- backend/: FastAPI service with PostgreSQL, Alembic migrations, JWT auth, and RBAC.
- frontend/: Next.js static site for task and user management.
- .github/workflows/: GitHub Actions for CI/CD with SAST and container scanning.

### Setup

#### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker
- PostgreSQL (local or via docker-compose)

#### Local Development

- Copy .env.example to .env and fill in values.
- Run docker-compose up to start PostgreSQL, backend, and frontend dev server.
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000

#### Environment Variables

- DB_HOST, DB_NAME, DB_USER, DB_PASSWORD: PostgreSQL connection.
- JWT_SECRET_KEY: Secret for JWT signing.
- JWT_ALGORITHM: Token algorithm (default: HS256).
- ACCESS_TOKEN_EXPIRE_MINUTES: Token expiry (default: 30).

### Deployment

- Backend: Build Docker image (backend/Dockerfile) and deploy to ECS.
- Frontend: Run next export and serve static files via S3 or Nginx.
- Use AWS Secrets Manager for JWT_SECRET_KEY and Parameter Store for DB creds.

### CI/CD

- GitHub Actions workflow (.github/workflows/ci-cd.yaml) includes:
- SAST with Semgrep
- Backend/frontend builds
- Container scanning with Trivy
- Push to ECR

### Testing Infrastructure

- Backend runs Alembic migrations on startup.
- RBAC: Admins access all users/tasks; regular users access own data only.
- ALB routes: /_ to frontend, /api/v1/_ to backend.
