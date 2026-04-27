from typing import Literal
from typing import Annotated
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
from graph import build_graph
from langgraph.types import Command
import uuid
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
graph = build_graph()


class IdeaRequest(BaseModel):
    raw_idea: str
    skill_level: Literal["beginner","intermediate","advanced"] 

class ResumeRequest(BaseModel):
    thread_id: str
    answers: list[str]
       

@app.get("/")
def root():
    return {"status": "Blueprint Agent is running"}

@app.post("/generate")
def generate(request: IdeaRequest):
    initial_state = {
        "raw_idea": request.raw_idea,
        "skill_level": request.skill_level,
    }
    thread_id = str(uuid.uuid4())
    config = {
        'configurable':{'thread_id':thread_id}
    }
    result = graph.invoke(initial_state,config=config)
    snapshot = graph.get_state(config)
    if snapshot.next:
        if snapshot.tasks and snapshot.tasks[0].interrupts:
            interrupt_data = snapshot.tasks[0].interrupts[0].value
            return {    
            'status': "clarification_needed",
            "thread_id": thread_id,
            "questions": interrupt_data.get("questions", [])
        }
        return {'status': "paused", "thread_id": thread_id} 
    pdf_bytes = result.get("blueprint_pdf_bytes", b"")
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=blueprint.pdf"}
    )    

@app.post('/resume')
def resume(request: ResumeRequest):
    thread_id = request.thread_id
    config = {'configurable': {'thread_id': thread_id}}
    
    result = graph.invoke(
        Command(resume=request.answers),
        config=config
    )
    pdf_bytes = result.get("blueprint_pdf_bytes", b"")
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=blueprint.pdf"}
    )