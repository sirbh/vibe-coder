from tools.getFiles import get_project_files_from_container
from tools.createProject import create_next_project_container, LaunchStatus

from langchain_core.messages import HumanMessage, SystemMessage

import json

from pydantic import BaseModel
from agents.vibe_coder_agent_v3 import graph, read_file_as_string
from agents.coder_agent import get_agent


from fastapi.middleware.cors import CORSMiddleware


from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

user_input = read_file_as_string("prompts/user_prompt.txt")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Root route
@app.get("/")
def read_root():
    return {"message": "vibe coder API is running!"}

@app.get("/api/project-files")
def read_files(container_name: str, project_name: str):
    files = get_project_files_from_container(container_name, project_name)
    if not files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No files found in project '{project_name}' in container '{container_name}'."
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "files": files,
            "message": f"Files retrieved successfully from project '{project_name}' in container '{container_name}'."
        }
    )

@app.get("/api/create-project/")
def create_project(project_name: str):
    """
    Creates a new Next.js project with the given name.
    """
    resp = create_next_project_container(project_name)

    if resp["status"] == LaunchStatus.SUCCESS:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "success",
                "container_name": resp["container_name"],
                "port": resp["port"],
                "message": f"Project '{project_name}' created successfully."
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project '{project_name}'."
        )
    

class ChatRequest(BaseModel):
    message: str
    poject_name: str  # <-- typo kept to match your frontend
    container_name: str

@app.post("/api/chat")
def chat(payload: ChatRequest):
    print(f"Received message: {payload.message}")
    print(f"Project Name: {payload.poject_name}")
    print(f"Container Name: {payload.container_name}")

    system = read_file_as_string("prompts/system_v3.text").replace("{{PROJECT_FILES_HERE}}",json.dumps(get_project_files_from_container(payload.container_name,payload.poject_name),indent=2))

    input = user_input.replace("{{USER_MESSAGE}}", payload.message).replace("{{PROJECT_NAME}}", payload.poject_name).replace("{{PROJECT_CONTAINER}}", payload.container_name) 


    print (f"Input to graph: {input}")
    print (f"System prompt: {system}")

    agent = get_agent(system)

    messages = [HumanMessage(content=input)]
    result = agent.invoke({"messages": messages})

    result_message = result["messages"][-1]

    print(f"Result message: {result_message}")

    # result = graph.invoke({
    #     message: input,
    # })
    return {
        "message": f"{result_message.content}"
    }


