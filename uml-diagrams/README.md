# QuizzApp-RBMI UML Diagrams

This directory contains comprehensive UML diagrams for the QuizzApp-RBMI project, visualizing the system architecture, workflows, and database design.

## 📋 Diagram Index

### 1. Class Diagram (`1-class-diagram.puml`)
**Purpose:** Shows the complete database schema with all entities, attributes, relationships, and enumerations.

**Key Elements:**
- 7 main entities (User, Subject, QuestionBank, Quiz, Question, QuizAttempt, Answer)
- Enumerations (RoleEnum, QuestionTypeEnum, DifficultyLevel)
- Relationships and cardinalities
- Quiz timing and custom marking features

**Use When:** Understanding data model structure, planning database changes, or explaining system design.

---

### 2. Use Case Diagram (`2-use-case-diagram.puml`)
**Purpose:** Illustrates system functionality from user perspective, showing what each role (Admin, Teacher, Student) can do.

**Key Elements:**
- 31 use cases across 7 categories
- Actor-to-use-case relationships
- Include/extend relationships
- Permission boundaries by role

**Categories:**
- User Management
- Subject Management
- Question Bank
- Quiz Management
- Quiz Taking
- Analytics & Reports
- Authentication

**Use When:** Understanding user permissions, planning features, or training new users.

---

### 3. Authentication Sequence (`3-sequence-authentication.puml`)
**Purpose:** Details the login flow from credential submission to JWT token generation.

**Flow:**
1. User enters credentials
2. Frontend sends POST to `/api/v1/auth/login`
3. Backend validates email and password
4. Security service generates JWT token
5. Token returned and stored in localStorage

**Use When:** Debugging authentication issues, implementing security features, or onboarding developers.

---

### 4. Quiz Creation Sequence (`4-sequence-quiz-creation.puml`)
**Purpose:** Shows the complete workflow for creating a quiz with timing parameters and question bank integration.

**Flow:**
1. Teacher browses question bank with filters
2. Fills quiz details (timing, marking scheme)
3. Selects questions from bank or creates manually
4. Backend creates quiz with transaction
5. Questions linked to quiz

**Key Features:**
- Question bank filtering
- Timing configuration (scheduled start, duration, grace period)
- Custom marking scheme (+/- points)
- Database transaction handling

**Use When:** Understanding quiz creation process, debugging timing issues, or planning new quiz features.

---

### 5. Quiz Attempt Sequence (`5-sequence-quiz-attempt.puml`)
**Purpose:** Comprehensive workflow for students taking a quiz, from availability check to result calculation.

**Flow:**
1. Check quiz availability (timing validation)
2. Start quiz attempt (creates attempt record)
3. Answer questions (stored locally)
4. Submit quiz (timing validation + scoring)
5. Calculate score with custom marking
6. Display results

**Timing Validations:**
- Quiz available from `scheduled_start_time`
- Can start until `scheduled_start_time + grace_period_minutes`
- Must complete within `duration_minutes`
- Grace period doesn't extend duration

**Scoring Logic:**
- Score = (correct_count × marks_per_correct) + (incorrect_count × marks_per_incorrect)
- Percentage = (score / max_possible_score) × 100

**Use When:** Debugging quiz attempt issues, understanding timing enforcement, or explaining scoring logic.

---

### 6. Statistics Retrieval Sequence (`6-sequence-statistics.puml`)
**Purpose:** Shows how different statistics are calculated and retrieved for teachers and students.

**Statistics Types:**

**Dashboard Stats (Admin/Teacher):**
- Total users by role
- Total subjects, questions, quizzes
- Average quiz scores
- Recently active users

**Teacher Statistics:**
- Quizzes created per teacher
- Students reached
- Average student scores
- Last activity timestamp

**Student Statistics:**
- Total attempts and completion rate
- Average, best, and worst scores
- Subject-wise performance
- Time management analysis

**Use When:** Understanding analytics calculations, debugging statistics queries, or planning new metrics.

---

### 7. Component Diagram (`7-component-diagram.puml`)
**Purpose:** System architecture showing frontend, backend, and database layers with component interactions.

**Layers:**

**Frontend:**
- React Application (Vite dev server)
- Components (Auth, Dashboard, Quiz, BulkUpload)
- Context (AuthContext, ToastContext)
- API Service Layer (Axios)

**Backend:**
- FastAPI Application
- 7 API Routers (Auth, Users, Subjects, QuestionBank, Quizzes, Attempts, Stats)
- Core Services (Security, Quiz, Dependency Injection)
- Data Layer (SQLAlchemy ORM, Pydantic Schemas, Alembic)

**Database:**
- MySQL with 7 tables
- Managed by Alembic migrations

**Use When:** Understanding system architecture, planning integrations, or explaining technical stack.

---

### 8. Deployment Diagram (`8-deployment-diagram.puml`)
**Purpose:** Shows deployment architecture for both development and production environments.

**Development Setup:**
- Frontend: Vite Dev Server (Port 5173)
- Backend: Uvicorn ASGI (Port 8000)
- Database: Local MySQL (Port 3306)

**Production Setup:**
- Nginx Reverse Proxy (Ports 80/443)
- Gunicorn + Uvicorn Workers
- Static React Build
- Managed Cloud MySQL (AWS RDS / DigitalOcean)
- SSL with Let's Encrypt

**Security Layers:**
- CORS configuration
- JWT authentication (HS256)
- Bcrypt password hashing
- SQL injection prevention (ORM)
- Input validation (Pydantic)
- HTTPS in production

