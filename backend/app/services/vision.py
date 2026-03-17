import base64
import httpx
from app.config import settings


async def analyze_image_with_vision(image_data: str, crisis_type: str = "general") -> dict:
    """
    Analyze an image using NVIDIA Nemotron Nano 12B 2 VL via OpenRouter.
    Returns analysis of what's happening and how to navigate to safety.
    """
    
    prompt = """You are a crisis assistant. Analyze this image and provide:
1. WHAT IS HAPPENING - Describe the crisis situation you see (fire, accident, medical emergency, etc.)
2. SEVERITY - Is it critical, high, moderate, or low?
3. IMMEDIATE ACTIONS - What should the person do right now to stay safe?
4. HOW TO EXIT/ESCAPE - Specific directions on how to navigate away from danger

Be concise but thorough. Focus on life-safety first."""

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    ]

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.openrouter_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.vision_model_name,
                "messages": messages,
                "max_tokens": 1024,
            }
        )

    if response.status_code != 200:
        error = response.json()
        raise Exception(f"Vision API error: {error}")

    result = response.json()
    return {
        "analysis": result["choices"][0]["message"]["content"],
        "model": settings.vision_model_name,
    }


def encode_image_to_base64(image_bytes: bytes) -> str:
    """Encode image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")
