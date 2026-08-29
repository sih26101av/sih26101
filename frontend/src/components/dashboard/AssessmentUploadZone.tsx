import React, { useRef, useState } from "react";
import { Bot, Globe, Paperclip, Loader2, CheckCircle, XCircle, ArrowRight } from "lucide-react";

interface AssessmentUploadZoneProps {
  userId?: string;
  onQuizPassed?: () => void;
  onViewProgress?: () => void;
}

const AssessmentUploadZone: React.FC<AssessmentUploadZoneProps> = ({ userId = 'usr_720465595', onQuizPassed, onViewProgress }) => {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "quiz" | "grading" | "result">("idle");
  const [loadingText, setLoadingText] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  
  const [quizData, setQuizData] = useState<any>(null);
  const [answers, setAnswers] = useState<number[]>([]);
  const [scoreInfo, setScoreInfo] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setErrorMsg("");
    }
  };

  const handleGenerate = async () => {
    if (!file) { 
      setErrorMsg("Please attach a document."); 
      return; 
    }
    setErrorMsg("");
    setStatus("loading");
    setLoadingText("Parsing document...");

    try {
      const formData = new FormData();
      formData.append("file", file);

      setTimeout(() => setLoadingText("Gemini generating questions..."), 1500);

      const res = await fetch("http://localhost:8000/api/v1/rag/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Failed to generate quiz");
      }

      const data = await res.json();
      setQuizData(data);
      setAnswers(new Array(data.questions.length).fill(-1));
      setStatus("quiz");
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "An error occurred");
      setStatus("idle");
    }
  };

  const handleAnswer = (qIndex: number, optIndex: number) => {
    const newAnswers = [...answers];
    newAnswers[qIndex] = optIndex;
    setAnswers(newAnswers);
  };

  const submitQuiz = async () => {
    if (answers.includes(-1)) {
      setErrorMsg("Please answer all questions.");
      return;
    }
    setErrorMsg("");
    setStatus("grading");

    try {
      const res = await fetch("http://localhost:8000/api/v1/rag/grade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          quiz_id: quizData.quiz_id,
          answers: answers
        })
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Failed to grade quiz");
      }

      const data = await res.json();
      setScoreInfo(data);
      setStatus("result");
      
      if (data.passed && onQuizPassed) {
        onQuizPassed(); // Triggers refetch in background
      }
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "An error occurred during grading");
      setStatus("quiz");
    }
  };

  const reset = () => {
    setFile(null);
    setQuizData(null);
    setAnswers([]);
    setScoreInfo(null);
    setStatus("idle");
    setErrorMsg("");
    if (inputRef.current) inputRef.current.value = "";
  };

  if (status === "loading" || status === "grading") {
    return (
      <div className="bg-white dark:bg-slate-800/40 rounded-3xl border border-slate-100 dark:border-slate-700/50 p-6 flex flex-col items-center justify-center min-h-[250px] gap-4">
        <Loader2 className="animate-spin text-blue-500" size={40} />
        <p className="text-slate-600 dark:text-slate-300 font-medium">
          {status === "loading" ? loadingText : "Evaluating answers..."}
        </p>
      </div>
    );
  }

  if (status === "result" && scoreInfo) {
    const { passed, score, correct_count, total_questions, message } = scoreInfo;
    return (
      <div className="bg-white dark:bg-slate-800/40 rounded-3xl border border-slate-100 dark:border-slate-700/50 p-6 flex flex-col items-center justify-center min-h-[250px] gap-4 text-center">
        {passed ? (
          <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/40 flex items-center justify-center mb-2">
            <CheckCircle className="text-emerald-500" size={32} />
          </div>
        ) : (
          <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/40 flex items-center justify-center mb-2">
            <XCircle className="text-red-500" size={32} />
          </div>
        )}
        <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">
          {passed ? "Assessment Passed!" : "Assessment Failed"}
        </h3>
        <p className="text-slate-600 dark:text-slate-300 font-medium">
          You scored {score}% ({correct_count} / {total_questions})
        </p>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">{message}</p>
        
        <div className="flex gap-3 mt-4">
          <button onClick={reset} className="px-5 py-2 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl font-semibold hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">
            {passed ? "Done" : "Try Again"}
          </button>
          {passed && onViewProgress && (
            <button onClick={onViewProgress} className="px-5 py-2 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-colors">
              View Progress
            </button>
          )}
        </div>
      </div>
    );
  }

  if (status === "quiz" && quizData) {
    return (
      <div className="bg-white dark:bg-slate-800/40 rounded-3xl border border-slate-100 dark:border-slate-700/50 p-6 max-h-[600px] overflow-y-auto custom-scrollbar">
        <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100 mb-4 flex items-center gap-2">
          <Bot size={20} className="text-blue-500" /> Generated Quiz
        </h3>
        {errorMsg && <p className="text-red-500 text-sm mb-4">{errorMsg}</p>}
        <div className="space-y-6">
          {quizData.questions.map((q: any, qIndex: number) => (
            <div key={qIndex} className="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-4 border border-slate-100 dark:border-slate-700">
              <p className="font-semibold text-slate-800 dark:text-slate-200 mb-3">{qIndex + 1}. {q.question}</p>
              <div className="space-y-2">
                {q.options.map((opt: string, optIndex: number) => (
                  <label key={optIndex} className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 dark:border-slate-600 cursor-pointer hover:bg-blue-50 dark:hover:bg-slate-700 transition-colors">
                    <input 
                      type="radio" 
                      name={`question-${qIndex}`} 
                      className="w-4 h-4 text-blue-600"
                      checked={answers[qIndex] === optIndex}
                      onChange={() => handleAnswer(qIndex, optIndex)}
                    />
                    <span className="text-sm text-slate-700 dark:text-slate-300">{opt}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-6 flex justify-end gap-3">
          <button onClick={reset} className="px-5 py-2.5 rounded-xl font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600 transition-colors">
            Cancel
          </button>
          <button onClick={submitQuiz} className="px-5 py-2.5 rounded-xl font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors flex items-center gap-2">
            Submit Quiz <ArrowRight size={16} />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-slate-800/40 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none p-6 flex flex-col gap-5 transition-colors duration-300">
      <div className="flex items-center gap-4">
        <div className="w-[44px] h-[44px] rounded-[14px] bg-[#1e2a4a] dark:bg-blue-900/40 flex items-center justify-center flex-shrink-0 transition-colors duration-300">
          <Bot size={22} className="text-white dark:text-blue-400 transition-colors duration-300" />
        </div>
        <div>
          <h3 className="text-slate-900 dark:text-white font-extrabold text-[15px] leading-tight tracking-tight mb-0.5 transition-colors duration-300">AI Assessment Generator</h3>
          <p className="text-slate-500 dark:text-slate-400 text-[12px] transition-colors duration-300">RAG Document-to-Quiz Pipeline</p>
        </div>
      </div>

      <div>
        <div className="px-1 mb-3">
          <input ref={inputRef} type="file" className="hidden" accept=".pdf,.txt,.docx,.pptx" onChange={handleFileChange} />
          <div 
            onClick={() => inputRef.current?.click()}
            className="w-full border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-2xl p-6 flex flex-col items-center justify-center cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors text-center min-h-[120px]"
          >
            <Paperclip size={24} className="text-slate-400 dark:text-slate-500 mb-2" />
            {file ? (
              <span className="text-blue-600 dark:text-blue-400 font-semibold">{file.name}</span>
            ) : (
              <span className="text-slate-500 dark:text-slate-400 text-sm font-medium">Click to upload training document (.pdf, .pptx, .txt)</span>
            )}
          </div>
        </div>
        
        {errorMsg && <p className="text-red-500 text-sm px-1 mb-2 font-medium">{errorMsg}</p>}
      </div>

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