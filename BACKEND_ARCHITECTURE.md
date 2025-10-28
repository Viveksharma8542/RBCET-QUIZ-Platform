# Backend Architecture Documentation

## Overview
This document describes the complete backend architecture for the QuizzApp-RBMI system with role-based access control, quiz timing management, and comprehensive statistics tracking.

## Database Schema

### Users Table
Stores all users (Admin, Teachers, Students) with role-based fields.

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL,
    phone_number VARCHAR(20),
    student_id VARCHAR(50) UNIQUE,
    department VARCHAR(100),
    class_year VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_student_id (student_id),
    INDEX idx_role (role)
);
```

### Subjects Table
Stores academic subjects for organizing quizzes and question banks.

```sql
CREATE TABLE subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) UNIQUE NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    department VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_name (name)
);
```

### Quizzes Table
Stores quizzes created by teachers with timing and marking configurations.

```sql
CREATE TABLE quizzes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    creator_id INT NOT NULL,
    subject_id INT,
    department VARCHAR(100),
    class_year VARCHAR(20),
    scheduled_start_time DATETIME,
    duration_minutes INT NOT NULL DEFAULT 30,
    grace_period_minutes INT NOT NULL DEFAULT 5,
    marks_per_correct FLOAT DEFAULT 1.0,
    marks_per_incorrect FLOAT DEFAULT 0.0,
    total_marks FLOAT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
    INDEX idx_creator (creator_id),
    INDEX idx_subject (subject_id),
    INDEX idx_active (is_active)
);
```

### Questions Table
Stores questions for specific quizzes.

```sql
CREATE TABLE questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quiz_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    option_a VARCHAR(500),
    option_b VARCHAR(500),
    option_c VARCHAR(500),
    option_d VARCHAR(500),
    correct_answer VARCHAR(500) NOT NULL,
    marks FLOAT DEFAULT 1.0,
    `order` INT DEFAULT 0,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
    INDEX idx_quiz (quiz_id)
);
```

### Question Bank Table
Stores reusable questions organized by subject.

```sql
CREATE TABLE question_bank (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    option_a VARCHAR(500),
    option_b VARCHAR(500),
    option_c VARCHAR(500),
    option_d VARCHAR(500),
    correct_answer VARCHAR(500) NOT NULL,
    difficulty_level VARCHAR(20),
    topic VARCHAR(200),
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_subject (subject_id),
    INDEX idx_difficulty (difficulty_level),
    INDEX idx_creator (created_by)
);
```

### Quiz Attempts Table
Stores student attempts at quizzes with completion tracking.

```sql
CREATE TABLE quiz_attempts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quiz_id INT NOT NULL,
    student_id INT NOT NULL,
    score FLOAT,
    total_marks FLOAT NOT NULL,
    percentage FLOAT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    submitted_at DATETIME,
    is_completed BOOLEAN DEFAULT FALSE,
    time_taken_minutes INT,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_quiz (quiz_id),
    INDEX idx_student (student_id),
    INDEX idx_completed (is_completed)
);
```

### Answers Table
Stores individual answers for each quiz attempt.

```sql
CREATE TABLE answers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    attempt_id INT NOT NULL,
    question_id INT NOT NULL,
    answer_text TEXT,
    is_correct BOOLEAN,
    marks_awarded FLOAT DEFAULT 0,
    FOREIGN KEY (attempt_id) REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_attempt (attempt_id)
);
```

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /login` - Login with form data (returns JWT token)
- `POST /login-json` - Login with JSON data (returns JWT token)

### Users (`/api/v1/users`)
- `POST /` - Create new user (Admin only)
- `POST /bulk` - Bulk create users from CSV (Admin only)
- `GET /` - Get all users with filters (Admin only)
- `GET /{user_id}` - Get specific user
- `PUT /{user_id}` - Update user (Admin or self)
- `DELETE /{user_id}` - Delete user (Admin only)
- `GET /me` - Get current user profile

### Subjects (`/api/v1/subjects`)
- `POST /` - Create subject (Admin/Teacher)
- `GET /` - Get all subjects
- `GET /{subject_id}` - Get specific subject
- `PUT /{subject_id}` - Update subject (Admin)
- `DELETE /{subject_id}` - Delete subject (Admin)

### Question Bank (`/api/v1/question-bank`)
- `POST /` - Add question to bank (Teacher/Admin)
- `GET /` - Get questions with filters (subject_id, difficulty, topic)
- `GET /{question_id}` - Get specific question
- `PUT /{question_id}` - Update question (Creator/Admin)
- `DELETE /{question_id}` - Delete question (Creator/Admin)
- `GET /subjects/{subject_id}/stats` - Get question bank statistics for a subject

### Quizzes (`/api/v1/quizzes`)
- `POST /` - Create quiz (Teacher only)
- `GET /` - Get all quizzes (filtered by role)
- `GET /{quiz_id}` - Get quiz details
- `PUT /{quiz_id}` - Update quiz (Creator only)
- `DELETE /{quiz_id}` - Delete quiz (Creator only)
- `GET /{quiz_id}/availability` - Check if quiz is available to start

### Quiz Attempts (`/api/v1/attempts`)
- `POST /start` - Start a quiz attempt
- `POST /submit` - Submit quiz answers
- `GET /quiz/{quiz_id}` - Get all attempts for a quiz (Teacher/Admin)
- `GET /student/{student_id}` - Get student's attempts
- `GET /{attempt_id}` - Get specific attempt details

