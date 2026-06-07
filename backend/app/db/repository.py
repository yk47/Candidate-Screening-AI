"""Repository pattern for database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from .models import Session as SessionModel, Question, ResumeData, SessionEvaluation
import uuid


class SessionRepository:
    """Repository for session operations."""
    
    @staticmethod
    def create(db: Session, candidate_name: str, email: str, role: str, resume_text: str, resume_filename: str = None, topics: list = None) -> SessionModel:
        """Create a new session."""
        session = SessionModel(
            id=str(uuid.uuid4()),
            candidate_name=candidate_name,
            email=email,
            role=role,
            resume_text=resume_text,
            resume_filename=resume_filename,
            topics=topics
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_by_id(db: Session, session_id: str) -> Optional[SessionModel]:
        """Get session by ID."""
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    @staticmethod
    def update_status(db: Session, session_id: str, status: str):
        """Update session status."""
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            session.status = status
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def update_topics(db: Session, session_id: str, topics: list):
        """Update session topics."""
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            session.topics = topics
            db.commit()
            db.refresh(session)
        return session


class ResumeDataRepository:
    """Repository for resume data operations."""
    
    @staticmethod
    def create(db: Session, session_id: str, skills: list = None, technologies: list = None, 
               experience_years: int = None, domain_exposure: list = None, education: str = None) -> ResumeData:
        """Create resume data entry."""
        resume_data = ResumeData(
            id=str(uuid.uuid4()),
            session_id=session_id,
            skills=skills,
            technologies=technologies,
            experience_years=experience_years,
            domain_exposure=domain_exposure,
            education=education
        )
        db.add(resume_data)
        db.commit()
        db.refresh(resume_data)
        return resume_data
    
    @staticmethod
    def get_by_session(db: Session, session_id: str) -> Optional[ResumeData]:
        """Get resume data by session ID."""
        return db.query(ResumeData).filter(ResumeData.session_id == session_id).first()


class QuestionRepository:
    """Repository for question operations."""
    
    @staticmethod
    def create(db: Session, session_id: str, question_number: int, question_text: str, 
               topic: str, difficulty: str = None, retrieved_context: str = None, 
               context_chunks: list = None) -> Question:
        """Create a new question."""
        question = Question(
            id=str(uuid.uuid4()),
            session_id=session_id,
            question_number=question_number,
            question_text=question_text,
            topic=topic,
            difficulty=difficulty,
            retrieved_context=retrieved_context,
            context_chunks=context_chunks
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question
    
    @staticmethod
    def get_by_session(db: Session, session_id: str) -> List[Question]:
        """Get all questions for a session."""
        return db.query(Question).filter(Question.session_id == session_id).order_by(Question.question_number).all()
    
    @staticmethod
    def update_answer(db: Session, question_id: str, answer_text: str, evaluation_score: float = None, feedback: str = None):
        """Update question with answer and evaluation."""
        question = db.query(Question).filter(Question.id == question_id).first()
        if question:
            question.answer_text = answer_text
            question.evaluation_score = evaluation_score
            question.feedback = feedback
            db.commit()
            db.refresh(question)
        return question


class SessionEvaluationRepository:
    """Repository for session evaluation operations."""
    
    @staticmethod
    def create(db: Session, session_id: str, total_questions: int, total_answered: int,
               average_score: float = None, overall_score: float = None, 
               hiring_recommendation: str = None,
               strengths: list = None, weaknesses: list = None,
               topic_wise_breakdown: dict = None, communication_assessment: dict = None,
               learning_path: list = None, 
               recommendations: str = None, summary: str = None,
               early_termination: int = 0, termination_reason: str = None) -> SessionEvaluation:
        """Create session evaluation."""
        evaluation = SessionEvaluation(
            id=str(uuid.uuid4()),
            session_id=session_id,
            total_questions=total_questions,
            total_answered=total_answered,
            average_score=average_score,
            overall_score=overall_score,
            hiring_recommendation=hiring_recommendation,
            strengths=strengths,
            weaknesses=weaknesses,
            topic_wise_breakdown=topic_wise_breakdown,
            communication_assessment=communication_assessment,
            learning_path=learning_path,
            recommendations=recommendations,
            summary=summary,
            early_termination=early_termination,
            termination_reason=termination_reason
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation
    
    @staticmethod
    def get_by_session(db: Session, session_id: str) -> Optional[SessionEvaluation]:
        """Get evaluation by session ID."""
        return db.query(SessionEvaluation).filter(SessionEvaluation.session_id == session_id).first()
