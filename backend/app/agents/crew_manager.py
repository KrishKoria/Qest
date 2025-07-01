from crewai import Agent, Crew, Task, Process, LLM
from crewai.project import CrewBase, agent, crew, task
import yaml
import os
from typing import Dict, Any, Optional
import logging
from langdetect import detect
from ..config.settings import get_settings
from ..tools.mongodb_tool import MongoDBTool
from ..tools.external_api_tool import ExternalAPITool

logger = logging.getLogger(__name__)


class CrewManager:
    """Manages the CrewAI agents and orchestrates their interactions."""
    
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "..", "config", "agents.yaml")
        self.agents_config = self._load_config()
        self.mongodb_tool = MongoDBTool()
        self.external_api_tool = ExternalAPITool()
        settings = get_settings()
        
        # Validate OpenAI API key
        if not settings.openai_api_key or settings.openai_api_key == "sk-your-actual-openai-api-key-here":
            raise ValueError(
                "OPENAI_API_KEY is required. Please set OPENAI_API_KEY in your .env file. "
                "Get your API key from https://platform.openai.com/api-keys"
            )
        
        self.llm = LLM(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
        )
        # Initialize agents
        self.support_agent = self._create_support_agent()
        self.dashboard_agent = self._create_dashboard_agent()
        
        logger.info("CrewManager initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configurations from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"Failed to load agent config: {e}")
            raise
    
    def _create_support_agent(self) -> Agent:
        """Create the support agent."""
        config = self.agents_config['support_agent']
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=config.get('verbose', True),
            allow_delegation=config.get('allow_delegation', False),
            max_iter=config.get('max_iter', 25),
            memory=config.get('memory', True),
            tools=[self.mongodb_tool, self.external_api_tool],
            llm=self.llm
        )
    
    def _create_dashboard_agent(self) -> Agent:
        """Create the dashboard agent."""
        config = self.agents_config['dashboard_agent']
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=config.get('verbose', True),
            allow_delegation=config.get('allow_delegation', False),
            max_iter=config.get('max_iter', 20),
            memory=config.get('memory', True),
            tools=[self.mongodb_tool],  # Dashboard agent only needs read access
            llm=self.llm
        )
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of the input text."""
        try:
            return detect(text)
        except:
            return "en"  # Default to English
    
    def _create_task(self, agent: Agent, query: str, language: str = "en", context: Optional[Dict] = None) -> Task:
        """Create a task for the given agent."""
        
        # Add language context to the query
        enhanced_query = query
        if language != "en":
            enhanced_query = f"[Language: {language}] {query}"
        
        # Add context if provided
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            enhanced_query += f"\n\nAdditional Context:\n{context_str}"
        
        return Task(
            description=enhanced_query,
            expected_output="A comprehensive and helpful response to the user's query, formatted in a clear and professional manner.",
            agent=agent
        )
    
    async def handle_support_query(self, query: str, language: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle a support agent query."""
        try:
            # Detect language if not provided
            if not language:
                language = self._detect_language(query)
            
            # Create task for support agent
            task = self._create_task(self.support_agent, query, language, context)
            
            # Create crew and execute
            crew = Crew(
                agents=[self.support_agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                "response": str(result),
                "agent": "support",
                "language": language,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Support query error: {e}")
            raise
    
    async def handle_dashboard_query(self, query: str, language: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle a dashboard agent query."""
        try:
            # Detect language if not provided
            if not language:
                language = self._detect_language(query)
            
            # Create task for dashboard agent
            task = self._create_task(self.dashboard_agent, query, language, context)
            
            # Create crew and execute
            crew = Crew(
                agents=[self.dashboard_agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                "response": str(result),
                "agent": "dashboard",
                "language": language,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Dashboard query error: {e}")
            raise
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the available agents."""
        return {
            "support_agent": {
                "role": self.support_agent.role,
                "goal": self.support_agent.goal,
                "tools": [tool.name for tool in self.support_agent.tools]
            },
            "dashboard_agent": {
                "role": self.dashboard_agent.role,
                "goal": self.dashboard_agent.goal,
                "tools": [tool.name for tool in self.dashboard_agent.tools]
            }
        }
