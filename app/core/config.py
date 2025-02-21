from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # CustomGPT settings
    CUSTOMGPT_API_KEY: str
    CUSTOMGPT_AGENT_ID: str
    WATCH_FOLDER: str = "./watch_folder"
    BASE_URL: str = "https://app.customgpt.ai/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()