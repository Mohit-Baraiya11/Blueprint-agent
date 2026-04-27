from langgraph.types import interrupt
from state import ProjectBlueprintState

def hitl_node(state: ProjectBlueprintState):
    """Interrupt node"""
    questions = state["clarification_questions"]

    if not questions:
        return {
            "needs_human_input": False,
            "current_agent": "validation_agent"
            }
    answers = interrupt({"questions": questions})        

    return {
        "needs_human_input": False,
        "user_answers": answers,
        "current_agent": "validation_agent"
    }