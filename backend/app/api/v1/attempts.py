from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List
from app.db.database import get_db
from app.models.models import User, Quiz, QuizAttempt, Answer, Question, RoleEnum
from app.schemas.schemas import (
    QuizAttemptStart, QuizAttemptSubmit, QuizAttemptResponse,
    QuizAttemptDetailResponse
)
from app.core.deps import get_current_active_user, require_role
from app.services.quiz_service import check_quiz_availability, calculate_quiz_score

router = APIRouter()

@router.post("/start", response_model=QuizAttemptResponse)
async def start_quiz_attempt(
    attempt_data: QuizAttemptStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start a quiz attempt. Validates timing constraints and student eligibility.
    """
    # Verify quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == attempt_data.quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    if not quiz.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz is not active"
        )
    
    # Check for existing attempt
    existing_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz.id,
        QuizAttempt.student_id == current_user.id
    ).first()
    
    # Check quiz availability based on timing rules
    availability = check_quiz_availability(quiz, current_user.id, existing_attempt)
    
    if not availability.can_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=availability.message
        )
    
    # If student has incomplete attempt, return it
    if existing_attempt and not existing_attempt.is_completed:
        return existing_attempt
    
    # If student already completed the quiz
    if existing_attempt and existing_attempt.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already completed this quiz"
        )
    
    # Create new attempt
    db_attempt = QuizAttempt(
        quiz_id=quiz.id,
        student_id=current_user.id,
        total_marks=quiz.total_marks,
        is_completed=False,
        is_graded=False
    )
    
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    
    return db_attempt

@router.post("/submit", response_model=QuizAttemptResponse)
async def submit_quiz_attempt(
    attempt_id: int,
    submission: QuizAttemptSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit quiz answers and calculate score based on custom marking scheme.
    """
    # Get attempt
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    
    # Verify ownership
    if attempt.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your attempt"
        )
    
    # Check if already submitted
    if attempt.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz already submitted"
        )
    
    # Get quiz for marking scheme
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    
    # Check if deadline passed
    deadline = attempt.started_at + timedelta(minutes=quiz.duration_minutes)
    if datetime.utcnow() > deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz time expired. Cannot submit."
        )
    
    # Process and save answers
    answers_list = []
    for answer_data in submission.answers:
        question = db.query(Question).filter(Question.id == answer_data.question_id).first()
        if question:
            # Check answer correctness
            is_correct = answer_data.answer_text.strip().lower() == question.correct_answer.strip().lower()
            
            # Create answer object
            db_answer = Answer(
                attempt_id=attempt.id,
                question_id=question.id,
                answer_text=answer_data.answer_text,
                is_correct=is_correct,
                marks_awarded=0  # Will be calculated by service
            )
            answers_list.append(db_answer)
            db.add(db_answer)
    
    # Calculate score using custom marking scheme
    total_score, percentage = calculate_quiz_score(answers_list, quiz)
    
    # Calculate time taken
    time_taken = int((datetime.utcnow() - attempt.started_at).total_seconds() / 60)
    
    # Update attempt
    attempt.score = total_score
    attempt.percentage = percentage
    attempt.submitted_at = datetime.utcnow()
    attempt.is_completed = True
    attempt.time_taken_minutes = time_taken
    
    db.commit()
    db.refresh(attempt)
    
    return attempt

@router.get("/my-attempts", response_model=List[QuizAttemptResponse])
async def get_my_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all quiz attempts for the current student.
    """
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id
    ).order_by(QuizAttempt.started_at.desc()).all()
    return attempts

@router.get("/quiz/{quiz_id}", response_model=List[QuizAttemptResponse], dependencies=[Depends(require_role([RoleEnum.ADMIN, RoleEnum.TEACHER]))])
async def get_quiz_attempts(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all attempts for a specific quiz. Teachers can only see attempts for their quizzes.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Teachers can only view attempts for their own quizzes
    if current_user.role == RoleEnum.TEACHER and quiz.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view attempts for your own quizzes"
        )
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    return attempts

@router.get("/student/{student_id}", response_model=List[QuizAttemptResponse], dependencies=[Depends(require_role([RoleEnum.ADMIN, RoleEnum.TEACHER]))])
async def get_student_attempts(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all quiz attempts for a specific student.
    """
    student = db.query(User).filter(
        User.id == student_id,
        User.role == RoleEnum.STUDENT
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == student_id
    ).order_by(QuizAttempt.started_at.desc()).all()
    return attempts

@router.get("/{attempt_id}", response_model=QuizAttemptDetailResponse)
async def get_attempt_details(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific quiz attempt including answers.
    """
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    
    # Students can only view their own attempts
    # Teachers can view attempts for their quizzes
    # Admins can view all attempts
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    
    if current_user.role == RoleEnum.STUDENT and attempt.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own attempts"
        )
    
    if current_user.role == RoleEnum.TEACHER and quiz.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view attempts for your own quizzes"
        )
    
    return attempt
