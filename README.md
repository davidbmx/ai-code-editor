# FastAPI Project

A simple FastAPI application.

## Setup

1. Activate the virtual environment:

   ```
   source venv/bin/activate
   ```

2. Install dependencies (if not already installed):
   ```
   pip install -r requirements.txt
   ```

## Running the application

Start the server:

```
python app.py
```

Or using uvicorn directly:

```
uvicorn app:app --reload
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

# AIDB

## Graph API with Streaming

This project includes a FastAPI application that uses LangGraph for streaming responses. The API allows you to interact with a graph-based workflow to generate and process content.

### Features

- RESTful API built with FastAPI
- Streaming responses using Server-Sent Events (SSE)
- LangGraph integration for complex workflows
- CORS enabled for frontend integration

### Getting Started

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Run the API server**

```bash
python app.py
```

This will start the server at http://localhost:8000

3. **Test with the included HTML client**

Open `test_client.html` in your browser to try out the streaming API.

### API Endpoints

#### `GET /`

Root endpoint returning a welcome message.

#### `POST /chat`

Chat endpoint with streaming responses.

**Request body:**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Your message here"
    }
  ],
  "config": {
    "thread_id": "123"
  }
}
```

**Response:**

Server-Sent Events (SSE) stream with the following format:

```
data: {"role": "assistant", "content": "Response content here"}
```

### Using the Streaming API in JavaScript

Here's a basic example of how to consume the streaming API in a web application:

```javascript
async function fetchChatStream(messages) {
  const response = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      messages: messages,
      config: { thread_id: "123" },
    }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const event of events) {
      if (event.startsWith("data: ")) {
        const data = JSON.parse(event.substring(6));
        // Process the data
        console.log(data);
      }
    }
  }
}
```

### LangGraph Integration

The API leverages the LangGraph library to create complex workflows with multiple stages and conditional routing.
