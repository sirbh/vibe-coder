import os
import json
import getpass

from langgraph.graph import MessagesState, StateGraph, START
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.store.base import BaseStore
from langchain_core.runnables.config import RunnableConfig

from db.memory import store, checkpointer

from agents.coder_agent.prompts.system_prompt import MODEL_SYSTEM_MESSAGE
from agents.coder_agent.tools.applyUpdates import apply_updates
from agents.coder_agent.tools.getProjectFiles import get_project_files

from utils.fileReader import read_file_as_string


# === Load your OpenAI key ===
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

# === Setup tools and LLM ===
tools = [apply_updates, get_project_files]
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

# === Read system prompt ===
system_prompt = read_file_as_string("agents/coder_agent/prompts/system.txt")

# === Define custom state ===
class CoderAgentState(MessagesState):
    summary: str

# === Assistant function ===
def assistant(state: CoderAgentState, config: RunnableConfig, store: BaseStore):
    project_id = config["configurable"]["project_id"]
    namespace = ("projects", project_id)
    projects = store.get(namespace, "project_details")

    print(f"Projects Namespace: {projects}")
    project_name = projects.value.get("project_name")
    container_name = projects.value.get("container_name")

    print(f"Project Name: {project_name}")
    print(f"Container Name: {container_name}")

    system_msg = MODEL_SYSTEM_MESSAGE.format(
        project_name=project_name,
        container_name=container_name
    )

    print("I really hope this works")

    return {
        "messages": [
            llm_with_tools.invoke(
                [SystemMessage(content=str(system_msg))] + state["messages"]
            )
        ]
    }

# === Build the LangGraph ===
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")  # Optional: loop back if needed

# === Compile the graph ===
graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)
