# Database Schema Documentation

## Overview

The AutoSense AI platform uses PostgreSQL with a comprehensive relational schema designed for:
- Multi-tenant data isolation (showroom-level)
- Time-series sensor data storage
- AI diagnosis tracking with feedback loop
- Complete repair workflow management
- Audit trail for compliance

## Schema Diagram

```
┌─────────────┐
│   users     │──┐
└─────────────┘  │
                 │
┌─────────────┐  │  ┌──────────────┐
│  showrooms  │◄─┴──│   vehicles   │
└─────────────┘     └──────────────┘
       │                    │
       │                    ├──► sensor_readings
       │                    ├──► diagnoses
       │                    ├──► appointments
       │                    └──► repair_cases
       │                              │
       ├──► parts                     ├──► repair_steps
       │                              ├──► parts_used
       └──► repair_cases              └──► invoices

┌──────────────────┐
│  knowledge_docs  │  (for RAG system)
└──────────────────┘

┌──────────────┐
│  audit_logs  │  (security & compliance)
└──────────────┘
```

## Core Tables

### users
**Purpose**: Authentication and role-based access control

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| email | String(255) | Unique email address |
| hashed_password | String(255) | Bcrypt hashed password |
| full_name | String(255) | User's full name |
| phone | String(20) | Contact number |
| role | Enum | admin, showroom, mechanic, owner |
| showroom_id | Integer | FK to showrooms (null for admin/owner) |
| is_active | Boolean | Account status |
| is_verified | Boolean | Email verification status |
| created_at | DateTime | Account creation timestamp |
| updated_at | DateTime | Last update timestamp |
| last_login | DateTime | Last login timestamp |

**Indexes**: email, role, showroom_id

**Key Relationships**:
- Belongs to showroom (nullable)
- Owns vehicles (as owner)
- Assigned to repair cases (as mechanic)

---

### showrooms
**Purpose**: Service center/dealership management

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String(255) | Showroom name |
| code | String(50) | Unique identifier code |
| address | Text | Full address |
| city | String(100) | City |
| state | String(100) | State |
| pincode | String(10) | Postal code |
| phone | String(20) | Contact number |
| email | String(255) | Contact email |
| region | String(100) | Geographic region |
| manager_name | String(255) | Manager name |
| capacity | Integer | Max concurrent repairs (default: 10) |
| is_active | Boolean | Operational status |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Indexes**: name, code

**Key Relationships**:
- Has many users (staff)
- Has many vehicles (home showroom)
- Has many repair cases
- Has many parts (inventory)

---

### vehicles
**Purpose**: Vehicle registry and health tracking

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| vin | String(17) | Vehicle Identification Number |
| registration_number | String(50) | License plate (unique) |
| make | String(100) | Manufacturer (e.g., Tata) |
| model | String(100) | Model name (e.g., Nexon) |
| year | Integer | Manufacturing year |
| variant | String(100) | Variant/trim level |
| color | String(50) | Vehicle color |
| owner_id | Integer | FK to users |
| home_showroom_id | Integer | FK to showrooms |
| current_mileage | Float | Odometer reading (km) |
| health_status | Enum | healthy, watch, warning, critical |
| health_score | Float | 0-100 scale |
| last_service_date | DateTime | Last service completion |
| next_service_due | DateTime | Scheduled next service |
| notes | Text | Additional information |
| created_at | DateTime | Registration timestamp |
| updated_at | DateTime | Last update timestamp |

**Indexes**: vin, registration_number, owner_id, home_showroom_id, health_status

**Key Relationships**:
- Belongs to owner (user)
- Belongs to home showroom
- Has many sensor readings (time-series)
- Has many diagnoses
- Has many repair cases
- Has many appointments

---

