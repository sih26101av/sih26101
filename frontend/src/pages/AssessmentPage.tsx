import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Bot, CheckCircle, XCircle, ArrowRight, 
  ArrowLeft, FileText, Timer,
  Search, User, ChevronDown, X,
  LayoutDashboard, FilePlus, History, Settings, Video, Mic, File, Link as LinkIcon, Sun, Moon
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../hooks/useTheme";

const AssessmentPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';
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

  const [activeTab, setActiveTab] = useState('new_quiz');
  const [selectedFormat, setSelectedFormat] = useState('pdf');
  const [searchTerm, setSearchTerm] = useState('');
  
  const [historyData] = useState([
    { id: 1, date: 'Oct 26, 2023', title: 'Biology_Ch3_Lecture.mp4', type: 'Video', score: '90%', action: 'Review' },
    { id: 2, date: 'Oct 26, 2023', title: 'Cell Structure Formats.mp4', type: 'PDF', score: '75%', action: 'Retake' },
    { id: 3, date: 'Oct 26, 2023', title: 'Advanced Topics.pdf', type: 'PDF', score: '82%', action: 'Review' }
  ]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setErrorMsg("");
    }
  };

  const triggerFileInput = () => {
    if (inputRef.current) inputRef.current.click();
  };

  const handleGenerate = async () => {
    if (!file) { 
      setErrorMsg("Please upload a document to proceed."); 
      return; 
    }
    setErrorMsg("");
    setStatus("loading");
    setLoadingText("Extracting knowledge base...");

    setTimeout(() => { setLoadingText("Generating Q&A pairs..."); }, 2000);
    setTimeout(() => { setLoadingText("Finalizing assessment..."); }, 4000);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("user_id", userId);
      formData.append("difficulty", "Medium");
      
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
      setStatus("quiz");
      
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "An error occurred");
      setStatus("idle");
    }
  };

  const handleOptionSelect = (qIndex: number, optionIndex: number) => {
    const newAnswers = [...answers];
    newAnswers[qIndex] = optionIndex;
    setAnswers(newAnswers);
  };

  const handleSubmitQuiz = async () => {
    if (answers.includes(-1)) {
      setErrorMsg("Please answer all questions before submitting.");
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

  const uploadOptions = [
    { id: 'video', label: 'Upload Video', icon: <Video className="w-8 h-8 text-blue-600 mb-2" /> },
    { id: 'audio', label: 'Upload Audio', icon: <Mic className="w-8 h-8 text-blue-600 mb-2" /> },
    { id: 'pdf',   label: 'Upload PDF',   icon: <FileText className="w-8 h-8 text-blue-600 mb-2" /> },
    { id: 'word',  label: 'Upload Word Doc', icon: <File className="w-8 h-8 text-blue-600 mb-2" /> },
    { id: 'text',  label: 'Paste Text/URL', icon: <LinkIcon className="w-8 h-8 text-blue-600 mb-2" /> },
  ];

  const filteredHistory = historyData.filter(item => 
    item.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-screen bg-[#F2F0EF] dark:bg-slate-950 font-sans text-slate-800 dark:text-slate-200 overflow-hidden relative z-0">
      
      {/* Network Mesh Background */}
      <div
        className="absolute inset-0 z-[-1] pointer-events-none"
        style={{
          backgroundImage: 'url("/bg-mesh.png")',
          backgroundSize: "cover",
          backgroundPosition: "top right",
          backgroundRepeat: "no-repeat",
          opacity: 0.5,
        }}
      />

      {/* Sidebar */}
      <aside className="w-64 bg-[#F2F0EF] dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col shrink-0">
        <div className="h-16 flex items-center px-6 text-xl font-bold border-b border-slate-200 dark:border-slate-800">
          Assessment Studio
        </div>
        <nav className="flex-1 px-4 py-6 space-y-2">
          <button 
            onClick={() => navigate("/dashboard-redirect")}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg font-medium transition-colors ${activeTab === 'dashboard' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50'}`}
          >
            <LayoutDashboard className="w-5 h-5" /> Dashboard
          </button>
          <button 
            onClick={() => setActiveTab('new_quiz')}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg font-medium transition-colors ${activeTab === 'new_quiz' ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
          >
            <FilePlus className="w-5 h-5" /> New Quiz
          </button>
          <button 
            onClick={() => setActiveTab('history')}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg font-medium transition-colors ${activeTab === 'history' ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
          >
            <History className="w-5 h-5" /> History
          </button>
          <button 
            onClick={() => setActiveTab('settings')}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg font-medium transition-colors ${activeTab === 'settings' ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
          >
            <Settings className="w-5 h-5" /> Settings
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
        
        {/* Top Navbar */}
        <header className="h-16 bg-[#F2F0EF]/80 backdrop-blur-md dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 shrink-0 z-10">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate(-1)} className="p-2 -ml-2 rounded-full hover:bg-slate-200/50 dark:hover:bg-slate-800 transition-colors">
              <ArrowLeft className="w-5 h-5 text-slate-500" />
            </button>
            <h1 className="font-bold text-lg">Dashboard</h1>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="relative w-64 hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text" 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search history..." 
                className="w-full pl-9 pr-4 py-2 bg-[#F2F0EF] dark:bg-slate-800 border border-transparent dark:border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" 
              />
            </div>
            <button onClick={toggleTheme} className="p-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300">
               {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <div className="flex items-center gap-2 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-1.5 cursor-pointer hover:bg-slate-200/50 dark:hover:bg-slate-800">
              <div className="w-6 h-6 bg-slate-200 dark:bg-slate-700 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-slate-500 dark:text-slate-300" />
              </div>
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">User profile</span>
              <ChevronDown className="w-4 h-4 text-slate-400" />
            </div>
          </div>
        </header>

        {/* Scrollable Content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 relative">
          
          {status === "idle" && (
            <div className="max-w-6xl mx-auto space-y-6">
              
              {activeTab === 'new_quiz' && (
                <>
                  {/* Card 1: Generate New Assessment */}
                  <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-6">
                    <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-4">Generate New Assessment</h2>
                    
                    <input ref={inputRef} type="file" className="hidden" accept=".pdf,.txt,.docx,.pptx,.mp4,.mp3" onChange={handleFileChange} />
                    
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                      {uploadOptions.map((opt) => {
                        const isSelected = selectedFormat === opt.id;
                        return (
                          <div 
                            key={opt.id} 
                            onClick={() => { setSelectedFormat(opt.id); triggerFileInput(); }}
                            className={`border rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition-all text-center ${
                              isSelected 
                                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-sm' 
                                : 'border-slate-200 dark:border-slate-700 hover:border-blue-500 hover:shadow-md'
                            }`}
                          >
                            {opt.icon}
                            <span className={`text-sm font-medium ${isSelected ? 'text-blue-700 dark:text-blue-300' : 'text-slate-700 dark:text-slate-300'}`}>
                              {opt.label}
                            </span>
                          </div>
                        );
                      })}
                    </div>

                    {file && (
                      <div className="bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 px-4 py-3 rounded-lg mb-6 flex items-center justify-between border border-blue-100 dark:border-blue-800/50">
                        <div className="flex items-center gap-2">
                          <FileText className="w-5 h-5" />
                          <span className="font-medium">{file.name}</span>
                        </div>
                        <button onClick={() => setFile(null)} className="p-1 hover:bg-blue-100 dark:hover:bg-blue-800/50 rounded-md">
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    )}

                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                      <button 
                        onClick={handleGenerate}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors"
                      >
                        Generate Quiz
                      </button>
                      
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Difficulty Level (Easy/Medium/Hard)</span>
                        <div className="w-12 h-6 bg-blue-600 rounded-full relative cursor-pointer">
                          <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Card 2: Recent Assessment Results */}
                  <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 flex flex-col md:flex-row items-center gap-8">
                    {/* Circle Chart */}
                    <div className="relative w-32 h-32 shrink-0">
                      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="40" stroke="currentColor" strokeWidth="12" fill="none" className="text-slate-100 dark:text-slate-700" />
                        <circle cx="50" cy="50" r="40" stroke="#2563eb" strokeWidth="12" fill="none" strokeDasharray="251.2" strokeDashoffset={251.2 * (1 - 0.85)} strokeLinecap="round" />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-2xl font-black text-slate-800 dark:text-white">85%</span>
                        <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">(17/20)</span>
                      </div>
                    </div>
                    
                    {/* Details */}
                    <div className="flex-1 w-full grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-3">
                        <div className="flex items-start gap-2">
                          <span className="text-sm font-semibold text-slate-800 dark:text-slate-200 w-16">Source:</span>
                          <span className="text-sm text-slate-600 dark:text-slate-400">Biology_Ch3_Lecture.mp4</span>
                        </div>
                        <div className="flex items-start gap-2">
                          <span className="text-sm font-semibold text-slate-800 dark:text-slate-200 w-16">Date:</span>
                          <span className="text-sm text-slate-600 dark:text-slate-400">Oct 26, 2023</span>
                        </div>
                        <div className="flex items-start gap-2">
                          <span className="text-sm font-semibold text-slate-800 dark:text-slate-200 w-16">Topic:</span>
                          <span className="text-sm text-slate-600 dark:text-slate-400">Cell Structure</span>
                        </div>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="border-t border-slate-100 dark:border-slate-700 pt-4">
                          <p className="font-medium text-slate-800 dark:text-slate-200 mb-2">Simplistic multiple-choice format: is.</p>
                          <div className="flex items-center gap-4 text-slate-600 dark:text-slate-400">
                            <div className="flex items-center gap-1"><CheckCircle className="w-4 h-4 text-green-500"/> Correct</div>
                            <div className="flex items-center gap-1"><div className="w-4 h-4 rounded-full border border-slate-300" /> Incorrect</div>
                            <div className="flex items-center gap-1"><XCircle className="w-4 h-4 text-red-500"/> Incorrect</div>
                          </div>
                        </div>
                        <div className="border-t border-slate-100 dark:border-slate-700 pt-4">
                          <p className="font-medium text-slate-800 dark:text-slate-200 mb-2">Sample questions aligns the equations _______.</p>
                          <div className="flex items-center gap-4 text-slate-600 dark:text-slate-400">
                            <div className="flex items-center gap-1"><CheckCircle className="w-4 h-4 text-green-500"/> Correct</div>
                            <div className="flex items-center gap-1"><div className="w-4 h-4 rounded-full border border-slate-300" /> Incorrect</div>
                            <div className="flex items-center gap-1"><XCircle className="w-4 h-4 text-red-500"/> Incorrect</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {(activeTab === 'new_quiz' || activeTab === 'history') && (
                <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
                  <div className="p-5 border-b border-slate-200 dark:border-slate-700">
                    <h3 className="font-bold text-slate-800 dark:text-white">Assessment History</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="bg-[#F2F0EF] dark:bg-slate-800/50 text-slate-500 dark:text-slate-400">
                        <tr>
                          <th className="px-6 py-3 font-semibold">Date</th>
                          <th className="px-6 py-3 font-semibold">Quiz Title/Source</th>
                          <th className="px-6 py-3 font-semibold">Content Type</th>
                          <th className="px-6 py-3 font-semibold">Score</th>
                          <th className="px-6 py-3 font-semibold">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                        {filteredHistory.map(row => (
                          <tr key={row.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                            <td className="px-6 py-4 text-slate-700 dark:text-slate-300">{row.date}</td>
                            <td className="px-6 py-4 text-slate-700 dark:text-slate-300">{row.title}</td>
                            <td className="px-6 py-4 text-slate-700 dark:text-slate-300 flex items-center gap-2">
                              {row.type === 'Video' ? <Video className="w-4 h-4"/> : <FileText className="w-4 h-4"/>} {row.type}
                            </td>
                            <td className="px-6 py-4 font-semibold text-slate-800 dark:text-slate-200">{row.score}</td>
                            <td className="px-6 py-4">
                              <button className="px-4 py-1.5 border border-blue-600 text-blue-600 rounded-full hover:bg-blue-50 dark:hover:bg-blue-900/20 font-medium">
                                {row.action}
                              </button>
                            </td>
                          </tr>
                        ))}
                        {filteredHistory.length === 0 && (
                          <tr>
                            <td colSpan={5} className="px-6 py-8 text-center text-slate-500">No history found for "{searchTerm}"</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {activeTab === 'settings' && (
                <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-12 text-center">
                  <Settings className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">Settings</h2>
                  <p className="text-slate-500 dark:text-slate-400">Preferences and configuration options will appear here.</p>
                </div>
              )}
            </div>
          )}

          {/* LOADING & GRADING STATES */}
          {(status === "loading" || status === "grading") && (
            <div className="absolute inset-0 z-50 flex items-center justify-center bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
              <div className="flex flex-col items-center gap-6">
                <div className="relative w-16 h-16">
                  <div className="absolute inset-0 border-4 border-blue-200 dark:border-blue-900/50 rounded-full" />
                  <div className="absolute inset-0 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  <Bot className="absolute inset-0 m-auto w-6 h-6 text-blue-600" />
                </div>
                <div className="text-center">
                  <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-1">AI Agent Working</h3>
                  <p className="text-sm font-medium text-blue-600 animate-pulse">{loadingText}</p>
                </div>
              </div>
            </div>
          )}

          {/* QUIZ VIEW */}
          {status === "quiz" && quizData && (
            <div className="max-w-4xl mx-auto pb-20">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-2xl font-black text-slate-800 dark:text-white mb-2">Assessment Ready</h2>
                  <p className="text-slate-500 dark:text-slate-400 font-medium">{quizData.questions.length} questions • Medium Difficulty</p>
                </div>
                <div className="flex items-center gap-2 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 px-4 py-2 rounded-lg font-bold">
                  <Timer size={18} />
                  <span>20:00</span>
                </div>
              </div>

              <div className="space-y-6">
                {quizData.questions.map((q: any, i: number) => (
                  <div key={i} className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 md:p-8 shadow-sm">
                    <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100 mb-6">
                      <span className="text-slate-400 dark:text-slate-500 mr-3">{i + 1}.</span>
                      {q.question}
                    </h3>
                    <div className="space-y-3">
                      {q.options.map((opt: string, optIdx: number) => {
                        const isSelected = answers[i] === optIdx;
                        return (
                          <label 
                            key={optIdx} 
                            className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all ${isSelected ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20' : 'border-slate-100 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'}`}
                          >
                            <input
                              type="radio"
                              name={`q-${i}`}
                              className="hidden"
                              checked={isSelected}
                              onChange={() => handleOptionSelect(i, optIdx)}
                            />
                            <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ${isSelected ? 'border-blue-600' : 'border-slate-300 dark:border-slate-600'}`}>
                              {isSelected && <div className="w-2.5 h-2.5 bg-blue-600 rounded-full" />}
                            </div>
                            <span className={`font-medium ${isSelected ? 'text-blue-900 dark:text-blue-100' : 'text-slate-700 dark:text-slate-300'}`}>{opt}</span>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>

              <div className="fixed bottom-0 left-0 right-0 p-4 md:p-6 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-t border-slate-200 dark:border-slate-800 flex justify-center z-10">
                <button
                  onClick={handleSubmitQuiz}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-12 py-3 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all hover:scale-105"
                >
                  Submit Assessment <ArrowRight size={20} />
                </button>
              </div>
            </div>
          )}

          {/* RESULT VIEW */}
          {status === "result" && scoreInfo && (
            <div className="max-w-2xl mx-auto">
              <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-[2rem] p-8 md:p-12 shadow-xl text-center">
                <div className="w-24 h-24 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle className="w-12 h-12 text-green-500" />
                </div>
                
                <h2 className="text-3xl font-black text-slate-800 dark:text-white mb-2">Assessment Complete!</h2>
                <p className="text-slate-500 dark:text-slate-400 font-medium mb-8">You've successfully completed the module.</p>
                
                <div className="grid grid-cols-2 gap-4 mb-8">
                  <div className="bg-slate-50 dark:bg-slate-900/50 rounded-2xl p-6 border border-slate-100 dark:border-slate-700">
                    <p className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-1">Score</p>
                    <p className="text-4xl font-black text-slate-800 dark:text-white">{Math.round((scoreInfo.score / scoreInfo.total) * 100)}%</p>
                  </div>
                  <div className="bg-slate-50 dark:bg-slate-900/50 rounded-2xl p-6 border border-slate-100 dark:border-slate-700">
                    <p className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-1">Correct</p>
                    <p className="text-4xl font-black text-slate-800 dark:text-white">{scoreInfo.score}<span className="text-xl text-slate-400">/{scoreInfo.total}</span></p>
                  </div>
                </div>

                <button
                  onClick={reset}
                  className="w-full bg-slate-900 dark:bg-slate-100 hover:bg-slate-800 dark:hover:bg-white text-white dark:text-slate-900 py-4 rounded-xl font-bold transition-all"
                >
                  Return to Dashboard
                </button>
              </div>
            </div>
          )}
          
        </main>
      </div>
    </div>
  );
};

export default AssessmentPage;
