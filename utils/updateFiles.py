import subprocess
import tempfile
import os
from typing import List, Dict

from utils.getFiles import get_project_files_from_container

def apply_updates_to_container(container_name: str, project_name: str, updated_files: List[Dict[str, str]]) -> None:
    """
    Applies updates to project files inside the Docker container.

    Args:
        container_name: Name of the running Docker container.
        project_name: The name of the project inside the container (e.g., "my-app").
        updated_files: List of {"path": ..., "content": ...} to write.
    """
    for file in updated_files:
        container_path = f"/{project_name}/{file['path']}"
        
        # Step 1: Write content to a temp file on the host
        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as tmp:
            tmp.write(file["content"])
            tmp_path = tmp.name

        try:
            # Step 2: Ensure parent directory exists inside container
            dir_path = os.path.dirname(container_path)
            subprocess.run(
                ["docker", "exec", container_name, "mkdir", "-p", dir_path],
                check=True
            )

            # Step 3: Copy the file into the container
            subprocess.run(
                ["docker", "cp", tmp_path, f"{container_name}:{container_path}"],
                check=True
            )
        finally:
            os.remove(tmp_path)  # Cleanup temp file


# apply_updates_to_container("nextjs-hlrso6","my-next-app",get_project_files_from_container("nextjs-hlrso6", "my-next-app"))