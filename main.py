from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class Message(BaseModel):
    message: str

@app.post("/assistant")
async def assistant(data: Message):
    """Simple endpoint that takes user message and returns AI response."""
    response = client.responses.create(
        model="gpt-4o-mini",
        input=data.message
    )

    return {"reply": response.output_text}
