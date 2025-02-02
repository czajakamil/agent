from langfuse.openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from typing import Optional, Union, AsyncGenerator, List, Dict, Literal, Any
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

# 1. Constants and Type Definitions
IMAGE_SIZES = Literal['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792']
IMAGE_QUALITY = Literal['standard', 'hd']

class Role(str, Enum):
    """Available roles for chat messages."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class Message:
    """A chat message with role and content.
    
    Attributes:
        role: The role of the message sender (system, user, or assistant)
        content: The actual content of the message
        timestamp: When the message was created (defaults to current time)
        session_id: Optional identifier for grouping messages in conversations
        user_id: Optional identifier of the user who sent the message
        tags: List of tags associated with the message
        
    Note:
        The tags attribute uses field(default_factory=list) instead of just =[] 
        to ensure each Message instance gets its own new list. This avoids the common
        pitfall where all instances would share the same list due to Python's 
        mutable default argument behavior.
        
    Example:
        >>> msg1 = Message(role=Role.USER, content="Hello")
        >>> msg2 = Message(role=Role.USER, content="Hi", tags=["greeting"])
        >>> msg1.tags.append("test")  # Only affects msg1's tags
        >>> print(msg2.tags)  # Still only contains ["greeting"]
    """
    role: Role
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None
    user_id: str = ""
    tags: List[str] = field(default_factory=list)

class MessageHistory:
    """A collection of messages with history management capabilities.
    
    This class manages a conversation history, including message tracking
    and session management.
    
    Attributes:
        messages (List[Message]): List of messages in the conversation
        session_id (str): Unique identifier for this conversation session
    """
    
    def __init__(self, session_id: Optional[str] = None) -> None:
        """Initialize message history.
        
        Args:
            session_id: Optional session ID for tracking conversations
        """
        self.messages: List[Message] = []
        self.session_id = session_id or str(uuid.uuid4())

    def add_message(self, role: str, content: str, user_id: str = "", tags: Optional[List[str]] = None) -> Message:
        """Add a new message to the history.
        
        Args:
            role: The role of the message sender ("system"/"user"/"assistant")
            content: The content of the message
            user_id: Optional identifier of the user
            tags: Optional list of tags for the message
            
        Returns:
            The newly created Message object
            
        Raises:
            ValueError: If role is not one of: "system", "user", "assistant"
        """
        role = role.lower()
        if role not in ["system", "user", "assistant"]:
            raise ValueError("Role must be one of: system, user, assistant")
            
        message = Message(
            role=Role(role),
            content=content, 
            session_id=self.session_id,
            user_id=user_id,
            tags=tags if tags is not None else []
        )
        self.messages.append(message)
        return message

# 2. Configuration
@dataclass
class OpenAIServiceConfig:
    """Configuration for OpenAI service."""
    api_key: str
    model: str = "gpt-4o"
    max_retries: int = 4

@dataclass
class CompletionConfig:
    """Configuration for completion requests.
    
    Preset configurations available:
    - code_generation: For generating syntactically correct code (temp=0.2, top_p=0.1)
    - creative_writing: For creative and diverse text generation (temp=0.7, top_p=0.8)
    - chatbot: For balanced conversational responses (temp=0.5, top_p=0.5)
    - code_comments: For generating concise code comments (temp=0.3, top_p=0.2)
    - data_analysis: For generating correct and efficient scripts (temp=0.2, top_p=0.1)
    - exploratory_code: For exploring creative code solutions (temp=0.6, top_p=0.7)
    
    Examples:
        # Using default configuration
        >>> config = CompletionConfig()
        >>> print(f"Default settings: temp={config.temperature}, top_p={config.top_p}")
        
        # Using preset for code generation
        >>> code_config = CompletionConfig.code_generation()
        >>> service.completion(messages, config=code_config)
        
        # Using preset for creative writing with streaming
        >>> creative_config = CompletionConfig.creative_writing()
        >>> creative_config.stream = True
        >>> service.completion(messages, config=creative_config)
        
        # Custom configuration
        >>> custom_config = CompletionConfig(
        ...     temperature=0.8,
        ...     top_p=0.9,
        ...     stream=True,
        ...     presence_penalty=0.2
        ... )
        
        # Using different presets for different tasks
        >>> for code in code_samples:
        ...     # Generate code with strict parameters
        ...     result = service.completion(code, config=CompletionConfig.code_generation())
        ...     # Generate creative comments for the code
        ...     comments = service.completion(result, config=CompletionConfig.code_comments())
    """
    model: str = "gpt-4o"
    temperature: float = 0.5
    top_p: float = 0.5
    stream: bool = False
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    
    def __post_init__(self):
        """Validate configuration values."""
        if not 0 <= self.temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        if not 0 <= self.top_p <= 1:
            raise ValueError("Top_p must be between 0 and 1")

    @classmethod
    def code_generation(cls) -> 'CompletionConfig':
        """For generating syntactically correct code."""
        return cls(temperature=0.2, top_p=0.1)

    @classmethod
    def creative_writing(cls) -> 'CompletionConfig':
        """For creative and diverse text generation."""
        return cls(temperature=0.7, top_p=0.8)

    @classmethod
    def chatbot(cls) -> 'CompletionConfig':
        """For balanced conversational responses."""
        return cls(temperature=0.5, top_p=0.5)

    @classmethod
    def code_comments(cls) -> 'CompletionConfig':
        """For generating concise code comments."""
        return cls(temperature=0.3, top_p=0.2)

    @classmethod
    def data_analysis(cls) -> 'CompletionConfig':
        """For generating correct and efficient scripts."""
        return cls(temperature=0.2, top_p=0.1)

    @classmethod
    def exploratory_code(cls) -> 'CompletionConfig':
        """For exploring creative code solutions."""
        return cls(temperature=0.6, top_p=0.7)

# 4. Main Service Class
class OpenAIService:
    """Service for interacting with OpenAI APIs."""

    def __init__(self, completion_config: CompletionConfig = CompletionConfig()):
        """Initialize OpenAI service.
        
        Args:
            completion_config: Configuration for completions (defaults to CompletionConfig())
        """
        self.config = self._load_config()
        self.client = AsyncOpenAI(
            api_key=self.config.api_key,
            max_retries=self.config.max_retries
        )
        self.completion_config = completion_config

    # 4.1 Initialization Methods
    def _load_config(self) -> OpenAIServiceConfig:
        """Load OpenAI API key from environment variables.
        
        Raises:
            ValueError: If OPENAI_API_KEY is not found
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        return OpenAIServiceConfig(api_key=api_key)

    # 4.3 Core API Methods
    async def create_embedding(self, text: str, model: str = "text-embedding-3-large") -> List[float]:
        """Create embeddings for given text."""
        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty")
            
        response = await self.client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding

    async def completion(
        self,
        conversation: MessageHistory,
        config: Optional[CompletionConfig] = None,
        name: Optional[str] = None 
    ) -> Union[str, AsyncGenerator[str, None]]:
        """Get completion from OpenAI API with LangFuse tracking."""
        config = config or self.completion_config
        
        params = {
            "model": config.model,
            "messages": [{"role": msg.role.value, "content": msg.content} for msg in conversation.messages],
            "temperature": config.temperature,
            "top_p": config.top_p,
            "stream": config.stream,
            "presence_penalty": config.presence_penalty,
            "frequency_penalty": config.frequency_penalty,

            "name": name,
            "user": conversation.messages[-1].user_id if conversation.messages else "",
            "session_id": conversation.session_id
        }
        
        if config.stream:
            return self._stream_response(params)
        
        response = await self.client.chat.completions.create(**params)
        return response.choices[0].message.content

    async def _stream_response(self, params: Dict) -> AsyncGenerator[str, None]:
        """Handle streaming response from OpenAI API.
        
        Args:
            params: Parameters for the API call
            
        Yields:
            Chunks of the generated response
        """
        async for chunk in await self.client.chat.completions.create(**params):
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    async def transcribe_audio(
        self, 
        audio_file_path: str, 
        model: str = "whisper-1", 
        language: Optional[str] = None
    ) -> str:
        """
        Transkrypcja pliku audio przy użyciu OpenAI Whisper.
        :param audio_file_path: Ścieżka do pliku audio
        :param model: Model Whisper do użycia (domyślnie "whisper-1")
        :param language: Opcjonalny kod języka (np. "pl" dla polskiego)
        :return: Tekst transkrypcji
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                request_params = {
                    "model": model,
                    "file": audio_file,
                }
                
                if language:
                    request_params["language"] = language
                
                response = await self.client.audio.transcriptions.create(**request_params)
                return response.text
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Nie znaleziono pliku audio: {audio_file_path}")
        except Exception as e:
            raise RuntimeError(f"Błąd podczas transkrypcji audio: {e}")

    async def print_stream(
        self, 
        conversation: MessageHistory, 
        config: Optional[CompletionConfig] = None
    ) -> str:
        """Print streaming completion and return the full response.
        
        Args:
            conversation: Message history containing the conversation
            config: Optional completion configuration
            
        Returns:
            Complete response as a string
        """
        config = config or self.completion_config
        config.stream = True  # Ensure streaming is enabled
        
        full_response = []
        response_stream = await self.completion(conversation, config=config)
        if isinstance(response_stream, AsyncGenerator):
            async for chunk in response_stream:
                print(chunk, end='', flush=True)
                full_response.append(chunk)
        else:
            print(response_stream, end='', flush=True)
            full_response.append(response_stream)
        print()
        
        complete_response = ''.join(full_response)
        conversation.add_message("assistant", complete_response)
        
        return complete_response