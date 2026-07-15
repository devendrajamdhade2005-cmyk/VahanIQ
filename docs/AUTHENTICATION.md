# Authentication & Authorization Guide

## Overview

AutoSense AI uses JWT (JSON Web Tokens) for authentication with role-based access control (RBAC).

## Architecture

```
┌─────────────┐     Login      ┌──────────────┐
│   Client    │───────────────>│   Backend    │
│             │<───────────────│   (FastAPI)  │
└─────────────┘   JWT Tokens   └──────────────┘
                                      │
                                      │ Verify
                                      ↓
                              ┌───────────────┐
                              │  PostgreSQL   │
                              │  (User table) │
                              └───────────────┘
```

## User Roles

### 1. **Admin** (`admin`)
- **Purpose**: Platform-wide oversight and configuration
- **Access**: Everything across all showrooms
- **Capabilities**:
  - Manage all users, showrooms, vehicles
  - View all repair cases and diagnoses
  - Configure ML models and knowledge base
  - Access audit logs
  - Reset user passwords

### 2. **Showroom Manager** (`showroom`)
- **Purpose**: Manage one service center
- **Access**: Only their assigned showroom
- **Capabilities**:
  - View and manage vehicles in their showroom
  - Assign repair cases to mechanics
  - Manage parts inventory
  - View showroom analytics
  - Manage showroom staff (view only)

### 3. **Mechanic** (`mechanic`)
- **Purpose**: Diagnose and repair vehicles
- **Access**: Their assigned showroom and repair cases
- **Capabilities**:
  - View assigned repair cases
  - Access AI diagnoses and repair guides
  - Mark repair steps complete
  - Provide feedback on diagnoses
  - Use parts from inventory

### 4. **Owner** (`owner`)
- **Purpose**: Monitor vehicle health
- **Access**: Only their own vehicles
- **Capabilities**:
  - View vehicle health status
  - See diagnoses and alerts
  - Book appointments
  - Approve repair estimates
  - View service history

## Authentication Flow

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "user@example.com",
  "role": "mechanic",
  "full_name": "John Doe"
}
```

### Using Access Token

Include the access token in the `Authorization` header for all subsequent requests:

```http
GET /api/vehicles/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Refresh

Access tokens expire after 30 minutes. Use the refresh token to get a new access token:

```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "mechanic@example.com",
  "full_name": "John Doe",
  "role": "mechanic",
  "showroom_id": 1,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-20T14:25:00Z"
}
```

## Password Management

### Change Password (Self)

```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

### Reset Password (Admin Only)

```http
POST /api/auth/reset-password
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "email": "user@example.com",
  "new_password": "newpassword123"
}
```

## Access Control Rules

### Data Isolation

#### Showroom-Level Isolation
All showroom staff (managers, mechanics) can ONLY access data from their assigned showroom:

```python
# Automatic filtering in queries
SELECT * FROM vehicles 
WHERE home_showroom_id = :user_showroom_id
```

#### Owner-Level Isolation
Vehicle owners can ONLY access their own vehicles:

```python
# Automatic filtering in queries
SELECT * FROM vehicles 
WHERE owner_id = :user_id
```

### Endpoint Protection

Endpoints are protected using FastAPI dependencies:

```python
from app.core.dependencies import (
    get_current_user,      # Any authenticated user
    require_admin,          # Admin only
    require_showroom_manager,  # Admin or Showroom Manager
    require_mechanic,       # Admin, Showroom, or Mechanic
)

@router.get("/admin-only")
async def admin_endpoint(user: User = Depends(require_admin)):
    # Only admins can access
    pass

@router.get("/showroom-data")
async def showroom_endpoint(user: User = Depends(require_showroom_manager)):
    # Admins and showroom managers can access
    pass
```

## Security Best Practices

### Password Requirements
- Minimum 8 characters
- Hashed using bcrypt with automatic salt
- Never stored in plain text
- Never logged or transmitted in responses

### JWT Token Security
- **Access Token**: Short-lived (30 minutes)
- **Refresh Token**: Longer-lived (7 days)
- Signed with HS256 algorithm
- Secret key stored in environment variables
- Tokens are stateless (no database lookup per request)

### HTTPS Only
In production, all authentication endpoints MUST use HTTPS.

### Token Storage (Frontend)
- **Access Token**: Store in memory (React state)
- **Refresh Token**: Store in httpOnly cookie (preferred) or secure storage
- **Never**: Store tokens in localStorage or sessionStorage for production

## Test Accounts

After running `python seed_data.py`, these accounts are available:

| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| Admin | admin@autosense.ai | admin123 | Full platform access |
| Showroom Manager | manager.mumbai@autosense.ai | manager123 | Mumbai showroom |
| Mechanic | mechanic.mumbai@autosense.ai | mechanic123 | Mumbai mechanic |
| Owner | owner@example.com | owner123 | Test vehicle owner |

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```
**Cause**: Invalid or expired token
**Action**: Re-authenticate with login endpoint

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```
**Cause**: Insufficient permissions
**Action**: User doesn't have required role

### 403 Forbidden (Data Isolation)
```json
{
  "detail": "Access denied to this showroom"
}
```
**Cause**: Trying to access data from another showroom
**Action**: Request is blocked for security

## Audit Logging

All authentication events are logged in the `audit_logs` table:

- Successful logins
- Failed login attempts
- Password changes
- Password resets
- User creation/updates/deletion

Example audit log entry:
```json
{
  "user_id": 1,
  "action": "login_success",
  "resource_type": "user",
  "resource_id": 1,
  "description": "User logged in: admin@autosense.ai",
  "ip_address": "192.168.1.1",
  "success": "success",
  "created_at": "2024-01-20T14:25:00Z"
}
```

## API Testing with cURL

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@autosense.ai",
    "password": "admin123"
  }'
```

### Access Protected Endpoint
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create User (Admin)
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "full_name": "New User",
    "role": "mechanic",
    "showroom_id": 1
  }'
```

## Frontend Integration

### React Example with Axios

```typescript
import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000/api'
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/auth/refresh', {
            refresh_token: refreshToken
          });
          localStorage.setItem('access_token', data.access_token);
          // Retry original request
          error.config.headers.Authorization = `Bearer ${data.access_token}`;
          return api.request(error.config);
        } catch {
          // Refresh failed, redirect to login
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Login function
export const login = async (email: string, password: string) => {
  const { data } = await api.post('/auth/login', { email, password });
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  return data;
};
```

## Troubleshooting

### "Could not validate credentials"
- Check token is being sent in Authorization header
- Verify token hasn't expired
- Ensure SECRET_KEY in .env matches between sessions

### "Inactive user"
- User account has been disabled
- Contact admin to reactivate account

### "Access denied to this showroom"
- User trying to access data outside their showroom
- This is by design for security - cannot be bypassed

### Token not working after server restart
- If SECRET_KEY changed, all existing tokens are invalid
- Users must re-authenticate
- Keep SECRET_KEY consistent across deployments

## Related Documentation

- [Database Schema](DATABASE_SCHEMA.md) - User and audit log tables
- [API Documentation](API.md) - Complete API reference
- [Setup Guide](SETUP.md) - Environment configuration
