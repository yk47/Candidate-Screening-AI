"""FastAPI endpoints for interview workflow."""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from fastapi import Form
from sqlalchemy.orm import Session
from typing import Optional
import traceback
import uuid

from ..db.database import get_db
from ..db.repository import SessionRepository, ResumeDataRepository
from ..services.interview_service import InterviewService
from ..graph.state import InterviewState

router = APIRouter(prefix="/api/interview", tags=["interview"])

# Lazy singleton for InterviewService to avoid heavy imports at module level
_interview_service = None

def get_interview_service():
    global _interview_service
    if _interview_service is None:
        _interview_service = InterviewService()
    return _interview_service

# Pydantic models for request/response
from pydantic import BaseModel

class StartInterviewRequest(BaseModel):
    candidate_name: str
    email: Optional[str] = None
    role: str
    resume_text: str

class AnswerSubmissionRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str

class SessionResponse(BaseModel):
    session_id: str
    candidate_name: str
    role: str
    status: str

class QuestionResponse(BaseModel):
    question_id: str
    question_number: int
    question_text: str
    topic: str
    difficulty: str


@router.post("/start", response_model=SessionResponse)
async def start_interview(request: Request, db: Session = Depends(get_db)):
    """Start a new interview session.
    
    Args:
        request: Interview start request with candidate info
        db: Database session
        
    Returns:
        Session information
    """
    try:
        print("========== START INTERVIEW ==========")

        # Support both JSON and multipart/form-data
        content_type = request.headers.get("content-type", "")
        resume_text = ""
        candidate_name = None
        email = None
        role = None
        resume_file = None

        print(f"Content-Type: {content_type}")

        if "application/json" in content_type:
            payload = await request.json()

            candidate_name = payload.get("candidate_name")
            email = payload.get("email")
            role = payload.get("role")
            resume_text = payload.get("resume_text", "")

            print("Received JSON payload")

        else:
            form = await request.form()

            candidate_name = form.get("candidate_name")
            email = form.get("email")
            role = form.get("role")
            resume_text = form.get("resume_text") or ""
            resume_file = form.get("resume_file")

            print("Received multipart form-data")
            print(f"candidate_name={candidate_name}")
            print(f"email={email}")
            print(f"role={role}")
            print(f"resume_file_present={resume_file is not None}")

        if not candidate_name or not role:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields"
            )

        # Extract resume text if file uploaded
        if resume_file:
            try:
                print("Processing uploaded resume...")

                contents = await resume_file.read()

                if getattr(resume_file, "content_type", "") == "text/plain":
                    extracted_text = contents.decode(errors="ignore")

                elif getattr(resume_file, "content_type", "") == "application/pdf":
                    import io
                    from PyPDF2 import PdfReader

                    reader = PdfReader(io.BytesIO(contents))
                    pages = [p.extract_text() or "" for p in reader.pages]
                    extracted_text = "\n".join(pages)

                else:
                    extracted_text = ""

                if extracted_text.strip():
                    resume_text = extracted_text

                print(f"Extracted resume text length: {len(resume_text)}")

            except Exception as pdf_error:
                print("PDF extraction failed:")
                print(str(pdf_error))
                import traceback
                traceback.print_exc()

        print("Creating session...")

        session = SessionRepository.create(
            db=db,
            candidate_name=candidate_name,
            email=email,
            role=role,
            resume_text=resume_text
        )

        print(f"Session created: {session.id}")

        print("Parsing resume...")

        extracted = get_interview_service().parse_resume(resume_text)

        print("Resume parsed successfully")
        print(f"Extracted data: {extracted}")

        ResumeDataRepository.create(
            db=db,
            session_id=session.id,
            skills=extracted.get("skills", []),
            technologies=extracted.get("technologies", []),
            experience_years=extracted.get("experience_years", 0),
            domain_exposure=extracted.get("domain_exposure", [])
        )

        print("Resume data stored successfully")

        return SessionResponse(
            session_id=session.id,
            candidate_name=session.candidate_name,
            role=session.role,
            status=session.status
        )

    except Exception as e:
        print("========== START INTERVIEW ERROR ==========")
        print(f"Error: {str(e)}")

        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/next-question", response_model=QuestionResponse)
