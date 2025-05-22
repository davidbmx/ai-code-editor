from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uvicorn
from any_code_graph import app
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

app_api = FastAPI(title="Graph API with Streaming")

# Add CORS middleware
app_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    config: Optional[Dict[str, Any]] = {"thread_id": "123"}

def format_event(event):
    """Format event data for SSE"""
    formatted_data = None
    if "messages" in event and isinstance(event["messages"], list):
        for msg in event["messages"]:
            if hasattr(msg, "content"):
                formatted_data = {"role": "assistant", "content": msg.content}
            elif isinstance(msg, dict) and "content" in msg:
                formatted_data = {"role": "assistant", "content": msg["content"]}
    
    if formatted_data is None:
        if isinstance(event, dict):
            formatted_data = {"role": "system", "content": json.dumps(event, ensure_ascii=False)}
        else:
            formatted_data = {"role": "system", "content": str(event)}
    
    return formatted_data

@app_api.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint with streaming response"""
    
    # Convert Pydantic model to dict for langgraph
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    async def event_generator():
        for event in app.stream({"messages": messages}, request.config, stream_mode="values"):
            formatted_event = format_event(event)
            if formatted_event:
                yield f"data: {json.dumps(formatted_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@app_api.get("/")
async def root():
    return {"message": "Welcome to the Graph API with streaming responses"}

if __name__ == "__main__":
    uvicorn.run("app:app_api", host="0.0.0.0", port=8000, reload=True)
