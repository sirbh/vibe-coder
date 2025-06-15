# agent.py

from langgraph.graph import MessagesState, StateGraph, START
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from agents.coder_agent.prompts.system_prompt import MODEL_SYSTEM_MESSAGE
from agents.coder_agent.tools.applyUpdates import apply_updates
from agents.coder_agent.tools.getProjectFiles import get_project_files
from utils.fileReader import read_file_as_string

from langchain_core.runnables.config import RunnableConfig

# Tools and model
tools = [apply_updates, get_project_files]
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

system_prompt = read_file_as_string("agents/coder_agent/prompts/system.txt")

class CoderAgentState(MessagesState):
    summary: str

def assistant(state: CoderAgentState, config: RunnableConfig, store):
    project_id = config["configurable"]["project_id"]
    namespace = ("projects", project_id)
    projects = store.get(namespace, "project_details")

    project_name = projects.value.get("project_name")
    container_name = projects.value.get("container_name")

    system_msg = MODEL_SYSTEM_MESSAGE.format(
        project_name=project_name,
        container_name=container_name
    )

    return {
        "messages": [
            llm_with_tools.invoke(
                [SystemMessage(content=str(system_msg))] + state["messages"]
            )
        ]
    }

# This function creates the graph ONCE
def create_graph(store, checkpointer):
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")

    return builder.compile(store=store, checkpointer=checkpointer)
