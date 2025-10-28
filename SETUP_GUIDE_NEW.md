# QuizzApp-RBMI Setup Guide

## New Architecture Implementation Guide

This guide will help you set up the newly implemented backend architecture with MySQL database, role-based access control, quiz timing, and statistics tracking.

## Prerequisites

### For Linux/macOS:
- Python 3.9 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### For Windows:
- Python 3.9 or higher ([Download](https://www.python.org/downloads/))
- MySQL 8.0 or higher ([Download](https://dev.mysql.com/downloads/installer/))
- Git Bash or PowerShell

## Step 1: Database Setup

### Install MySQL

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

**Windows:**
Download and install from [MySQL Downloads](https://dev.mysql.com/downloads/installer/)

### Create Database

```bash
# Login to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE quizapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'quizapp_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON quizapp_db.* TO 'quizapp_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Step 2: Backend Setup

### Clone Repository
```bash
cd ~/Projects
git clone <your-repository-url>
cd QuizzApp-RBMI/backend
```

### Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
```

If you get execution policy error on Windows:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note for Windows users:** If you encounter errors installing `pydantic-core`, you need to install Rust:
1. Visit [https://win.rustup.rs/](https://win.rustup.rs/)
2. Download and run `rustup-init.exe`
3. Follow the installation prompts
4. Restart your terminal
5. Run `pip install -r requirements.txt` again

### Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Update the following in `.env`:
```bash
DATABASE_URL=mysql+pymysql://quizapp_user:your_secure_password@localhost:3306/quizapp_db
SECRET_KEY=generate-a-strong-random-key-here
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=change-this-to-secure-password
```

To generate a secure SECRET_KEY:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Database Migration

### Initialize Alembic (if not already done)
```bash
# Check if alembic folder exists
ls alembic/

# If not, initialize it
alembic init alembic
```

### Configure Alembic

Edit `alembic/env.py` and update the `sqlalchemy.url` configuration:

```python
# Around line 20-25
from app.core.config import settings
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

# Around line 35
from app.models.models import Base
target_metadata = Base.metadata
```

### Create and Run Migration

```bash
# Create migration
alembic revision --autogenerate -m "Initial schema with new architecture"

# Apply migration
alembic upgrade head
```

## Step 4: Verify Setup

### Start Backend Server

```bash
# Make sure venv is activated
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
Admin user created: admin@yourdomain.com
```

### Test API

Open your browser and visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Root: http://localhost:8000/

### Test Admin Login

**Using Swagger UI (http://localhost:8000/docs):**
1. Expand `POST /api/v1/auth/login-json`
2. Click "Try it out"
3. Enter:
   ```json
   {
     "username": "admin@yourdomain.com",
     "password": "your-admin-password"
   }
   ```
4. Click "Execute"
5. You should get a response with `access_token`

**Using curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@yourdomain.com",
    "password": "your-admin-password"
  }'
```

## Step 5: Create Test Data

### Get Admin Token First

```bash
# Login and save token to variable (Linux/macOS)
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@macquiz.com","password":"admin123"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Verify token
echo "Token: $TOKEN"
```

**For Windows PowerShell:**
```powershell
$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/auth/login-json" -ContentType "application/json" -Body '{"username":"admin@macquiz.com","password":"admin123"}'
$TOKEN = $response.access_token
Write-Host "Token: $TOKEN"
```

### Create a Teacher

**Note: Endpoint requires trailing slash (`/`) and role must be uppercase**

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

**Expected Response:**
```json
{
  "id": 2,
  "email": "teacher1@university.edu",
  "first_name": "John",
  "last_name": "Doe",
  "role": "TEACHER",
  "phone_number": "+1234567890",
  "department": "Computer Science",
  "created_at": "2025-10-26T12:00:00"
}
```

### Create a Student

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student1@university.edu",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "STUDENT",
    "phone_number": "+1234567891",
    "student_id": "CS2021001",
    "department": "Computer Science",
    "class_year": "3rd Year",
    "password": "student123"
  }'
```

### Verify Users Created

```bash
# Get all users
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN"

# Get only teachers
curl -X GET "http://localhost:8000/api/v1/users/?role=TEACHER" \
  -H "Authorization: Bearer $TOKEN"

# Get only students
curl -X GET "http://localhost:8000/api/v1/users/?role=STUDENT" \
  -H "Authorization: Bearer $TOKEN"
```

### Create a Subject

Login as teacher or admin, then:

```bash
curl -X POST "http://localhost:8000/api/v1/subjects/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Structures and Algorithms",
    "code": "CS301",
    "description": "Introduction to data structures",
    "department": "Computer Science"
  }'
```

### Add Questions to Question Bank

```bash
curl -X POST "http://localhost:8000/api/v1/question-bank/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_id": 1,
    "question_text": "What is the time complexity of binary search?",
    "question_type": "SINGLE_CHOICE",
    "option_a": "O(n)",
    "option_b": "O(log n)",
    "option_c": "O(n^2)",
    "option_d": "O(1)",
    "correct_option": "B",
    "difficulty_level": "MEDIUM",
    "topic": "Searching Algorithms",
    "marks": 2
  }'
```

### Create a Quiz with Timing

```bash
curl -X POST "http://localhost:8000/api/v1/quizzes/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Midterm Exam - Data Structures",
    "description": "Covers arrays, linked lists, and trees",
    "subject_id": 1,
    "scheduled_start_time": "2025-10-30T10:00:00",
    "duration_minutes": 60,
    "grace_period_minutes": 10,
    "marks_per_correct": 4.0,
    "marks_per_incorrect": -1.0,
    "questions": [
      {
        "question_text": "What is a stack?",
        "question_type": "SINGLE_CHOICE",
        "option_a": "FIFO structure",
        "option_b": "LIFO structure",
        "option_c": "Random access",
        "option_d": "None of the above",
        "correct_option": "B",
        "marks": 4
      }
    ]
  }'
```

**Quiz Timing Explanation:**
- **scheduled_start_time**: When the quiz becomes available
- **duration_minutes**: How long students have to complete (60 minutes)
- **grace_period_minutes**: Extra time window to start the quiz (10 minutes)
- Students can start the quiz from `10:00 AM` to `10:10 AM` (grace period)
- Once started, they have 60 minutes to complete
- **marks_per_correct**: Points awarded for correct answers (+4)
- **marks_per_incorrect**: Points deducted for wrong answers (-1)

## Step 6: Test Quiz Workflow

### 1. Student Checks Quiz Availability
```bash
# Login as student first
STUDENT_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"student1@university.edu","password":"student123"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Check if quiz is available
curl -X GET "http://localhost:8000/api/v1/quizzes/1/availability" \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

**Expected Response:**
```json
{
  "is_available": true,
  "message": "Quiz is available",
  "can_start": true,
  "scheduled_start_time": "2025-10-30T10:00:00",
  "grace_period_end": "2025-10-30T10:10:00"
}
```

### 2. Student Starts Quiz
```bash
curl -X POST "http://localhost:8000/api/v1/attempts/start/1" \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

**Expected Response:**
```json
{
  "attempt_id": 1,
  "quiz_id": 1,
  "started_at": "2025-10-30T10:05:00",
  "must_submit_by": "2025-10-30T11:05:00",
  "questions": [...]
}
```

### 3. Student Submits Answers
```bash
curl -X POST "http://localhost:8000/api/v1/attempts/1/submit" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {
        "question_id": 1,
        "selected_option": "B"
      },
      {
        "question_id": 2,
        "selected_option": "B"
      }
    ]
  }'
```

**Expected Response:**
```json
{
  "attempt_id": 1,
  "score": 8.0,
  "percentage": 100.0,
  "total_questions": 2,
  "correct_answers": 2,
  "incorrect_answers": 0,
  "time_taken_minutes": 25,
  "submitted_at": "2025-10-30T10:30:00"
}
```

### 4. Admin Views Statistics

**Teacher Stats:**
```bash
curl -X GET "http://localhost:8000/api/v1/stats/teachers" \
  -H "Authorization: Bearer $TOKEN"
```

**Student Stats:**
```bash
curl -X GET "http://localhost:8000/api/v1/stats/student/3" \
  -H "Authorization: Bearer $TOKEN"
```

**Dashboard:**
```bash
curl -X GET "http://localhost:8000/api/v1/stats/dashboard" \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### MySQL Connection Error
```
Error: Can't connect to MySQL server
```
**Solution:**
- Check if MySQL is running: 
  - Linux: `sudo systemctl status mysql`
  - macOS: `brew services list`
  - Windows: Open Services Manager (`services.msc`) and check MySQL service
- Verify credentials in `.env`
- Check if port 3306 is not blocked: `sudo netstat -tlnp | grep 3306` (Linux)

### Database Role Case Sensitivity Issue
```
{"detail": "Not enough permissions"}
```
**Issue:** The database stores roles in uppercase (`ADMIN`, `TEACHER`, `STUDENT`) but backend code expects lowercase.

**Solution:**
Check your role in database:
```sql
mysql -u quizapp_admin -p quizapp_db
SELECT id, email, role FROM users WHERE email = 'admin@macquiz.com';
```

If role is uppercase, update `backend/app/models/models.py`:
```python
class RoleEnum(str, Enum):
    ADMIN = "ADMIN"      # Match database values
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
```

Then restart the server and get a fresh token.

### API Endpoint 307 Redirect Error
```
HTTP/1.1 307 Temporary Redirect
```
**Issue:** FastAPI endpoints require trailing slashes.

**Solution:** Add `/` at the end of endpoints:
- ❌ `/api/v1/users`
- ✅ `/api/v1/users/`

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### PyMySQL Not Found
```
ModuleNotFoundError: No module named 'pymysql'
```
**Solution:**
```bash
pip install pymysql cryptography
```

### Alembic Migration Errors
```
Target database is not up to date
```
**Solution:**
```bash
alembic stamp head  # Mark current state
alembic revision --autogenerate -m "Fix schema"
alembic upgrade head
```

### Permission Errors (Windows)
```
PermissionError: [WinError 5] Access is denied
```
**Solution:**
- Run terminal as Administrator
- Or use: `pip install --user -r requirements.txt`

### Token Expired Error
```
{"detail": "Could not validate credentials"}
```
**Solution:**
Tokens expire after 30 minutes (default). Login again to get a fresh token:
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@macquiz.com","password":"admin123"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
```

### Database Connection Check
```python
# Quick test script: test_db_connection.py
from app.db.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

Run: `python test_db_connection.py`

## Production Deployment Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Update `ADMIN_PASSWORD` to a secure password
- [ ] Use environment-specific `.env` files
- [ ] Set up proper MySQL user with limited privileges
- [ ] Enable MySQL SSL connections
- [ ] Configure CORS_ORIGINS to only include production domains
- [ ] Set up HTTPS/TLS for API
- [ ] Implement rate limiting
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)
- [ ] Set up reverse proxy (Nginx/Apache)

## Next Steps

1. Read [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) for detailed API documentation
2. Explore the interactive API docs at http://localhost:8000/docs
3. Set up the frontend (if applicable)
4. Customize roles and permissions as needed
5. Add more subjects and questions to the question bank

## Support

For issues and questions:
- Check the [README.md](../README.md)
- Review API documentation at `/docs`
- Check application logs
- Verify database connection and migrations

## Quick Reference Commands

```bash
# ========================================
# Environment Setup
# ========================================

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Start server
uvicorn app.main:app --reload

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Reset database (CAUTION: Deletes all data!)
alembic downgrade base
alembic upgrade head

# ========================================
# Authentication & Token Management
# ========================================

# Get admin token (Linux/macOS)
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@macquiz.com","password":"admin123"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Verify token
echo "Token: $TOKEN"

# Get student token
STUDENT_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"student1@university.edu","password":"student123"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# ========================================
# MySQL Database Commands
# ========================================

# Check MySQL status
sudo systemctl status mysql           # Linux
brew services list | grep mysql       # macOS
Get-Service -Name MySQL80             # Windows PowerShell

# Login to MySQL
mysql -u quizapp_admin -p quizapp_db

# Useful MySQL queries
SELECT id, email, role FROM users;
SELECT * FROM quizzes;
SELECT * FROM quiz_attempts WHERE student_id = 3;
SHOW TABLES;
DESCRIBE users;

# ========================================
# API Endpoint Quick Reference
# ========================================

# Create user (note trailing slash!)
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'

# Get all users
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN"

# Filter users by role
curl -X GET "http://localhost:8000/api/v1/users/?role=TEACHER" \
  -H "Authorization: Bearer $TOKEN"

# Create subject
curl -X POST "http://localhost:8000/api/v1/subjects/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'

# Create quiz
curl -X POST "http://localhost:8000/api/v1/quizzes/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'

# Check quiz availability
curl -X GET "http://localhost:8000/api/v1/quizzes/1/availability" \
  -H "Authorization: Bearer $STUDENT_TOKEN"

# Start quiz attempt
curl -X POST "http://localhost:8000/api/v1/attempts/start/1" \
  -H "Authorization: Bearer $STUDENT_TOKEN"

# Submit quiz
curl -X POST "http://localhost:8000/api/v1/attempts/1/submit" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'

# Get statistics
curl -X GET "http://localhost:8000/api/v1/stats/dashboard" \
  -H "Authorization: Bearer $TOKEN"

# ========================================
# Troubleshooting Commands
# ========================================

# Check Python version
python --version

# Check pip packages
pip list | grep fastapi
pip list | grep sqlalchemy

# Test database connection
python -c "from app.db.database import engine; print(engine.connect())"

# Check if port 8000 is in use
lsof -i :8000          # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Check MySQL connection
mysql -u quizapp_admin -p -h localhost -P 3306 quizapp_db

# View backend logs (if running in background)
tail -f backend.log

# Generate new SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

