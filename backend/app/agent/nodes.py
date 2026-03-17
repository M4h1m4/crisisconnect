import json
from langchain_openai import ChatOpenAI
from app.config import settings
from app.agent.state import AgentState
from app.tools.google_geocode import geocode_location
from app.tools.google_places import search_by_queries

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=settings.model_name,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            temperature=0.3,
            max_tokens=1024,
        )
    return _llm


def analyze_situation(state: AgentState) -> dict:
    """Analyze the user's crisis and determine what resources to search for."""
    prompt = (
        "You are a crisis assessment AI. Analyze the user's message and determine:\n"
        "1. What category of crisis this is\n"
        "2. How urgent it is\n"
        "3. What Google Maps search queries would find helpful nearby resources\n"
        "4. Any immediate advice to give RIGHT NOW before finding resources\n\n"
        "Respond in STRICT JSON format (no markdown, no backticks):\n"
        "{\n"
        '  "category": "short label like food, shelter, medical, financial, legal, automotive, safety, general",\n'
        '  "urgency": "critical or high or medium or low",\n'
        '  "search_queries": ["query1", "query2", "query3"],\n'
        '  "immediate_advice": "One urgent action to take right now, or empty string if none"\n'
        "}\n\n"
        "Examples:\n"
        '- "I\'m hungry" → {"category": "food", "urgency": "high", "search_queries": ["food bank", "community kitchen", "soup kitchen"], "immediate_advice": ""}\n'
        '- "My wallet was stolen" → {"category": "financial", "urgency": "high", "search_queries": ["police station", "bank branch"], "immediate_advice": "Call your bank immediately to freeze your cards."}\n'
        '- "My car broke down" → {"category": "automotive", "urgency": "medium", "search_queries": ["auto repair shop", "tow truck service", "gas station"], "immediate_advice": "Turn on your hazard lights and move to a safe spot if possible."}\n'
        '- "Someone is having a seizure" → {"category": "medical", "urgency": "critical", "search_queries": ["hospital", "emergency room", "urgent care"], "immediate_advice": "Call 911 immediately. Do not restrain the person. Clear the area around them."}\n\n'
        f'User message: "{state["user_message"]}"\n\n'
        "Respond with ONLY the JSON object, nothing else."
    )

    response = _get_llm().invoke(prompt)
    raw = response.content.strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "category": "general",
            "urgency": "low",
            "search_queries": [],
            "immediate_advice": "",
        }

    return {
        "category": parsed.get("category", "general"),
        "urgency": parsed.get("urgency", "medium"),
        "search_queries": parsed.get("search_queries", [])[:4],
        "immediate_advice": parsed.get("immediate_advice", ""),
    }


def classify_crisis_intent(state: AgentState) -> dict:
    """Determine crisis type from vision AI analysis."""
    print(f"[DEBUG] classify_crisis_intent called with image analysis")
    prompt = (
        "Analyze this crisis situation description and classify it into exactly ONE emergency category.\n\n"
        "Categories:\n"
        "- fire: smoke, flames, fire, burning, fire hazard\n"
        "- medical: injured, bleeding, unconscious, sick, accident victim, trauma\n"
        "- accident: car crash, vehicle collision, traffic accident, hit and run\n"
        "- emergency: danger, assault, threat, life-threatening, crime in progress\n"
        "- general: unclear, not an emergency\n\n"
        f"Crisis description: \"{state['user_message']}\"\n\n"
        "Respond with ONLY the category name (fire/medical/accident/emergency/general), nothing else."
    )

    print(f"[DEBUG] Calling LLM for crisis intent classification...")
    response = _get_llm().invoke(prompt)
    print(f"[DEBUG] Crisis intent response: {response.content[:50]}...")
    intent = response.content.strip().lower()

    valid = {"fire", "medical", "accident", "emergency", "general"}
    if intent not in valid:
        intent = "emergency"

    return {"intent": intent}


def resolve_location(state: AgentState) -> dict:
    """Resolve user location from text if coordinates not provided."""
    if state.get("user_lat") and state.get("user_lng"):
        return {"location_resolved": True}

    prompt = (
        "Extract any location or landmark mentioned in this message.\n"
        "If there is a location, respond with ONLY the location name/address.\n"
        'If there is no location mentioned, respond with ONLY "none".\n\n'
        f'Message: "{state["user_message"]}"'
    )

    response = _get_llm().invoke(prompt)
    location_text = response.content.strip()

    if location_text.lower() == "none":
        return {"location_resolved": False}

    coords = geocode_location(location_text)
    if coords:
        return {
            "user_lat": coords["latitude"],
            "user_lng": coords["longitude"],
            "location_resolved": True,
        }

    return {"location_resolved": False}


def find_resources(state: AgentState) -> dict:
    """Search for nearby resources using LLM-generated queries."""
    if not state.get("location_resolved") or not state.get("user_lat"):
        return {"resources": []}

    queries = state.get("search_queries", [])
    if not queries:
        return {"resources": []}

    resources = search_by_queries(
        latitude=state["user_lat"],
        longitude=state["user_lng"],
        queries=queries,
        category=state.get("category", "general"),
    )

    return {"resources": [r.model_dump() for r in resources]}


def generate_response(state: AgentState) -> dict:
    """Generate a helpful response with resource information and immediate advice."""
    resources = state.get("resources", [])
    category = state.get("category", "general")
    urgency = state.get("urgency", "medium")
    immediate_advice = state.get("immediate_advice", "")

    if not state.get("location_resolved"):
        prefix = ""
        if immediate_advice:
            prefix = f"URGENT: {immediate_advice}\n\n"
        return {
            "response": (
                f"{prefix}"
                "I also want to help you find resources nearby. "
                "Could you share your location? You can either click the "
                "location button or tell me where you are (e.g., 'near SJSU')."
            )
        }

    if not resources:
        fallback = ""
        if immediate_advice:
            fallback = f"{immediate_advice}\n\n"
        return {
            "response": (
                f"{fallback}"
                f"I wasn't able to find {category} resources near your location. "
                "Try sharing a more specific location, or call 211 for local resource referrals."
            )
        }

    resource_text = ""
    for i, r in enumerate(resources, 1):
        status = ""
        if r.get("is_open") is True:
            status = " | Open now"
        elif r.get("is_open") is False:
            status = " | Currently closed"
        resource_text += f"{i}. {r['name']} — {r['address']}{status}\n"

    urgency_instruction = ""
    if urgency == "critical":
        urgency_instruction = (
            "This is CRITICAL. Lead with the most urgent action (call 911, etc). "
            "Be direct and commanding.\n"
        )
    elif urgency == "high":
        urgency_instruction = "This is urgent. Be direct and action-oriented.\n"

    advice_section = ""
    if immediate_advice:
        advice_section = f"Immediate advice to include: {immediate_advice}\n"

    prompt = (
        "You are CrisisConnect, a direct crisis resource assistant.\n"
        f"Situation: {category} (urgency: {urgency})\n"
        f'User message: "{state["user_message"]}"\n\n'
        f"{urgency_instruction}"
        f"{advice_section}"
        f"Resources found nearby:\n{resource_text}\n"
        "Rules:\n"
        "- If there is immediate advice, state it FIRST.\n"
        "- Then recommend the top resource with its address.\n"
        "- Mention open/closed status if available.\n"
        "- Give one actionable next step.\n"
        "- List remaining resources briefly.\n"
        "- Be concise. No filler. Plain text only. No markdown.\n"
        "- Maximum 5 short lines total."
    )

    response = _get_llm().invoke(prompt)
    return {"response": response.content}
