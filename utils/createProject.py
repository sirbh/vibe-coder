import subprocess, random, socket, string, time, requests, os

from enum import Enum
from typing import TypedDict


def find_free_port() -> int:
    """Find a free port on the host system."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def random_container_name(prefix="proj"):
    return f"{prefix}-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def wait_for_app_ready(port: int, timeout: int = 120) -> bool:

    host = os.getenv("HOST", "localhost")
    print(os.getenv("HOST"))
    url = f"http://{host}:{port}"
    for _ in range(timeout):
        try:
            res = requests.get(url)
            if res.status_code in [200, 404]:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    return False

class LaunchStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class ContainerLaunchResult(TypedDict):
    status: LaunchStatus
    container_name: str
    port: int


def create_next_project_container(project_name: str) -> ContainerLaunchResult:
    """
    Creates a new Next.js app in a Docker container on a free host port.
    Returns a dict with status, container name, and port.
    """
    port = find_free_port()
    container_name = random_container_name()

    command = [
        "docker", "run", "-d",
        "--name", container_name,
        "-p", f"{port}:3000",
        "node:18",
        "bash", "-c",
        f"npm install -g create-next-app@15.3.3 && "
        f"create-next-app {project_name} --use-npm --yes && "
        f"cd {project_name} && "
        f"sed -i 's/next dev/next dev -H 0.0.0.0/' package.json && "
        f"npm install && "
        f"npm run dev"
    ]

    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        status = LaunchStatus.SUCCESS if wait_for_app_ready(port) else LaunchStatus.FAILURE
    except subprocess.CalledProcessError:
        status = LaunchStatus.FAILURE

    return {
        "status": status,
        "container_name": container_name,
        "port": port
    }


