"use client";

import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Terminal, Globe, Search, ShoppingBag, Lightbulb, Play } from "lucide-react";

interface LogEntry {
  text: string;
  time: string;
}

interface Competitor {
  id: number;
  name: string;
  url: string;
  extracted_pricing_info: string;
}

interface Recommendation {
  id: number;
  strategy: string;
  actionable_steps: string;
}

interface TaskResult {
  task: any;
  competitors: Competitor[];
  recommendations: Recommendation;
}

export default function Home() {
  const [url, setUrl] = useState("");
  const [taskId, setTaskId] = useState<number | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<TaskResult | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll logs
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setLogs([]);
    setResult(null);
    setIsProcessing(true);

    try {
      // 1. Create task
      const res = await axios.post("http://localhost:8000/tasks", { url });
      const newTaskId = res.data.id;
      setTaskId(newTaskId);

      // 2. Connect to SSE
      const eventSource = new EventSource(`http://localhost:8000/stream_task/${newTaskId}`);
      
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.log) {
          setLogs((prev) => [...prev, { text: data.log, time: new Date().toLocaleTimeString() }]);
        }
        
        if (data.status === "completed" || data.status === "failed") {
          eventSource.close();
          setIsProcessing(false);
          if (data.status === "completed") {
            fetchFinalResult(newTaskId);
          }
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setIsProcessing(false);
        setLogs((prev) => [...prev, { text: "Connection error.", time: new Date().toLocaleTimeString() }]);
      };

    } catch (error) {
      console.error(error);
      setIsProcessing(false);
      alert("Failed to start research.");
    }
  };

  const fetchFinalResult = async (id: number) => {
    try {
      const res = await axios.get(`http://localhost:8000/tasks/${id}`);
      setResult(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        
        <header className="text-center space-y-4">
          <div className="inline-flex items-center justify-center p-3 bg-blue-600 rounded-full mb-2">
            <Globe className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">
            Autonomous E-Commerce AI Researcher
          </h1>
          <p className="text-lg text-slate-500 max-w-2xl mx-auto">
            Give us your store URL. Our AI will analyze your niche, hunt down your competitors, bypass their bot protection, scrape their prices, and formulate a winning strategy for you.
          </p>
        </header>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex space-x-4">
            <input
              type="url"
              placeholder="https://your-store.com"
              className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
              disabled={isProcessing}
            />
            <button
              type="submit"
              disabled={isProcessing}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-8 py-3 rounded-xl font-semibold flex items-center space-x-2 transition-colors"
            >
              {isProcessing ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Researching...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 fill-current" />
                  <span>Start AI Agent</span>
                </>
              )}
            </button>
          </div>
        </form>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Terminal / Live Logs */}
          <div className="bg-slate-900 rounded-2xl shadow-xl overflow-hidden flex flex-col h-[600px]">
            <div className="bg-slate-800 px-4 py-3 flex items-center space-x-2 border-b border-slate-700">
              <Terminal className="w-4 h-4 text-slate-400" />
              <span className="text-sm font-medium text-slate-300">Agent Thoughts Terminal</span>
              <div className="flex-1" />
              {isProcessing && <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />}
            </div>
            <div className="p-4 flex-1 overflow-y-auto font-mono text-sm space-y-3">
              {logs.length === 0 ? (
                <p className="text-slate-600 italic">Awaiting instructions...</p>
              ) : (
                logs.map((log, i) => (
                  <div key={i} className="flex space-x-3">
                    <span className="text-slate-500 shrink-0">[{log.time}]</span>
                    <span className="text-green-400">{log.text}</span>
                  </div>
                ))
              )}
              <div ref={logsEndRef} />
            </div>
          </div>

          {/* Results Area */}
          <div className="h-[600px] overflow-y-auto space-y-6">
            {!result ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-2xl">
                <Search className="w-12 h-12 mb-4 opacity-50" />
                <p>Final report will appear here once research completes.</p>
              </div>
            ) : (
              <>
                {/* Competitors List */}
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                  <div className="flex items-center space-x-2 mb-6">
                    <ShoppingBag className="w-6 h-6 text-blue-600" />
                    <h2 className="text-xl font-bold">Identified Competitors</h2>
                  </div>
                  <div className="space-y-4">
                    {result.competitors.length === 0 ? (
                      <p className="text-slate-500 italic">No competitors found.</p>
                    ) : (
                      result.competitors.map((comp) => (
                        <div key={comp.id} className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                          <a href={comp.url} target="_blank" rel="noreferrer" className="text-lg font-bold text-blue-600 hover:underline">
                            {comp.name}
                          </a>
                          <p className="text-sm text-slate-600 mt-2">{comp.extracted_pricing_info}</p>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* AI Recommendation */}
                {result.recommendations && (
                  <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-6 rounded-2xl shadow-lg text-white">
                    <div className="flex items-center space-x-2 mb-6">
                      <Lightbulb className="w-6 h-6 text-yellow-300" />
                      <h2 className="text-xl font-bold">AI Strategy & Actions</h2>
                    </div>
                    <div className="space-y-4">
                      <div className="bg-white/10 p-4 rounded-xl backdrop-blur-sm">
                        <p className="whitespace-pre-wrap">{result.recommendations.actionable_steps}</p>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
