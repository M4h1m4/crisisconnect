from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models.schemas import ChatRequest, ChatResponse, ImageCrisisRequest, AuthorityNotification

app = FastAPI(title="CrisisConnect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    from app.agent.graph import run_agent

    result = await run_agent(request)
    return result


@app.post("/api/crisis/image", response_model=dict)
async def crisis_from_image(request: ImageCrisisRequest):
    """Handle crisis reports with image/ARCore location data."""
    from app.services.crisis import (
        process_arcore_location,
        analyze_image_for_crisis,
        notify_authorities,
    )

    location = process_arcore_location(
        request.arcore_location,
        request.latitude,
        request.longitude,
    )

    analysis = await analyze_image_for_crisis(request.description)

    if not location:
        return {
            "status": "error",
            "message": "Location data required. Please provide ARCore location or GPS coordinates.",
            "analysis": analysis,
        }

    if analysis["crisis_type"] in ["fire", "medical", "accident", "emergency"]:
        authority_notification = await notify_authorities(
            crisis_type=analysis["crisis_type"],
            location=location,
            description=request.description,
            image_url=request.image_url,
        )
    else:
        authority_notification = AuthorityNotification(
            authorities_notified=False,
            notification_id=None,
            message="Situation does not appear to require emergency authorities.",
            location_sent=location,
        )

    return {
        "status": "success",
        "analysis": analysis,
        "location": location,
        "authorities": authority_notification.model_dump(),
    }


@app.post("/api/crisis/analyze-image")
async def analyze_image(
    image: UploadFile = File(...),
    crisis_type: str = Form(default="general"),
):
    """Analyze an image using NVIDIA Vision model to detect crisis and provide exit navigation."""
    from app.services.vision import analyze_image_with_vision, encode_image_to_base64
    from app.services.crisis import process_arcore_location, notify_authorities
    from app.models.schemas import AuthorityNotification

    image_bytes = await image.read()
    base64_image = encode_image_to_base64(image_bytes)

    try:
        vision_result = await analyze_image_with_vision(base64_image, crisis_type)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to analyze image: {str(e)}",
        }

    return {
        "status": "success",
        "analysis": vision_result["analysis"],
        "model": vision_result["model"],
    }


@app.post("/api/crisis/analyze-and-guide", response_model=ChatResponse)
async def analyze_image_and_guide(
    image: UploadFile = File(...),
    latitude: Optional[float] = Form(default=None),
    longitude: Optional[float] = Form(default=None),
):
    """Analyze an image using Vision AI and provide guidance with resources."""
    from app.services.vision import analyze_image_with_vision, encode_image_to_base64

    image_bytes = await image.read()
    base64_image = encode_image_to_base64(image_bytes)

    print(f"[DEBUG] Starting vision analysis...")
    try:
        vision_result = await analyze_image_with_vision(base64_image, "general")
    except Exception as e:
        print(f"[DEBUG] Vision error: {e}")
        return ChatResponse(
            reply=f"Failed to analyze image: {str(e)}",
            resources=[],
            user_lat=latitude,
            user_lng=longitude,
        )

    analysis = vision_result["analysis"]
    print(f"[DEBUG] Vision analysis complete")

    # Create a prompt that includes the analysis and asks for resources
    prompt = f"""The user has shared an image of an emergency situation. Here is the AI visual analysis:

{analysis}

Based on this crisis situation, provide:
1. Immediate safety actions
2. Emergency resources nearby (use the location if provided: {latitude}, {longitude})
3. How to navigate to safety"""

    from app.agent.graph import run_agent
    from app.models.schemas import ChatRequest

    request = ChatRequest(
        message=prompt,
        latitude=latitude,
        longitude=longitude,
    )

    print(f"[DEBUG] Calling agent for resources...")
    try:
        result = await run_agent(request)
        print(f"[DEBUG] Agent result received")
        return result
    except Exception as e:
        print(f"[DEBUG] Agent error: {e}")
        return ChatResponse(
            reply=f"AI Analysis:\n{analysis}\n\nNote: Could not fetch nearby resources: {str(e)}",
            resources=[],
            user_lat=latitude,
            user_lng=longitude,
        )
