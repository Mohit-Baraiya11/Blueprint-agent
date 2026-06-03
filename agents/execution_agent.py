from state import ProjectBlueprintState
import os
from functools import lru_cache
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
class ExecutionOutput(BaseModel):
    phases: list[dict]      # [{"name": "Phase 1", "duration": "2 weeks", "tasks": [...]}]
    mvp_scope: str
    timeline_weeks: int
    risks: list[str]

@lru_cache(maxsize=1)
def get_parser():
    from langchain_core.output_parsers import PydanticOutputParser

    return PydanticOutputParser(pydantic_object=ExecutionOutput)

@lru_cache(maxsize=1)
def get_chain():
    from langchain_groq import ChatGroq
    parser = get_parser()

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
    return llm | parser

def execution_node(state: ProjectBlueprintState) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage
    parser = get_parser()
    SYSTEM_PROMPT = f"""
        You are a project manager and technical mentor.
        Analyze the project idea, architecture, stack, and user's skill level.
        Create a realistic, week-by-week execution plan for an MVP.
        Include risks and scope limitations.

        Return JSON matching this schema:
        {parser.get_format_instructions()}
        """

    project_summary = f"""
    PROJECT IDEA: {state['clarified_idea']}
    ARCHITECTURE: {state['architecture']}
    TECH STACK: {state['tech_stack']}
    USER SKILL LEVEL: {state['skill_level']}
    """

    response = get_chain().invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=project_summary)
    ])

    return {
        "execution_plan": {
            "phases": response.phases,
            "mvp_scope": response.mvp_scope,
            "timeline_weeks": response.timeline_weeks,
        },
        "risks": response.risks,
        "current_agent": "blueprint_generator"
    }
if __name__ == "__main__":
    initial_state = {
        "clarified_idea": "An app where students find study partners nearby",
        "architecture": {"components": ["Auth", "Matching", "Location"]},
        "tech_stack": {"frontend": "React", "backend": "FastAPI", "database": "Supabase"},
        "skill_level": "beginner"
    }
    result = execution_node(initial_state)
    print(result)    
