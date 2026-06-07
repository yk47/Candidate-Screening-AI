"""State management for the interview workflow graph."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class WorkflowStatus(str, Enum):
    """Status of workflow execution."""
    STARTED = "started"
    RESUME_PARSED = "resume_parsed"
    TOPICS_GENERATED = "topics_generated"
    CONTEXT_RETRIEVED = "context_retrieved"
    QUESTION_GENERATED = "question_generated"
    ANSWER_RECEIVED = "answer_received"
    ANSWER_EVALUATED = "answer_evaluated"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class InterviewState:
    """State object for the interview workflow."""
    
    # Session info
    session_id: str
    candidate_name: str
    email: str
    role: str
    resume_text: str
    
    # Resume parsing
    extracted_skills: List[str] = field(default_factory=list)
    extracted_technologies: List[str] = field(default_factory=list)
    experience_years: Optional[int] = None
    domain_exposure: List[str] = field(default_factory=list)
    
    # Topic generation
    topics: List[str] = field(default_factory=list)
    current_topic_index: int = 0
    
    # Question generation
    current_question_number: int = 1
    current_question_text: str = ""
    current_difficulty: str = "intermediate"
    current_topic: str = ""
    retrieved_context: str = ""
    context_chunks: List[Dict] = field(default_factory=list)
    
    # Answer handling
    current_answer: str = ""
    answer_score: Optional[float] = None
    answer_feedback: str = ""
    
    # Interview progress
    questions_asked: List[Dict] = field(default_factory=list)
    answers_received: List[Dict] = field(default_factory=list)
    
    # Evaluation
    average_score: Optional[float] = None
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: str = ""
    
    # Configuration
    max_questions: int = 5
    
    # Metadata
    status: WorkflowStatus = WorkflowStatus.STARTED
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert state to dictionary."""
        return {
            "session_id": self.session_id,
            "candidate_name": self.candidate_name,
            "email": self.email,
            "role": self.role,
            "extracted_skills": self.extracted_skills,
            "topics": self.topics,
            "current_question_number": self.current_question_number,
            "current_question_text": self.current_question_text,
            "current_topic": self.current_topic,
            "questions_asked": len(self.questions_asked),
            "answers_received": len(self.answers_received),
            "status": self.status.value,
            "average_score": self.average_score,
            "max_questions": self.max_questions
        }
    
    def should_continue_interview(self) -> bool:
        """Check if interview should continue."""
        return (
            self.current_question_number < self.max_questions
            and self.status != WorkflowStatus.ERROR
        )
    
    def add_question(self, question_dict: Dict):
        """Add a question to the interview."""
        self.questions_asked.append(question_dict)
    
    def add_answer(self, answer_dict: Dict):
        """Add an answer to the interview."""
        self.answers_received.append(answer_dict)
    
    def calculate_average_score(self):
        """Calculate average score from all answered questions."""
        if self.answers_received:
            scores = [a.get("score", 0) for a in self.answers_received if "score" in a]
            if scores:
                self.average_score = sum(scores) / len(scores)
