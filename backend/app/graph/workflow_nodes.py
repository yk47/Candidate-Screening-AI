"""Workflow nodes for LangGraph state machine."""

from typing import Any
from ..graph.state import InterviewState, WorkflowStatus
from ..services.interview_service import InterviewService


class WorkflowNodes:
    """Nodes for the interview workflow graph."""
    
    def __init__(self):
        """Initialize workflow nodes."""
        self.interview_service = InterviewService()
    
    def parse_resume_node(self, state: InterviewState) -> InterviewState:
        """Parse candidate resume and extract information.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with parsed resume data
        """
        try:
            extracted = self.interview_service.parse_resume(state.resume_text)
            
            state.extracted_skills = extracted.get("skills", [])
            state.extracted_technologies = extracted.get("technologies", [])
            state.experience_years = extracted.get("experience_years", 0)
            state.domain_exposure = extracted.get("domain_exposure", [])
            
            state.status = WorkflowStatus.RESUME_PARSED
            return state
        except Exception as e:
            state.status = WorkflowStatus.ERROR
            state.error_message = f"Error parsing resume: {str(e)}"
            return state
    
    def generate_topics_node(self, state: InterviewState) -> InterviewState:
        """Generate interview topics based on resume and role.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with topics
        """
        try:
            extracted_data = {
                "skills": state.extracted_skills,
                "technologies": state.extracted_technologies,
                "experience_years": state.experience_years,
                "domain_exposure": state.domain_exposure,
                "resume_text": state.resume_text
            }
            
            topics = self.interview_service.generate_topics(extracted_data, state.role)
            state.topics = topics
            state.status = WorkflowStatus.TOPICS_GENERATED
            
            return state
        except Exception as e:
            state.status = WorkflowStatus.ERROR
            state.error_message = f"Error generating topics: {str(e)}"
            return state
    
    def retrieve_context_node(self, state: InterviewState) -> InterviewState:
        """Retrieve relevant context for the current topic.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with retrieved context
        """
        try:
            if state.current_topic_index >= len(state.topics):
                state.status = WorkflowStatus.COMPLETED
                return state
            
            current_topic = state.topics[state.current_topic_index]
            state.current_topic = current_topic
            
            # Enhance query with resume data
            enhanced_query = self.interview_service.rag_retriever.enhance_query(
                state.resume_text,
                current_topic,
                state.role
            )
            
            # Retrieve context
            retrieval = self.interview_service.rag_retriever.retrieve_context(
                state.role,
                enhanced_query,
                k=5
            )
            
            state.retrieved_context = retrieval.get("context", "")
            state.context_chunks = retrieval.get("results", [])
            state.status = WorkflowStatus.CONTEXT_RETRIEVED
            
            return state
        except Exception as e:
            state.status = WorkflowStatus.ERROR
            state.error_message = f"Error retrieving context: {str(e)}"
            return state
    
    def generate_question_node(self, state: InterviewState) -> InterviewState:
        """Generate interview question.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with generated question
        """
        try:
            extracted_data = {
                "skills": state.extracted_skills,
                "technologies": state.extracted_technologies,
                "experience_years": state.experience_years,
                "domain_exposure": state.domain_exposure,
                "resume_text": state.resume_text
            }
            
            # Determine difficulty
            if state.experience_years < 2:
                difficulty = "beginner"
            elif state.experience_years < 5:
                difficulty = "intermediate"
            else:
                difficulty = "advanced"
            
            state.current_difficulty = difficulty
            
            # Generate question
            question_data = self.interview_service.llm_service.generate_question(
                topic=state.current_topic,
                role=state.role,
                difficulty=difficulty,
                skills=state.extracted_skills,
                experience_years=state.experience_years,
                retrieved_context=state.retrieved_context
            )
            
            state.current_question_text = question_data.get("question", "")
            
            # Add to questions list
            state.add_question({
                "number": state.current_question_number,
                "text": state.current_question_text,
                "topic": state.current_topic,
                "difficulty": difficulty,
                "context": state.retrieved_context
            })
            
            state.status = WorkflowStatus.QUESTION_GENERATED
            return state
        except Exception as e:
            state.status = WorkflowStatus.ERROR
            state.error_message = f"Error generating question: {str(e)}"
            return state
    
    def evaluate_answer_node(self, state: InterviewState) -> InterviewState:
        """Evaluate candidate's answer.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with evaluation
        """
        try:
            if not state.current_answer:
                state.status = WorkflowStatus.ERROR
                state.error_message = "No answer provided"
                return state
            
            # Get reference context
            reference_context = state.retrieved_context
            
            # Evaluate answer
            evaluation = self.interview_service.llm_service.evaluate_answer(
                question=state.current_question_text,
                answer=state.current_answer,
                topic=state.current_topic,
                role=state.role,
                reference_context=reference_context
            )
            
            state.answer_score = evaluation.get("score", 0.5)
            state.answer_feedback = evaluation.get("feedback", "")
            
            # Add to answers list
            state.add_answer({
                "number": state.current_question_number,
                "text": state.current_answer,
                "score": state.answer_score,
                "feedback": state.answer_feedback
            })
            
            state.status = WorkflowStatus.ANSWER_EVALUATED
            return state
        except Exception as e:
            state.status = WorkflowStatus.ERROR
            state.error_message = f"Error evaluating answer: {str(e)}"
            return state
    
    def next_question_node(self, state: InterviewState) -> InterviewState:
        """Prepare for next question or complete interview.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        state.current_question_number += 1
        state.current_topic_index += 1
        state.current_answer = ""
        
        if state.should_continue_interview():
            # Prepare for next question
            state.status = WorkflowStatus.STARTED
        else:
            # Calculate average score and finalize
            state.calculate_average_score()
            state.status = WorkflowStatus.COMPLETED
        
        return state
