from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt
from app.schemas.quiz import QuizOut, QuizDetail, QuizSubmit, AttemptOut, AttemptResult
from app.auth import get_current_student
from app.models.student import Student

router = APIRouter(prefix="/students/me/quizzes", tags=["students"])


# GET all available quizzes
@router.get("/", response_model=list[QuizOut])
def list_quizzes(
    topic:      str | None = None,
    difficulty: str | None = None,
    db:         Session    = Depends(get_db),
    current:    Student    = Depends(get_current_student),
):
    q = db.query(Quiz)
    if topic:      q = q.filter(Quiz.topic.ilike(f"%{topic}%"))
    if difficulty: q = q.filter(Quiz.difficulty == difficulty)
    return q.all()


# GET single quiz with questions (no correct answers exposed)
@router.get("/{quiz_id}", response_model=QuizDetail)
def get_quiz(
    quiz_id: int,
    db:      Session = Depends(get_db),
    current: Student = Depends(get_current_student),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    return quiz


# POST submit answers → get score
@router.post("/{quiz_id}/submit", response_model=AttemptResult)
def submit_quiz(
    quiz_id:  int,
    payload:  QuizSubmit,
    db:       Session = Depends(get_db),
    current:  Student = Depends(get_current_student),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(404, "Quiz not found")

    questions = {q.id: q.correct_answer for q in quiz.questions}
    if not questions:
        raise HTTPException(400, "Quiz has no questions")

    score = sum(
        1 for a in payload.answers
        if a.question_id in questions and a.answer.lower() == questions[a.question_id].lower()
    )
    total      = len(questions)
    passed     = score / total >= 0.6
    percentage = round(score / total * 100, 1)

    attempt = QuizAttempt(
        student_id=current.id,
        quiz_id=quiz_id,
        score=score,
        total=total,
        passed=passed,
    )
    db.add(attempt); db.commit(); db.refresh(attempt)

    return AttemptResult(
        id=attempt.id,
        quiz_id=quiz_id,
        score=score,
        total=total,
        passed=passed,
        attempted_at=attempt.attempted_at,
        percentage=percentage,
        feedback="Passed! Well done." if passed else f"Failed. Score: {score}/{total}. Try again.",
    )


# GET my quiz history
@router.get("/history/me", response_model=list[AttemptOut])
def my_quiz_history(
    db:      Session = Depends(get_db),
    current: Student = Depends(get_current_student),
):
    return db.query(QuizAttempt).filter(QuizAttempt.student_id == current.id).all()
