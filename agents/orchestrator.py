from state import ProjectBlueprintState

def orchestrator_node(state: ProjectBlueprintState) -> dict:
    print("[Orchestrator] Pipeline started.")
    print(f"Idea: {state['raw_idea'][:80]}...")

    return {
        "current_agent": "clarification_agent",
        "iteration_count": 0,
        "errors": [],
        "clarification_questions": [],
        "user_answers": [],
        "competitors": [],
        "learning_gaps": [],
        "risks": [],
    }