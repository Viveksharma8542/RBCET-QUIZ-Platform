from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.models import User, Quiz, Question, QuestionBank, RoleEnum, QuizAttempt
from app.schemas.schemas import QuizCreate, QuizResponse, QuizDetailResponse, QuizUpdate, QuizAvailability
from app.core.deps import get_current_active_user, require_role
from app.services.quiz_service import check_quiz_availability

router = APIRouter()

@router.post("/", response_model=QuizResponse, dependencies=[Depends(require_role([RoleEnum.ADMIN, RoleEnum.TEACHER]))])
async def create_quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new quiz with custom marking scheme and questions from manual input or question bank.
    Only teachers and admins can create quizzes.
    """
    # Validate that user is teacher or admin
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can create quizzes"
        )
    
    # Calculate total marks from manual questions
    total_marks = sum(q.marks for q in quiz_data.questions)
    
    # Add marks from question bank questions
    total_marks += len(quiz_data.questions_from_bank) * quiz_data.marks_per_correct
    
    # Create quiz
    db_quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        creator_id=current_user.id,
        subject_id=quiz_data.subject_id,
        department=quiz_data.department,
        class_year=quiz_data.class_year,
        scheduled_start_time=quiz_data.scheduled_start_time,
        duration_minutes=quiz_data.duration_minutes,
        grace_period_minutes=quiz_data.grace_period_minutes,
        marks_per_correct=quiz_data.marks_per_correct,
        marks_per_incorrect=quiz_data.marks_per_incorrect,
        total_marks=total_marks
    )
    
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    # Create questions from manual input
    for question_data in quiz_data.questions:
        db_question = Question(
            quiz_id=db_quiz.id,
            question_bank_id=question_data.question_bank_id,
            question_text=question_data.question_text,
            question_type=question_data.question_type,
            option_a=question_data.option_a,
            option_b=question_data.option_b,
            option_c=question_data.option_c,
            option_d=question_data.option_d,
            correct_answer=question_data.correct_answer,
            marks=question_data.marks,
            order=question_data.order
        )
        db.add(db_question)
    
    # Create questions from question bank
    for qb_data in quiz_data.questions_from_bank:
        # Get question from bank
        qb_question = db.query(QuestionBank).filter(
            QuestionBank.id == qb_data.question_bank_id
        ).first()
        
        if not qb_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question bank item {qb_data.question_bank_id} not found"
            )
        
        # Copy question from bank to quiz
        db_question = Question(
            quiz_id=db_quiz.id,
            question_text=qb_question.question_text,
            question_type=qb_question.question_type,
            option_a=qb_question.option_a,
            option_b=qb_question.option_b,
            option_c=qb_question.option_c,
            option_d=qb_question.option_d,
            correct_answer=qb_question.correct_answer,
            marks=qb_data.marks,
            order=qb_data.order
        )
        db.add(db_question)
    
    db.commit()
    db.refresh(db_quiz)
    
    return db_quiz

@router.get("/", response_model=List[QuizResponse])
async def get_all_quizzes(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    subject_id: int = None,
    department: str = None,
    class_year: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all quizzes with filtering options.
    Students see only active quizzes for their department/class.
    Teachers see their own quizzes.
    Admins see all quizzes.
    """
    query = db.query(Quiz)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Quiz.is_active == is_active)
    
    if subject_id:
        query = query.filter(Quiz.subject_id == subject_id)
    
    if department:
        query = query.filter(Quiz.department == department)
    
    if class_year:
        query = query.filter(Quiz.class_year == class_year)
    
    # Role-based filtering
    if current_user.role == RoleEnum.STUDENT:
        # Students see only active quizzes for their department/class
        query = query.filter(Quiz.is_active == True)
        if current_user.department:
            query = query.filter(Quiz.department == current_user.department)
        if current_user.class_year:
            query = query.filter(Quiz.class_year == current_user.class_year)
    elif current_user.role == RoleEnum.TEACHER:
        # Teachers see their own quizzes
        query = query.filter(Quiz.creator_id == current_user.id)
    # Admins see all quizzes (no additional filter)
    
    # Additional filters
    if is_active is not None:
        query = query.filter(Quiz.is_active == is_active)
    
    if subject_id:
        query = query.filter(Quiz.subject_id == subject_id)
    
    if department:
        query = query.filter(Quiz.department == department)
    
    if class_year:
        query = query.filter(Quiz.class_year == class_year)
    
    quizzes = query.order_by(Quiz.created_at.desc()).offset(skip).limit(limit).all()
    return quizzes

