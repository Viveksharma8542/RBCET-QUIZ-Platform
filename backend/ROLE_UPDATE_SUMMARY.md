# Role Enum Update Summary

## Changes Made

All role handling has been updated to use **UPPERCASE** enum values to match the MySQL database schema.

### 1. Updated Files

#### ✅ `app/schemas/schemas.py`
```python
class RoleEnum(str, Enum):
    ADMIN = "ADMIN"      # Changed from "admin"
    TEACHER = "TEACHER"  # Changed from "teacher"
    STUDENT = "STUDENT"  # Changed from "student"
```

#### ✅ `app/api/v1/users.py`
- Updated all `require_role()` calls to use `RoleEnum.ADMIN` instead of `"admin"`
- Updated role comparisons to use `RoleEnum.TEACHER` and `RoleEnum.STUDENT`
- Updated bulk upload to validate and convert roles to uppercase
- Updated get_all_users to handle uppercase role filtering

#### ✅ `app/models/models.py`
- Already using uppercase: `RoleEnum.ADMIN`, `RoleEnum.TEACHER`, `RoleEnum.STUDENT`

#### ✅ `app/main.py`
- Already using uppercase: `RoleEnum.ADMIN` for admin user creation

### 2. API Usage Changes

All API requests must now use **UPPERCASE** role values:

#### ❌ OLD (Lowercase - No longer works):
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -d '{"role": "teacher", ...}'
```

#### ✅ NEW (Uppercase - Required):
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -d '{"role": "TEACHER", ...}'
```

### 3. Valid Role Values

- `"ADMIN"` - Administrator with full access
- `"TEACHER"` - Teacher who can create quizzes and questions
- `"STUDENT"` - Student who can take quizzes

### 4. Query Parameter Changes

#### Get users by role:
```bash
# ❌ OLD
GET /api/v1/users/?role=teacher

# ✅ NEW (accepts both, converts to uppercase internally)
GET /api/v1/users/?role=TEACHER
GET /api/v1/users/?role=teacher  # Also works, auto-converted
```

### 5. Database Schema

The MySQL database uses ENUM type with uppercase values:
```sql
`role` ENUM('ADMIN', 'TEACHER', 'STUDENT')
```

### 6. Bulk Upload CSV Format

CSV files for bulk user upload must use uppercase roles:

```csv
role,first_name,last_name,email,password,student_id,department,class_year
TEACHER,John,Doe,john@example.com,pass123,,Computer Science,
STUDENT,Jane,Smith,jane@example.com,pass456,CS001,Computer Science,3rd Year
```

## Migration Steps

### 1. Stop the Backend Server
```bash
# Press Ctrl+C in the terminal running uvicorn
```

### 2. No Database Migration Needed
The database already uses uppercase ENUM values, so no migration is required.

### 3. Restart the Backend Server
```bash
uvicorn app.main:app --reload
```

### 4. Get Fresh Authentication Token
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@macquiz.com","password":"admin123"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
```

### 5. Test User Creation
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher1@university.edu",
    "first_name": "John",
    "last_name": "Doe",
    "role": "TEACHER",
    "phone_number": "+1234567890",
    "department": "Computer Science",
    "password": "teacher123"
  }'
```

## Verification

### Check Existing Users
```bash
# Get all users
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN"

# Filter by role
curl -X GET "http://localhost:8000/api/v1/users/?role=TEACHER" \
  -H "Authorization: Bearer $TOKEN"
```

### Expected Response
```json
{
  "id": 2,
  "email": "teacher1@university.edu",
  "first_name": "John",
  "last_name": "Doe",
  "role": "TEACHER",  // ← Uppercase
  "department": "Computer Science",
  ...
}
```

## Troubleshooting

### Issue: "Not enough permissions"
**Solution:** Get a fresh token after restarting the server.

### Issue: "Invalid role" validation error
**Solution:** Ensure role is uppercase: `"ADMIN"`, `"TEACHER"`, or `"STUDENT"`.

### Issue: 422 Validation Error
**Cause:** Using lowercase role values.
**Solution:** Change to uppercase in your request.

## Summary

✅ **Backend code updated** - All role handling uses uppercase enums  
✅ **Database schema** - Already using uppercase ENUM values  
✅ **API endpoints** - All accept and return uppercase roles  
✅ **Setup guide** - Updated with uppercase role examples  
✅ **Bulk upload** - Validates and requires uppercase roles  

**Important:** All new API requests must use uppercase role values (`"ADMIN"`, `"TEACHER"`, `"STUDENT"`).
