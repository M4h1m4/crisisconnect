from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str
    google_maps_api_key: str
    model_name: str = "nvidia/nemotron-3-super-120b-a12b:free"
    vision_model_name: str = "nvidia/nemotron-nano-12b-v2-vl:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    class Config:
        env_file = ".env"


settings = Settings()
