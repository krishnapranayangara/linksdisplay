# Link Organizer Backend API

A production-grade Flask REST API for managing bookmarks and links with categorization features.

## 🚀 Features

- **CRUD Operations**: Full Create, Read, Update, Delete operations for links and categories
- **Categorization**: Organize links into logical groups
- **Search**: Search links by title with case-insensitive matching
- **Pinning**: Pin important links for quick access
- **Statistics**: Get insights about your links and categories
- **Health Monitoring**: Built-in health checks and system monitoring
- **Error Logging**: Comprehensive API call logging and monitoring
- **Production Ready**: Proper error handling, logging, and configuration management
- **Comprehensive Testing**: Unit and integration tests with coverage reporting

## 🏗️ Architecture

The application follows a clean, modular architecture:

```
backend/
├── app.py                 # Main application factory
├── config.py             # Configuration management
├── models/               # Database models
│   ├── __init__.py
│   ├── category.py       # Category model and schema
│   ├── link.py          # Link model and schema
│   └── error.py         # Error logging model
├── services/             # Business logic layer
│   ├── __init__.py
│   ├── category_service.py
│   ├── link_service.py
│   └── error_service.py
├── api/                  # API endpoints
│   ├── __init__.py
│   ├── categories.py     # Category endpoints
│   ├── links.py         # Link endpoints
│   └── health.py        # Health check endpoints
├── routes/               # Additional API routes
│   └── errors.py        # Error logging endpoints
├── middleware/           # Request middleware
│   └── request_logger.py # Request logging middleware
├── tests/               # Test suite
│   ├── __init__.py
│   ├── conftest.py      # Test configuration
│   ├── test_models.py   # Model tests
│   └── test_api.py      # API integration tests
└── requirements.txt     # Dependencies
```

## 🛠️ Technology Stack

- **Framework**: Flask 2.3.3
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Serialization**: Marshmallow for data validation and serialization
- **Testing**: pytest with coverage reporting
- **Code Quality**: Black, flake8, isort
- **Production Server**: Gunicorn
- **Monitoring**: psutil for system metrics

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL user and database
sudo -u postgres psql
CREATE USER admin WITH PASSWORD 'admin';
CREATE DATABASE link_organizer_dev OWNER admin;
CREATE DATABASE link_organizer_test OWNER admin;
GRANT ALL PRIVILEGES ON DATABASE link_organizer_dev TO admin;
GRANT ALL PRIVILEGES ON DATABASE link_organizer_test TO admin;
\q

# Initialize database
python -c "from app import init_db; init_db()"
```

### 3. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your settings
DATABASE_URL=postgresql://admin:admin@localhost:5432/link_organizer_dev
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### 4. Run the Application

```bash
# Development mode
python app.py

# Or use the Makefile
make dev
```

The API will be available at `http://localhost:5000`

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m unit      # Unit tests only
pytest -m api       # API tests only
pytest -m models    # Model tests only
```

### Test Coverage

The project maintains >80% test coverage. Coverage reports are generated in HTML format and can be viewed in `htmlcov/index.html`.

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication
Currently, the API doesn't require authentication. In production, implement JWT or OAuth2.

### Endpoints

#### Health Checks
- `GET /api/health` - Get API health status and system metrics
- `GET /api/ping` - Simple connectivity test

#### Categories
- `GET /api/categories` - Get all categories
- `GET /api/categories/{id}` - Get category by ID
- `POST /api/categories` - Create new category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category
- `GET /api/categories/stats` - Get category statistics

#### Links
- `GET /api/links` - Get all links
- `GET /api/links?category_id={id}` - Get links by category
- `GET /api/links/{id}` - Get link by ID
- `POST /api/links` - Create new link
- `PUT /api/links/{id}` - Update link
- `DELETE /api/links/{id}` - Delete link
- `PATCH /api/links/{id}/pin` - Toggle link pin status
- `GET /api/links/search?q={term}` - Search links by title
- `GET /api/links/pinned` - Get pinned links
- `GET /api/links/stats` - Get link statistics

#### Error Logging
- `GET /api/errors` - Get error logs with filtering
- `GET /api/errors/{id}` - Get specific error log
- `GET /api/errors/statistics` - Get error statistics
- `DELETE /api/errors/cleanup` - Clean up old error logs
- `GET /api/errors/export` - Export error logs

### Request/Response Format

All requests and responses use JSON format.

#### Example: Create Category
```bash
POST /api/categories
Content-Type: application/json

