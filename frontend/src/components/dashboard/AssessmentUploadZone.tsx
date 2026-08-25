/**
 * FILE: src/components/dashboard/AssessmentUploadZone.tsx
 */

import React, { useCallback, useRef, useState } from 'react';
import { Upload, FileText, Loader2, CheckCircle2, AlertCircle, Cpu } from 'lucide-react';

interface AssessmentUploadZoneProps { onFileSelect?: (file: File) => void; }
type UploadState = 'idle' | 'dragging' | 'uploading' | 'success' | 'error';
const ACCEPTED_TYPES = ['.pdf', '.pptx', '.txt'];
const ACCEPTED_MIME = ['application/pdf', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'text/plain'];

const AssessmentUploadZone: React.FC<AssessmentUploadZoneProps> = ({ onFileSelect }) => {
  const [uploadState, setUploadState] = useState<UploadState>('idle');
  const [fileName, setFileName] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    if (!ACCEPTED_MIME.includes(file.type)) {
      setErrorMsg('Unsupported format. Please upload PDF, PPTX, or TXT.');
      setUploadState('error'); return;
    }
    setErrorMsg(null); setFileName(file.name); setUploadState('uploading');
    setTimeout(() => { setUploadState('success'); onFileSelect?.(file); }, 2000);
  }, [onFileSelect]);

  const onDrop = useCallback((e: React.DragEvent) => { e.preventDefault(); setUploadState('idle'); const f = e.dataTransfer.files[0]; if(f) handleFile(f); }, [handleFile]);
  const onDragOver = (e: React.DragEvent) => { e.preventDefault(); setUploadState('dragging'); };
  const onDragLeave = () => setUploadState('idle');
  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => { const f = e.target.files?.[0]; if(f) handleFile(f); };

  const zoneContent = () => {
    if (uploadState === 'uploading') return (
      <div className="flex flex-col items-center gap-2 py-2">
        <Loader2 size={32} className="text-blue-600 dark:text-blue-500 animate-spin" />
        <p className="text-sm font-semibold text-blue-700 dark:text-blue-400">AI Processing Document…</p>
        <p className="text-xs text-slate-500 dark:text-slate-400 text-center">Running <span className="font-mono text-slate-600 dark:text-slate-300">DocumentParserFactory</span> → LLM prompt → <span className="font-mono text-slate-600 dark:text-slate-300">AssessmentBuilder</span></p>
        {fileName && <span className="text-xs text-slate-400 italic truncate max-w-full px-2">{fileName}</span>}
      </div>
    );
    if (uploadState === 'success') return (
      <div className="flex flex-col items-center gap-2 py-2">
        <CheckCircle2 size={32} className="text-green-600 dark:text-green-500" />
        <p className="text-sm font-bold text-green-700 dark:text-green-400">Assessment Generated!</p>
        <p className="text-xs text-slate-500 dark:text-slate-400 text-center">Quiz has been saved and is now live for learners.</p>
        <button onClick={() => { setUploadState('idle'); setFileName(null); }} className="text-xs text-blue-600 dark:text-blue-400 hover:underline mt-1">Upload another document</button>
      </div>
    );
    if (uploadState === 'error') return (
      <div className="flex flex-col items-center gap-2 py-2">
        <AlertCircle size={32} className="text-red-500 dark:text-red-400" />
        <p className="text-sm font-semibold text-red-600 dark:text-red-400">{errorMsg}</p>
        <button onClick={() => { setUploadState('idle'); setErrorMsg(null); }} className="text-xs text-blue-600 dark:text-blue-400 hover:underline">Try again</button>
      </div>
    );
    return (
      <div className="flex flex-col items-center gap-3 py-2">
        <div className="w-14 h-14 rounded-full bg-blue-50 dark:bg-blue-900/30 border-2 border-dashed border-blue-300 dark:border-blue-700 flex items-center justify-center">
          <Upload size={24} className="text-blue-500 dark:text-blue-400" />
        </div>
        <div className="text-center">
          <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">Drop a training document here</p>
          <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">or <button onClick={() => inputRef.current?.click()} className="text-blue-600 dark:text-blue-400 hover:underline font-medium">click to browse</button></p>
        </div>
        <div className="flex gap-2 flex-wrap justify-center">
          {ACCEPTED_TYPES.map(ext => (
            <span key={ext} className="flex items-center gap-1 text-xs bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700 px-2 py-0.5 rounded-full font-mono"><FileText size={10} />{ext}</span>
          ))}
        </div>
      </div>
    );
  };

  const dropzoneClass = `rounded-xl border-2 border-dashed px-4 py-6 cursor-pointer flex flex-col items-center justify-center transition-all duration-200
    ${uploadState === 'dragging' ? 'border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20 scale-[1.01]' : ''}
    ${uploadState === 'success'  ? 'border-green-400 dark:border-green-500 bg-green-50 dark:bg-green-900/20' : ''}
    ${uploadState === 'error'    ? 'border-red-400 dark:border-red-500 bg-red-50 dark:bg-red-900/20' : ''}
    ${uploadState === 'uploading'? 'border-blue-400 dark:border-blue-500 bg-blue-50 dark:bg-blue-900/20' : ''}
    ${uploadState === 'idle'     ? 'border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50/40 dark:hover:bg-blue-900/30' : ''}`;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden transition-colors">
      <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800 bg-gradient-to-r from-slate-50 to-white dark:from-slate-900 dark:to-slate-900">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-900 dark:bg-blue-800 flex items-center justify-center">
            <Cpu size={15} className="text-white" />
          </div>
          <div>
            <h3 className="text-slate-900 dark:text-white font-bold text-sm">AI Assessment Generator</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500">RAG Document-to-Quiz Pipeline</p>
          </div>
        </div>
      </div>
      <div className="p-4">
        <div className={dropzoneClass} onDrop={onDrop} onDragOver={onDragOver} onDragLeave={onDragLeave} onClick={() => uploadState === 'idle' && inputRef.current?.click()}>
          {zoneContent()}
        </div>
        <input ref={inputRef} type="file" accept={ACCEPTED_TYPES.join(',')} className="hidden" onChange={onInputChange} />
        <p className="text-xs text-slate-400 dark:text-slate-500 text-center mt-3 leading-relaxed">
          Uploaded documents are processed by the MoSPI AI engine (LangChain + LLM).
        </p>
      </div>
    </div>
  );
};
export default AssessmentUploadZone;