@router.get("/{quiz_id}/availability", response_model=QuizAvailability)
async def check_quiz_timing(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check if a quiz is available for the student to start based on timing rules.
    """
    if current_user.role != RoleEnum.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can check quiz availability"
        )
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check if student has an existing attempt
    existing_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == current_user.id
    ).first()
    
    availability = check_quiz_availability(quiz, current_user.id, existing_attempt)
    return availability

@router.get("/{quiz_id}", response_model=QuizDetailResponse)
async def get_quiz(
    quiz_id: int,
    include_answers: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific quiz.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check permissions
    if current_user.role == RoleEnum.STUDENT and not quiz.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Quiz not available"
        )
    
    return quiz

@router.put("/{quiz_id}", response_model=QuizResponse, dependencies=[Depends(require_role([RoleEnum.ADMIN, RoleEnum.TEACHER]))])
async def update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update quiz details including timing and marking scheme.
    Only quiz creator or admin can update.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check if user can update (creator or admin)
    if current_user.role != RoleEnum.ADMIN and quiz.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    update_data = quiz_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quiz, field, value)
    
    db.commit()
    db.refresh(quiz)
    
    return quiz

@router.delete("/{quiz_id}", dependencies=[Depends(require_role([RoleEnum.ADMIN, RoleEnum.TEACHER]))])
async def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a quiz. Only quiz creator or admin can delete.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check if user can delete (creator or admin)
    if current_user.role != RoleEnum.ADMIN and quiz.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(quiz)
    db.commit()
    
    return {"message": "Quiz deleted successfully"}


@router.get("/{quiz_id}/statistics")
async def get_quiz_statistics(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "teacher"]))
):
    """
    Get detailed statistics for a quiz (Teacher/Admin only)
    """
    from app.models.models import QuizAttempt
    from sqlalchemy import func
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check permissions
    if current_user.role == "teacher" and quiz.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this quiz's statistics"
        )
    
    total_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id
    ).count()
    
    completed_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.is_completed == True
    ).count()
    
    average_score = db.query(func.avg(QuizAttempt.score)).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.is_completed == True
    ).scalar() or 0
    
    average_percentage = db.query(func.avg(QuizAttempt.percentage)).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.is_completed == True
    ).scalar() or 0
    
    highest_score = db.query(func.max(QuizAttempt.score)).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.is_completed == True
    ).scalar() or 0
    
    lowest_score = db.query(func.min(QuizAttempt.score)).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.is_completed == True,
        QuizAttempt.score > 0
    ).scalar() or 0
    
    return {
        "quiz_id": quiz_id,
        "quiz_title": quiz.title,
        "total_marks": quiz.total_marks,
        "total_attempts": total_attempts,
        "completed_attempts": completed_attempts,
        "in_progress": total_attempts - completed_attempts,
        "average_score": round(average_score, 2),
        "average_percentage": round(average_percentage, 2),
        "highest_score": highest_score,
        "lowest_score": lowest_score,
        "pass_rate": round((completed_attempts / total_attempts * 100), 2) if total_attempts > 0 else 0
    }


@router.get("/{quiz_id}/attempts")
async def get_quiz_attempts(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "teacher"]))
):
    """
    Get all attempts for a quiz (Teacher/Admin only)
    """
    from app.models.models import QuizAttempt
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check permissions
    if current_user.role == "teacher" and quiz.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this quiz's attempts"
        )
    
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id
    ).all()
    
    return attempts