{
  "name": "Work",
  "description": "Work-related links"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Work",
    "description": "Work-related links",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "links_count": 0
  },
  "message": "Category created successfully"
}
```

#### Example: Create Link
```bash
POST /api/links
Content-Type: application/json

{
  "title": "Google",
  "url": "https://google.com",
  "description": "Search engine",
  "categoryId": 1,
  "pinned": true
}
```

## 🔧 Development

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Run all checks (lint + test)
make check
```

### Database Migrations

For production, consider using Alembic for database migrations:

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/testing/production) | development |
| `DATABASE_URL` | PostgreSQL connection string | postgresql://admin:admin@localhost:5432/link_organizer_dev |
| `SECRET_KEY` | Flask secret key | dev-secret-key-change-in-production |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:3000 |

## 🚀 Production Deployment

### Using Gunicorn

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or use the Makefile
make run
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Environment Configuration

For production, set these environment variables:

```bash
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@host:5432/dbname
export SECRET_KEY=your-secure-secret-key
export CORS_ORIGINS=https://yourdomain.com
```

## 📊 Monitoring

### Health Checks

The API provides comprehensive health monitoring:

- System metrics (CPU, memory, disk usage)
- Database connectivity
- Application status

### Error Logging

The API automatically logs all requests and responses for monitoring and debugging:

#### Features
- **Automatic Logging**: All API calls are automatically logged with request/response details
- **Request Details**: Method, endpoint, headers, parameters, client IP, user agent
- **Response Details**: Status code, response data, error messages, timing
- **Performance Metrics**: Request duration, response times
- **Security**: Sensitive headers (Authorization, Cookie) are automatically sanitized
- **Filtering**: Filter logs by method, endpoint, status code, date range
- **Statistics**: Get aggregated statistics for monitoring and analytics
- **Export**: Export logs in JSON format for analysis
- **Cleanup**: Automatic cleanup of old logs to manage storage

#### Example Usage

```bash
# Get all error logs
curl http://localhost:3001/api/errors

# Get logs with filtering
curl "http://localhost:3001/api/errors?method=POST&status_code=400"

# Get error statistics
curl http://localhost:3001/api/errors/statistics

# Export logs
curl http://localhost:3001/api/errors/export?limit=100

# Clean up old logs (older than 30 days)
curl -X DELETE "http://localhost:3001/api/errors/cleanup?days=30"
```

#### Log Data Structure

Each log entry contains:
- **Request Info**: Method, endpoint, headers, parameters, client IP, user agent
- **Response Info**: Status code, response data, error messages, error type
- **Timing**: Request time, response time, duration in milliseconds
- **Context**: Session ID, user ID (if available)

### Logging

Logs are written to `logs/link_organizer.log` in production mode with rotation.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Workflow

```bash
# Setup development environment
make dev-setup

# Make changes and test
make test

# Format and lint code
make format
make lint

# Run all checks
make check
```

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the API documentation at `/api/docs`
2. Review the test cases for usage examples
3. Check the logs for error details
4. Open an issue on GitHub

## 🔄 API Versioning

The current API version is v1. Future versions will be available at `/api/v2/`, etc.

## 📈 Performance

- Database queries are optimized with proper indexing
- Connection pooling is configured for production
- Response caching can be added for frequently accessed data
- Consider using Redis for session storage in production 