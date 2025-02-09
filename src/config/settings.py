from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

@dataclass
class Settings:
    """Application settings and configuration."""
    
    # OpenAI Settings
    openai_api_key: str
    openai_model: str = "gpt-4o"
    
    # Todoist Settings
    todoist_api_key: Optional[str] = None
    
    # Server Settings
    api_port: int = 8000
    gradio_port: int = 7860
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Create settings from environment variables."""
        load_dotenv()
        
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
            
        return cls(
            openai_api_key=openai_api_key,
            openai_model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
            todoist_api_key=os.getenv('TODOIST_API_KEY'),
            api_port=int(os.getenv('API_PORT', '8000')),
            gradio_port=int(os.getenv('GRADIO_PORT', '7860')),
        )

# Create a global settings instance
settings = Settings.from_env() 