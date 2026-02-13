from typing import Dict, Any, List
from agents.historian import HistorianAgent
from agents.newsroom import NewsroomAgent
from agents.macro_strategist import MacroStrategistAgent
from agents.contrarian import ContrarianAgent
from agents.executioner import ExecutionerAgent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings

class Orchestrator:
    """
    The Lead Coordinator for Alpha-Omega.
    Manages the "Council of Experts" workflow: Ingestion -> Debate -> Synthesis -> Action.
    """
    def __init__(self):
        self.historian = HistorianAgent(llm_backend="google")
        self.newsroom = NewsroomAgent(llm_backend="google")
        self.macro = MacroStrategistAgent(llm_backend="google")
        self.contrarian = ContrarianAgent(llm_backend="google")
        self.executioner = ExecutionerAgent(llm_backend="google")
        
        # Coordinator LLM for synthesis
        self.coordinator_llm = ChatGoogleGenerativeAI(
            model=settings.DEFAULT_LLM_MODEL, 
            temperature=0.3,
            google_api_key=settings.GOOGLE_API_KEY
        )

    def synthesize_reports(self, reports: Dict[str, str], symbol: str) -> Dict[str, Any]:
        """
        Synthesizes reports from Historian, Newsroom, and Macro into a Consensus View.
        Also calculates a preliminary confidence score.
        """
        prompt = f"""
        You are the Head of Research for a hedge fund.
        Synthesize the following reports for {symbol} into a single "Consensus View":
        
        --- The Historian (Technical) ---
        {reports['historian']}
        
        --- The Newsroom (Sentiment) ---
        {reports['newsroom']}
        
        --- The Macro-Strategist (Global) ---
        {reports['macro']}
        
        Output Requirements:
        1. A concise "Consensus View" paragraph summary.
        2. A numeric "Confidence Score" (0.0 to 1.0) based on the alignment of signals.
        
        Format:
        Consensus View: [Summary]
        Confidence Score: [0.0-1.0]
        """
        
        response = self.coordinator_llm.invoke([HumanMessage(content=prompt)]).content
        
        # Simple parsing (robust parsing would be needed in prod)
        lines = response.split('\n')
        consensus_view = "Analysis unavailable."
        confidence_score = 0.5
        
        for line in lines:
            if "Consensus View:" in line:
                consensus_view = line.replace("Consensus View:", "").strip()
            if "Confidence Score:" in line:
                try:
                    confidence_score = float(line.replace("Confidence Score:", "").strip())
                except ValueError:
                    pass
                    
        return {
            "consensus_view": consensus_view,
            "confidence_score": confidence_score,
            "full_synthesis": response
        }

    def run_cycle(self, symbol: str) -> str:
        """
        Runs the full Alpha-Omega trading cycle.
        """
        print(f"--- Starting Alpha-Omega Cycle for {symbol} ---")
        
        # 1. Ingestion & Individual Analysis
        print("1. Gathering Intelligence from Agents...")
        reports = {}
        reports['historian'] = self.historian.execute("Analyze price action.", {"symbol": symbol})
        reports['newsroom'] = self.newsroom.execute("Analyze sentiment.", {"symbol": symbol})
        reports['macro'] = self.macro.execute("Analyze macro regime impact.", {"symbol": symbol})
        
        # 2. Initial Synthesis
        print("2. Synthesizing Preliminary Consensus...")
        synthesis = self.synthesize_reports(reports, symbol)
        
        # 3. The Debate (Contrarian Challenge)
        print("3. The Contrarian is challenging the view...")
        challenge = self.contrarian.execute(
            "Challenge this consensus.", 
            {"symbol": symbol, "consensus_view": synthesis['consensus_view']}
        )
        
        # 4. Final Decision (Executioner)
        print("4. The Executioner is deciding...")
        
        final_context = {
            "symbol": symbol,
            "analysis_summary": f"""
            Consensus View: {synthesis['consensus_view']}
            Confidence Score: {synthesis['confidence_score']}
            Contrarian Challenge: {challenge}
            """,
            "confidence_score": synthesis['confidence_score'] # Pass the score clearly
        }
        
        decision = self.executioner.execute("Make final trade decision.", final_context)
        
        print("--- Cycle Complete ---\n")
        return decision
