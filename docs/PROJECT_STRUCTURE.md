# Project Structure

## Overview

AutoSense AI is organized as a monorepo with separate backend, frontend, and ML components.

```
VahanIQ/
├── backend/                 # FastAPI backend service
├── frontend/                # React frontend application
├── ml/                      # Machine learning components
├── docs/                    # Documentation
└── .github/                 # GitHub workflows
```

## Backend Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/         # API endpoint definitions
│   │       ├── auth.py     # Authentication routes
│   │       ├── users.py    # User management
│   │       ├── vehicles.py # Vehicle management
│   │       ├── diagnoses.py # AI diagnoses
│   │       ├── repairs.py  # Repair cases
│   │       ├── showrooms.py # Showroom management
│   │       └── appointments.py # Appointment booking
│   ├── core/
│   │   ├── config.py       # Application configuration
│   │   ├── database.py     # Database connection
│   │   ├── security.py     # JWT & password hashing
│   │   └── dependencies.py # FastAPI dependencies
│   ├── models/             # SQLAlchemy database models
│   │   ├── user.py
│   │   ├── vehicle.py
│   │   ├── showroom.py
│   │   ├── diagnosis.py
│   │   └── repair.py
│   ├── services/           # Business logic layer
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── vehicle_service.py
│   │   └── diagnosis_service.py
│   ├── ml/                 # ML prediction service
│   │   ├── predictor.py    # XGBoost model wrapper
│   │   ├── explainer.py    # SHAP explainability
│   │   └── preprocessor.py # Feature engineering
│   └── rag/                # RAG system
│       ├── vector_store.py # FAISS index management
│       ├── embeddings.py   # Sentence transformers
│       └── retriever.py    # Context retrieval
├── tests/                  # Unit and integration tests
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variables template
```

## Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── admin/         # Admin dashboard components
│   │   ├── showroom/      # Showroom dashboard components
│   │   ├── mechanic/      # Mechanic dashboard components
│   │   ├── owner/         # Car owner dashboard components
│   │   └── shared/        # Reusable components
│   │       ├── ui/        # shadcn/ui components
│   │       ├── Layout.tsx
│   │       ├── Header.tsx
│   │       └── Sidebar.tsx
│   ├── pages/             # Route components
│   │   ├── admin/
│   │   ├── showroom/
│   │   ├── mechanic/
│   │   └── owner/
│   ├── services/          # API client services
│   │   ├── api.ts         # Axios configuration
│   │   ├── auth.ts        # Authentication API
│   │   ├── vehicles.ts    # Vehicle API
│   │   └── diagnoses.ts   # Diagnosis API
│   ├── hooks/             # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useWebSocket.ts
│   │   └── useVehicles.ts
│   ├── utils/             # Utility functions
│   │   ├── cn.ts          # Class name utilities
│   │   ├── formatters.ts  # Data formatters
│   │   └── validators.ts  # Form validation
│   ├── types/             # TypeScript type definitions
│   │   ├── api.ts
│   │   ├── user.ts
│   │   ├── vehicle.ts
│   │   └── diagnosis.ts
│   ├── App.tsx            # Root application component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles
├── public/                # Static assets
├── package.json           # Node dependencies
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite configuration
└── tailwind.config.js     # Tailwind CSS configuration
```

## ML Structure

```
ml/
├── models/                # Trained model files (.pkl, .joblib)
│   ├── failure_prediction_model.pkl
│   ├── shap_explainer.pkl
│   └── .gitkeep
├── data/                  # Dataset files
│   ├── raw/              # Original datasets
│   ├── processed/        # Preprocessed data
│   └── synthetic/        # Generated synthetic data
├── notebooks/            # Jupyter notebooks for experiments
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_rag_testing.ipynb
└── scripts/              # Training and preprocessing scripts
    ├── train_prediction_model.py
    ├── prepare_rag_index.py
    ├── generate_synthetic_data.py
    └── evaluate_model.py
```

## Key Design Patterns

### Backend

- **Repository Pattern**: Models define data structure, services implement business logic
- **Dependency Injection**: FastAPI's `Depends()` for database sessions, auth, etc.
- **Async/Await**: All database operations use async SQLAlchemy
- **Multi-tenancy**: Every query filtered by showroom_id/owner_id at DB layer

### Frontend

- **Component Structure**: Atomic design (atoms → molecules → organisms)
- **Data Fetching**: React Query for server state management
- **Client State**: Zustand for local state (auth, UI preferences)
- **Type Safety**: Full TypeScript coverage with strict mode

## Development Workflow

1. **Feature Development**
   - Create feature branch: `git checkout -b feature/feature-name`
   - Implement backend models → services → routes
   - Implement frontend types → services → components → pages
   - Write tests
   - Create PR for review

2. **Database Changes**
   - Modify SQLAlchemy models
   - Generate migration: `alembic revision --autogenerate -m "Description"`
   - Review and edit migration file
   - Apply: `alembic upgrade head`

3. **Testing**
   - Backend: `pytest` with coverage
   - Frontend: Component tests with Vitest/React Testing Library
   - Integration: End-to-end tests with Playwright (Phase 2)

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`: LLM access
- See `.env.example` for full list

### Frontend (.env.local)
- `VITE_API_BASE_URL`: Backend API URL
- `VITE_WS_URL`: WebSocket URL
- See `.env.example` for full list

## Deployment Structure

```
Production:
├── Backend: Railway/Render
├── Frontend: Vercel
├── Database: Supabase/Neon (managed PostgreSQL)
└── Storage: S3-compatible (for files/manuals)
```

## Security Considerations

- **Never commit**: `.env` files, API keys, database credentials
- **Always use**: Environment variables for sensitive data
- **RBAC enforcement**: Server-side on every endpoint
- **Data isolation**: Hard-coded in queries, not just UI filters
- **Input validation**: Both client and server-side
- **Audit logging**: Track all admin and sensitive actions
