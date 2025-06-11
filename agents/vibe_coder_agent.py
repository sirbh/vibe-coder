import os, getpass
from dotenv import load_dotenv

from typing import List, Dict

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

# Load your OpenAI key
load_dotenv()
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")
_set_env("OPENAI_API_KEY")

config = {"configurable": {"thread_id": "vibe_code_1"}}
memory = MemorySaver()

def read_file_as_string(filepath: str) -> str:
    """Read the entire contents of a file and return as a string."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

system_prompt = read_file_as_string("prompts/system.txt")


@tool
def get_project_files(
    root_dir: str,
) -> list[dict[str, str]]:
    """
    Recursively reads code files from the given project directory and returns a list
    of { "path": ..., "content": ... } dictionaries.


    Returns:
        List of { "path": str, "content": str } objects.
    """
    include_exts = [".ts", ".tsx", ".js", ".jsx", ".json", ".css", ".html", ".md"]
    exclude_dirs = set(["node_modules", ".git", ".next", "build", "dist", "public", "out"])
    ignore_files = set(["package-lock.json", "yarn.lock"])

    file_objects = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip unwanted directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:
            if filename in ignore_files:
                continue

            if not any(filename.endswith(ext) for ext in include_exts):
                continue

            full_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(full_path, root_dir)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    file_objects.append({
                        "path": relative_path.replace("\\", "/"),  # Normalize for Windows
                        "content": content
                    })
            except Exception as e:
                print(f"⚠️ Skipped file {relative_path}: {e}")

    return file_objects


@tool
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
def apply_updates(root:str,updated_files: List[Dict[str, str]]) -> None:
    """
    Writes updated files into the given root project directory.
    
    Args:
        root: Root directory of your project
        updated_files: List of {"path": ..., "content": ...} to write
    """
    for file in updated_files:
        path = os.path.join(root, file["path"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(file["content"])

print(get_project_files("projects/lawrm"))



tools = [create_next_app, apply_updates, get_project_files]

# 2. LLM setup with tools
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

# 3. System message
sys_msg = SystemMessage(content=system_prompt)

# 4. Assistant node: calls LLM
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# 5. Graph setup
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")  # optional: loop back to LLM if needed

# Compile
graph = builder.compile(checkpointer=memory)


while True:
    user_input = input("You: ")
    if user_input.lower() in {"exit", "quit"}:
        print("👋 Exiting OpenAPI bot.")
        break

    messages = [HumanMessage(content=user_input)]
    result = graph.invoke({"messages": messages}, config)

    print("\n🔍 Bot:")
    result["messages"][-1].pretty_print()
