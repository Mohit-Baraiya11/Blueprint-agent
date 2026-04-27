from typing import TypedDict


class ProjectBlueprintState(TypedDict):
    # INPUT
    raw_idea: str
    skill_level: str    # "beginner", "intermediate", "advanced"

    # CLARIFICATION
    clarification_questions: list[str]
    needs_human_input: bool
    user_answers: list[str]
    clarified_idea: str

    # VALIDATION
    validation_result: dict     
    competitors: list[str]
    unique_angle: str

    # ARCHITECTURE
    architecture: dict          

    # STACK
    tech_stack: dict            
    learning_gaps: list[str]

    # EXECUTION
    execution_plan: dict       
    risks: list[str]

    # OUTPUT
    blueprint_markdown: str
    blueprint_pdf_bytes: bytes


    # CONTROL
    current_agent: str
    errors: list[str]          
    iteration_count: int