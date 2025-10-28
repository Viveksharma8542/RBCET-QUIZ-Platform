from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_current_user, get_db
from app.models.models import QuestionBank, User, Subject, RoleEnum
from app.schemas.schemas import QuestionBankCreate, QuestionBankResponse, DifficultyLevel

router = APIRouter()

@router.post("/", response_model=QuestionBankResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    question: QuestionBankCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a question to the question bank (Teacher or Admin only)
    """
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can add questions to the bank"
        )
    
    # Verify subject exists
    subject = db.query(Subject).filter(Subject.id == question.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    db_question = QuestionBank(**question.dict(), created_by=current_user.id)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    return db_question

@router.get("/", response_model=List[QuestionBankResponse])
def get_questions(
    subject_id: Optional[int] = None,
    difficulty_level: Optional[DifficultyLevel] = None,
    topic: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get questions from the question bank with filtering options
    """
    query = db.query(QuestionBank)
    
    if subject_id:
        query = query.filter(QuestionBank.subject_id == subject_id)
    
    if difficulty_level:
        query = query.filter(QuestionBank.difficulty_level == difficulty_level)
    
    if topic:
        query = query.filter(QuestionBank.topic.ilike(f"%{topic}%"))
    
    questions = query.offset(skip).limit(limit).all()
    return questions

@router.get("/{question_id}", response_model=QuestionBankResponse)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific question from the question bank
    """
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question

@router.put("/{question_id}", response_model=QuestionBankResponse)
def update_question(
    question_id: int,
    question_update: QuestionBankCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a question in the question bank (Creator, Teacher, or Admin only)
    """
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check permissions
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can update questions"
        )
    
    if current_user.role == RoleEnum.TEACHER and question.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teachers can only update their own questions"
        )
    
    for key, value in question_update.dict().items():
        setattr(question, key, value)
    
    db.commit()
    db.refresh(question)
    
    return question

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a question from the question bank (Creator or Admin only)
    """
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check permissions
    if current_user.role != RoleEnum.ADMIN and question.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own questions"
        )
    
    db.delete(question)
    db.commit()
    
    return None

@router.get("/subjects/{subject_id}/stats")
def get_subject_question_stats(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about questions in a subject's question bank
    """
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    total_questions = db.query(QuestionBank).filter(QuestionBank.subject_id == subject_id).count()
    
    easy_count = db.query(QuestionBank).filter(
        QuestionBank.subject_id == subject_id,
        QuestionBank.difficulty_level == DifficultyLevel.EASY
    ).count()
    
    medium_count = db.query(QuestionBank).filter(
        QuestionBank.subject_id == subject_id,
        QuestionBank.difficulty_level == DifficultyLevel.MEDIUM
    ).count()
    
    hard_count = db.query(QuestionBank).filter(
        QuestionBank.subject_id == subject_id,
        QuestionBank.difficulty_level == DifficultyLevel.HARD
    ).count()
    
    return {
        "subject_id": subject_id,
        "subject_name": subject.name,
        "total_questions": total_questions,
        "by_difficulty": {
            "easy": easy_count,
            "medium": medium_count,
            "hard": hard_count
        }
    }
