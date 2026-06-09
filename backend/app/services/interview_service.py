"""Interview service orchestrating the workflow."""

from typing import Dict, List, Optional
import json
from sqlalchemy.orm import Session

from .llm_service import LLMService
from ..db.repository import SessionRepository, ResumeDataRepository, QuestionRepository, SessionEvaluationRepository


class InterviewService:
    """Service managing the complete interview workflow."""
    
    def __init__(self):
        """Initialize interview service."""
        self.llm_service = LLMService()
        # Lazy init RAG to avoid loading chromadb/sentence-transformers at startup
        self._rag_retriever = None
    
    @property
    def rag_retriever(self):
        """Lazy-loaded RAG retriever."""
        if self._rag_retriever is None:
            from ..rag.retriever import RAGRetriever
            self._rag_retriever = RAGRetriever()
        return self._rag_retriever
    
    def parse_resume(self, resume_text: str) -> Dict:
        """Parse and extract information from resume.
        
        Args:
            resume_text: Resume text content
            
        Returns:
            Extracted resume data
        """
        # Simple extraction logic - in production this would use LLM
        extracted = {
            "skills": self._extract_skills(resume_text),
            "technologies": self._extract_technologies(resume_text),
            "experience_years": self._extract_experience_years(resume_text),
            "domain_exposure": self._extract_domains(resume_text),
        }
        
        return extracted
    
    def _extract_skills(self, resume_text: str) -> List[str]:
        """Extract technical skills from resume."""
        skills = []
        skill_keywords = ["python", "java", "javascript", "go", "rust", "c++",
                         "sql", "nosql", "rest", "graphql", "microservices",
                         "docker", "kubernetes", "git", "agile", "leadership"]
        
        resume_lower = resume_text.lower()
        for skill in skill_keywords:
            if skill in resume_lower:
                skills.append(skill.title())
        
        return skills[:10]  # Return top 10
    
    def _extract_technologies(self, resume_text: str) -> List[str]:
        """Extract technologies from resume."""
        techs = []
        tech_keywords = ["react", "angular", "vue", "fastapi", "django", "flask",
                        "postgresql", "mongodb", "redis", "elasticsearch", "aws", "gcp",
                        "azure", "jenkins", "gitlab", "github", "terraform"]
        
        resume_lower = resume_text.lower()
        for tech in tech_keywords:
            if tech in resume_lower:
                techs.append(tech.title())
        
        return techs[:8]  # Return top 8
    
    def _extract_experience_years(self, resume_text: str) -> int:
        """Extract years of experience from resume."""
        import re
        
        years = re.findall(r'(\d+)\s*(?:years?|yrs?)', resume_text, re.IGNORECASE)
        
        if years:
            return max(int(y) for y in years)
        
        return 0
    
    def _extract_domains(self, resume_text: str) -> List[str]:
        """Extract domain exposure from resume."""
        domains = []
        domain_keywords = ["backend", "frontend", "fullstack", "devops", "cloud",
                          "machine learning", "data science", "ai", "web",
                          "mobile", "iot", "blockchain", "fintech", "healthtech"]
        
        resume_lower = resume_text.lower()
        for domain in domain_keywords:
            if domain in resume_lower:
                domains.append(domain.title())
        
        return domains
    
    def generate_topics(self, extracted_data: Dict, role: str) -> List[str]:
        """Generate interview topics based on resume and role.
        
        Args:
            extracted_data: Extracted resume data
            role: Target role
            
        Returns:
            List of interview topics
        """
        topics = self.llm_service.generate_topics(
            skills=extracted_data.get("skills", []),
            technologies=extracted_data.get("technologies", []),
            experience_years=extracted_data.get("experience_years", 0),
            domain_exposure=extracted_data.get("domain_exposure", []),
            role=role
        )
        
        return topics
    
    def generate_question(self, db: Session, session_id: str, topic: str, role: str,
                         extracted_data: Dict, question_number: int) -> Dict:
        """Generate an interview question.
        
        Args:
            db: Database session
            session_id: Interview session ID
            topic: Interview topic
            role: Target role
            extracted_data: Extracted resume data
            question_number: Question number in sequence
            
        Returns:
            Question with context
        """
        # Determine difficulty
        experience = extracted_data.get("experience_years", 0)
        if experience < 2:
            difficulty = "beginner"
        elif experience < 5:
            difficulty = "intermediate"
        else:
            difficulty = "advanced"
        
        # Enhance query with resume data
        enhanced_query = self.rag_retriever.enhance_query(
            extracted_data.get("resume_text", ""),
            topic,
            role
        )
        
        # Retrieve relevant context
        retrieval = self.rag_retriever.retrieve_context(role, enhanced_query, k=5)
        retrieved_context = retrieval.get("context", "")
        
        # Generate question
        question_data = self.llm_service.generate_question(
            topic=topic,
            role=role,
            difficulty=difficulty,
            skills=extracted_data.get("skills", []),
            experience_years=experience,
            retrieved_context=retrieved_context
        )
        
        # Store in database
        question = QuestionRepository.create(
            db=db,
            session_id=session_id,
            question_number=question_number,
            question_text=question_data.get("question", ""),
            topic=topic,
            difficulty=difficulty,
            retrieved_context=retrieved_context,
            context_chunks=retrieval.get("results", [])
        )
        
        return {
            "id": question.id,
            "question": question_data.get("question", ""),
            "topic": topic,
            "difficulty": difficulty,
            "question_number": question_number
        }
    
    def evaluate_answer(self, db: Session, session_id: str, question_id: str, answer: str,
                       question_text: str, topic: str, role: str,
                       reference_context: str) -> Dict:
        """Evaluate candidate's answer with adaptive tracking.
        
        Args:
            db: Database session
            session_id: Interview session ID
            question_id: Question ID
            answer: Candidate's answer
            question_text: The question
            topic: Topic
            role: Target role
            reference_context: Knowledge base context
            
        Returns:
            Evaluation result with early termination signal if applicable
        """
        evaluation = self.llm_service.evaluate_answer(
            question=question_text,
            answer=answer,
            topic=topic,
            role=role,
            reference_context=reference_context
        )
        
        # Update in database
        score = evaluation.get("score", 0.5)
        feedback = evaluation.get("feedback", "")
        
        QuestionRepository.update_answer(
            db=db,
            question_id=question_id,
            answer_text=answer,
            evaluation_score=score,
            feedback=feedback
        )
        
        # Get session for adaptive tracking
        session = SessionRepository.get_by_id(db, session_id)
        
        # Check for early termination conditions
        should_terminate = False
        termination_reason = None
        
        # IMMEDIATE TERMINATION: If score is below 5/10 (0.5 on 0-1 scale), stop immediately
        if score < 0.5:
            should_terminate = True
            termination_reason = "poor_answer_quality"
        # Also check consecutive bad answers as secondary condition
        elif score < 0.50:
            session.consecutive_bad_answers += 1
        else:
            session.consecutive_bad_answers = 0  # Reset counter on good answer
        
        # Update confidence score (exponential moving average)
        session.confidence_score = (session.confidence_score * 0.7) + (score * 0.3)
        
        # Check for low overall confidence
        if session.confidence_score < 0.30:
            should_terminate = True
            termination_reason = "insufficient_foundational_knowledge"
        
        if should_terminate:
            session.interview_terminated_early = 1
            session.termination_reason = termination_reason
            session.status = "completed"
        
        # Commit session updates
        db.commit()
        
        # Add early termination flag to response if applicable
        if should_terminate:
            evaluation["interview_terminated"] = True
            evaluation["termination_reason"] = termination_reason
        
        return evaluation
    
    def generate_session_summary(self, db: Session, session_id: str) -> Dict:
        """Generate comprehensive final evaluation report.
        
        Args:
            db: Database session
            session_id: Interview session ID
            
        Returns:
            Comprehensive evaluation report
        """
        session = SessionRepository.get_by_id(db, session_id)
        questions = QuestionRepository.get_by_session(db, session_id)
        
        if not questions:
            return {"error": "No questions found for session"}
        
        # Calculate metrics
        answered = [q for q in questions if q.answer_text]
        scores = [q.evaluation_score for q in answered if q.evaluation_score is not None]
        average_score = sum(scores) / len(scores) if scores else 0
        overall_score = round(average_score * 10, 1)  # Convert to 0-10 scale
        
        # Determine hiring recommendation
        if overall_score >= 7.5:
            hiring_recommendation = "Strong Hire"
        elif overall_score >= 6.0:
            hiring_recommendation = "Hire"
        elif overall_score >= 4.5:
            hiring_recommendation = "Borderline"
        else:
            hiring_recommendation = "No Hire"
        
        # Build topic-wise breakdown
        topic_breakdown = {}
        for q in answered:
            topic = q.topic
            if topic not in topic_breakdown:
                topic_breakdown[topic] = {
                    "questions": [],
                    "scores": [],
                    "observations": "",
                    "suggestions": ""
                }
            
            score = q.evaluation_score or 0
            topic_breakdown[topic]["questions"].append(q.question_text)
            topic_breakdown[topic]["scores"].append(score)
        
        # Generate topic summaries and suggestions
        strengths = []
        weaknesses = []
        
        for topic, data in topic_breakdown.items():
            avg_topic_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            data["score"] = round(avg_topic_score * 10, 1)
            
            if avg_topic_score > 0.7:
                strengths.append(topic)
                data["observations"] = f"Strong understanding of {topic}. Demonstrated solid knowledge and practical awareness."
                data["suggestions"] = "Continue building expertise in this area."
            elif avg_topic_score > 0.5:
                data["observations"] = f"Fair understanding of {topic}. Covers fundamentals but needs more depth."
                data["suggestions"] = f"Study advanced concepts in {topic} and practice real-world scenarios."
            else:
                weaknesses.append(topic)
                data["observations"] = f"Limited understanding of {topic}. Missing key concepts."
                data["suggestions"] = f"Review {topic} fundamentals and focus on core concepts."
        
        # Communication assessment based on feedback patterns
        communication_assessment = {
            "clarity": "Good" if average_score > 0.6 else "Fair",
            "technical_vocabulary": "Strong" if average_score > 0.7 else "Adequate" if average_score > 0.5 else "Needs Work",
            "explanation_quality": "Excellent" if average_score > 0.75 else "Good" if average_score > 0.6 else "Fair"
        }
        
        # Generate learning path based on weaknesses
        learning_path = []
        learning_priority = {
            "Machine Learning Fundamentals": ["Feature Engineering", "Model Evaluation Metrics"],
            "Feature Engineering": ["Data Preprocessing", "Model Evaluation Metrics"],
            "System Design Fundamentals": ["Scalability and Load Balancing", "Distributed Systems"],
            "Database Optimization": ["System Design Fundamentals", "Distributed Systems"],
            "Neural Networks": ["Deep Learning Architectures", "Computer Vision"],
            "NLP Techniques": ["Deep Learning Architectures", "Neural Networks"],
            "API Design Patterns": ["System Design Fundamentals", "Scalability and Load Balancing"],
        }
        
        for weak in weaknesses:
            learning_path.append({
                "topic": weak,
                "priority": "High",
                "suggested_resources": "Study fundamentals, practice with real-world datasets, implement from scratch",
                "prerequisites": learning_priority.get(weak, [])
            })
        
        # Build summary text
        summary_text = f"""
Interview Summary for {session.candidate_name}

Position: {session.role}
Total Questions: {len(questions)}
Questions Answered: {len(answered)}
Overall Score: {overall_score}/10
Hiring Recommendation: {hiring_recommendation}

Interview {("ended early due to: " + (session.termination_reason or "insufficient knowledge")) if session.interview_terminated_early else "completed successfully"}.

Technical Strengths:
{', '.join(strengths) if strengths else 'None identified'}

Technical Weaknesses:
{', '.join(weaknesses) if weaknesses else 'None identified'}

Communication Clarity: {communication_assessment["clarity"]}
Technical Vocabulary: {communication_assessment["technical_vocabulary"]}
Explanation Quality: {communication_assessment["explanation_quality"]}

Recommendation: {hiring_recommendation}
"""
        
        # Create comprehensive report
        report = {
            "session_id": session_id,
            "role": session.role,
            "candidate_name": session.candidate_name,
            "total_questions": len(questions),
            "questions_answered": len(answered),
            "average_score": average_score,
            "overall_score": overall_score,
            "hiring_recommendation": hiring_recommendation,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "topic_wise_breakdown": topic_breakdown,
            "communication_assessment": communication_assessment,
            "learning_path": learning_path,
            "summary": summary_text,
            "early_termination": session.interview_terminated_early == 1,
            "termination_reason": session.termination_reason,
            "questions_and_answers": [
                {
                    "question": q.question_text,
                    "topic": q.topic,
                    "difficulty": q.difficulty,
                    "score": q.evaluation_score,
                    "answer": q.answer_text,
                    "feedback": q.feedback,
                    "answered": q.answer_text is not None
                }
                for q in questions
            ]
        }
        
        # Store evaluation
        SessionEvaluationRepository.create(
            db=db,
            session_id=session_id,
            total_questions=len(questions),
            total_answered=len(answered),
            average_score=average_score,
            overall_score=overall_score,
            hiring_recommendation=hiring_recommendation,
            strengths=strengths,
            weaknesses=weaknesses,
            topic_wise_breakdown=topic_breakdown,
            communication_assessment=communication_assessment,
            learning_path=learning_path,
            summary=summary_text,
            early_termination=1 if session.interview_terminated_early else 0,
            termination_reason=session.termination_reason,
            recommendations=f"Recommended action: {hiring_recommendation}"
        )
        
        return report
