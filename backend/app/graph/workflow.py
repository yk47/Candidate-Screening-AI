"""LangGraph workflow orchestration."""

from typing import Dict, Optional
from ..graph.state import InterviewState, WorkflowStatus
from ..graph.workflow_nodes import WorkflowNodes

try:
    from langgraph.graph import StateGraph
except ImportError:
    StateGraph = None


class InterviewWorkflow:
    """LangGraph workflow for interview orchestration."""
    
    def __init__(self):
        """Initialize workflow."""
        self.nodes = WorkflowNodes()
        
        if StateGraph:
            self.graph = self._build_graph()
        else:
            self.graph = None
    
    def _build_graph(self):
        """Build the LangGraph state machine.
        
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(InterviewState)
        
        # Add nodes
        workflow.add_node("parse_resume", self.nodes.parse_resume_node)
        workflow.add_node("generate_topics", self.nodes.generate_topics_node)
        workflow.add_node("retrieve_context", self.nodes.retrieve_context_node)
        workflow.add_node("generate_question", self.nodes.generate_question_node)
        workflow.add_node("evaluate_answer", self.nodes.evaluate_answer_node)
        workflow.add_node("next_question", self.nodes.next_question_node)
        
        # Set entry point
        workflow.set_entry_point("parse_resume")
        
        # Add edges
        workflow.add_edge("parse_resume", "generate_topics")
        workflow.add_edge("generate_topics", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_question")
        workflow.add_edge("generate_question", "evaluate_answer")
        workflow.add_edge("evaluate_answer", "next_question")
        
        # Add conditional edge
        workflow.add_conditional_edges(
            "next_question",
            self._should_continue,
            {
                "continue": "retrieve_context",
                "end": "parse_resume"  # Dummy end node
            }
        )
        
        # Set finish point
        workflow.set_finish_point("next_question")
        
        return workflow.compile()
    
    def _should_continue(self, state: InterviewState) -> str:
        """Determine if interview should continue.
        
        Args:
            state: Current workflow state
            
        Returns:
            'continue' or 'end'
        """
        if state.should_continue_interview():
            return "continue"
        else:
            return "end"
    
    def run_interview(self, initial_state: InterviewState) -> Dict:
        """Run the interview workflow.
        
        Args:
            initial_state: Initial interview state
            
        Returns:
            Final state and results
        """
        if not self.graph:
            return {
                "error": "LangGraph not available",
                "status": "error"
            }
        
        try:
            # Execute the workflow
            final_state = self.graph.invoke(initial_state)
            
            return {
                "status": final_state.status.value,
                "session_id": final_state.session_id,
                "questions_asked": len(final_state.questions_asked),
                "answers_received": len(final_state.answers_received),
                "average_score": final_state.average_score,
                "error": final_state.error_message
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    def parse_resume(self, state: InterviewState) -> InterviewState:
        """Parse resume step."""
        return self.nodes.parse_resume_node(state)
    
    def generate_topics(self, state: InterviewState) -> InterviewState:
        """Generate topics step."""
        return self.nodes.generate_topics_node(state)
    
    def retrieve_context(self, state: InterviewState) -> InterviewState:
        """Retrieve context step."""
        return self.nodes.retrieve_context_node(state)
    
    def generate_question(self, state: InterviewState) -> InterviewState:
        """Generate question step."""
        return self.nodes.generate_question_node(state)
    
    def evaluate_answer(self, state: InterviewState) -> InterviewState:
        """Evaluate answer step."""
        return self.nodes.evaluate_answer_node(state)
    
    def next_question(self, state: InterviewState) -> InterviewState:
        """Next question step."""
        return self.nodes.next_question_node(state)
