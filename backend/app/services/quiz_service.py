from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.models.models import Quiz, QuizAttempt
from app.schemas.schemas import QuizAvailability

def check_quiz_availability(quiz: Quiz, student_id: int, existing_attempt: Optional[QuizAttempt] = None) -> QuizAvailability:
    """
    Check if a quiz is available for a student to start based on timing rules.
    
    Rules:
    - If scheduled_start_time is None, quiz is always available
    - If scheduled_start_time is set:
        - Student can start within grace_period_minutes after scheduled_start_time
        - After grace period expires, student cannot start
        - Example: Start time 12:00 PM, duration 30 mins, grace period 5 mins
            - Can start: 12:00 PM - 12:05 PM
            - Cannot start after: 12:05 PM
            - Must submit by: start_time + duration
    
    Returns:
        QuizAvailability object with availability status and timing information
    """
    now = datetime.utcnow()
    
    # If student already has an attempt, check if they can continue
    if existing_attempt and not existing_attempt.is_completed:
        # Calculate deadline
        deadline = existing_attempt.started_at + timedelta(minutes=quiz.duration_minutes)
        
        if now > deadline:
            return QuizAvailability(
                is_available=False,
                can_start=False,
                message="Quiz time has expired. You cannot continue this attempt.",
                scheduled_start=quiz.scheduled_start_time,
                grace_period_end=None,
                quiz_end=deadline
            )
        
        return QuizAvailability(
            is_available=True,
            can_start=True,
            message="You can continue your quiz attempt.",
            scheduled_start=quiz.scheduled_start_time,
            grace_period_end=None,
            quiz_end=deadline
        )
    
    # If student already completed the quiz
    if existing_attempt and existing_attempt.is_completed:
        return QuizAvailability(
            is_available=False,
            can_start=False,
            message="You have already completed this quiz.",
            scheduled_start=quiz.scheduled_start_time,
            grace_period_end=None,
            quiz_end=existing_attempt.submitted_at
        )
    
    # If quiz has no scheduled start time, it's always available
    if not quiz.scheduled_start_time:
        return QuizAvailability(
            is_available=True,
            can_start=True,
            message="Quiz is available. You can start anytime.",
            scheduled_start=None,
            grace_period_end=None,
            quiz_end=None
        )
    
    # Calculate grace period end time
    grace_period_end = quiz.scheduled_start_time + timedelta(minutes=quiz.grace_period_minutes)
    
    # Check if current time is before scheduled start
    if now < quiz.scheduled_start_time:
        return QuizAvailability(
            is_available=False,
            can_start=False,
            message=f"Quiz will be available on {quiz.scheduled_start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            scheduled_start=quiz.scheduled_start_time,
            grace_period_end=grace_period_end,
            quiz_end=None
        )
    
    # Check if grace period has expired
    if now > grace_period_end:
        return QuizAvailability(
            is_available=False,
            can_start=False,
            message=f"Grace period expired. You needed to start before {grace_period_end.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            scheduled_start=quiz.scheduled_start_time,
            grace_period_end=grace_period_end,
            quiz_end=None
        )
    
    # Quiz is available within grace period
    time_remaining = int((grace_period_end - now).total_seconds() / 60)
    return QuizAvailability(
        is_available=True,
        can_start=True,
        message=f"Quiz is available. You have {time_remaining} minute(s) left to start.",
        scheduled_start=quiz.scheduled_start_time,
        grace_period_end=grace_period_end,
        quiz_end=None
    )

def calculate_quiz_score(answers: list, quiz: Quiz) -> Tuple[float, float]:
    """
    Calculate the score for a quiz attempt based on custom marking scheme.
    
    Args:
        answers: List of Answer objects with is_correct field set
        quiz: Quiz object with marking scheme (marks_per_correct, marks_per_incorrect)
    
    Returns:
        Tuple of (total_score, percentage)
    """
    score = 0.0
    total_questions = len(answers)
    
    for answer in answers:
        if answer.is_correct:
            score += quiz.marks_per_correct
            answer.marks_awarded = quiz.marks_per_correct
        else:
            score -= quiz.marks_per_incorrect  # Negative marking
            answer.marks_awarded = -quiz.marks_per_incorrect
    
    # Calculate total possible marks
    max_possible_score = total_questions * quiz.marks_per_correct
    
    # Calculate percentage (ensure it doesn't go below 0)
    percentage = max(0, (score / max_possible_score) * 100) if max_possible_score > 0 else 0
    
    return score, round(percentage, 2)
