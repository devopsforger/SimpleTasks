# Task Management Application

A production-ready, full-stack task management application built with FastAPI backend and Next.js frontend. Features user authentication, role-based access control, and real-time task management.

## 🚀 Features

- **Backend**: FastAPI with async PostgreSQL, JWT authentication, and role-based access control
- **Frontend**: Next.js 15 with TypeScript, Tailwind CSS, and responsive design
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Containerized**: Docker and Docker Compose for easy development and deployment
- **Authentication**: JWT-based secure authentication system
- **Authorization**: Admin and regular user roles with appropriate permissions

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Alembic, Pydantic, JWT
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, Axios
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose
- **Package Management**: UV (Python), npm (Node.js)

## 📁 Project Structure

```
SimpleTasks/
├── backend/          # FastAPI backend application
├── frontend/         # Next.js frontend application
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SimpleTasks
   ```

2. **Set up environment variables**
   ```bash
   # Copy and edit the environment template
   cp .env.example .env
   # Edit .env with your preferred values
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432

### Default Admin Account

After first setup, register a new user with admin privileges through the registration form.

## 📚 Documentation

- [Backend Documentation](./backend/README.md) - API details, setup, and development
- [Frontend Documentation](./frontend/README.md) - UI components, features, and development

## 🔧 Development

### Running Services Individually

```bash
# Backend only
docker-compose up backend

# Frontend only  
docker-compose up frontend

# Database only
docker-compose up db
```

### Stopping the Application

```bash
docker-compose down
```

### Viewing Logs

```bash
docker-compose logs -f
```

## 🐳 Production Deployment

For production deployment, use the provided Docker Compose production configuration:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control
- CORS protection
- SQL injection prevention
- Environment variable security

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

