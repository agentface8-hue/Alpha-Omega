from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings

class BaseAgent(ABC):
    """
    Abstract base class for all Alpha-Omega agents.
    """

    def __init__(
        self, 
        name: str, 
        role: str, 
        goal: str, 
        llm_backend: str = "google",
        model: str = settings.DEFAULT_LLM_MODEL,
        tools: List[Any] = None
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.llm_backend = llm_backend
        self.model_name = model
        self.tools = tools or []
        self.llm = self._initialize_llm()
        self.memory: List[BaseMessage] = []

    def _initialize_llm(self):
        """Initialize the LLM based on backend choice."""
        if self.llm_backend == "openai":
            # Lazy import or keep valid if installed
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=self.model_name,
                temperature=0.7,
                api_key=settings.OPENAI_API_KEY
            )
        elif self.llm_backend == "anthropic":
            return ChatAnthropic(
                model=self.model_name,
                temperature=0.7,
                api_key=settings.ANTHROPIC_API_KEY
            )
        elif self.llm_backend == "google":
            return ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=0.7,
                google_api_key=settings.GOOGLE_API_KEY
            )
        else:
            raise ValueError(f"Unsupported LLM backend: {self.llm_backend}")

    def add_to_memory(self, message: BaseMessage):
        """Add a message to the agent's memory."""
        self.memory.append(message)

    def clear_memory(self):
        """Clear the agent's memory."""
        self.memory = []

    @abstractmethod
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Main execution method for the agent.
        Must be implemented by subclasses.
        """
        pass

    def _build_system_prompt(self) -> str:
        """Constructs the system prompt based on role and goal."""
        return f"""
        You are {self.name}, the {self.role}.
        Your goal is: {self.goal}.
        
        Operate as a top-tier expert in your field. 
        Provide well-reasoned, data-backed analysis.
        """

    def query_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Helper method to query the LLM with the current memory and a new prompt.
        """
        sys_prompt = system_prompt or self._build_system_prompt()
        messages = [SystemMessage(content=sys_prompt)] + self.memory + [HumanMessage(content=prompt)]
        
        response = self.llm.invoke(messages)
        return response.content
