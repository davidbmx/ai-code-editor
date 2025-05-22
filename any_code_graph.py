from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from typing_extensions import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import tools_condition
from langgraph.graph.message import AnyMessage, add_messages
from typing import Annotated
import os
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

PRIMARY_PROMPT = open("any_coder_prompt.md").read()


sandbox_path = "sandbox-any"

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
llm = ChatOpenAI(model="gpt-4o-mini")

@tool
def run_neccesary_commands(command: str):
    """Run neccesary commands for the project
    Args:
        command: the command to run the neccesary commands
        example: npm install && npm run dev 
    """
    print(f"Running neccesary commands with command: {command}")

    logs = os.system(f"cd {sandbox_path} && {command}")
    print(logs)
    return f"Neccesary commands run successfully feedback: \n\n {logs}"

@tool
def write_file(path: str, content: str):
    """Guarda un archivo en el sistema de archivos."""
    full_path = os.path.join(sandbox_path, path)
    print("creating: {path}")
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    return f"Archivo escrito: {path}"


@tool
def run_commands(command: str):
    """
    Ejecuta comandos necesarios en el sandbox para preparar o iniciar el proyecto.
    Args:
        command: Comando a ejecutar (ej. 'npm install && npm run dev')
    """
    import subprocess
    try:
        print("executing: {command}")
        result = subprocess.run(
            command,
            shell=True,
            cwd=sandbox_path,
            capture_output=True,
            text=True,
            timeout=120  # Evita que se quede colgado
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}



tools = [write_file, run_commands]

def coder(state: State) -> State:
    coder_with_tools = llm.bind_tools(tools)
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", PRIMARY_PROMPT),
            ("placeholder", "{messages}"),
        ]
    )
    print("creating code")
    chain = prompt_template | coder_with_tools
    result = chain.invoke(state)
    return {"messages": [result]}

def planner(state: State) -> State:
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "Eres un asistente que genera un plan detallado para crear un proyecto de software crea solo el plan de estructura y tecnologias pasos a seguir no el codigo."),
            ("placeholder", "{messages}"),
        ]
    )
    chain = prompt_template | llm
    result = chain.invoke(state)
    return {"messages": [result]}

workflow = StateGraph(State)
# workflow.add_node("planner", planner)
workflow.add_node("coder", coder)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "coder")
workflow.add_conditional_edges(
    "coder",
    tools_condition,
)
workflow.add_edge("tools", "coder")

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
