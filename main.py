import streamlit as st
from any_code_graph import app
import json

config = {
    "thread_id": "123",
}

st.set_page_config(page_title="Generador UI LLM", layout="wide")

st.markdown(
    """
    <style>
    .chat-container {height: 80vh; overflow-y: auto; border-radius: 12px; border: 1px solid #e5e7eb; background: #fff;}
    .preview-frame {border: 2px solid #e5e7eb; border-radius: 12px;}
    </style>
    """,
    unsafe_allow_html=True,
)

def format_state_for_chat(state):
    """Formatea el estado del grafo para mostrarlo en el chat."""
    formatted_messages = []
    if "messages" in state and isinstance(state["messages"], list):
        for msg in state["messages"]:
            role = "assistant" if hasattr(msg, "role") and msg.role == "assistant" else "user" if hasattr(msg, "role") and msg.role == "user" else "info"
            content = ""
            if hasattr(msg, "content"):
                content = msg.content
            elif isinstance(msg, dict) and "content" in msg:
                content = msg["content"]
            elif isinstance(msg, dict):
                content = json.dumps(msg, indent=2, ensure_ascii=False)
            else:
                content = str(msg)
            formatted_messages.append({"role": role, "content": content})
    elif isinstance(state, dict):
        formatted_messages.append({"role": "info", "content": json.dumps(state, indent=2, ensure_ascii=False)})
    else:
        formatted_messages.append({"role": "info", "content": str(state)})
    return formatted_messages

st.title("✨ Generador de interfaces Next.js + Tailwind (tipo V0/Bolt)")
st.markdown("Interactúa con el modelo y visualiza el resultado en vivo.")

col1, col2 = st.columns([1, 2], gap="large")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

with col1:
    st.header("Chat")
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat_history"]:
            st.chat_message(msg["role"]).write(msg["content"])
    user_input = st.chat_input("Escribe tu mensaje...")
    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.spinner("Esperando respuesta del modelo..."):
            messages = [{"role": "user", "content": user_input}]
            for event in app.stream({"messages": messages}, config, stream_mode="values"):
                formatted_event = format_state_for_chat(event)
                for msg in formatted_event:
                    st.session_state["chat_history"].append(msg)
        st.rerun()

with col2:
    st.header("Previsualización en vivo")
    st.components.v1.iframe("http://localhost:3000/", height=700, scrolling=True)