### sensor_readings
**Purpose**: Time-series OBD-II sensor data

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| vehicle_id | Integer | FK to vehicles |
| timestamp | DateTime | Reading timestamp |
| rpm | Float | Engine RPM |
| speed | Float | Vehicle speed (km/h) |
| engine_load | Float | Engine load (%) |
| coolant_temp | Float | Coolant temperature (°C) |
| intake_temp | Float | Intake air temperature (°C) |
| throttle_position | Float | Throttle position (%) |
| maf | Float | Mass Air Flow (g/s) |
| fuel_pressure | Float | Fuel pressure (kPa) |
| fuel_level | Float | Fuel level (%) |
| fuel_trim_short | Float | Short-term fuel trim (%) |
| fuel_trim_long | Float | Long-term fuel trim (%) |
| o2_voltage | Float | O2 sensor voltage |
| brake_fluid_pressure | Float | Brake pressure (bar) |
| brake_pad_thickness_* | Float | Pad thickness (mm) - 4 wheels |
| transmission_temp | Float | Transmission temperature (°C) |
| gear_position | Integer | Current gear |
| battery_voltage | Float | Battery voltage |
| dtc_codes | String(500) | Comma-separated DTC codes |
| mileage | Float | Odometer at reading (km) |
| created_at | DateTime | Ingestion timestamp |

**Composite Index**: (vehicle_id, timestamp) for efficient time-series queries

**Key Relationships**:
- Belongs to vehicle

---

### diagnoses
**Purpose**: AI-generated failure predictions with explainability

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| vehicle_id | Integer | FK to vehicles |
| failure_type | Enum | engine, transmission, brake, etc. |
| failure_probability | Float | 0.0 to 1.0 |
| severity | String(20) | low, medium, high, critical |
| explanation_text | Text | Plain-language explanation |
| technical_details | Text | Technical details for mechanics |
| shap_values | Text | JSON of SHAP explainability values |
| primary_sensor_signals | Text | JSON of key contributing sensors |
| recommended_actions | Text | JSON of recommended actions |
| estimated_time_to_failure | Float | Days/hours until failure |
| status | Enum | predicted, confirmed, false_positive, resolved |
| is_critical | Boolean | Requires immediate attention |
| model_version | String(50) | ML model version used |
| prediction_confidence | Float | Model confidence score |
| predicted_at | DateTime | Prediction timestamp |
| confirmed_at | DateTime | Mechanic confirmation timestamp |
| resolved_at | DateTime | Resolution timestamp |

**Indexes**: vehicle_id, failure_type, status, is_critical, predicted_at

**Key Relationships**:
- Belongs to vehicle
- Has many repair cases

---

### repair_cases
**Purpose**: Complete repair workflow tracking

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| vehicle_id | Integer | FK to vehicles |
| diagnosis_id | Integer | FK to diagnoses (nullable) |
| technician_id | Integer | FK to users (mechanic) |
| showroom_id | Integer | FK to showrooms |
| case_number | String(50) | Unique case identifier |
| title | String(255) | Brief description |
| description | Text | Detailed description |
| status | Enum | waiting, diagnosing, in_repair, qc, completed, cancelled |
| priority | String(20) | low, normal, high, urgent |
| started_at | DateTime | Work start timestamp |
| completed_at | DateTime | Completion timestamp |
| estimated_completion | DateTime | Estimated completion |
| actual_duration_minutes | Integer | Actual time taken |
| estimated_cost | Float | Initial cost estimate |
| actual_cost | Float | Final cost |
| labor_cost | Float | Labor charges |
| parts_cost | Float | Parts charges |
| requires_approval | Boolean | Needs customer approval |
| is_approved | Boolean | Customer approved |
| approved_at | DateTime | Approval timestamp |
| mechanic_feedback | Text | Feedback for ML improvement |
| diagnosis_accuracy | Enum | correct, partially_correct, incorrect |
| actual_issue_found | Text | What was actually wrong |
| internal_notes | Text | Private notes |
| created_at | DateTime | Case creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Indexes**: vehicle_id, diagnosis_id, technician_id, showroom_id, case_number, status

**Key Relationships**:
- Belongs to vehicle
- Belongs to diagnosis (nullable)
- Assigned to technician (user)
- Belongs to showroom
- Has many repair steps
- Has many parts used
- Has one invoice

---

### repair_steps
**Purpose**: Checklist of repair actions

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| repair_case_id | Integer | FK to repair_cases |
| step_number | Integer | Sequence order |
| title | String(255) | Step title |
| description | Text | Detailed instructions |
| is_safety_critical | Boolean | Critical safety step |
| is_completed | Boolean | Completion status |
| completed_at | DateTime | Completion timestamp |
| notes | Text | Mechanic notes |
| estimated_duration_minutes | Integer | Time estimate |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Indexes**: repair_case_id

**Key Relationships**:
- Belongs to repair case

---

