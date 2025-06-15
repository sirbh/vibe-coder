from utils.getFiles import get_project_files_from_container

from langchain_core.tools import tool

from typing import List, Dict

@tool
def get_project_files(container_name: str, project_name: str) -> List[Dict[str, str]]:
    """
    Retrieves the list of files in the project directory inside the Docker container.

    Args:
        container_name: Name of the running Docker container.
        project_name: The name of the project inside the container (e.g., "my-app").

    Returns:
        List of files in the project directory.
    """
    return get_project_files_from_container(container_name, project_name)