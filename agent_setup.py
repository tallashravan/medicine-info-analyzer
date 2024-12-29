import os
from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools
from prompts import INSTRUCTIONS, SYSTEM_PROMPT

def load_environment_variables():
    """Load environment variables from .env file."""
    load_dotenv()
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    if not TAVILY_API_KEY or not GOOGLE_API_KEY:
        raise EnvironmentError("API keys are not set. Please check your .env file.")

    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def initialize_agent():
    """Initialize and return the Tavily agent."""
    try:
        agent = Agent(
            name="tavily",
            instructions=INSTRUCTIONS,
            model=Gemini(id="gemini-2.0-flash-exp"),
            tools=[TavilyTools()],
            markdown=True,
            system_prompt=SYSTEM_PROMPT
        )
        return agent
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Tavily Agent: {str(e)}")