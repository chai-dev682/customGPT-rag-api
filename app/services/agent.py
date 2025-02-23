from sseclient import SSEClient
from typing import Dict, Any
import requests
import json
import os
from app.core.config import settings

class AgentService:
    BASE_URL = settings.BASE_URL
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.CUSTOMGPT_API_KEY}",
            "Content-Type": "application/json"
        }
    
    def list_agents(self) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/projects"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return json.loads(response.text)["data"]
    
    def create_agent(self, project_name: str, file_path: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/projects"

        with open(file_path, 'rb') as f:
            file_data = {'file': (os.path.basename(file_path), f)}
        
        payload = {
            "project_name": (None, project_name),
            "file": file_data
        }
        response = requests.post(url, headers=self.headers, files=payload)
        # return the project id
        return json.loads(response.text)["data"]["id"]
    
    # Check status of the project if chat bot is active
    def check_agent_status(self, project_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/projects/{project_id}"
        response = requests.get(url, headers=self.headers)
        # return the chat bot status
        return json.loads(response.text)["data"]["is_chat_active"]
    
    # Create a conversation before sending a message to the chat bot
    def create_conversation(self, project_id: str, name: str = "My First Conversation") -> Dict[str, Any]:
        url = f"{self.BASE_URL}/projects/{project_id}/conversations"
        response = requests.post(url, headers=self.headers, data=json.dumps({"name": name}))
        # return the conversation id
        return json.loads(response.text)["data"]["session_id"]
    
    def chat_with_agent(self, prompt: str, project_id: str, conversation_id: str, stream: int = 0) -> Any:
        url = f"{self.BASE_URL}/projects/{project_id}/conversations/{conversation_id}/messages"
        payload = {
            "prompt": prompt,
            "stream": stream
        }
        if stream == 1:
            stream_response = requests.post(url, stream=True, headers={"Accept": "text/event-stream"}.update(self.headers), data=json.dumps(payload))
            response = SSEClient(stream_response)
            for event in response:
                yield event.data
        else:
            response = requests.post(url, stream=False, headers=self.headers, data=json.dumps(payload))
            return response
