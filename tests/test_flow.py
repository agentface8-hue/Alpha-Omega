import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure the project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- MOCK ALL DEPENDENCIES BEFORE IMPORTING PROJECT MODULES ---
modules_to_mock = [
    'langchain_core', 
    'langchain_core.messages', 
    'langchain_openai', 
    'langchain_anthropic',
    'pandas',
    'yfinance',
    'pydantic',
    'pydantic_settings'
]

for module in modules_to_mock:
    sys.modules[module] = MagicMock()

# Specific mocks for classes used in type hints or inheritance
sys.modules['langchain_core.messages'].BaseMessage = MagicMock
sys.modules['langchain_core.messages'].HumanMessage = MagicMock
sys.modules['langchain_core.messages'].SystemMessage = MagicMock
sys.modules['pydantic_settings'].BaseSettings = MagicMock
sys.modules['pydantic_settings'].SettingsConfigDict = MagicMock
sys.modules['pydantic'].Field = MagicMock

# Now import project modules
from core.orchestrator import Orchestrator

class TestAlphaOmegaFlow(unittest.TestCase):

    def setUp(self):
        # We need to ensure the settings are mocked appropriately if used during import
        pass

    @patch('agents.base_agent.ChatOpenAI')
    @patch('core.orchestrator.ChatOpenAI')
    def test_full_cycle(self, mock_orchestrator_llm, mock_agent_llm):
        # Setup Mocks
        mock_llm_instance = MagicMock()
        mock_orchestrator_llm.return_value = mock_llm_instance
        mock_agent_llm.return_value = mock_llm_instance
        
        # Mocks for agent return values are simpler here since they use query_llm which uses invoke
        # We just need invoke to return a mock with .content
        
        mock_content = MagicMock()
        mock_content.content = "Mocked Agent Analysis"
        
        mock_synthesis_content = MagicMock()
        mock_synthesis_content.content = "Consensus View: Bullish\nConfidence Score: 0.88"
        
        def side_effect(messages):
            # Check content of the first message (SystemPrompt)
            # Since messages are mocks, we access .content attribute
            system_prompt = messages[0].content if messages else ""
            
            # MagicMock .content might be a mock if not set, but we instantiated SystemMessage(content=...)
            # However, since SystemMessage is a MagicMock class, the instance created has content set if we passed it in __init__
            # BUT: MagicMock(content="foo").content IS "foo".
            
            # To be safe, check if we can stringify it
            prompt_str = str(system_prompt)
            
            if "Head of Research" in prompt_str:
                return mock_synthesis_content
            else:
                return mock_content

        mock_llm_instance.invoke.side_effect = side_effect

        # Mock the individual agents' methods if they fail due to missing huge deps (like pandas implementation)
        # But since we mocked pandas module, any call like pd.DataFrame() returns a mock, so code should run.
        
        orchestrator = Orchestrator()
        
        # We need to mock the data fetching methods on the agents themselves to avoid empty dataframe errors if logic depends on it
        orchestrator.historian.fetch_historical_data = MagicMock(return_value=MagicMock()) # Returns mock df
        orchestrator.historian.calculate_technical_indicators = MagicMock(return_value=MagicMock())
        orchestrator.newsroom.fetch_news = MagicMock(return_value=["News 1", "News 2"])
        orchestrator.macro.fetch_macro_data = MagicMock(return_value={
            "10Y_Yield": 4.0, "2Y_Yield": 4.2, "Yield_Curve": "Inverted", 
            "VIX": 15, "Fed_Policy": "Pause", "Geopolitics": "Stable"
        })

        # Run
        decision = orchestrator.run_cycle("NVDA")

        # Assertions
        self.assertIn("Mocked Agent Analysis", decision) 
        print("\nTest passed! Decision output:", decision)

if __name__ == '__main__':
    unittest.main()
