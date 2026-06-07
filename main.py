import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from loguru import logger

# 1. Imports exactly from your final agent setup
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

# Import tools and helpers from your local files
from getmenus import get_menu, get_today, setup_logging
# Assuming your exchange rate logic is inside exchangerates.py or getmenus.py:
try:
    from exchangerates import get_exchange_rates # Adjust this import name if different!
except ImportError:
    # If it's directly bundled in getmenus or another tool, we ensure it's referenced
    pass

# Initialize project logging and environments
setup_logging()
load_dotenv()
logger.info("Environment loaded.")

logger.info(f"Today's date (Seoul time): {get_today()}")

# 2. Replicate your precise Azure OpenAI Language Model setup from your notebook
llm = ChatOpenAI(
    base_url=os.environ["AZURE_FOUNDRY_ENDPOINT"],
    api_key=os.environ["AZURE_FOUNDRY_API_KEY"],
    model=os.environ["AZURE_FOUNDRY_MODEL"],
    timeout=300,
    temperature=0.5,
    max_tokens=25000
)
logger.info("LLM ready.")

today = get_today()

# 3. CRITICAL UPDATE: Explicitly command the bot to handle currency and format beautifully!
# Update this block inside your main.py file
SYSTEM_PROMPT = (
    f"You are a helpful campus menu assistant. Today's date is {today} (Asia/Seoul).\n"
    "You have full access to a connected Supabase database containing campus menus and a daily currency exchange cache (`fx_rates_daily_cache`).\n"
    "Use your tools to fetch menu data and provide real-time currency conversions when requested by the user.\n\n"
    
    "CRITICAL TRANSLATION INSTRUCTIONS:\n"
    "1. YOU MUST TRANSLATE EVERYTHING TO ENGLISH. Do not leave any Korean characters (Hangul) in the final response.\n"
    "2. Every single dish name, university name, and cafeteria location MUST be fully translated into natural English.\n\n"
    
    "CRITICAL FORMATTING INSTRUCTIONS:\n"
    "1. DO NOT include introductory conversational text, meta-commentary, greetings, or descriptions about what tools or databases you fetched information from. Start directly with the menu content.\n"
    "2. Format everything using clean, standard Markdown nested lists exactly like this template:\n\n"
    "[University Name] [Optional Campus Name, e.g., — ERICA Campus]\n\n"
    "  * [Cafeteria Name, e.g., Student Cafeteria]\n"
    "      - [Meal Type, e.g., Breakfast / Lunch / Dinner] ([Serving Time]) — Price: [Price in KRW or Converted Currency if requested]\n"
    "          * [Dish 1]\n"
    "          * [Dish 2]\n"
    "          * [Dish 3]\n\n"
    "3. Keep a blank line between different universities. Avoid emojis, lines like '---', or extra symbols. Make it look like a clean, minimal text tree blueprint."
)

# Build the agent with tools attached (Make sure get_menu handles the DB/cache query orchestration)
agent = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_menu] # Add any dedicated exchange rate tools here if separated in your notebook!
)
logger.info("Agent ready.")

# 4. Initialize FastAPI web server gateway
app = FastAPI()

# Allow your local Live Server browser tab to talk to this script without CORS blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    question = request.message
    logger.info(f"Incoming Front-end Question: '{question}'")
    
    try:
        # Run the agent exactly how it was running in your notebook cells
        result = agent.invoke({"messages": [{"role": "user", "content": question}]})
        
        # Pull out the response text via your reversed message inspection logic
        answer = ""
        for message in reversed(result.get("messages", [])):
            content = getattr(message, "content", None)
            if isinstance(content, str) and content.strip():
                answer = content
                break
                
        logger.info(f"Agent answered successfully with {len(answer)} characters.")
        
        # Fallback boundary check if the response comes back blank
        if not answer.strip():
            return {"reply": "I don't know exactly what it is, but I can help you with finding a university or suitable menu for you!"}
            
        return {"reply": answer}

    except Exception as e:
        logger.error(f"Error handling agent invocation: {str(e)}")
        # Secure fallback text structure
        return {"reply": "I don't know exactly what it is, but I can help you with finding a university or suitable menu for you!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)  # <-- Change this to 8001