### Statistics (`/api/v1/stats`)
- `GET /dashboard` - Overall dashboard stats (Admin)
- `GET /teachers` - All teacher statistics (Admin)
- `GET /teachers/{teacher_id}` - Specific teacher stats
- `GET /students` - All student statistics (Admin/Teacher)
- `GET /students/{student_id}` - Specific student stats

## Role-Based Access Control

### Admin
- Create/manage all users (teachers and students)
- View all statistics (teachers, students, dashboard)
- Manage subjects
- View/manage all quizzes and question banks
- Full system access

### Teacher
- Create and manage their own quizzes
- Add questions to question bank
- View question bank for quiz creation
- Set custom marking schemes (+/- for correct/incorrect)
- Add questions manually or from question bank
- View statistics for their quizzes
- View student performance on their quizzes
- Cannot create users

### Student
- Take quizzes assigned to their department/class
- View their own statistics and quiz history
- Cannot create quizzes or access question bank
- Cannot view other student's data

## Quiz Timing Logic

### Time-Based Quiz Access
1. **No Scheduled Start Time**: Quiz available anytime
2. **With Scheduled Start Time**:
   - Quiz becomes available at `scheduled_start_time`
   - Students can start within `grace_period_minutes` after start time
   - Example: Start 12:00 PM, Grace 5 mins, Duration 30 mins
     - Can start: 12:00 PM - 12:05 PM
     - Cannot start after: 12:05 PM
     - Must complete by: (start_time + duration)

### Implementation
```python
# Quiz timing check (in quiz_service.py)
def check_quiz_availability(quiz, student_id, existing_attempt):
    # Returns QuizAvailability with:
    # - is_available: bool
    # - can_start: bool
    # - message: str
    # - scheduled_start: datetime
    # - grace_period_end: datetime
    # - quiz_end: datetime
```

## Marking Scheme

### Custom Marking per Quiz
- `marks_per_correct`: Points awarded for correct answer (default: 1.0)
- `marks_per_incorrect`: Points deducted for wrong answer (default: 0.0)
- Enables negative marking when needed

### Score Calculation
```python
score = (correct_answers * marks_per_correct) - (incorrect_answers * marks_per_incorrect)
percentage = (score / max_possible_score) * 100
```

## Teacher Statistics

For each teacher, the system tracks:
- `total_quizzes_created`: Number of quizzes created
- `total_questions_created`: Total questions across all quizzes
- `total_students_attempted`: Unique students who took their quizzes
- `average_quiz_score`: Average percentage across all quiz attempts
- `last_quiz_created`: Date of most recent quiz

## Student Statistics

For each student, the system tracks:
- `total_quizzes_attempted`: Number of quiz attempts started
- `total_quizzes_completed`: Number of quiz attempts finished
- `average_score`: Average score across completed quizzes
- `average_percentage`: Average percentage across completed quizzes
- `highest_score`: Best score achieved
- `lowest_score`: Lowest score achieved
- `last_quiz_attempted`: Date of most recent attempt

## Question Bank Features

- Organized by subject
- Reusable across multiple quizzes
- Supports difficulty levels (easy, medium, hard)
- Topic-based organization
- Teachers can add their own questions
- Questions can be pulled into quizzes during creation

## Setup Instructions

### 1. Database Setup (MySQL)
```sql
CREATE DATABASE quizapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'quizapp_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON quizapp_db.* TO 'quizapp_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Environment Configuration
Update `.env` file:
```bash
DATABASE_URL=mysql+pymysql://quizapp_user:your_password@localhost:3306/quizapp_db
SECRET_KEY=your-secret-key-change-in-production
ADMIN_EMAIL=admin@macquiz.com
ADMIN_PASSWORD=admin123
```

### 3. Install Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
# Initialize Alembic (if not done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema with new architecture"

# Apply migration
alembic upgrade head
```

### 5. Start Server
```bash
uvicorn app.main:app --reload
```

## API Usage Examples

### Create a Subject
```bash
curl -X POST "http://localhost:8000/api/v1/subjects" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Structures",
    "code": "CS201",
    "description": "Introduction to Data Structures",
    "department": "Computer Science"
  }'
```

### Create a Quiz with Timing
```bash
curl -X POST "http://localhost:8000/api/v1/quizzes" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Data Structures Midterm",
    "subject_id": 1,
    "scheduled_start_time": "2025-10-25T12:00:00",
    "duration_minutes": 30,
    "grace_period_minutes": 5,
    "marks_per_correct": 2.0,
    "marks_per_incorrect": 0.5,
    "questions": [
      {
        "question_text": "What is a stack?",
        "question_type": "mcq",
        "option_a": "FIFO",
        "option_b": "LIFO",
        "option_c": "Random",
        "option_d": "None",
        "correct_answer": "LIFO",
        "marks": 2.0,
        "order": 1
      }
    ]
  }'
```

### Get Teacher Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/stats/teachers/2" \
  -H "Authorization: Bearer <token>"
```

### Get Student Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/stats/students/5" \
  -H "Authorization: Bearer <token>"
```

## Migration from SQLite to MySQL

1. Export existing data (if any)
2. Update DATABASE_URL in `.env`
3. Run new migrations
4. Import data (if applicable)

## Security Considerations

- JWT tokens expire after 30 minutes (configurable)
- Passwords hashed using bcrypt
- Role-based access control on all endpoints
- SQL injection prevention through SQLAlchemy ORM
- CORS configured for allowed origins only

## Performance Optimizations

- Database indexes on frequently queried fields
- Efficient joins for statistics calculations
- Pagination on list endpoints
- Connection pooling via SQLAlchemy

## Testing

Access interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
