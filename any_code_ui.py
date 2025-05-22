import streamlit as st
from pathlib import Path
from any_code_graph import app, State
from typing import Dict, Any

# Aquí importas tu graph o el executor que tengas
# Por ejemplo:
# from my_graph import agent_executor

def invoke_graph(query: str) -> Dict[str, Any]:
    """Invoke the graph with the user's query and return the response."""
    try:
        # Create initial state with user message
        state = State(messages=[{"role": "user", "content": query}])
        
        # Invoke the graph with the state
        response = app.invoke(state, config={"thread_id": "123"})
        
        # Extract the last message from the response
        if isinstance(response, dict) and "messages" in response:
            messages = response["messages"]
            if messages and len(messages) > 0:
                last_message = messages[-1]
                if hasattr(last_message, "content"):
                    return last_message.content
                elif isinstance(last_message, dict) and "content" in last_message:
                    return last_message["content"]
        
        return str(response)
    except Exception as e:
        st.error(f"Error invoking graph: {str(e)}")
        return f"Lo siento, hubo un error al procesar tu solicitud: {str(e)}"

if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(layout="wide", page_title="Coder UI")

st.markdown("## Chat")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 💬 Conversación")
    
    for msg in st.session_state.messages:
        role, content = msg["role"], msg["content"]
        if role == "user":
            st.markdown(f"**🧑 Tú:** {content}")
        else:
            st.markdown(f"**🤖 AI:** {content}")

    st.markdown("---")
    with st.form("chat-form", clear_on_submit=True):
        user_input = st.text_input("💡 Escribe tu idea del proyecto:", key="input", label_visibility="collapsed")
        submitted = st.form_submit_button("Enviar")

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Invocar el graph con la pregunta del usuario
        with st.spinner("Procesando tu solicitud..."):
            ai_response = invoke_graph(user_input)
            
            # Si la respuesta es un string, la agregamos directamente
            if isinstance(ai_response, str):
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            # Si es un diccionario, intentamos extraer el contenido
            elif isinstance(ai_response, dict):
                content = ai_response.get("content", str(ai_response))
                st.session_state.messages.append({"role": "assistant", "content": content})
            else:
                st.session_state.messages.append({"role": "assistant", "content": str(ai_response)})

with col2:
    st.markdown("### 📁 Vista del Proyecto")

    tab1, tab2 = st.tabs(["📝 Código", "✅ Resultado"])

    with tab1:
        st.markdown("#### Archivos Generados")
        sandbox = Path("sandbox-any")
        if sandbox.exists():
            for file in sandbox.rglob("*"):
                if file.is_file():
                    st.markdown(f"**`{file.relative_to(sandbox)}`**")
                    content = file.read_text()
                    st.code(content, language=file.suffix.lstrip('.'))

    with tab2:
        st.markdown("#### Resultado del Código")
        result_path = sandbox / "result.txt"
        if result_path.exists():
            st.text(result_path.read_text())
        else:
            st.info("Aún no se ha generado ningún resultado.")
