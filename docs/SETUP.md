# AutoSense AI Platform - Setup Guide

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/downloads/)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd VahanIQ
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and configure your settings:
# - DATABASE_URL
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - API keys for LLMs
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb autosense_db

# Or using psql:
psql -U postgres
CREATE DATABASE autosense_db;
\q

# Update DATABASE_URL in .env:
# DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/autosense_db

# Run migrations (when available)
# alembic upgrade head
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local if needed
# VITE_API_BASE_URL should point to your backend
```

### 5. ML Model Setup (Optional for initial testing)

```bash
# Navigate to ML directory
cd ../ml

# Download datasets (instructions in ml/data/README.md)
# Train initial model (when script is available)
# python scripts/train_prediction_model.py
```

## 🏃 Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/api/docs`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 🔑 Getting API Keys

### Claude API (Anthropic)

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

### OpenAI API (Alternative)

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new secret key
5. Add to `.env`: `OPENAI_API_KEY=sk-...`

## 📊 Database Migrations (Using Alembic)

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🧪 Running Tests

### Backend Tests

```bash
cd backend
pytest
pytest --cov=app  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'app'`
- **Solution**: Make sure you're in the `backend` directory and the virtual environment is activated

**Problem**: Database connection error
- **Solution**: Check if PostgreSQL is running and DATABASE_URL in `.env` is correct

**Problem**: Import errors with pydantic
- **Solution**: Ensure you have pydantic v2+ installed: `pip install --upgrade pydantic`

### Frontend Issues

**Problem**: `Cannot find module '@/...'`
- **Solution**: Check tsconfig.json path aliases are correctly configured

**Problem**: Vite build errors
- **Solution**: Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)

## 🤝 Need Help?

Contact the development team or open an issue in the repository.
