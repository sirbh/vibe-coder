from langchain_core.tools import tool

from typing import List, Dict

from utils.updateFiles import apply_updates_to_container

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
