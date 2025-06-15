import json, uuid, os

from dotenv import load_dotenv
load_dotenv()


from pydantic import BaseModel

from contextlib import asynccontextmanager


from utils.getFiles import get_project_files_from_container
from utils.createProject import create_next_project_container, LaunchStatus
from utils.fileReader import read_file_as_string

from langchain_core.messages import HumanMessage
from langgraph.store.postgres import PostgresStore

from agents.coder_agent.agent import graph

from db.memory import store,checkpointer, store_ctx, checkpointer_ctx

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse

from agents.coder_agent.prompts.system_prompt import MODEL_SYSTEM_MESSAGE



user_input = read_file_as_string("prompts/user_prompt.txt")
DB_URI = os.environ.get("DB_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = store
    app.state.checkpointer = checkpointer
    yield
    store_ctx.__exit__(None, None, None)
    checkpointer_ctx.__exit__(None, None, None)

app = FastAPI(lifespan=lifespan)

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
    val = MODEL_SYSTEM_MESSAGE.format(
        project_name="vibe-coder",
        container_name="proj-vju59a"
    )
    print(f"System Prompt: {val}")
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
    try:
        # Create the project container
        resp = create_next_project_container(project_name)
        print("Container Response:", resp)  # Optional: Debug output

        if resp["status"] != LaunchStatus.SUCCESS:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create project '{project_name}'."
            )

        namespace_for_memory = ("projects", resp["container_name"] + "_space")
        key = "project_details"
        value = {
                "project_name": project_name,
                "container_name": resp["container_name"]
            }

        store.put(namespace_for_memory, key, value)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "success",
                "container_name": resp["container_name"],
                "port": resp["port"],
                "message": f"Project '{project_name}' created successfully."
            }
        )

    except Exception as e:
        print("Error:", str(e))  # Optional: Debug output
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    

class ChatRequest(BaseModel):
    message: str
    project_name: str  # <-- typo kept to match your frontend
    container_name: str

@app.post("/api/chat")
def chat(payload: ChatRequest):
    print(f"Received message: {payload.message}")
    print(f"Project Name: {payload.project_name}")
    print(f"Container Name: {payload.container_name}")

   
    config = {"configurable": {"thread_id": payload.container_name+"_thread", "project_id": payload.container_name+"_space"}}

    messages = [HumanMessage(content=payload.message)]

    # async def even_generator():
    #     async for event in graph.astream_events(
    #         {"messages": messages, "summary": ""},
    #         config=config,
    #         version="v2"
    #     ):
    #         if event["event"] == "on_chat_model_stream" and event['metadata'].get('langgraph_node','') == "assistant":
    #             data = event["data"]
    #             # Yield text to client
    #             yield data["chunk"].content
    
    # return StreamingResponse(even_generator(), media_type="text/plain")



    result = graph.invoke({"messages": messages, "summary":""},config=config)

    result_message = result["messages"][-1]

    print(f"Result message: {result_message}")

    return {
        "message": f"{result_message.content}"
    }