### parts
**Purpose**: Parts inventory management per showroom

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| showroom_id | Integer | FK to showrooms |
| sku | String(100) | Stock Keeping Unit |
| name | String(255) | Part name |
| description | Text | Detailed description |
| category | String(100) | Part category |
| unit_price | Float | Price per unit |
| currency | String(3) | Currency code (default: INR) |
| stock_quantity | Integer | Current stock level |
| min_stock_threshold | Integer | Reorder threshold |
| max_stock_capacity | Integer | Maximum stock capacity |
| supplier_name | String(255) | Supplier name |
| supplier_part_number | String(100) | Supplier's part number |
| lead_time_days | Integer | Delivery lead time |
| is_active | Boolean | Part availability status |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| last_restocked_at | DateTime | Last restock timestamp |

**Indexes**: showroom_id, sku, name

**Property**: is_low_stock (computed: stock_quantity <= min_stock_threshold)

**Key Relationships**:
- Belongs to showroom
- Used in many repair cases (via parts_used)

---

### parts_used
**Purpose**: Junction table for parts consumed in repairs

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| repair_case_id | Integer | FK to repair_cases |
| part_id | Integer | FK to parts |
| quantity | Integer | Quantity used |
| unit_price_at_use | Float | Price at time of use |
| total_cost | Float | Total cost (qty × price) |
| used_at | DateTime | Usage timestamp |

**Indexes**: repair_case_id, part_id

**Key Relationships**:
- Belongs to repair case
- References part

---

### appointments
**Purpose**: Customer appointment booking and tracking

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| vehicle_id | Integer | FK to vehicles |
| showroom_id | Integer | FK to showrooms |
| appointment_number | String(50) | Unique identifier |
| requested_date | DateTime | Requested appointment time |
| confirmed_date | DateTime | Confirmed appointment time |
| service_type | String(100) | Type of service |
| reason | Text | Customer's issue description |
| status | Enum | requested, confirmed, checked_in, in_progress, completed, cancelled, no_show |
| preferred_contact_method | String(20) | phone, email, sms |
| reminder_sent | DateTime | Reminder sent timestamp |
| customer_notes | Text | Customer notes |
| internal_notes | Text | Staff notes |
| created_at | DateTime | Booking timestamp |
| updated_at | DateTime | Last update timestamp |
| checked_in_at | DateTime | Check-in timestamp |

**Indexes**: vehicle_id, showroom_id, appointment_number, requested_date, status

**Key Relationships**:
- Belongs to vehicle
- Belongs to showroom

---

### invoices
**Purpose**: Billing and payment tracking

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| repair_case_id | Integer | FK to repair_cases (unique) |
| invoice_number | String(50) | Unique invoice number |
| invoice_date | DateTime | Invoice generation date |
| due_date | DateTime | Payment due date |
| subtotal | Float | Amount before tax |
| labor_cost | Float | Labor charges |
| parts_cost | Float | Parts charges |
| tax_amount | Float | Tax amount (GST) |
| tax_percentage | Float | Tax rate (default: 18%) |
| discount_amount | Float | Discount applied |
| total_amount | Float | Final amount |
| is_paid | Boolean | Payment status |
| paid_at | DateTime | Payment timestamp |
| payment_method | String(50) | Payment method |
| transaction_id | String(100) | Transaction reference |
| pdf_url | String(500) | Invoice PDF URL |
| notes | Text | Invoice notes |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Indexes**: repair_case_id, invoice_number

**Key Relationships**:
- One-to-one with repair case

---

### knowledge_docs
**Purpose**: RAG system knowledge base

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| title | String(500) | Document title |
| doc_type | String(50) | manual, bulletin, guide, faq |
| category | String(100) | Category/topic |
| content | Text | Document content |
| content_summary | Text | Brief summary |
| file_url | String(500) | Original file location |
| file_type | String(20) | pdf, txt, html |
| embedding_id | String(100) | FAISS index reference |
| chunk_index | Integer | Chunk number if split |
| applicable_makes | String(500) | Comma-separated makes |
| applicable_models | String(500) | Comma-separated models |
| year_from | Integer | Applicable from year |
| year_to | Integer | Applicable to year |
| is_active | Boolean | Document active status |
| is_verified | Boolean | Quality verified |
| version | String(20) | Document version |
| superseded_by | Integer | ID of newer version |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| published_at | DateTime | Publication timestamp |

**Indexes**: title, doc_type, embedding_id

**Key Relationships**: None (standalone knowledge base)

