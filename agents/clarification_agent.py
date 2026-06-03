import os
from functools import lru_cache
from dotenv import load_dotenv
from state import ProjectBlueprintState
from pydantic import BaseModel


load_dotenv()


class ClarificationOutput(BaseModel):
    is_clear: bool
    clarified_idea: str
    questions: list[str]

@lru_cache(maxsize=1)
def get_chain():
    from langchain_groq import ChatGroq
    from langchain_core.output_parsers import PydanticOutputParser

    parser = PydanticOutputParser(
        pydantic_object=ClarificationOutput
    )

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )
    return llm | parser

SYSTEM_PROMPT = """
You are a product analyst. Analyze the project idea and find gaps.
Return ONLY a JSON object with this structure:
{
    "is_clear": true/false,
    "clarified_idea": "your understanding in 2-3 sentences",
    "questions": ["question 1", "question 2"]
}
If clear, set questions to [].
Return ONLY JSON. No explanation.
"""

def clarification_node(state: ProjectBlueprintState) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage

    print(f"{state['current_agent']} is running....")
    chain = get_chain()

    response = chain.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Idea : {state['raw_idea']}")
    ])
    return {
        "clarified_idea": response.clarified_idea,
        "clarification_questions": response.questions,
        "needs_human_input": len(response.questions) > 0,
        "current_agent": "hitl_node" if len(response.questions) > 0 else "validation_agent",
    }
