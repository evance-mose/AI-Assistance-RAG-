from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

app = FastAPI()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7
)


store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Create prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])


chain = prompt | llm
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

class Message(BaseModel):
    message: str

@app.post("/assistant")
async def assistant(data: Message):
    try:
        # Get response with conversation history
        response = chain_with_history.invoke(
            {"input": data.message},
            config={"configurable": {"session_id": "default"}}
        )
        
        return {"reply": response.content}
    
    except Exception as e:
        return JSONResponse(
            content={"error": f"API Error: {str(e)}"},
            status_code=500
        )

@app.get("/")
async def root():
    return {"message": "AI Assistant API is running"}

@app.post("/reset")
async def reset_conversation():
    """Reset conversation history"""
    if "default" in store:
        store["default"].clear()
    return {"message": "Conversation history cleared"}