---

### audit_logs
**Purpose**: Security, compliance, and change tracking

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | FK to users (nullable for system actions) |
| action | String(100) | Action performed |
| resource_type | String(50) | Resource affected |
| resource_id | Integer | ID of affected resource |
| description | Text | Action description |
| changes | JSON | Before/after values |
| ip_address | String(45) | Request IP address |
| user_agent | String(500) | Browser/client info |
| endpoint | String(255) | API endpoint called |
| success | String(20) | success, failure, error |
| error_message | Text | Error details if failed |
| created_at | DateTime | Action timestamp |

**Indexes**: user_id, action, resource_type, created_at

**Key Relationships**:
- Belongs to user (nullable)

---

## Data Isolation Rules

### Showroom-Level Isolation
**Critical security requirement**: Every query must enforce showroom-level data isolation.

```sql
-- Example: Get vehicles for a showroom manager
SELECT * FROM vehicles 
WHERE home_showroom_id = :current_user_showroom_id;

-- Example: Get repair cases for a showroom
SELECT * FROM repair_cases 
WHERE showroom_id = :current_user_showroom_id;
```

### Owner-Level Isolation
```sql
-- Example: Get vehicles for a car owner
SELECT * FROM vehicles 
WHERE owner_id = :current_user_id;
```

### Never Use Client-Side Filtering
❌ Wrong: Filter in frontend
✅ Correct: Filter in SQL query with user's showroom_id/owner_id

---

## Enumerations

### UserRole
- `admin`: Platform administrator
- `showroom`: Showroom manager
- `mechanic`: Service technician
- `owner`: Vehicle owner

### VehicleStatus
- `healthy`: All systems normal (green)
- `watch`: Minor issues detected (yellow)
- `warning`: Moderate issues, service soon (orange)
- `critical`: Severe issues, immediate attention (red)

### FailureType
- `engine`, `transmission`, `brake`, `electrical`, `suspension`, `cooling`, `fuel_system`, `exhaust`, `other`

### DiagnosisStatus
- `predicted`: AI generated, awaiting mechanic review
- `confirmed`: Mechanic confirmed accurate
- `false_positive`: Mechanic determined incorrect
- `resolved`: Issue fixed

### RepairStatus
- `waiting`: In queue
- `diagnosing`: Being diagnosed
- `in_repair`: Actively being repaired
- `qc`: Quality check in progress
- `completed`: Work finished
- `cancelled`: Cancelled

### FeedbackOutcome
- `correct`: Diagnosis was accurate
- `partially_correct`: Partially accurate
- `incorrect`: Diagnosis was wrong

### AppointmentStatus
- `requested`, `confirmed`, `checked_in`, `in_progress`, `completed`, `cancelled`, `no_show`

---

## Performance Optimizations

### Indexes
- All foreign keys are indexed
- Composite index on (vehicle_id, timestamp) for sensor_readings
- Status fields are indexed for filtering
- Timestamps are indexed for date-range queries

### Partitioning (Future)
For large-scale deployments, consider partitioning:
- `sensor_readings` by timestamp (monthly partitions)
- `audit_logs` by timestamp (quarterly partitions)

### Archival Strategy
- Archive sensor_readings older than 2 years
- Archive audit_logs older than 5 years
- Keep diagnoses and repair_cases indefinitely for ML training

---

## Migration Strategy

### Development
```bash
# Create tables directly
python init_db.py
```

### Production
```bash
# Use Alembic migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

---

## Backup Strategy

### Daily
- Full database backup
- Retention: 7 days

### Weekly
- Full backup with extended retention
- Retention: 4 weeks

### Monthly
- Archived full backup
- Retention: 12 months

### Critical Tables (Extra Protection)
- `users`, `vehicles`, `repair_cases`, `invoices`
- Replicate to standby server

---

## Schema Evolution Guidelines

1. **Never break existing APIs** - Use migrations, not destructive changes
2. **Add columns with defaults** - Ensure existing rows work
3. **Deprecate, don't delete** - Mark columns as deprecated before removal
4. **Version migrations** - Use Alembic's sequential versioning
5. **Test migrations** - Always test on copy of production data first

---

## Related Documentation

- [Setup Guide](SETUP.md) - How to initialize the database
- [API Documentation](API.md) - How models map to API endpoints
- [Project Structure](PROJECT_STRUCTURE.md) - Where models are defined
