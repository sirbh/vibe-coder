'use client'

import { useEffect, useRef, useState } from "react"

interface IChatPanelProps {
  port: string
  projectName: string
  containerName: string
}

export default function ChatPanel({ port, projectName, containerName }: IChatPanelProps) {
  const [messages, setMessages] = useState<{ role: "user" | "bot"; text: string }[]>([])
  const [input, setInput] = useState("")
  const [iframeUrl, setIframeUrl] = useState("http://localhost:" + port)
  const [iframeKey, setIframeKey] = useState(0)
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  const handleSend = async () => {
    const trimmed = input.trim()
    if (!trimmed) return

    setMessages((prev) => [...prev, { role: "user", text: trimmed }])
    setInput("")
    setLoading(true)

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmed,
          project_name: projectName,
          container_name: containerName,
        }),
      })

      if (!res.ok || !res.body) {
        throw new Error("❌ Invalid streaming response")
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder("utf-8")

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })

        setMessages((prev) => {
          const last = prev[prev.length - 1]
          if (last?.role === "bot") {
            return [...prev.slice(0, -1), { role: "bot", text: last.text + chunk }]
          } else {
            return [...prev, { role: "bot", text: chunk }]
          }
        })
      }
    } catch (err) {
      console.error("Error talking to server:", err)
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "❌ Error talking to server" },
      ])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className="flex h-screen w-full">
      {/* Left: Chat Panel */}
      <div className="w-1/3 bg-zinc-900 text-white flex flex-col border-r border-zinc-700 py-12">
        <div className="p-4 border-b border-zinc-700">
          <h2 className="text-xl font-semibold">🤖 Chat Panel</h2>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-2 space-y-2">
          {messages.length === 0 ? (
            <p className="text-sm text-zinc-400">No messages yet.</p>
          ) : (
            messages.map((msg, i) => (
              <div
                key={i}
                className={`p-2 rounded text-sm ${
                  msg.role === "user" ? "bg-blue-800 text-right" : "bg-zinc-800"
                }`}
              >
                {msg.text}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t border-zinc-700">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey && !loading) {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder={loading ? "Please wait..." : "Type a message..."}
            disabled={loading}
            rows={2}
            className={`w-full resize-none border rounded px-3 py-2 text-sm outline-none focus:ring ${
              loading
                ? "bg-zinc-700 text-zinc-400 border-zinc-600 cursor-not-allowed"
                : "bg-zinc-800 text-white border-zinc-600 focus:ring-blue-500"
            }`}
          />
        </div>
      </div>

      {/* Right: Iframe with URL and reload */}
      <div className="w-2/3 bg-zinc-800 flex flex-col">
        <div className="flex items-center justify-between border-b border-zinc-700 bg-zinc-900 text-white px-4 border-l">
          <h2 className="text-xl font-semibold px-2">URL</h2>
          <input
            type="text"
            value={iframeUrl}
            onChange={(e) => setIframeUrl(e.target.value)}
            className="flex-1 h-10 bg-zinc-800 text-white border border-zinc-600 px-3 py-1 text-sm outline-none mr-2"
          />
          <button
            onClick={() => setIframeKey((prev) => prev + 1)}
            className="bg-zinc-700 hover:bg-zinc-600 text-white px-3 py-1 text-sm rounded"
          >
            🔄 Reload
          </button>
        </div>

        <div className="flex-1">
          <iframe
            key={iframeKey}
            src={iframeUrl}
            className="w-full h-full border-0"
            sandbox="allow-same-origin allow-scripts allow-forms"
          />
        </div>
      </div>
    </div>
  )
}
