"""Database models for the candidate screening system."""

from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class Session(Base):
    """Interview session model."""
    
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, index=True)
    candidate_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    role = Column(String(100), nullable=False, index=True)
    resume_text = Column(Text, nullable=False)
    resume_filename = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default="active", nullable=False)  # active, completed, paused
    topics = Column(JSON, nullable=True)
    
    # Adaptive interview tracking
    confidence_score = Column(Float, default=0.5, nullable=False)  # Tracks overall confidence (0-1)
    consecutive_bad_answers = Column(Integer, default=0, nullable=False)  # Counts bad answers
    interview_terminated_early = Column(Integer, default=0, nullable=False)  # 0=ongoing, 1=early termination
    termination_reason = Column(String(255), nullable=True)  # Why interview ended early
    
    # Relationships
    extracted_data = relationship("ResumeData", back_populates="session", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan")
    evaluation = relationship("SessionEvaluation", back_populates="session", uselist=False, cascade="all, delete-orphan")


class ResumeData(Base):
    """Extracted resume data."""
    
    __tablename__ = "resume_data"
    
    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    
    skills = Column(JSON, nullable=True)  # List of skills
    technologies = Column(JSON, nullable=True)  # List of technologies
    experience_years = Column(Integer, nullable=True)
    domain_exposure = Column(JSON, nullable=True)  # List of domains
    education = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="extracted_data")


class Question(Base):
    """Interview questions."""
    
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    topic = Column(String(255), nullable=False, index=True)
    difficulty = Column(String(50), nullable=True)  # beginner, intermediate, advanced
    
    # RAG traceability
    retrieved_context = Column(Text, nullable=True)
    context_chunks = Column(JSON, nullable=True)  # Store chunk IDs or references
    
    answer_text = Column(Text, nullable=True)
    evaluation_score = Column(Float, nullable=True)  # 0-1 or 0-100
    feedback = Column(Text, nullable=True)
    
    asked_at = Column(DateTime, nullable=True)
    answered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    session = relationship("Session", back_populates="questions")


class SessionEvaluation(Base):
    """Final evaluation and summary."""
    
    __tablename__ = "session_evaluations"
    
    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True, unique=True)
    
    total_questions = Column(Integer, nullable=False)
    total_answered = Column(Integer, nullable=False)
    average_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)  # Final score out of 10
    
    # Hiring decision
    hiring_recommendation = Column(String(50), nullable=True)  # Strong Hire, Hire, Borderline, No Hire
    
    # Detailed assessment
    strengths = Column(JSON, nullable=True)  # List of strengths
    weaknesses = Column(JSON, nullable=True)  # List of weaknesses
    topic_wise_breakdown = Column(JSON, nullable=True)  # {topic: {score, observations, suggestions}}
    communication_assessment = Column(JSON, nullable=True)  # {clarity, vocabulary, explanation_quality}
    learning_path = Column(JSON, nullable=True)  # Recommended topics to study
    
    summary = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    early_termination = Column(Integer, default=0, nullable=False)  # 1 if terminated early
    termination_reason = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="evaluation")