**Use When:** Planning deployments, configuring servers, or troubleshooting production issues.

---

### 9. Database ERD (`9-database-erd.puml`)
**Purpose:** Entity-Relationship Diagram showing detailed database schema with constraints and indexes.

**Tables:**
1. **users** - User accounts with roles
2. **subjects** - Academic subjects/departments
3. **question_bank** - Reusable question repository
4. **quizzes** - Quiz metadata with timing/marking
5. **questions** - Quiz-specific questions
6. **quiz_attempts** - Student attempt records
7. **answers** - Student responses

**Key Relationships:**
- User creates Subjects, QuestionBank, Quizzes
- Subject contains QuestionBank items and categorizes Quizzes
- QuestionBank sources Questions (optional)
- Quiz has Questions and is attempted by Students
- Attempt contains Answers

**Indexes:**
- users.email (unique)
- subjects.code (unique)
- Performance indexes on foreign keys

**Use When:** Database design review, planning migrations, optimizing queries, or explaining data structure.

---

## 🛠️ How to View Diagrams

### Option 1: VS Code Extension (Recommended)
1. Install **PlantUML** extension by jebbs
2. Install Java (required for PlantUML)
3. Open any `.puml` file
4. Press `Alt + D` to preview diagram

### Option 2: Online Viewer
1. Copy contents of `.puml` file
2. Visit [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
3. Paste code and view rendering

### Option 3: Command Line
```bash
# Install PlantUML
npm install -g node-plantuml

# Generate PNG from .puml file
puml generate 1-class-diagram.puml -o output/

# Generate all diagrams
puml generate *.puml -o output/
```

### Option 4: Export to Image
Using VS Code PlantUML extension:
1. Open `.puml` file
2. Right-click in editor
3. Select "PlantUML: Export Current Diagram"
4. Choose format (PNG, SVG, PDF)

---

## 📚 Diagram Usage Guide

### For Developers
- **New to Project:** Start with **Use Case Diagram** (2) → **Component Diagram** (7) → **Class Diagram** (1)
- **Understanding Features:** Check corresponding **Sequence Diagrams** (3-6)
- **Database Work:** Refer to **Database ERD** (9) and **Class Diagram** (1)
- **Deployment:** Review **Deployment Diagram** (8)

### For Project Managers
- **Feature Planning:** **Use Case Diagram** (2)
- **User Stories:** **Sequence Diagrams** (3-6)
- **System Overview:** **Component Diagram** (7)

### For Students/Learners
- **Quiz Flow:** **Quiz Attempt Sequence** (5)
- **Authentication:** **Authentication Sequence** (3)
- **Statistics:** **Statistics Sequence** (6)

### For DevOps/SysAdmins
- **Deployment Planning:** **Deployment Diagram** (8)
- **Database Setup:** **Database ERD** (9)
- **Architecture Review:** **Component Diagram** (7)

---

## 🎨 Diagram Conventions

### Color Coding
- **Entities/Classes:** Pink (`#FFAAAA`)
- **Components:** Green/Blue
- **Servers:** Light Blue (`#E3F2FD`)
- **Databases:** Orange (`#FFF3E0`)

### Notation
- **PK** (Red Bold): Primary Key
- **FK** (Blue): Foreign Key
- **Solid Lines:** Direct relationships/calls
- **Dotted Lines:** Include/extend relationships
- **Arrows:** Direction of dependency

### PlantUML Keywords
- `@startuml` / `@enduml`: Diagram boundaries
- `class`, `entity`: Define entities
- `participant`, `actor`: Sequence diagram elements
- `component`, `node`, `database`: Deployment elements
- `-->`, `..>`: Different relationship types

---

## 🔄 Updating Diagrams

When making changes to the system:

1. **Code Changes Require Diagram Updates:**
   - Added new table? → Update **Class Diagram** (1) and **ERD** (9)
   - New API endpoint? → Update **Component Diagram** (7) and relevant **Sequence Diagram**
   - Changed user permissions? → Update **Use Case Diagram** (2)
   - Modified deployment? → Update **Deployment Diagram** (8)

2. **Diagram Update Checklist:**
   - [ ] Verify syntax with PlantUML preview
   - [ ] Update related diagrams for consistency
   - [ ] Add notes for complex logic
   - [ ] Update this README if adding new diagrams

3. **Naming Convention:**
   - Format: `[number]-[diagram-type].puml`
   - Example: `10-new-feature-sequence.puml`

---

## 📖 Additional Resources

- **PlantUML Official Documentation:** https://plantuml.com/
- **UML Tutorial:** https://www.uml-diagrams.org/
- **PlantUML Cheat Sheet:** https://plantuml.com/guide
- **VS Code PlantUML Extension:** https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml

---

## 🤝 Contributing

When adding new diagrams:
1. Follow existing naming conventions
2. Add comprehensive notes explaining complex logic
3. Update this README with diagram description
4. Test rendering before committing
5. Keep diagrams focused (one responsibility per diagram)

---

## 📝 Notes

- All diagrams use **PlantUML** syntax for version control and text-based editing
- Diagrams are synchronized with codebase as of the latest update
- For large system changes, update multiple diagrams to maintain consistency
- Consider exporting diagrams to PNG/SVG for documentation that doesn't support PlantUML

---

**Last Updated:** 2024
**Maintained By:** QuizzApp-RBMI Development Team
