from app.core.config import settings

class AgentService:
    BASE_URL = settings.BASE_URL
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.CUSTOMGPT_API_KEY}",
            "Content-Type": "application/json"
        }
    