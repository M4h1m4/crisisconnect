from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes import (
    classify_intent,
    resolve_location,
    find_resources,
    generate_response,
)
from app.models.schemas import ChatRequest, ChatResponse, Resource


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("resolve_location", resolve_location)
    graph.add_node("find_resources", find_resources)
    graph.add_node("generate_response", generate_response)

    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "resolve_location")
    graph.add_edge("resolve_location", "find_resources")
    graph.add_edge("find_resources", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile()


_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        _agent = build_graph()
    return _agent


async def run_agent(request: ChatRequest) -> ChatResponse:
    print(f"[DEBUG] Starting agent with message: {request.message}")
    initial_state: AgentState = {
        "user_message": request.message,
        "user_lat": request.latitude,
        "user_lng": request.longitude,
        "intent": "",
        "location_resolved": False,
        "resources": [],
        "response": "",
    }

    print(f"[DEBUG] Invoking agent...")
    result = _get_agent().invoke(initial_state)
    print(f"[DEBUG] Agent invocation complete")

    resources = [Resource(**r) for r in result.get("resources", [])]

    return ChatResponse(
        reply=result["response"],
        resources=resources,
        user_lat=result.get("user_lat"),
        user_lng=result.get("user_lng"),
    )
