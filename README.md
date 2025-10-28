"# 🎓 MacQuiz - Quiz Application with Role-Based Management

> A modern, full-stack quiz platform designed for educational institutions with comprehensive role-based access control, question bank management, and advanced analytics.
---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Environment Setup](#-environment-setup)
- [Development](#-development)
- [Production Deployment](#-production-deployment)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🔐 Role-Based Access Control
- **Admin**: Complete system management, user creation, analytics dashboard
- **Teacher**: Subject management, question bank, quiz creation with custom scoring
- **Student**: Quiz participation, performance tracking, detailed statistics

### 📚 Question Bank System
- Reusable question repository organized by subjects
- Difficulty levels: Easy, Medium, Hard
- Topic-based organization
- Mix manual and question bank questions in quizzes

### ⏱️ Smart Quiz Management
- **Time-based scheduling**: Set start times with grace periods
- **Custom marking schemes**: Configure positive/negative marking per quiz
- **Multiple question types**: MCQ, True/False, Short Answer
- **Auto-grading**: Instant results with custom scoring logic
- **Department & class filtering**: Targeted quiz assignment

### 📊 Comprehensive Analytics
- **Dashboard Statistics**: System-wide metrics and activity feed
- **Teacher Analytics**: Quiz creation stats, student reach, performance metrics
- **Student Analytics**: Attempt history, score trends, completion rates
- **Real-time Insights**: Performance tracking and detailed reports

### 🚀 Advanced Features
- **Bulk User Import**: Upload users via CSV/Excel files
- **Subject Management**: Organize quizzes and questions by academic subjects
- **Activity Tracking**: Monitor teacher and student engagement
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.115.0 | Modern Python web framework |
| **SQLAlchemy** | 2.0.36 | SQL toolkit and ORM |
| **MySQL** | 8.0+ | Production database |
| **PyMySQL** | 1.1.0 | MySQL driver for Python |
| **Alembic** | 1.14.0 | Database migration tool |
| **Pydantic** | 2.9.2 | Data validation |
| **JWT** | - | Token-based authentication |
| **Bcrypt** | 4.2.1 | Password hashing |
| **Uvicorn** | 0.32.0 | ASGI server |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.1.1 | UI library |
| **Vite** | 7.1.7 | Build tool and dev server |
| **React Router** | 7.9.4 | Client-side routing |
| **Tailwind CSS** | 4.1.14 | Utility-first CSS framework |
| **Lucide React** | 0.546.0 | Icon library |

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.9 or higher
- **Node.js** 16 or higher
- **MySQL** 8.0 or higher
- **Git** (for cloning the repository)

### Installation

#### 🐧 Linux / 🍎 macOS

1. **Clone the repository**
```bash
git clone https://github.com/SVIGHNESH/MacQuiz.git
cd MacQuiz
```

2. **Set up MySQL database**
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

3. **Configure environment variables**
```bash
# Create .env file in backend directory
cd backend
cat > .env << EOF
DATABASE_URL=mysql+pymysql://quizapp_user:your_secure_password@localhost:3306/quizapp_db
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ADMIN_EMAIL=admin@macquiz.com
ADMIN_PASSWORD=admin123
EOF
cd ..
```

4. **Start both servers**
```bash
chmod +x start.sh
./start.sh
```

#### 🪟 Windows

1. **Clone the repository**
```cmd
git clone https://github.com/SVIGHNESH/MacQuiz.git
cd MacQuiz
```

2. **Set up MySQL database**
```cmd
REM Login to MySQL
mysql -u root -p

 Create database and user
CREATE DATABASE quizapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'quizapp_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON quizapp_db.* TO 'quizapp_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

3. **Configure environment variables**
```cmd
 Create .env file in backend directory
cd backend
copy con .env
DATABASE_URL=mysql+pymysql://quizapp_user:your_secure_password@localhost:3306/quizapp_db
SECRET_KEY=your-generated-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ADMIN_EMAIL=admin@macquiz.com
ADMIN_PASSWORD=admin123

cd ..
```

4. **Start both servers**
```cmd
start.bat
```

### 🎯 Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 🔑 Default Credentials

```
Email: admin@macquiz.com
Password: admin123
```

> ⚠️ **Security Warning**: Change these credentials immediately in production!

---

## 📁 Project Structure

```
MacQuiz/
├── 📄 start.sh                    # Linux/macOS startup script
├── 📄 start.bat                   # Windows startup script
├── 📄 stop.sh                     # Shutdown script
├── 📄 stop.bat                    # Windows shutdown script
├── 📄 README.md                   # This file
├── 📄 PROJECT_SUMMARY.md          # Detailed project overview
├── 📄 SETUP_GUIDE_NEW.md          # Comprehensive setup guide
├── 📄 QUICKSTART.md               # 5-minute quick start
│
├── 📂 backend/                    # FastAPI Backend
│   ├── 📄 requirements.txt        # Python dependencies
│   ├── 📄 run.sh                  # Backend startup script
│   ├── 📄 .env                    # Environment variables
│   ├── 📄 README.md               # Backend documentation
│   ├── 📄 API_EXAMPLES.md         # API usage examples
│   │
│   └── 📂 app/
│       ├── 📄 main.py             # FastAPI application entry
│       │
│       ├── 📂 api/v1/             # API Endpoints (v1)
│       │   ├── 📄 auth.py         # Authentication & login
│       │   ├── 📄 users.py        # User CRUD operations
│       │   ├── 📄 subjects.py     # Subject management
│       │   ├── 📄 question_bank.py # Question bank system
│       │   ├── 📄 quizzes.py      # Quiz management
│       │   ├── 📄 attempts.py     # Quiz attempts & grading
│       │   └── 📄 stats.py        # Analytics & statistics
│       │
│       ├── 📂 core/               # Core Functionality
│       │   ├── 📄 config.py       # Configuration settings
│       │   ├── 📄 security.py     # Security utilities
│       │   └── 📄 deps.py         # Dependencies & auth
│       │
│       ├── 📂 models/             # Database Models
│       │   └── 📄 models.py       # SQLAlchemy models
│       │
│       ├── 📂 schemas/            # Request/Response Schemas
│       │   └── 📄 schemas.py      # Pydantic schemas
│       │
│       ├── 📂 services/           # Business Logic
│       │   └── 📄 quiz_service.py # Quiz timing & scoring
│       │
│       └── 📂 db/                 # Database Configuration
│           └── 📄 database.py     # Database setup & session
│
├── 📂 frontend/                   # React Frontend
│   ├── 📄 package.json            # Node dependencies
│   ├── 📄 vite.config.js          # Vite configuration
│   ├── 📄 tailwind.config.js      # Tailwind CSS config
│   ├── 📄 index.html              # HTML entry point
│   │
│   └── 📂 src/
│       ├── 📄 main.jsx            # React entry point
│       ├── 📄 App.jsx             # Main App component
│       ├── 📄 index.css           # Global styles
│       │
│       ├── 📂 pages/              # Page Components
│       │   ├── 📄 login.jsx       # Login page
│       │   ├── 📄 dashBoard.jsx   # Admin/Teacher dashboard
│       │   └── 📄 studentDashboard.jsx # Student dashboard
│       │
│       ├── 📂 components/         # Reusable Components
│       │   ├── 📄 ProtectedRoute.jsx # Auth protection
│       │   ├── 📄 BulkUploadModal.jsx # Bulk user upload
│       │   └── 📄 footer.jsx      # Footer component
│       │
│       ├── 📂 context/            # React Context
│       │   ├── 📄 AuthContext.jsx # Authentication state
│       │   └── 📄 ToastContext.jsx # Toast notifications
│       │
│       └── 📂 services/           # API Services
│           └── 📄 api.js          # API client
│
└── 📂 uml-diagrams/               # UML Documentation
    ├── 📄 1-class-diagram.puml
    ├── 📄 2-use-case-diagram.puml
    ├── 📄 3-sequence-authentication.puml
    ├── 📄 4-sequence-quiz-creation.puml
    ├── 📄 5-sequence-quiz-attempt.puml
    ├── 📄 6-sequence-statistics.puml
    ├── 📄 7-component-diagram.puml
    ├── 📄 8-deployment-diagram.puml
    ├── 📄 9-database-erd.puml
    └── 📄 README.md
```

---

## 📡 API Documentation

### Authentication
```
POST   /api/v1/auth/login          # OAuth2 form login
POST   /api/v1/auth/login-json     # JSON login
```

### User Management (Admin Only)
```
POST   /api/v1/users/              # Create user
GET    /api/v1/users/              # List all users
GET    /api/v1/users/me            # Get current user
GET    /api/v1/users/{id}          # Get user by ID
PUT    /api/v1/users/{id}          # Update user
DELETE /api/v1/users/{id}          # Delete user
POST   /api/v1/users/bulk-create   # Bulk user import
```

### Subject Management
```
POST   /api/v1/subjects/           # Create subject (Teacher/Admin)
GET    /api/v1/subjects/           # List all subjects
GET    /api/v1/subjects/{id}       # Get subject details
PUT    /api/v1/subjects/{id}       # Update subject (Admin)
DELETE /api/v1/subjects/{id}       # Delete subject (Admin)
```

### Question Bank
```
POST   /api/v1/question-bank/      # Add question (Teacher/Admin)
GET    /api/v1/question-bank/      # List questions with filters
GET    /api/v1/question-bank/{id}  # Get question details
PUT    /api/v1/question-bank/{id}  # Update question (Creator/Admin)
DELETE /api/v1/question-bank/{id}  # Delete question (Creator/Admin)
```

### Quiz Management
```
POST   /api/v1/quizzes/            # Create quiz (Teacher/Admin)
GET    /api/v1/quizzes/            # List quizzes (role-filtered)
GET    /api/v1/quizzes/{id}        # Get quiz details
GET    /api/v1/quizzes/{id}/availability # Check quiz timing
PUT    /api/v1/quizzes/{id}        # Update quiz (Teacher/Admin)
DELETE /api/v1/quizzes/{id}        # Delete quiz (Teacher/Admin)
```

### Quiz Attempts
```
POST   /api/v1/attempts/start      # Start quiz attempt
POST   /api/v1/attempts/submit     # Submit answers
GET    /api/v1/attempts/my-attempts # Get user's attempts
GET    /api/v1/attempts/quiz/{id}  # Get quiz attempts (Teacher/Admin)
GET    /api/v1/attempts/{id}       # Get attempt details
```

### Statistics & Analytics
```
GET    /api/v1/stats/dashboard     # Dashboard stats (Admin)
GET    /api/v1/stats/teachers      # All teacher statistics
GET    /api/v1/stats/teachers/{id} # Specific teacher stats
GET    /api/v1/stats/students      # All student statistics
GET    /api/v1/stats/students/{id} # Specific student stats
```

**Total: 40+ API endpoints**

📖 **Detailed API Examples**: See [backend/API_EXAMPLES.md](backend/API_EXAMPLES.md)

---

## 🗄️ Database Schema

### Core Tables

#### 👥 Users
- Authentication (email, hashed_password)
- Profile (first_name, last_name, phone_number)
- Role (ADMIN/TEACHER/STUDENT - Enum)
- Student fields (student_id, department, class_year)
- Activity tracking (created_at, last_active)

#### 📚 Subjects
- Subject information (name, code, description)
- Department organization
- Links to quizzes and question bank

#### 💡 Question Bank
- Reusable questions by subject
- Question types (MCQ, True/False, Short Answer)
- Difficulty levels (easy/medium/hard)
- Topic organization
- Creator tracking

#### 📝 Quizzes
- Quiz metadata (title, description)
- Subject linking
- **Timing configuration:**
  - scheduled_start_time
  - duration_minutes
  - grace_period_minutes
- **Custom marking scheme:**
  - marks_per_correct
  - marks_per_incorrect
- Filtering (department, class_year)

#### ❓ Questions
- Question content and type
- MCQ options (option_a, option_b, option_c, option_d)
- Correct answer and marks
- Question order

#### 📊 Quiz Attempts
- Student-quiz relationship
- Results (score, percentage)
- Timing (started_at, submitted_at)
- Completion status

#### ✅ Answers
- Student responses
- Evaluation (is_correct, marks_awarded)

**Database Diagram**: See [uml-diagrams/9-database-erd.puml](uml-diagrams/9-database-erd.puml)

---

## ⚙️ Environment Setup

### Backend Environment Variables (.env)

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://quizapp_user:password@localhost:3306/quizapp_db

# Security
SECRET_KEY=your-secret-key-here-use-secrets-token-urlsafe-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Default Admin Credentials
ADMIN_EMAIL=admin@macquiz.com
ADMIN_PASSWORD=admin123
```

**Generate Secure SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Frontend Environment Variables (.env)

```env
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Development

### Backend Development

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests (when implemented)
pytest tests/
```

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```

---

## 🚢 Production Deployment

### Backend Deployment Checklist

- [ ] Generate strong `SECRET_KEY`
- [ ] Change default admin credentials
- [ ] Set up production MySQL database
- [ ] Configure environment variables
- [ ] Run database migrations
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS for production domain
- [ ] Enable logging and monitoring
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Use production ASGI server (Gunicorn + Uvicorn)

### Frontend Deployment Checklist

- [ ] Update `VITE_API_URL` to production backend
- [ ] Build for production: `npm run build`
- [ ] Configure CDN for static assets
- [ ] Enable HTTPS/SSL
- [ ] Set up caching headers
- [ ] Configure error tracking (Sentry, etc.)

### Recommended Platforms

**Backend:**
- AWS EC2 + RDS (MySQL)
- Google Cloud Platform + Cloud SQL
- DigitalOcean Droplets + Managed MySQL
- Railway / Render / Fly.io

**Frontend:**
- Vercel (recommended)
- Netlify
- AWS Amplify
- Cloudflare Pages

**Database:**
- AWS RDS for MySQL
- Google Cloud SQL
- DigitalOcean Managed Databases
- PlanetScale

---

## 📚 Documentation

### Core Documentation
- **[README.md](README.md)** - This file (project overview)
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Detailed project summary
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start guide
- **[SETUP_GUIDE_NEW.md](SETUP_GUIDE_NEW.md)** - Comprehensive setup guide

### Backend Documentation
- **[backend/README.md](backend/README.md)** - Backend architecture
- **[backend/API_EXAMPLES.md](backend/API_EXAMPLES.md)** - API usage examples
- **[backend/ROLE_UPDATE_SUMMARY.md](backend/ROLE_UPDATE_SUMMARY.md)** - Role implementation

### Feature Guides
- **[BULK_UPLOAD_GUIDE.md](BULK_UPLOAD_GUIDE.md)** - Bulk user import guide
- **[BULK_UPLOAD_VISUAL_GUIDE.md](BULK_UPLOAD_VISUAL_GUIDE.md)** - Visual guide

### UML Diagrams
### UML Diagrams
- **[uml-diagrams/README.md](uml-diagrams/README.md)** - UML documentation
- Class Diagram, Use Case, Sequence Diagrams, ERD, etc.