async def get_next_question(session_id: str, db: Session = Depends(get_db)):
    """Get the next interview question.
    
    Args:
        session_id: Interview session ID
        db: Database session
        
    Returns:
        Question details
    """
    try:
        import random
        session = SessionRepository.get_by_id(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if interview was terminated early
        if session.interview_terminated_early:
            raise HTTPException(status_code=400, detail="completed")
        
        resume_data = ResumeDataRepository.get_by_session(db, session_id)
        if not resume_data:
            raise HTTPException(status_code=400, detail="Resume data not found")
        
        extracted_data = {
            "skills": resume_data.skills or [],
            "technologies": resume_data.technologies or [],
            "experience_years": resume_data.experience_years or 0,
            "domain_exposure": resume_data.domain_exposure or [],
            "resume_text": session.resume_text
        }
        
        # For now, generate topics on first question
        from ..db.models import Question as QuestionModel
        existing_questions = db.query(QuestionModel).filter(QuestionModel.session_id == session_id).all()
        
        if not existing_questions:
            # First question - generate topics and shuffle them for randomization
            topics = get_interview_service().generate_topics(extracted_data, session.role)
            random.shuffle(topics)
            session.topics = topics
            db.commit()
        else:
            topics = session.topics or []
        
        question_number = len(existing_questions) + 1
        
        # Adaptive question count: Ask between 5-10 questions based on confidence
        # Minimum questions = 5, Maximum = 10
        max_questions = 10
        min_questions = 5
        
        # If confidence is low, stop early (this is checked in evaluate_answer)
        # If we have enough questions and confidence is high, can stop at 6-7
        if question_number > max_questions:
            raise HTTPException(status_code=400, detail="completed")
        
        # Get topic for this question (cycle through topics if needed)
        topic = topics[min(question_number - 1, len(topics) - 1)] if topics else "General Knowledge"
        
        question_data = get_interview_service().generate_question(
            db=db,
            session_id=session_id,
            topic=topic,
            role=session.role,
            extracted_data=extracted_data,
            question_number=question_number
        )
        
        return QuestionResponse(
            question_id=question_data["id"],
            question_number=question_data["question_number"],
            question_text=question_data["question"],
            topic=question_data["topic"],
            difficulty=question_data["difficulty"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/submit-answer")
async def submit_answer(request: AnswerSubmissionRequest, db: Session = Depends(get_db)):
    """Submit candidate answer.
    
    Args:
        request: Answer submission details
        db: Database session
        
    Returns:
        Evaluation result with early termination signal if applicable
    """
    try:
        from ..db.models import Question as QuestionModel
        
        question = db.query(QuestionModel).filter(QuestionModel.id == request.question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        session = SessionRepository.get_by_id(db, request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Evaluate answer with adaptive tracking
        evaluation = get_interview_service().evaluate_answer(
            db=db,
            session_id=request.session_id,
            question_id=request.question_id,
            answer=request.answer,
            question_text=question.question_text,
            topic=question.topic,
            role=session.role,
            reference_context=question.retrieved_context or ""
        )
        
        response = {
            "question_id": request.question_id,
            "score": evaluation.get("score", 0),
            "feedback": evaluation.get("feedback", ""),
            "strengths": evaluation.get("strengths", []),
            "weaknesses": evaluation.get("weaknesses", [])
        }
        
        # Check if interview should terminate early
        if evaluation.get("interview_terminated"):
            response["interview_terminated"] = True
            response["termination_reason"] = evaluation.get("termination_reason")
            # Generate final report
            report = get_interview_service().generate_session_summary(db, request.session_id)
            response["final_report"] = report
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_details(session_id: str, db: Session = Depends(get_db)):
    """Get session details.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Returns:
        Session information
    """
    session = SessionRepository.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    from ..db.models import Question as QuestionModel
    questions = db.query(QuestionModel).filter(QuestionModel.session_id == session_id).all()
    
    return {
        "session_id": session.id,
        "candidate_name": session.candidate_name,
        "role": session.role,
        "status": session.status,
        "created_at": session.created_at,
        "questions_asked": len(questions),
        "questions_answered": len([q for q in questions if q.answer_text])
    }


@router.get("/summary/{session_id}")
async def get_session_summary(session_id: str, db: Session = Depends(get_db)):
    """Get interview session summary.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Returns:
        Interview summary
    """
    try:
        summary = get_interview_service().generate_session_summary(db, session_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
