"use client";

import { useEffect, useState } from "react";
import Editor from "@monaco-editor/react";
import axiosInstance from "@/lib/axios";

type FileNode = {
  name: string;
  path: string;
  content?: string;
  children?: FileNode[];
  isDirectory: boolean;
};

interface IProjectViewerProps {
  containerName: string;
  projectName: string;
}

export default function ProjectViewer({containerName,projectName}: IProjectViewerProps) {
  const [files, setFiles] = useState<FileNode[]>([]);
  const [activeFile, setActiveFile] = useState<FileNode | null>(null);



  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const res = await axiosInstance.get("/project-files", {
          params: {
            container_name: containerName,
            project_name: projectName,
          },
        });
        const flatFiles = res.data.files as { path: string; content: string }[];
        const fileTree = buildFileTree(flatFiles);
        setFiles(fileTree);
      }
      catch (error) {
        console.error("Error fetching project files:", error);
      }
    };
    fetchFiles();
  }, []);

  function buildFileTree(flatFiles: { path: string; content: string }[]): FileNode[] {
    const root: FileNode[] = [];

    for (const file of flatFiles) {
      const parts = file.path.split("/");
      let currentLevel = root;

      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        const existing = currentLevel.find((f) => f.name === part);

        if (existing) {
          if (!existing.children) existing.children = [];
          currentLevel = existing.children;
        } else {
          const newNode: FileNode = {
            name: part,
            path: parts.slice(0, i + 1).join("/"),
            isDirectory: i !== parts.length - 1,
            content: i === parts.length - 1 ? file.content : undefined,
            children: i !== parts.length - 1 ? [] : undefined,
          };
          currentLevel.push(newNode);
          if (newNode.children) currentLevel = newNode.children;
        }
      }
    }

    return root;
  }

  const FileTree = ({ nodes }: { nodes: FileNode[] }) => (
    <ul className="pl-2 space-y-1">
      {nodes.map((node) => (
        <li key={node.path}>
          {node.isDirectory ? (
            <details className="group">
              <summary className="cursor-pointer hover:text-blue-400">{node.name}/</summary>
              {node.children && <FileTree nodes={node.children} />}
            </details>
          ) : (
            <button
              onClick={() => setActiveFile(node)}
              className="block w-full text-left text-sm px-2 py-1 rounded hover:bg-zinc-700"
            >
              {node.name}
            </button>
          )}
        </li>
      ))}
    </ul>
  );

  return (
    <div className="flex h-full w-full">
      {/* Sidebar */}
      <div className="w-1/3 bg-zinc-900 text-white overflow-auto p-4 py-12">
        <h2 className="text-xl font-semibold mb-4">📁 Project Files</h2>
        <FileTree nodes={files} />
      </div>

      {/* Editor */}
      <div className="w-2/3 p-4 bg-zinc-800">
        {activeFile ? (
          <>
            <h3 className="text-white text-sm mb-2">{activeFile.path}</h3>
            <Editor
              height="90vh"
              language={getLangFromPath(activeFile.path)}
              value={activeFile.content}
              theme="vs-dark"
              options={{ readOnly: true }}
            />
          </>
        ) : (
          <p className="text-white">Select a file to view</p>
        )}
      </div>
      
    </div>
  );
}

function getLangFromPath(path: string): string {
  if (path.endsWith(".ts") || path.endsWith(".tsx")) return "typescript";
  if (path.endsWith(".js") || path.endsWith(".jsx")) return "javascript";
  if (path.endsWith(".json")) return "json";
  if (path.endsWith(".css")) return "css";
  if (path.endsWith(".html")) return "html";
  if (path.endsWith(".md")) return "markdown";
  return "plaintext";
}
