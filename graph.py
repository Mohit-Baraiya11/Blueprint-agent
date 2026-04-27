from langgraph.graph import StateGraph, END, START
from state import ProjectBlueprintState
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver


MAX_ITERATIONS = 5

# import functions from each agent file (you'll create these next)
from agents.orchestrator import orchestrator_node
from agents.clarification_agent import clarification_node
from agents.hitl_node import hitl_node
from agents.validation_agent import validation_node
from agents.architecture_agent import architecture_node
from agents.stack_agent import stack_node
from agents.execution_agent import execution_node
from agents.blueprint_generator import blueprint_node
import os

def route_after_clarification(state: ProjectBlueprintState) -> str:
    if state["needs_human_input"]:
        return "hitl_node"
    return "validation_agent"

def build_graph():
    builder = StateGraph(ProjectBlueprintState)

    # nodes
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("clarification_agent", clarification_node)
    builder.add_node("hitl_node", hitl_node)
    builder.add_node("validation_agent", validation_node)
    builder.add_node("architecture_agent", architecture_node)
    builder.add_node("stack_agent", stack_node)
    builder.add_node("execution_agent", execution_node)
    builder.add_node("blueprint_generator", blueprint_node)

    # edges
    builder.add_edge(START, "orchestrator")
    builder.add_edge("orchestrator", "clarification_agent")
    builder.add_conditional_edges(
        "clarification_agent",
        route_after_clarification,
        {
            "hitl_node": "hitl_node",
            "validation_agent": "validation_agent"
        }
    )
    builder.add_edge("hitl_node", "validation_agent")
    builder.add_edge("validation_agent", "architecture_agent")
    builder.add_edge("architecture_agent", "stack_agent")
    builder.add_edge("stack_agent", "execution_agent")
    builder.add_edge("execution_agent", "blueprint_generator")
    builder.add_edge("blueprint_generator", END)

    os.makedirs("checkpoints", exist_ok=True)
    conn = sqlite3.connect("checkpoints/blueprints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)


    return builder.compile(checkpointer=checkpointer)
if __name__ == "__main__":
    graph = build_graph()
    print("✅ Graph compiled successfully")
    print("Nodes:", list(graph.nodes.keys()))    