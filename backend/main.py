from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import asyncio

# from database.postgres_setup import init_postgres_db # type: ignore
from backend.database.postgres_setup import init_postgres_db # type: ignore
from backend.agent.graph import create_graph

from .database.vector_store import init_vector_store

from .config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    init_postgres_db(settings.POSTGRES_URL)
    init_vector_store()
    app.state.graph = create_graph()

from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat(request: ChatRequest):
    graph = app.state.graph

    async def event_generator():
        async for event in graph.astream_events(
            {"messages": [m.dict() for m in request.messages]},
            config={"configurable": {"thread_id": "support_thread_123"}},
            version="v2"
        ):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    yield chunk.content

    return StreamingResponse(event_generator(), media_type="text/plain")