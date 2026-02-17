# EdTech Mobile App - Backend

FastAPI backend for EdTech mobile application with PostgreSQL database.

## Features

- ✅ User Authentication (JWT-based)
- ✅ User Registration & Email Verification
- ✅ Password Reset Flow
- ✅ User Profile Management
- ✅ Role-Based Access Control (Student, Instructor, Admin)
- ✅ PostgreSQL Database
- ✅ Redis Caching
- ✅ Docker Support

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Validation**: Pydantic
- **Caching**: Redis

## Project Structure

```
backend/
├── app/
│   ├── api/              # API route handlers
│   │   ├── auth.py       # Authentication endpoints
│   │   └── users.py      # User management endpoints
│   ├── models/           # Database models
│   │   └── user.py       # User, UserProfile, UserSession
│   ├── schemas/          # Pydantic schemas
│   │   └── user.py       # Request/Response schemas
│   ├── services/         # Business logic
│   │   └── user_service.py
│   ├── utils/            # Utility functions
│   │   ├── security.py   # JWT & password hashing
│   │   └── helpers.py    # Helper functions
│   ├── config.py         # Configuration
│   ├── database.py       # Database connection
│   └── dependencies.py   # FastAPI dependencies
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker services
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Docker & Docker Compose (for PostgreSQL & Redis)
- pip or pipenv

### 2. Clone and Setup

```bash
cd backend
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env and update SECRET_KEY and other settings
```

**Important**: Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Start Database (Docker)

```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379

### 7. Run the Application

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at: **http://localhost:8000**

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/verify-email` - Verify email with token
- `POST /api/v1/auth/password-reset/request` - Request password reset
- `POST /api/v1/auth/password-reset/confirm` - Reset password
- `GET /api/v1/auth/me` - Get current user

### User Management
- `GET /api/v1/users/me` - Get my profile
- `PUT /api/v1/users/me` - Update my profile
- `POST /api/v1/users/me/change-password` - Change password
- `GET /api/v1/users/{user_id}` - Get user by ID

### Health
- `GET /health` - Health check
- `GET /` - API information

## Example Requests

### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123"
  }'
```

### Get Current User (with token)
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Database Management

### Check Database Status
```bash
docker-compose ps
```

### Access PostgreSQL
```bash
docker exec -it edtech_postgres psql -U edtech_user -d edtech_db
```

### Access Redis
```bash
docker exec -it edtech_redis redis-cli
```

### Stop Services
```bash
docker-compose down
```

### Reset Database
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d
```

## Development

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
```

### Linting
```bash
flake8 app/
```

## Environment Variables

Key environment variables (see `.env.example` for all):

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key (must be secure)
- `REDIS_URL` - Redis connection string
- `DEBUG` - Enable debug mode (True/False)
- `ALLOWED_ORIGINS` - CORS allowed origins

## Next Steps

1. **Email Integration**: Configure SendGrid or SMTP for email verification and password resets
2. **File Upload**: Implement AWS S3 integration for user avatars
3. **Course Models**: Add course, lesson, and enrollment models
4. **Payment Integration**: Add Stripe/Razorpay for payments
5. **Testing**: Write comprehensive unit and integration tests
6. **Deployment**: Deploy to AWS, DigitalOcean, or Railway

## Security Notes

- ⚠️ **Always use HTTPS in production**
- ⚠️ **Never commit `.env` file to version control**
- ⚠️ **Use strong SECRET_KEY (min 32 characters)**
- ⚠️ **Regularly update dependencies**
- ⚠️ **Enable rate limiting in production**

## Support

For issues or questions, refer to the main roadmap document or create an issue in the repository.

## License

Commercial EdTech Application
# Gyan-Bharat-backend
