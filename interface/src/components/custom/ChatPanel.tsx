'use client'

import axiosInstance from "@/lib/axios";
import { useEffect, useRef, useState } from "react";

interface IChatPanelProps {
  port: string;
  projectName: string;
  containerName: string;
}

export default function ChatPanel({ port, projectName, containerName }: IChatPanelProps) {
  const [messages, setMessages] = useState<{ role: "user" | "bot"; text: string }[]>([]);
  const [input, setInput] = useState("");
  const [iframeUrl, setIframeUrl] = useState("http://localhost:" + port);
  const [iframeKey, setIframeKey] = useState(0);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");
    setLoading(true);

    try {
      const res = await axiosInstance.post("/chat", {
        message: trimmed,
        poject_name: projectName, // Note: typo preserved intentionally
        container_name: containerName,
      });

      if (res.status === 200 && res.data?.message) {
        setMessages((prev) => [...prev, { role: "bot", text: res.data.message }]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "bot", text: "❌ Error: Invalid response from server" },
        ]);
      }
    } catch (err) {
      console.error("Error talking to server:", err);
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "❌ Error talking to server" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Scroll to latest message when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex h-screen w-full">
      {/* Left: Chat Panel */}
      <div className="w-1/3 bg-zinc-900 text-white flex flex-col border-r border-zinc-700 py-12">
        {/* Header */}
        <div className="p-4 border-b border-zinc-700">
          <h2 className="text-xl font-semibold">🤖 Chat Panel</h2>
        </div>

        {/* Scrollable Messages */}
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

        {/* Input Box */}
        <div className="p-4 border-t border-zinc-700">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type a message..."
            disabled={loading}
            className="w-full bg-zinc-800 text-white border border-zinc-600 rounded px-3 py-2 text-sm outline-none focus:ring focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Right: Iframe with URL and reload */}
      <div className="w-2/3 bg-zinc-800 flex flex-col">
        {/* URL Bar and Reload */}
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

        {/* Iframe */}
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
  );
}
