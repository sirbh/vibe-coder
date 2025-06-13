'use client'

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import ProjectViewer from "./ProjectViewer"
import ChatPanel from "./ChatPanel"
import { useRouter, useSearchParams } from "next/navigation"

export default function Manager() {
  const searchParams = useSearchParams()
  const container = searchParams.get("container_name")
  const project = searchParams.get("project_name")
  const port = searchParams.get("port")

  const router = useRouter()

  console.log("Container:", container)
  console.log("Project:", project)
  console.log("Port:", port)

  if (!container || !project || !port) {
     router.push("/")
  }
  return (
    <Tabs defaultValue="project" className="w-screen h-screen relative bg-zinc-900 text-white">
      {/* Tab Buttons */}
      <TabsList className="absolute top-0 left-0 w-1/3 h-10 bg-zinc-900 text-white border-b border-zinc-700 rounded-none z-10">
        <TabsTrigger
          value="chat"
          className="text-zinc-400 disabled:text-zinc-500 disabled:cursor-not-allowed 
                     data-[state=active]:bg-zinc-800 data-[state=active]:text-white 
                     hover:bg-zinc-800 hover:text-white px-4 py-2 text-sm"
        >
          Chat
        </TabsTrigger>
        <TabsTrigger
          value="project"
          className="text-zinc-400 disabled:text-zinc-500 disabled:cursor-not-allowed 
                     data-[state=active]:bg-zinc-800 data-[state=active]:text-white 
                     hover:bg-zinc-800 hover:text-white px-4 py-2 text-sm"
        >
          Project Files
        </TabsTrigger>
      </TabsList>

      {/* Tab Content */}
      <TabsContent value="project">
        <ProjectViewer containerName={container!} projectName={project!} />
      </TabsContent>

      <TabsContent value="chat">
        <ChatPanel port={port!} containerName={container!} projectName={project!} />
      </TabsContent>
    </Tabs>
  )
}
