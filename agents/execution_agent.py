from state import ProjectBlueprintState
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()
class ExecutionOutput(BaseModel):
    phases: list[dict]      # [{"name": "Phase 1", "duration": "2 weeks", "tasks": [...]}]
    mvp_scope: str
    timeline_weeks: int
    risks: list[str]

parser = PydanticOutputParser(pydantic_object=ExecutionOutput)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
chain = llm | parser
def execution_node(state: ProjectBlueprintState) -> dict:
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

    response = chain.invoke([
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