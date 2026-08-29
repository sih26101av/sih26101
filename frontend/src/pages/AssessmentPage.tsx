import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Bot, CheckCircle, XCircle, ArrowRight, 
  ArrowLeft, FileText, BrainCircuit, Sparkles, UploadCloud, Timer
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

const AssessmentPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const userId = user?.username ?? 'usr_720465595';

  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "quiz" | "grading" | "result">("idle");
  const [loadingText, setLoadingText] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  
  const [quizData, setQuizData] = useState<any>(null);
  const [answers, setAnswers] = useState<number[]>([]);
  const [scoreInfo, setScoreInfo] = useState<any>(null);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setErrorMsg("");
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) {
      setFile(f);
      setErrorMsg("");
    }
  };

  const handleGenerate = async () => {
    if (!file) { 
      setErrorMsg("Please upload a document to proceed."); 
      return; 
    }
    setErrorMsg("");
    setStatus("loading");
    setLoadingText("Extracting knowledge base...");

    try {
      const formData = new FormData();
      formData.append("file", file);

      setTimeout(() => setLoadingText("Synthesizing questions via AI..."), 2000);

      const res = await fetch("http://localhost:8000/api/v1/rag/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Failed to generate assessment");
      }

      const data = await res.json();
      setQuizData(data);
      setAnswers(new Array(data.questions.length).fill(-1));
      setCurrentQuestionIdx(0);
      setStatus("quiz");
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "An error occurred during AI processing.");
      setStatus("idle");
    }
  };

  const handleAnswer = (optIndex: number) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestionIdx] = optIndex;
    setAnswers(newAnswers);
  };

  const nextQuestion = () => {
    if (currentQuestionIdx < quizData.questions.length - 1) {
      setCurrentQuestionIdx(currentQuestionIdx + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestionIdx > 0) {
      setCurrentQuestionIdx(currentQuestionIdx - 1);
    }
  };

  const submitQuiz = async () => {
    if (answers.includes(-1)) {
      setErrorMsg("Please answer all questions before submitting.");
      return;
    }
    setErrorMsg("");
    setStatus("grading");
    setLoadingText("Evaluating responses...");

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
        throw new Error(error.detail || "Failed to grade assessment");
      }

      const data = await res.json();
      setScoreInfo(data);
      setStatus("result");
      
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

  return (
    <div className="min-h-screen bg-[#f8fafc] dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300 relative overflow-hidden flex flex-col">
      <div 
        className="absolute inset-0 z-0 pointer-events-none opacity-50 dark:opacity-30"
        style={{ backgroundImage: 'url("/bg-mesh.png")', backgroundSize: "cover", backgroundPosition: "top right" }}
      />
      
      <nav className="relative z-10 w-full bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border-b border-slate-200/50 dark:border-slate-800/50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate(-1)}
            className="p-2 rounded-full hover:bg-slate-200/50 dark:hover:bg-slate-800/50 transition-colors"
          >
            <ArrowLeft size={20} className="text-slate-600 dark:text-slate-300" />
          </button>
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-1.5 rounded-lg">
              <BrainCircuit size={20} className="text-white" />
            </div>
            <h1 className="font-extrabold text-lg tracking-tight">AI Assessment Studio</h1>
          </div>
        </div>
      </nav>

      <main className="relative z-10 flex-1 flex flex-col items-center justify-center p-6 md:p-12 w-full max-w-5xl mx-auto">
        
        {status === "idle" && (
          <div className="w-full max-w-2xl bg-white/60 dark:bg-slate-900/60 backdrop-blur-2xl rounded-[2rem] border border-white/50 dark:border-slate-700/50 shadow-2xl p-8 md:p-12 animate-in fade-in zoom-in-95 duration-500">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-black mb-3 bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
                Generate Custom Quiz
              </h2>
              <p className="text-slate-500 dark:text-slate-400 font-medium">
                Upload any training manual, policy document, or SOP. Our AI will instantly synthesize a targeted assessment to test your competency.
              </p>
            </div>

            <div 
              className={`w-full border-2 border-dashed rounded-[1.5rem] p-10 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 ${
                file 
                  ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/20' 
                  : 'border-slate-300 dark:border-slate-600 hover:border-blue-400 hover:bg-slate-50 dark:hover:bg-slate-800/50'
              }`}
              onClick={() => inputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
            >
              <input ref={inputRef} type="file" className="hidden" accept=".pdf,.txt,.docx,.pptx" onChange={handleFileChange} />
              
              {file ? (
                <div className="flex flex-col items-center gap-3 animate-in fade-in zoom-in">
                  <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center">
                    <FileText size={32} className="text-blue-600 dark:text-blue-400" />
                  </div>
                  <span className="text-lg font-bold text-blue-900 dark:text-blue-100">{file?.name}</span>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-4 text-center">
                  <div className="w-20 h-20 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center shadow-inner">
                    <UploadCloud size={40} className="text-slate-400 dark:text-slate-500" />
                  </div>
                  <div>
                    <p className="text-lg font-bold text-slate-700 dark:text-slate-200">Drag & drop your document</p>
                    <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mt-1">or click to browse (.pdf, .pptx, .txt)</p>
                  </div>
                </div>
              )}
            </div>

            {errorMsg && (
              <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-600 dark:text-red-400 text-sm font-semibold flex items-center gap-2">
                <XCircle size={18} /> {errorMsg}
              </div>
            )}

            <button
              onClick={handleGenerate}
              className="mt-8 w-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg py-4 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-3 active:scale-[0.98]"
            >
              <Sparkles size={22} /> Generate Assessment Now
            </button>
          </div>
        )}

        {(status === "loading" || status === "grading") && (
          <div className="flex flex-col items-center justify-center space-y-6 animate-in fade-in duration-500">
            <div className="relative">
              <div className="w-24 h-24 border-4 border-blue-200 dark:border-blue-900 rounded-full animate-pulse" />
              <div className="w-24 h-24 border-4 border-blue-600 dark:border-blue-500 rounded-full animate-spin absolute inset-0 border-t-transparent dark:border-t-transparent" />
              <Bot size={32} className="absolute inset-0 m-auto text-blue-600 dark:text-blue-400" />
            </div>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-slate-500 dark:from-white dark:to-slate-400 bg-clip-text text-transparent">
              {loadingText}
            </h2>
          </div>
        )}

        {status === "quiz" && quizData && (
          <div className="w-full max-w-4xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-2xl rounded-[2rem] border border-white/50 dark:border-slate-700/50 shadow-2xl p-6 md:p-10 animate-in slide-in-from-bottom-8 duration-500">
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-slate-200 dark:border-slate-700/50">
              <div className="flex items-center gap-3">
                <div className="bg-blue-100 dark:bg-blue-900/50 p-2 rounded-lg">
                  <FileText size={24} className="text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h2 className="font-bold text-xl">{file?.name}</h2>
                  <p className="text-sm font-medium text-slate-500 dark:text-slate-400">AI Generated Assessment</p>
                </div>
              </div>
              <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-4 py-2 rounded-full font-bold text-slate-700 dark:text-slate-300">
                <Timer size={18} className="text-blue-500" />
                <span>Question {currentQuestionIdx + 1} of {quizData.questions.length}</span>
              </div>
            </div>

            {errorMsg && (
              <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-600 dark:text-red-400 text-sm font-semibold flex items-center gap-2">
                <XCircle size={18} /> {errorMsg}
              </div>
            )}

            <div className="mb-10 min-h-[300px]">
              <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-8 leading-tight">
                {quizData.questions[currentQuestionIdx].question}
              </h3>
              
              <div className="space-y-4">
                {quizData.questions[currentQuestionIdx].options.map((opt: string, optIndex: number) => {
                  const isSelected = answers[currentQuestionIdx] === optIndex;
                  return (
                    <div 
                      key={optIndex}
                      onClick={() => handleAnswer(optIndex)}
                      className={`p-5 rounded-2xl border-2 cursor-pointer transition-all duration-200 flex items-center gap-4 ${
                        isSelected 
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md' 
                          : 'border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-700 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                      }`}
                    >
                      <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
                        isSelected ? 'border-blue-500' : 'border-slate-300 dark:border-slate-600'
                      }`}>
                        {isSelected && <div className="w-3 h-3 bg-blue-500 rounded-full" />}
                      </div>
                      <span className={`text-lg font-medium ${isSelected ? 'text-blue-900 dark:text-blue-100' : 'text-slate-700 dark:text-slate-300'}`}>
                        {opt}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="flex items-center justify-between pt-6 border-t border-slate-200 dark:border-slate-700/50">
              <button 
                onClick={prevQuestion}
                disabled={currentQuestionIdx === 0}
                className="px-6 py-3 font-semibold text-slate-600 dark:text-slate-400 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
              >
                Previous
              </button>
              
              <div className="flex gap-2">
                {quizData.questions.map((_: any, idx: number) => (
                  <div 
                    key={idx}
                    className={`w-2.5 h-2.5 rounded-full transition-colors ${
                      idx === currentQuestionIdx ? 'bg-blue-600' : 
                      answers[idx] !== -1 ? 'bg-blue-300 dark:bg-blue-800' : 'bg-slate-200 dark:bg-slate-700'
                    }`}
                  />
                ))}
              </div>

              {currentQuestionIdx === quizData.questions.length - 1 ? (
                <button 
                  onClick={submitQuiz}
                  className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg transition-all flex items-center gap-2"
                >
                  Submit Assessment <CheckCircle size={20} />
                </button>
              ) : (
                <button 
                  onClick={nextQuestion}
                  className="px-8 py-3 bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100 font-bold rounded-xl shadow-lg transition-all flex items-center gap-2"
                >
                  Next <ArrowRight size={20} />
                </button>
              )}
            </div>
          </div>
        )}

        {status === "result" && scoreInfo && (
          <div className="w-full max-w-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-2xl rounded-[2rem] border border-white/50 dark:border-slate-700/50 shadow-2xl p-10 text-center animate-in zoom-in-95 duration-500">
            <div className="relative inline-flex items-center justify-center mb-8">
              <div className={`absolute inset-0 rounded-full blur-2xl opacity-50 ${scoreInfo.passed ? 'bg-emerald-400' : 'bg-red-400'}`} />
              <div className={`relative w-28 h-28 rounded-full flex items-center justify-center border-4 shadow-xl ${
                scoreInfo.passed ? 'bg-emerald-100 border-emerald-500 dark:bg-emerald-900/50' : 'bg-red-100 border-red-500 dark:bg-red-900/50'
              }`}>
                {scoreInfo.passed ? <CheckCircle size={56} className="text-emerald-500" /> : <XCircle size={56} className="text-red-500" />}
              </div>
            </div>
            
            <h2 className="text-4xl font-black mb-4">
              {scoreInfo.passed ? "Assessment Passed!" : "Assessment Failed"}
            </h2>
            
            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-6 mb-8 inline-block min-w-[300px]">
              <div className="text-6xl font-black mb-2 bg-gradient-to-br from-slate-800 to-slate-500 dark:from-white dark:to-slate-400 bg-clip-text text-transparent">
                {scoreInfo.score}%
              </div>
              <p className="text-lg font-medium text-slate-500 dark:text-slate-400">
                You answered {scoreInfo.correct_count} out of {scoreInfo.total_questions} correctly.
              </p>
            </div>
            
            <p className="text-lg font-medium text-slate-600 dark:text-slate-300 mb-10 max-w-lg mx-auto leading-relaxed">
              {scoreInfo.message}
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button 
                onClick={reset}
                className="w-full sm:w-auto px-8 py-4 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-bold rounded-xl hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              >
                Start New Assessment
              </button>
              <button 
                onClick={() => navigate(-1)}
                className="w-full sm:w-auto px-8 py-4 bg-blue-600 text-white font-bold rounded-xl shadow-lg hover:bg-blue-700 transition-all flex items-center justify-center gap-2"
              >
                Return to Dashboard <ArrowRight size={20} />
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AssessmentPage;
