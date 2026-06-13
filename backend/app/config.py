from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    model_name: str = "gpt-4o-mini"
    supabase_url: Optional[str] = None
    supabase_service_role_key: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
