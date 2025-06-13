import os, getpass
from dotenv import load_dotenv

from typing import List, Dict
import json

import subprocess

from langgraph.graph import MessagesState, StateGraph, START
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from openapi_spec_validator import validate_spec
from openapi_spec_validator.exceptions import OpenAPISpecValidatorError
import yaml

from tools.getFiles import get_project_files_from_container
from tools.updateFiles import apply_updates_to_container

# Load your OpenAI key
load_dotenv()
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")
_set_env("OPENAI_API_KEY")

# config = {"configurable": {"thread_id": "vibe_code_1"}}
# memory = MemorySaver()

def read_file_as_string(filepath: str) -> str:
    """Read the entire contents of a file and return as a string."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()




def get_project_files() -> list[dict[str, str]]:
    """
    Recursively reads code files from the given project directory and returns a list
    of { "path": ..., "content": ... } dictionaries.


    Returns:
        List of { "path": str, "content": str } objects.
    """
    # return get_project_files_from_container("nextjs-hlrso6", "my-next-app")
    return "file"



def create_next_app(project_name: str) -> str:
    """
    Creates a new Next.js app using npx in the specified target directory with the given project name.
    """
    target_directory = "projects"
    full_path = os.path.join(target_directory, project_name)

    try:
        os.makedirs(target_directory, exist_ok=True)

        # Use shell=True for proper PATH resolution on Windows
        subprocess.run(
            f"npx create-next-app@latest {project_name} --yes",
            cwd=target_directory,
            shell=True,
            check=True
        )

        return f"✅ Next.js app created successfully at: {full_path}"
    
    except Exception as e:
        return (
            f"❌ Unexpected error: {str(e)}.\n"
            "Ask user to fix the issue\n"
        )


@tool
def apply_updates(container_name: str, project_name: str, updated_files: List[Dict[str, str]]) -> None:
    """
    Applies updates to project files inside the Docker container.

    Args:
        container_name: Name of the running Docker container.
        project_name: The name of the project inside the container (e.g., "my-app").
        updated_files: List of {"path": ..., "content": ...} to write.
    """
    return apply_updates_to_container(container_name,project_name,updated_files)




tools = [apply_updates]

# 2. LLM setup with tools
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

# system_prompt = read_file_as_string("prompts/system_v3.txt").replace("{{PROJECT_FILES_HERE}}",json.dumps(get_project_files(),indent=2))


# # 3. System message
# sys_msg = SystemMessage(content=system_prompt)

# # 4. Assistant node: calls LLM
# def assistant(state: MessagesState):
#     return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# # 5. Graph setup
# builder = StateGraph(MessagesState)
# builder.add_node("assistant", assistant)
# builder.add_node("tools", ToolNode(tools))
# builder.add_edge(START, "assistant")
# builder.add_conditional_edges("assistant", tools_condition)
# builder.add_edge("tools", "assistant")  # optional: loop back to LLM if needed

# # Compile
# graph = builder.compile()


# while True:
#     user_input = input("You: ")
#     if user_input.lower() in {"exit", "quit"}:
#         print("👋 Exiting OpenAPI bot.")
#         break

#     messages = [HumanMessage(content=user_input)]
#     result = graph.invoke({"messages": messages}, config)

#     print("\n🔍 Bot:")
#     result["messages"][-1].pretty_print()


def get_agent(system_prompt: str) -> StateGraph:
    """
    Returns the compiled graph for the Vibe Coder agent.
    """
    sys_msg = SystemMessage(content=system_prompt)

    def assistant(state: MessagesState):
        return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# 5. Graph setup
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")  # optional: loop back to LLM if needed

    graph = builder.compile()


    return graph