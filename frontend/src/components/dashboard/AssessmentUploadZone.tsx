/**
 * FILE: src/components/dashboard/AssessmentUploadZone.tsx
 */

import React, { useRef, useState } from "react";
import { Bot, Globe, Paperclip } from "lucide-react";

interface AssessmentUploadZoneProps {
  onFileSelect?: (file: File) => void;
}

const AssessmentUploadZone: React.FC<AssessmentUploadZoneProps> = ({ onFileSelect }) => {
  const [query, setQuery] = useState("");
  const [attached, setAttached] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) { setAttached(file.name); onFileSelect?.(file); }
  };

  const handleGenerate = () => {
    if (!query.trim() && !attached) { alert("Please enter a query or attach a document."); return; }
    console.info("[AI Generator] Query:", query, "| File:", attached);
    alert(`Assessment queued!\nQuery: "${query}"\nDoc: ${attached ?? "None"}`);
  };

  return (
    <div className="bg-white dark:bg-slate-800/40 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none p-6 flex flex-col gap-5 transition-colors duration-300">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="w-[44px] h-[44px] rounded-[14px] bg-[#1e2a4a] dark:bg-blue-900/40 flex items-center justify-center flex-shrink-0 transition-colors duration-300">
          <Bot size={22} className="text-white dark:text-blue-400 transition-colors duration-300" />
        </div>
        <div>
          <h3 className="text-slate-900 dark:text-white font-extrabold text-[15px] leading-tight tracking-tight mb-0.5 transition-colors duration-300">AI Assessment Generator</h3>
          <p className="text-slate-500 dark:text-slate-400 text-[12px] transition-colors duration-300">RAG Document-to-Quiz Pipeline</p>
        </div>
      </div>

      {/* Query Textarea */}
      <div>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Start assessment query..."
          className="w-full border border-slate-200 dark:border-slate-700/50 rounded-[16px] px-5 py-4 text-[13px] text-slate-700 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-400/30 dark:focus:ring-blue-500/30 focus:border-blue-300 dark:focus:border-blue-500/50 resize-none min-h-[95px] leading-relaxed transition-all shadow-sm dark:shadow-none mb-3"
          rows={3}
        />
        
        {/* Attach file */}
        <div className="px-1">
          <input ref={inputRef} type="file" className="hidden" accept=".pdf,.txt,.docx,.pptx" onChange={handleFileChange} />
          <button
            onClick={() => inputRef.current?.click()}
            className="flex items-center gap-2 text-[12px] text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 font-medium transition-colors"
          >
            <Paperclip size={14} />
            {attached
              ? <span className="text-blue-600 dark:text-blue-400 font-semibold truncate max-w-[200px]">{attached}</span>
              : "Attach document (.pdf, .pptx, .txt)"}
          </button>
        </div>
      </div>

      {/* Generate Button — glossy shiny effect adapted for dark mode */}
      <button
        onClick={handleGenerate}
        className="relative w-full bg-gradient-to-r from-[#93c5fd] via-[#ffffff] to-[#93c5fd] dark:from-[#1e3a8a] dark:via-[#3b82f6] dark:to-[#1e3a8a] text-[#1e40af] dark:text-white border border-[#bfdbfe] dark:border-blue-700 shadow-[0_4px_16px_-2px_rgba(59,130,246,0.3)] dark:shadow-[0_4px_16px_-2px_rgba(37,99,235,0.4)] font-bold text-[14px] py-3.5 rounded-[16px] flex items-center justify-center gap-2 transition-all duration-300 active:scale-[0.98]"
      >
        <div className="absolute inset-0 rounded-[16px] pointer-events-none shadow-[inset_0_1px_3px_rgba(255,255,255,1)] dark:shadow-[inset_0_1px_2px_rgba(255,255,255,0.2)]" />
        <Globe size={16} className="text-[#2563eb] dark:text-blue-200 relative z-10 transition-colors duration-300" />
        <span className="relative z-10">Generate Assessment</span>
      </button>
    </div>
  );
};

export default AssessmentUploadZone;