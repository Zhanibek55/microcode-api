# 🚀 MicroCode API - Backend Service

> **FastAPI backend service for the AI-powered micro-automation platform**

## 📖 Overview

This is the main backend API service for MicroCode, built with FastAPI. It handles task analysis, AI integration, code generation, payment processing, and user management.

## 🏗️ Architecture

### Technology Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL via Supabase
- **ORM**: SQLAlchemy with Alembic migrations
- **Authentication**: Google OAuth + JWT tokens
- **AI Integration**: OpenAI GPT-4 + Claude (fallback)
- **Code Execution**: Docker sandboxed containers
- **Background Jobs**: Celery (Redis)
- **Monitoring**: Sentry + Railway metrics

### Core Components
- **Task Analysis Engine**: AI-powered task complexity assessment
- **Code Generation Pipeline**: Template-based script generation
- **Security Sandbox**: Docker-based code execution
- **Payment Gateway**: YooKassa + Stripe integration
- **User Management**: OAuth authentication and profiles
- **Notification System**: Telegram + WhatsApp integration

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL client
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Zhanibek55/microcode-api.git
cd microcode-api
```

2. **Setup environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Environment variables**
```bash
cp .env.example .env
# Configure your environment variables
```

4. **Database setup**
```bash
# Run migrations
alembic upgrade head
```

5. **Start development server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
microcode-api/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core configurations
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   ├── auth/             # Authentication
│   ├── ai/               # AI integration
│   ├── sandbox/          # Code execution
│   └── utils/            # Utilities
├── tests/                # Test files
├── alembic/              # Database migrations
├── docker/               # Docker configurations
├── scripts/              # Utility scripts
├── requirements.txt      # Dependencies
└── README.md
```

## 🔐 Security Features

- **Sandboxed Code Execution**: Docker containers with resource limits
- **Input Validation**: Pydantic models for all endpoints
- **Rate Limiting**: 10 requests/minute per user
- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Properly configured origins
- **Security Headers**: HSTS, CSP, X-Frame-Options

## 📊 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api/test_tasks.py
```

## 🐳 Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in production mode
docker-compose -f docker-compose.prod.yml up
```

## 🚀 Deployment

This service is designed to be deployed on Railway. See [deployment guide](./docs/deployment.md) for details.

## 📝 Development Roadmap

See the main [EXECUTION_PLAN.md](https://github.com/Zhanibek55/microcode-docs/blob/main/EXECUTION_PLAN.md) for the complete development roadmap.

### Current Phase: Foundation Setup (Weeks 1-2)
- [x] Repository setup
- [ ] FastAPI project structure
- [ ] Database models and migrations
- [ ] Authentication system
- [ ] Docker configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is part of the MicroCode platform. See the main repository for license details.

## 🔗 Related Repositories

- **[microcode-frontend](https://github.com/Zhanibek55/microcode-frontend)** - Next.js web application  
- **[microcode-admin](https://github.com/Zhanibek55/microcode-admin)** - Administrative dashboard
- **[microcode-docs](https://github.com/Zhanibek55/microcode-docs)** - Project documentation

---

*Built with ❤️ for automating the world, one script at a time.*