from state import ProjectBlueprintState
import os
from functools import lru_cache
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class StackOutput(BaseModel):
    frontend: str
    backend: str
    database: str
    infra: str
    reasons: dict        # {"frontend": "why", "backend": "why"...}
    learning_gaps: list[str]

@lru_cache(maxsize=1)
def get_chain():
    from langchain_groq import ChatGroq
    from langchain_core.output_parsers import PydanticOutputParser

    parser = PydanticOutputParser(pydantic_object=StackOutput)

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    return llm | parser

def stack_node(state: ProjectBlueprintState) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage

    SYSTEM_PROMPT = """
        You are a senior software architect and technical mentor.

        Analyze the project idea, architecture, and user's technical background.

        Choose a COMPLETE tech stack:
        - Frontend framework
        - Backend framework
        - Database system
        - Deployment/infra strategy

        CRITICAL: Include learning_gaps based on the user's background.

        Return ONLY JSON with structure:
        {
            "frontend": "...",
            "backend": "...",
            "database": "...",
            "infra": "...",
            "reasons": {"frontend": "why", "backend": "why", "database": "why", "infra": "why"},
            "learning_gaps": ["...", "..."]
        }
        """


    result = get_chain().invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
        Project Idea: {state['clarified_idea']}
        Architecture: {state['architecture']}
        Developer skill level: {state['skill_level']}
        Recommend stack based on their skill level. Avoid over-engineering for beginners.
        """)
    ])
    return {
        "tech_stack": {
            "frontend": result.frontend,
            "backend": result.backend,
            "database": result.database,
            "infra": result.infra,
            "reasons": result.reasons
        },
        "learning_gaps": result.learning_gaps,
        "current_agent": "execution_agent"
    }
if __name__ == "__main__":
    initial_state = {
        "clarified_idea": "An app where students find study partners nearby based on subject and college",
        "architecture": {
            "components": ["User Auth", "Matching Service", "Location Service", "Web App"],
            "api_routes": ["POST /register", "GET /study-groups", "POST /locations"],
            "db_schema": {"users": {"id": "integer", "name": "string"}}
        },
        "skill_level": "advance"
    }
    result = stack_node(initial_state)
    print(result)    
