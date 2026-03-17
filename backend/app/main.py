from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

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
