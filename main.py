from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI,RateLimitError
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

conversation = []

class Message(BaseModel):
    message: str



@app.post("/assistant")
async def assistant(data: Message):
    try:
        conversation.append({"role": "user", "content": data.message})
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            *conversation[-10:]
        ]
        response = client.responses.create(
            model="gpt-4o-mini",
            input=messages
        )
        ai_reply = response.output_text.strip()
        conversation.append({"role": "assistant", "content": ai_reply})
        return {"reply": ai_reply}
    except RateLimitError:
        return JSONResponse(
            content={"error": "You have exceeded your OpenAI quota. Please check your billing settings."},
            status_code=429
        )

