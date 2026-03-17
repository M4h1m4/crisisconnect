import uuid
from typing import Optional
from app.models.schemas import ARCoreLocation, AuthorityNotification


def process_arcore_location(
    arcore_location: Optional[ARCoreLocation],
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> dict:
    """Process ARCore location data and return standardized location dict."""
    
    if arcore_location:
        return {
            "latitude": arcore_location.latitude,
            "longitude": arcore_location.longitude,
            "altitude": arcore_location.altitude,
            "horizontal_accuracy": arcore_location.horizontal_accuracy,
            "vertical_accuracy": arcore_location.vertical_accuracy,
            "source": "arcore",
        }
    elif latitude and longitude:
        return {
            "latitude": latitude,
            "longitude": longitude,
            "altitude": None,
            "horizontal_accuracy": None,
            "vertical_accuracy": None,
            "source": "gps",
        }
    else:
        return None


async def notify_authorities(
    crisis_type: str,
    location: dict,
    description: Optional[str] = None,
    image_url: Optional[str] = None,
) -> AuthorityNotification:
    """Mock function to notify authorities (police, fire, ambulance) of crisis."""
    
    notification_id = str(uuid.uuid4())[:8]
    
    authority_mapping = {
        "fire": "Fire Department",
        "medical": "Emergency Medical Services (EMS)",
        "emergency": "Police Department",
        "accident": "Police + Fire + EMS",
        "default": "Police Department",
    }
    
    authorities = authority_mapping.get(crisis_type, authority_mapping["default"])
    
    location_str = f"{location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}"
    accuracy = location.get('horizontal_accuracy')
    if accuracy:
        location_str += f" (accuracy: {accuracy:.1f}m)"
    
    message = (
        f"CRISIS ALERT - {crisis_type.upper()}\n"
        f"Location: {location_str}\n"
        f"Description: {description or 'No description provided'}\n"
        f"Notifying: {authorities}\n"
        f"Notification ID: {notification_id}"
    )
    
    return AuthorityNotification(
        authorities_notified=True,
        notification_id=notification_id,
        message=f"Authorities have been notified. {authorities} are being dispatched to your location.",
        location_sent=location,
    )


async def analyze_image_for_crisis(
    description: Optional[str] = None,
) -> dict:
    """Use LLM to analyze image description and determine crisis type."""
    
    if not description:
        return {
            "crisis_type": "unknown",
            "severity": "unknown",
            "confidence": 0.0,
            "description": "No image or description provided",
        }
    
    from app.agent.nodes import _get_llm
    
    prompt = (
        "Analyze this crisis situation and classify it.\n\n"
        "Crisis types:\n"
        "- fire: smoke, flames, building on fire\n"
        "- medical: person unconscious, injured, bleeding, sick\n"
        "- accident: car crash, vehicle accident, collision\n"
        "- emergency: danger, assault, person in distress, life-threatening\n"
        "- general: non-emergency, unclear situation\n\n"
        "Severity levels:\n"
        "- critical: immediate danger to life, needs urgent response\n"
        "- high: serious situation, needs prompt response\n"
        "- moderate: needs attention but not immediately dangerous\n"
        "- low: minor situation\n\n"
        f"Situation description: {description}\n\n"
        "Respond with ONLY the crisis type and severity in this format:\n"
        "crisis_type: <type>\n"
        "severity: <severity>"
    )
    
    response = _get_llm().invoke(prompt)
    content = response.content.lower()
    
    crisis_type = "general"
    severity = "moderate"
    
    for ct in ["fire", "medical", "accident", "emergency"]:
        if ct in content:
            crisis_type = ct
            break
    
    if "critical" in content:
        severity = "critical"
    elif "high" in content:
        severity = "high"
    elif "moderate" in content:
        severity = "moderate"
    elif "low" in content:
        severity = "low"
    
    return {
        "crisis_type": crisis_type,
        "severity": severity,
        "confidence": 0.85,
        "description": description,
    }
