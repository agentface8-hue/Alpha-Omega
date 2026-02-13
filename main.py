import sys
import os

# Ensure the project root is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import Orchestrator
from config.settings import settings

def main():
    print(f"Initializing {settings.PROJECT_NAME} v{settings.VERSION}")
    
    # Check for API Keys
    if not settings.GOOGLE_API_KEY:
        print("WARNING: GOOGLE_API_KEY is missing.")
    else:
        k = settings.GOOGLE_API_KEY
        print(f"Loaded GOOGLE_API_KEY: {k[:10]}...{k[-5:]}")
    
    orchestrator = Orchestrator()
    
    # Example Symbol
    symbol = "NVDA"
    
    try:
        decision = orchestrator.run_cycle(symbol)
        print(f"FINAL DECISION for {symbol}:")
        print(decision)
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stdout)
        print(f"CRITICAL ERROR: {e}")
        sys.exit(0)

if __name__ == "__main__":
    main()
