from state import ProjectBlueprintState
import os
from functools import lru_cache
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Union

load_dotenv()

class ArchitectureOutput(BaseModel):
    components: list[str]
    db_schema: Union[dict, str]
    api_routes: list[str]
    svg_diagram: str

@lru_cache(maxsize=1)
def get_chain():
    from langchain_groq import ChatGroq
    from langchain_core.output_parsers import PydanticOutputParser

    parser = PydanticOutputParser(pydantic_object=ArchitectureOutput)

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    return llm | parser

def architecture_node(state:ProjectBlueprintState)->dict:
    from langchain_core.messages import HumanMessage, SystemMessage

    SYSTEM_PROMPT = """You are a software architect.
        Analyze the project idea and generate a complete system architecture.

        Return ONLY a JSON object with this structure:
        {
            "components": ["component1", "component2"],
            "db_schema": "describe tables and fields here",
            "api_routes": ["GET /route1", "POST /route2"],
            "svg_diagram": "<svg>...</svg>"
        }

        For the svg_diagram:
        - dark background ___
        - colored boxes for each component
        - arrows showing connections between them
        - white text labels
        - width 600, height 400

        Return ONLY JSON. No explanation.
        """
    result = get_chain().invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
        Project Idea: {state['clarified_idea']}
        
            Validation Result: {state['validation_result']}
            Competitors found: {state['competitors']}
            Unique angle: {state['unique_angle']}
            
            Generate the complete architecture for this project.
        """)
    ])
    return {
    "architecture": {
        "components": result.components,
        "db_schema": result.db_schema,
        "api_routes": result.api_routes,
        "svg_diagram": result.svg_diagram,
        },
        "current_agent": "stack_agent",
    }    
