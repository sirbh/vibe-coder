import subprocess
from typing import List, Dict

def get_project_files_from_container(container_name: str, project_name: str) -> List[Dict[str, str]]:
    include_exts = [".ts", ".tsx", ".js", ".jsx", ".json", ".css", ".html", ".md"]
    exclude_dirs = {"node_modules", ".git", ".next", "build", "dist", "public", "out"}
    ignore_files = {"package-lock.json", "yarn.lock"}

    # Step 1: Construct find expression string
    ext_expr = " -o ".join([f"-name '*{ext}'" for ext in include_exts])
    dir_expr = " ".join([f"-not -path '*/{d}/*'" for d in exclude_dirs])
    file_expr = " ".join([f"-not -name '{f}'" for f in ignore_files])

    # Final shell command string (all in one)
    find_cmd = f"find /{project_name} -type f \\( {ext_expr} \\) {dir_expr} {file_expr}"

    try:
        output = subprocess.check_output(
            ["docker", "exec", container_name, "bash", "-c", find_cmd],
            stderr=subprocess.STDOUT
        ).decode().strip()

        files = output.split("\n") if output else []
        file_objects = []

        for filepath in files:
            try:
                content = subprocess.check_output(
                    ["docker", "exec", container_name, "cat", filepath],
                    stderr=subprocess.DEVNULL
                ).decode("utf-8", errors="replace")
                relative_path = filepath.replace(f"/{project_name}/", "")
                file_objects.append({
                    "path": relative_path,
                    "content": content
                })
            except subprocess.CalledProcessError:
                continue

        return file_objects

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to read files:\n{e.output.decode()}")
        return []



# print(get_project_files_from_container("nextjs-hlrso6", "my-next-app"))