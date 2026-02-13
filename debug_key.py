from config.settings import settings
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

def test_key():
    key = settings.ANTHROPIC_API_KEY
    if not key:
        print("ERROR: ANTHROPIC_API_KEY is missing in settings.")
        return

    print(f"Loaded Key: {key[:15]}...{key[-5:]}")
    
    try:
        chat = ChatAnthropic(
            model=settings.DEFAULT_LLM_MODEL, 
            api_key=key
        )
        response = chat.invoke([HumanMessage(content="Hello, are you working?")])
        print("Success! Response:", response.content)
    except Exception as e:
        print("API Call Failed:", e)

if __name__ == "__main__":
    test_key()
