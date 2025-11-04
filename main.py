from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

conversation = []

class Message(BaseModel):
    message: str

@app.post("/assistant")
async def assistant(data: Message):
    """
    AI Assistant endpoint with short-term memory.
    Takes a user's message and returns the AI's response.
    """

    conversation.append({"role": "user", "content": data.message})


    messages = [
        {"role": "system", "content": "You are a helpful and concise AI assistant."},
        *conversation[-10:] 
    ]

    # Generate AI response
    response = client.responses.create(
        model="gpt-4o-mini",
        input= messages
    )


    reply = response.output_text.strip()

    # Add AI reply to memory
    conversation.append({"role": "assistant", "content": reply})

    return {"reply": reply}
