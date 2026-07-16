# AutoSense AI Platform - Test Credentials

## System Status ✅

**Backend Server**: http://localhost:8000 - RUNNING  
**Frontend App**: http://localhost:3000 - RUNNING  
**Database**: SQLite at `backend/autosense.db` - READY

---

## Test User Accounts

### 1. Admin Account
- **Email**: `admin@autosense.ai`
- **Password**: `admin123`
- **Role**: Administrator
- **Name**: System Administrator
- **Access**: Full system access

### 2. Showroom Manager
- **Email**: `manager.mumbai@autosense.ai`
- **Password**: `manager123`
- **Role**: Showroom Manager
- **Name**: Rajesh Kumar
- **Showroom**: Mumbai Central
- **Access**: Manage showroom, vehicles, mechanics

### 3. Mechanic
- **Email**: `mechanic.mumbai@autosense.ai`
- **Password**: `mechanic123`
- **Role**: Mechanic
- **Name**: Amit Patel
- **Showroom**: Mumbai Central
- **Access**: Create diagnoses, view vehicles

### 4. Vehicle Owner
- **Email**: `owner@example.com`
- **Password**: `owner123`
- **Role**: Vehicle Owner
- **Name**: Suresh Gupta
- **Access**: View own vehicles and diagnoses

---

## Sample Data

### Showrooms
1. **Mumbai Central** (ID: 1)
   - Address: 123 MG Road, Mumbai Central, Mumbai 400008
   - Manager: Rajesh Kumar
   - Contact: +91-22-1234-5678

2. **Pune Baner** (ID: 2)
   - Address: 456 Baner Road, Baner, Pune 411045
   - Manager: Not assigned
   - Contact: +91-20-8765-4321

### Vehicles
1. **Tata Nexon EV** (MH01AB1234)
   - Owner: Suresh Gupta
   - Year: 2023
   - VIN: NEXON123EV456789
   - Home Showroom: Mumbai Central

2. **Tata Harrier** (MH02CD5678)
   - Owner: Suresh Gupta
   - Year: 2024
   - VIN: HARRIER890XZ123456
   - Home Showroom: Mumbai Central

---

## How to Test

### 1. Open the Frontend
Navigate to: http://localhost:3000

### 2. Login
- Use any of the test accounts above
- Click "Sign In"
- You'll be redirected to your role-specific dashboard

### 3. Test Features by Role

**As Admin:**
- View overview dashboard with stats
- Manage all users across showrooms
- View all vehicles and diagnoses
- Access analytics

**As Showroom Manager:**
- View showroom overview
- Manage vehicles in your showroom
- Assign mechanics
- View showroom diagnoses

**As Mechanic:**
- Create AI-powered diagnoses
- View sensor data
- Generate repair guides using ML → RAG → LLM pipeline
- Update diagnosis status

**As Vehicle Owner:**
- View your vehicles' health scores
- See service history
- Check maintenance schedules
- Review past diagnoses

---

## API Testing

### Login API
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@autosense.ai","password":"admin123"}'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "admin@autosense.ai",
  "role": "admin",
  "full_name": "System Administrator"
}
```

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
Visit: http://localhost:8000/api/docs

---

## ML/RAG Status

⚠️ **Currently using mock implementations** (lightweight fallback mode)

The system is fully functional but using simple rule-based logic instead of full ML models. This allows the system to run without heavy dependencies.

**Mock Features:**
- Failure prediction uses rule-based heuristics
- RAG context returns placeholder data
- LLM integration still works with real Claude/GPT APIs

**To enable full ML stack:**
```bash
cd backend
pip3 install torch sentence-transformers faiss-cpu xgboost shap scikit-learn numpy pandas joblib --break-system-packages
# Then restart backend server
```

---

## Troubleshooting

### Frontend not loading?
- Check frontend process: http://localhost:3000
- Check browser console for errors

### Login not working?
- Verify backend is running: http://localhost:8000/health
- Check credentials match exactly (case-sensitive)

### API errors?
- Check backend logs for detailed error messages
- Verify CORS is configured correctly
- Ensure database has been initialized

---

## Next Steps

1. ✅ Test login with all 4 user roles
2. ✅ Verify role-based access control
3. ✅ Test vehicle list and details
4. 🔄 Create a test diagnosis (mechanic)
5. 🔄 Test AI pipeline (ML → RAG → LLM)
6. 🔄 Complete ML package installation
