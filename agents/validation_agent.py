import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from state import ProjectBlueprintState

load_dotenv()

class ValidationOutput(BaseModel):
    is_valid: bool
    problem_score:int=Field(default=0, description="Scale of 0-10")
    reason: str
    competitors: list[str]
    unique_angle: str

parser = PydanticOutputParser(pydantic_object=ValidationOutput)

tavily_tool = TavilySearch(max_results=3)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
chain = llm | parser

def validation_node(state:ProjectBlueprintState)->dict:
    search_results = tavily_tool.invoke(
        f"existing apps similar to {state['clarified_idea']}"
    )

    prompt = f"""
            You are a technical validation agent.
            Your job is to determine if an idea is worth pursuing.

            User Idea: {state['clarified_idea']}

            Search Results:
            {search_results}

            Output should be a JSON object with the following fields:
            "is_valid": true or false
            "problem_score": 1-10 (1=saturated, 10=unique)
            "reason": one sentence why
            "competitors": list of 2-3 similar apps
            "unique_angle": how this is different
            "feedback": optional advice

            Respond ONLY with the JSON, no markdown.
    """
    result = chain.invoke([
        SystemMessage(content="You are a strict technical validator."),
        HumanMessage(content=prompt)
    ])

    return {
        "validation_result": {
            "is_valid": result.is_valid,
            "problem_score": result.problem_score,
            "reason": result.reason,
        },
        "competitors": result.competitors,
        "unique_angle": result.unique_angle,
        "current_agent": "architecture_agent",
    }