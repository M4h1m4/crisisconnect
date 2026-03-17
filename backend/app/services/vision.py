import base64
import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)


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

    logger.info(f"[Vision] Calling OpenRouter with model: {settings.vision_model_name}")
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
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

        logger.info(f"[Vision] Response status: {response.status_code}")
        
        if response.status_code != 200:
            error = response.text
            logger.error(f"[Vision] API error: {error}")
            raise Exception(f"Vision API error: {error}")

        result = response.json()
        
        if "choices" not in result:
            logger.error(f"[Vision] No choices in response: {result}")
            raise Exception(f"Invalid response from Vision API: {result}")
        
        analysis = result["choices"][0]["message"]["content"]
        logger.info(f"[Vision] Analysis received: {analysis[:100]}...")
        
        return {
            "analysis": analysis,
            "model": settings.vision_model_name,
        }
    except Exception as e:
        logger.error(f"[Vision] Exception: {str(e)}")
        raise


def encode_image_to_base64(image_bytes: bytes) -> str:
    """Encode image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")
