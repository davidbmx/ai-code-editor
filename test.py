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

PRIMARY_PROMPT = open("prompt.md").read()


sandbox_path = "sandbox"

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    input: str
    code:  str
    refactored_code: str
    decision: str

class Evaluator(BaseModel):
    step: Literal["refactor", "not refactor"] = Field(
        description="Decide if need to refactor the code or not",
    )

# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
llm = ChatOpenAI(model="gpt-4o-mini")
llm_evaluator = llm.with_structured_output(Evaluator)

@tool
def install_dependencies(command: str):
    """Install dependencies for the project
    Args:
        command: the command to install the dependencies
        example: npm install
    """
    print(f"Installing dependencies with command: {command}")
    print(os.getcwd())
    os.system(f"cd {sandbox_path} && {command}")
    return "Dependencies installed successfully"

@tool
def run_neccesary_commands(command: str):
    """Run neccesary commands for the project
    Args:
        command: the command to run the neccesary commands
        example: npm install && npm run dev 
    """
    print(f"Running neccesary commands with command: {command}")
    print(os.getcwd())
    logs = os.system(f"cd {sandbox_path} && {command}")
    return f"Neccesary commands run successfully feedback: \n\n {logs}"

@tool
def run_project(command: str):
    """Run the project
    Args:
        command: the command to run the project
        example: npm run dev
    """
    print(f"Running project with command: {command}")
    # os.system(f"cd {sandbox_path} && {command}")
    return "Project running successfully"

@tool
def list_shadcn_ui_components() -> list[str]:
    """List all the shadcn/ui components installed

    """
    list_components = os.listdir(f"{sandbox_path}/src/components/ui")
    return list_components

@tool
def save_code(code: str, name_component: str):
    """
    Save the code in the sandbox
    the sandbox path is ./sandbox/
    Args:
        code: the code to save
        name_component: the name of the component, can include folder and extension
    """
    print("================================================")
    print(f"Saving code in {name_component}")

    # Normalizar extensión
    base, ext = os.path.splitext(name_component)
    if ext.lower() not in [".tsx", ".ts"]:
        name_component = base + ".tsx"

    full_path = f"{sandbox_path}/{name_component}"
    dir_path = os.path.dirname(full_path)
    os.makedirs(dir_path, exist_ok=True)
    with open(full_path, "w") as f:
        f.write(code)
    return f"Code saved successfully at {full_path}"

tools = [install_dependencies, run_project, save_code, list_shadcn_ui_components, run_neccesary_commands]

def planner(state: State) -> State:
    message = state["input"]
    prompt = f"""
    Actúa como un **analista de requerimientos y arquitecto de software senior**, con una profunda experiencia en el desarrollo de aplicaciones web y móviles.

    Tu principal objetivo es tomar la idea inicial del usuario y realizar un **análisis exhaustivo de los requerimientos**, identificando claramente las funcionalidades necesarias y la estructura de la aplicación. Luego, generarás un **plan de desarrollo detallado y estructurado** que servirá como una guía clara y comprensible para otro LLM encargado de la implementación del código.

    El plan debe ser lo suficientemente detallado para que el LLM de codificación pueda entender cada componente, sus responsabilidades y cómo se interconectan.

    Considera los siguientes aspectos en tu análisis y plan:

    1.  **Interpretación de la Idea del Usuario:** Comprende a fondo la necesidad y los objetivos detrás de la idea del usuario. Realiza preguntas aclaratorias si es necesario (aunque en este prompt asumiremos que la idea es clara).

    2.  **Identificación de Casos de Uso:** Define los casos de uso principales que los usuarios podrán realizar con la aplicación.

    3.  **Desglose Funcional:** Divide la aplicación en módulos o funcionalidades lógicas principales.

    4.  **Especificación de Requerimientos:** Para cada módulo o funcionalidad, detalla los requerimientos funcionales (qué debe hacer el sistema) y, si es posible, algunos requerimientos no funcionales relevantes (ej. rendimiento, seguridad básica).

    5.  **Diseño de la Arquitectura de Alto Nivel:** Describe la arquitectura general de la aplicación, incluyendo las principales capas o componentes y cómo interactúan entre sí (ej. frontend, backend, base de datos). Menciona las posibles tecnologías o paradigmas de desarrollo recomendados (sin ser demasiado específico en la implementación).

    6.  **Plan de Desarrollo por Módulos/Pantallas:** Organiza el desarrollo en módulos o pantallas clave, priorizando posiblemente las funcionalidades core. Para cada módulo/pantalla, indica las principales tareas de desarrollo necesarias.

    7.  **Estructura de Datos (Conceptual):** Describe brevemente las principales entidades de datos que la aplicación manejará y sus relaciones (sin necesidad de un esquema de base de datos detallado).

    8.  **Consideraciones para el LLM de Codificación:** Incluye notas o consideraciones específicas que el LLM de codificación debería tener en cuenta durante la implementación (ej. convenciones de nombrado, manejo de errores, principios de diseño).

    **Idea del Usuario:**
    {message}

    **Plan de Desarrollo Estructurado para el LLM de Codificación:**

    """

    result = llm.invoke(prompt)
    return {"messages": [{"role": "user", "content": result.content}]}

def coder(state: State) -> State:

    coder_with_tools = llm.bind_tools(tools)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", PRIMARY_PROMPT),
            ("placeholder", "{messages}"),
        ]
    )

    chain = prompt_template | coder_with_tools

    result = chain.invoke(state)
    return {"messages": [result]}

def reviewer(state: State) -> State:
    decision = llm_evaluator.invoke(
        [
            SystemMessage(
                content="You are a expert in reviewing code. Review carefully the following code and route the input to refactor or not refactor based on the code quality:"
            ),
            HumanMessage(content=state["code"]),
        ]
    )
    print(decision.step)
   
    return {"decision": decision.step}

def refactor(state: State) -> State:
    prompt = f"""
    You are a expert in refactoring code.
    You are given a code and you need to refactor it
    The code is the following:
    
    {state["code"]}
    """
    result = llm.invoke(prompt)
    return {"refactored_code": result.content}

def check_router(state: State) -> State:
    # return state["decision"]
    return "not refactor"



workflow = StateGraph(State)
# workflow.add_node("planner", planner)
workflow.add_node("coder", coder)
workflow.add_node("reviewer", reviewer)
workflow.add_node("refactor", refactor)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "coder")
# workflow.add_edge("planner", "coder")
# workflow.add_edge("coder", "reviewer")
workflow.add_conditional_edges(
    "coder",
    tools_condition,
    {
        
        "tools": "tools",
        END: END,
    },
)
workflow.add_edge("tools", "coder")
# workflow.add_conditional_edges(
#     "reviewer",
#     check_router,
#     {
#         "refactor": "refactor",
#         "not refactor": END,
#     },
# )
# workflow.add_edge("refactor", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
