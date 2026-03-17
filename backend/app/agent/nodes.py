from langchain_openai import ChatOpenAI
from app.config import settings
from app.agent.state import AgentState
from app.tools.google_geocode import geocode_location
from app.tools.google_places import search_nearby_resources

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


def classify_intent(state: AgentState) -> dict:
    """Determine what kind of help the user needs."""
    print(f"[DEBUG] classify_intent called with: {state['user_message']}")
    prompt = (
        "Classify the user's emergency need into exactly ONE category.\n\n"
        "Categories:\n"
        "- food: hungry, need food, haven't eaten, food bank\n"
        "- shelter: need a place to sleep, homeless, need housing, cold outside\n"
        "- medical: sick, injured, dizzy, fainted, bleeding, need doctor\n"
        "- emergency: in danger, assault, fire, someone collapsed, life-threatening\n"
        "- general: greeting, question, unclear need\n\n"
        f'User message: "{state["user_message"]}"\n\n'
        "Respond with ONLY the category name (food/shelter/medical/emergency/general), nothing else."
    )

    print(f"[DEBUG] Calling LLM for intent classification...")
    response = _get_llm().invoke(prompt)
    print(f"[DEBUG] LLM response received: {response.content[:50]}...")
    intent = response.content.strip().lower()

    valid = {"food", "shelter", "medical", "emergency", "general"}
    if intent not in valid:
        intent = "general"

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
    """Search for nearby resources based on intent and location."""
    if not state.get("location_resolved") or not state.get("user_lat"):
        return {"resources": []}

    if state["intent"] == "general":
        return {"resources": []}

    resources = search_nearby_resources(
        latitude=state["user_lat"],
        longitude=state["user_lng"],
        category=state["intent"],
    )

    return {"resources": [r.model_dump() for r in resources]}


def generate_response(state: AgentState) -> dict:
    """Generate a helpful, direct emergency assistant with resource information."""
    resources = state.get("resources", [])
    intent = state.get("intent", "general")

    if not state.get("location_resolved"):
        return {
            "response": (
                "I want to help you find resources nearby. "
                "Could you share your location? You can either click the "
                "location button or tell me where you are (e.g., 'near SJSU')."
            )
        }

    if intent == "general":
        prompt = (
            "You are CrisisConnect, an empathetic emergency resource assistant.\n"
            f'The user sent: "{state["user_message"]}"\n'
            "Respond helpfully. Let them know you can help find food, shelter, "
            "medical care, or emergency services.\n"
            "Keep it brief and warm (2-3 sentences)."
        )
        response = _get_llm().invoke(prompt)
        return {"response": response.content}

    if not resources:
        return {
            "response": (
                f"I wasn't able to find {intent} resources near your location. "
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

    emergency_note = ""
    if intent in ("medical", "emergency"):
        emergency_note = (
            "IMPORTANT: If this is a medical emergency or someone is in danger, "
            "start by telling them to call 911 immediately.\n"
        )

    prompt = (
        "You are CrisisConnect, a direct emergency resource assistant.\n"
        f"The user needs: {intent} resources.\n"
        f'User message: "{state["user_message"]}"\n\n'
        f"{emergency_note}"
        f"Resources found:\n{resource_text}\n"
        "Rules:\n"
        "- Be extremely concise. No filler, no fluff, no preamble.\n"
        "- Lead with the top recommendation and its address.\n"
        "- Mention open/closed status if available.\n"
        "- Give one actionable next step (direction, phone call, etc.).\n"
        "- List remaining resources briefly (name + address only).\n"
        "- Do NOT use markdown. Plain text only.\n"
        "- Maximum 3-4 short lines total."
    )

    response = _get_llm().invoke(prompt)
    return {"response": response.content}
