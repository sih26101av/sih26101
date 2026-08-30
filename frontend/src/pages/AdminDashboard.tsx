import React, { useState, useMemo, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, LineChart, Line 
} from 'recharts';
import { useNavigate } from 'react-router-dom';
import { 
  Bell, ChevronDown, CheckCircle, Flame, TrendingUp, Search, Filter, SlidersHorizontal, 
  User, AlertTriangle, Sun, Moon, RefreshCcw, Home, LogOut, KeyRound,
  LayoutDashboard, Users, BookOpen, FileText, Settings, ChevronLeft, ChevronRight
} from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import { useAuth } from '../context/AuthContext';
import { useAdminData } from '../hooks/useAdminData';
import type { AdminRosterRow } from '../hooks/useAdminData';
import { useSkillsData } from '../hooks/useSkillsData';
import type { SkillRow } from '../hooks/useSkillsData';

// ─── Static constants ─────────────────────────────────────────────────────────
const SPARKLINE_DATA = [
  { value: 110 }, { value: 112 }, { value: 108 }, { value: 116 }, { value: 115 }, { value: 120 }, { value: 124 }
];
const PIE_DATA = [
  { name: 'Core Skills',     value: 32, color: '#60a5fa' },
  { name: 'Advanced Skills', value: 68, color: '#94a3b8'  }
];
const ITEMS_PER_PAGE = 10;

// ─── Status helpers ───────────────────────────────────────────────────────────
function enrollmentLabel(status: number | undefined): string {
  if (status === 2) return 'Compliant';
  if (status === 1) return 'In Progress';
  return 'Training Required';
}

// ─── Subcomponents ────────────────────────────────────────────────────────────
const SkeletonCard = () => (
  <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700 animate-pulse">
    <div className="flex items-center gap-4">
      <div className="w-12 h-12 rounded-xl bg-slate-200 dark:bg-slate-700" />
      <div className="flex-1 space-y-2">
        <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/2" />
        <div className="h-7 bg-slate-200 dark:bg-slate-700 rounded w-1/3" />
      </div>
    </div>
  </div>
);

const ErrorBanner: React.FC<{ message: string; onRetry: () => void }> = ({ message, onRetry }) => (
  <div className="flex items-center gap-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700/50 rounded-2xl p-5 text-sm">
    <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
    <div className="flex-1">
      <p className="font-semibold text-red-700 dark:text-red-400">Failed to load data</p>
      <p className="text-red-600 dark:text-red-500 text-xs mt-0.5">{message}</p>
    </div>
    <button
      onClick={onRetry}
      className="flex items-center gap-1.5 px-4 py-2 bg-red-100 dark:bg-red-800/50 text-red-700 dark:text-red-300 rounded-lg font-medium text-xs hover:bg-red-200 dark:hover:bg-red-700/50 transition-colors"
    >
      <RefreshCcw className="w-3.5 h-3.5" /> Retry
    </button>
  </div>
);

// ─── Roster Row ───────────────────────────────────────────────────────────────
const RosterRow: React.FC<{ employee: AdminRosterRow }> = ({ employee }) => {
  const label  = enrollmentLabel(employee.enrollmentStatus);
  const isGood = label === 'Compliant';
  const isWarn = label === 'In Progress';
  return (
    <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30 transition-colors">
      <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-slate-800 dark:text-slate-200">
        {employee.firstName} {employee.lastName}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400">
        {employee.govId ?? employee.userId}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400">
        {employee.designation}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-800 dark:text-slate-200 font-medium">
        {employee.missingSkill ?? '—'}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm">
        <span className={`inline-flex items-center px-3 py-1 rounded-md text-xs font-semibold ${
          isGood
            ? 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400'
            : isWarn
            ? 'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
            : 'bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400'
        }`}>
          {label}
        </span>
      </td>
    </tr>
  );
};

// ─── Skill Row ───────────────────────────────────────────────────────────────
const SkillTableRow: React.FC<{ skill: SkillRow }> = ({ skill }) => {
  return (
    <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30 transition-colors">
      <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-slate-800 dark:text-slate-200">
        {skill.competency_id}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800 dark:text-slate-200">
        {skill.name}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm">
        <span className="inline-flex items-center px-3 py-1 rounded-md text-xs font-semibold bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
          {skill.category}
        </span>
      </td>
      <td className="px-6 py-4 text-sm text-slate-500 dark:text-slate-400 max-w-xs truncate">
        {skill.description}
      </td>
    </tr>
  );
};

// ─── Main Component ───────────────────────────────────────────────────────────
const AdminDashboard: React.FC = () => {
  const { theme, toggleTheme }                = useTheme();
  const navigate                              = useNavigate();
  const { logout }                            = useAuth();
  
  // Data Hooks
  const { roster, kpis, heatmap, isLoading, error, refetch } = useAdminData();
  const { skills, isLoading: isSkillsLoading, error: skillsError, refetch: refetchSkills } = useSkillsData();
  
  // State for Navigation and Search/Pagination
  const [activeTab, setActiveTab]             = useState<'dashboard' | 'officials' | 'skills'>('dashboard');
  const [searchTerm, setSearchTerm]           = useState('');
  const [currentPage, setCurrentPage]         = useState(1);

  const handleSignOut = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  // Reset to first page when search term or active tab changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, activeTab]);

  // ─── Roster Logic ───
  const filteredRoster = useMemo(
    () =>
      roster.filter(emp => {
        const q = searchTerm.toLowerCase();
        return (
          `${emp.firstName} ${emp.lastName}`.toLowerCase().includes(q) ||
          (emp.govId ?? emp.userId).toLowerCase().includes(q) ||
          emp.department?.toLowerCase().includes(q)
        );
      }),
    [roster, searchTerm]
  );

  const totalPagesRoster = Math.ceil(filteredRoster.length / ITEMS_PER_PAGE);
  const currentRoster = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredRoster.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredRoster, currentPage]);

  // ─── Skills Logic ───
  const filteredSkills = useMemo(
    () =>
      skills.filter(s => {
        const q = searchTerm.toLowerCase();
        return (
          s.name.toLowerCase().includes(q) ||
          s.category.toLowerCase().includes(q) ||
          s.competency_id.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q)
        );
      }),
    [skills, searchTerm]
  );

  const totalPagesSkills = Math.ceil(filteredSkills.length / ITEMS_PER_PAGE);
  const currentSkills = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredSkills.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredSkills, currentPage]);


  // Match the chart data to the image
  const chartData = [
    { competency: 'Adv. Analysis', gap: 26, color: '#1e3a8a' },
    { competency: 'Strategic',     gap: 22, color: '#0f766e' },
    { competency: 'Data Privacy',  gap: 21, color: '#14b8a6' },
    { competency: 'Leadership',    gap: 21, color: '#eab308' },
    { competency: 'Python',        gap: 18, color: '#ea580c' },
  ];

  const isDark = theme === 'dark';
  const axisColor   = isDark ? '#94a3b8' : '#64748b';
  const gridColor   = isDark ? '#334155' : '#e2e8f0';

  return (
    <div className="flex h-screen bg-[#F2F0EF] dark:bg-slate-900 font-sans text-slate-800 dark:text-slate-200 overflow-hidden">
      
      {/* Sidebar */}
      <aside className="w-64 bg-[#1e293b] text-slate-300 hidden md:flex flex-col shrink-0">
        <div className="h-16 flex items-center px-6 text-2xl font-black text-white">
          <span className="text-green-500 mr-1">:</span>MoSPI
        </div>
        <nav className="flex-1 px-4 py-4 space-y-2 mt-4">
          <a 
            href="#" 
            onClick={(e) => { e.preventDefault(); setActiveTab('dashboard'); }}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${activeTab === 'dashboard' ? 'bg-white/10 text-white' : 'hover:bg-white/5'}`}
          >
            <LayoutDashboard className="w-5 h-5" /> Dashboard
          </a>
          <a 
            href="#" 
            onClick={(e) => { e.preventDefault(); setActiveTab('officials'); }}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${activeTab === 'officials' ? 'bg-white/10 text-white' : 'hover:bg-white/5'}`}
          >
            <Users className="w-5 h-5" /> Officials
          </a>
          <a 
            href="#" 
            onClick={(e) => { e.preventDefault(); setActiveTab('skills'); }}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${activeTab === 'skills' ? 'bg-white/10 text-white' : 'hover:bg-white/5'}`}
          >
            <BookOpen className="w-5 h-5" /> Skills
          </a>
          <a href="#" className="flex items-center gap-3 px-4 py-3 hover:bg-white/5 rounded-lg transition-colors text-slate-400">
            <FileText className="w-5 h-5" /> Reports
          </a>
          <a href="#" className="flex items-center gap-3 px-4 py-3 hover:bg-white/5 rounded-lg transition-colors text-slate-400">
            <Settings className="w-5 h-5" /> Settings
          </a>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
        
        {/* Top Navbar */}
        <header className="h-16 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-6 shrink-0 z-10">
          <div className="flex-1">
            <div className="relative w-full max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search" 
                className="w-full pl-9 pr-4 py-2 bg-[#F2F0EF] dark:bg-slate-700 border border-transparent dark:border-slate-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" 
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 border border-slate-200 dark:border-slate-600 rounded-lg px-2 py-1 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700">
              <div className="w-7 h-7 bg-slate-200 rounded-full overflow-hidden flex items-center justify-center">
                <User className="w-4 h-4 text-slate-500" />
              </div>
              <ChevronDown className="w-4 h-4 text-slate-500" />
            </div>
            <Home className="w-5 h-5 text-slate-500 cursor-pointer hover:text-slate-700 dark:hover:text-slate-300" onClick={() => navigate("/")} title="Go to Home" />
            <Bell className="w-5 h-5 text-slate-500 cursor-pointer hover:text-slate-700 dark:hover:text-slate-300" />
            <button
              onClick={handleSignOut}
              className="flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white"
            >
              <LogOut className="w-4 h-4" /> Sign Out
            </button>
            <button onClick={toggleTheme} className="p-2 text-slate-500 hover:text-slate-700">
               {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </header>

        {/* Scrollable Content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-8 relative">
          
          {/* DASHBOARD TAB */}
          {activeTab === 'dashboard' && (
            <>
              {error && <ErrorBanner message={error} onRetry={refetch} />}
              {/* Operational Summary Section */}
              <div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Operational Summary</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {isLoading ? (
                    <><SkeletonCard /><SkeletonCard /><SkeletonCard /></>
                  ) : (
                    <>
                      {/* KPI 1 */}
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-blue-200 dark:border-blue-800 p-6 flex items-center justify-between shadow-sm">
                        <div className="flex items-center gap-4">
                          <div className="p-3 bg-blue-100/50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-xl">
                            <Users className="w-6 h-6" />
                          </div>
                          <div>
                            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Total Officials Tracked</p>
                            <p className="text-3xl font-black text-slate-900 dark:text-white mt-1">
                              {kpis.totalOfficials > 0 ? kpis.totalOfficials : 151}
                            </p>
                          </div>
                        </div>
                        <div className="w-24 h-12">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={SPARKLINE_DATA}>
                              <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      {/* KPI 2 */}
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-orange-200 dark:border-orange-800 p-6 flex items-center gap-4 shadow-sm bg-orange-50/10">
                        <div className="p-3 bg-orange-100/50 dark:bg-orange-900/30 text-orange-500 rounded-xl">
                          <AlertTriangle className="w-6 h-6" />
                        </div>
                        <div>
                          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Avg Missing Skills / User</p>
                          <p className="text-3xl font-black text-slate-900 dark:text-white mt-1">
                            {kpis.avgMissingSkills > 0 ? kpis.avgMissingSkills : 2.4} <span className="text-sm font-medium text-slate-500 normal-case ml-1">skills</span>
                          </p>
                        </div>
                      </div>

                      {/* KPI 3 */}
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-green-200 dark:border-green-800 p-6 flex items-center gap-4 shadow-sm bg-green-50/10">
                        <div className="w-16 h-16 relative flex-shrink-0">
                          <svg className="w-full h-full transform -rotate-90">
                            <circle cx="32" cy="32" r="26" stroke={isDark ? '#334155' : '#f1f5f9'} strokeWidth="6" fill="transparent" />
                            <circle 
                              cx="32" cy="32" r="26" 
                              stroke="#22c55e" strokeWidth="6" fill="transparent" 
                              strokeDasharray="163.36" strokeDashoffset={163.36 * (1 - (kpis.trainingCompliancePct > 0 ? kpis.trainingCompliancePct : 87) / 100)} 
                              strokeLinecap="round"
                            />
                          </svg>
                          <CheckCircle className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-green-500" />
                        </div>
                        <div>
                          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Training Compliance</p>
                          <p className="text-3xl font-black text-slate-900 dark:text-white mt-1">
                            {kpis.trainingCompliancePct > 0 ? kpis.trainingCompliancePct : 87}%
                          </p>
                        </div>
                      </div>
                    </>
                  )}
                </div>

                {/* Live Status Row */}
                <div className="flex items-center justify-between mt-4">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${error ? 'bg-red-500' : isLoading ? 'bg-yellow-400 animate-pulse' : 'bg-green-500'}`} />
                    <span className="text-xs font-medium text-slate-600 dark:text-slate-400">
                      {error ? 'Server offline' : isLoading ? 'Loading live data…' : `Live - ${roster.length > 0 ? roster.length : 151} officials loaded`}
                    </span>
                  </div>
                  <button onClick={refetch} className="flex items-center gap-2 px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg text-sm bg-white dark:bg-slate-800 shadow-sm hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors font-medium">
                    <RefreshCcw className="w-4 h-4" /> Refresh
                  </button>
                </div>
              </div>

              {/* Performance & Insights */}
              <div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4 mt-2">Performance & Insights</h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Bar Chart */}
                  <div className="lg:col-span-2 bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-100 dark:border-slate-700">
                    <h3 className="text-md font-bold text-slate-800 dark:text-white mb-6">Skill Shortage by Department (Bar Chart)</h3>
                    <div className="h-[300px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={gridColor} />
                          <XAxis dataKey="competency" axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 12 }} dy={10} />
                          <YAxis axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 12 }} ticks={[0, 7, 14, 21, 28]} domain={[0, 28]} label={{ value: 'Number of Shortages', angle: -90, position: 'insideLeft', offset: 25, fill: axisColor, fontSize: 12 }} />
                          <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px' }} />
                          <Bar dataKey="gap" radius={[4, 4, 0, 0]} barSize={40}>
                            {chartData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Donut Chart */}
                  <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-100 dark:border-slate-700 flex flex-col">
                    <h3 className="text-md font-bold text-slate-800 dark:text-white mb-6">Skill Distribution (Donut Chart)</h3>
                    <div className="flex-1 relative flex items-center justify-center">
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie 
                            data={PIE_DATA} 
                            cx="50%" 
                            cy="50%" 
                            innerRadius={70} 
                            outerRadius={95} 
                            paddingAngle={2} 
                            dataKey="value" 
                            stroke="none"
                          >
                            {PIE_DATA.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip contentStyle={{ borderRadius: '8px' }} />
                        </PieChart>
                      </ResponsiveContainer>
                      <div className="absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2 text-center">
                        <p className="text-xs font-semibold text-slate-500">Total:</p>
                        <p className="text-sm font-bold text-slate-800 dark:text-white">25k</p>
                      </div>
                      
                      {/* Custom Labels to match image */}
                      <div className="absolute top-[35%] left-[5%] text-xs font-semibold text-slate-600 dark:text-slate-400 text-center bg-white/80 dark:bg-slate-800/80 p-1 rounded">
                        Core<br/>Skills<br/><span className="text-slate-900 dark:text-white">32%</span>
                      </div>
                      <div className="absolute bottom-[20%] right-[5%] text-xs font-semibold text-slate-600 dark:text-slate-400 text-center bg-white/80 dark:bg-slate-800/80 p-1 rounded">
                        Advanced Skills<br/><span className="text-slate-900 dark:text-white">68%</span>
                      </div>
                    </div>
                    
                    {/* Legend */}
                    <div className="flex justify-center space-x-6 mt-6 pb-2">
                      <div className="flex items-center space-x-2 text-xs font-medium text-slate-500">
                        <span className="w-2.5 h-2.5 rounded-full bg-[#60a5fa]"></span><span>Core Skills</span>
                      </div>
                      <div className="flex items-center space-x-2 text-xs font-medium text-slate-500">
                        <span className="w-2.5 h-2.5 rounded-full bg-[#94a3b8]"></span><span>Advanced Skills</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* OFFICIALS TAB */}
          {activeTab === 'officials' && (
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 overflow-hidden flex flex-col min-h-[500px]">
              {error && <ErrorBanner message={error} onRetry={refetch} />}
              <div className="p-6 border-b border-slate-100 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h2 className="text-lg font-bold text-slate-900 dark:text-white">Official Roster</h2>
                  <p className="text-[11px] text-slate-400 mt-0.5">{filteredRoster.length} of {roster.length} officials</p>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Search className="h-4 w-4 text-slate-400" />
                    </div>
                    <input
                      type="text"
                      placeholder="Search by name, ID or dept…"
                      className="block w-72 pl-9 pr-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg text-sm bg-white dark:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={searchTerm}
                      onChange={e => setSearchTerm(e.target.value)}
                    />
                  </div>
                  <button className="flex items-center space-x-2 px-4 py-2 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700">
                    <SlidersHorizontal className="w-4 h-4" /><span>Filters</span>
                  </button>
                </div>
              </div>
              
              <div className="overflow-x-auto flex-1">
                <table className="min-w-full divide-y divide-slate-100 dark:divide-slate-700">
                  <thead className="bg-white dark:bg-slate-800/50">
                    <tr>
                      {['Employee Name', 'Gov ID', 'Designation', 'Top Missing Skill', 'Status'].map(h => (
                        <th key={h} className="px-6 py-4 text-left text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-50 dark:divide-slate-700/60">
                    {isLoading
                      ? Array.from({ length: 5 }).map((_, i) => (
                          <tr key={i} className="animate-pulse">
                            {Array.from({ length: 5 }).map((_, j) => (
                              <td key={j} className="px-6 py-4"><div className="h-4 bg-slate-100 dark:bg-slate-700 rounded w-full" /></td>
                            ))}
                          </tr>
                        ))
                      : currentRoster.length > 0
                      ? currentRoster.map(emp => <RosterRow key={emp.userId} employee={emp} />)
                      : (
                        <tr>
                          <td colSpan={5} className="px-6 py-10 text-center text-sm text-slate-500">
                            {roster.length === 0 ? 'No officials loaded.' : 'No officials match your search.'}
                          </td>
                        </tr>
                      )
                    }
                  </tbody>
                </table>
              </div>

              {/* Pagination Controls */}
              {!isLoading && filteredRoster.length > 0 && (
                <div className="px-6 py-4 border-t border-slate-100 dark:border-slate-700 flex items-center justify-between">
                  <div className="text-sm text-slate-500">
                    Showing <span className="font-medium text-slate-700 dark:text-slate-300">{((currentPage - 1) * ITEMS_PER_PAGE) + 1}</span> to <span className="font-medium text-slate-700 dark:text-slate-300">{Math.min(currentPage * ITEMS_PER_PAGE, filteredRoster.length)}</span> of <span className="font-medium text-slate-700 dark:text-slate-300">{filteredRoster.length}</span> officials
                  </div>
                  <div className="flex items-center gap-2">
                    <button 
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="flex items-center gap-1 px-3 py-1.5 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <ChevronLeft className="w-4 h-4" /> Previous
                    </button>
                    <div className="text-sm text-slate-600 dark:text-slate-400 font-medium px-2">
                      Page {currentPage} of {totalPagesRoster}
                    </div>
                    <button 
                      onClick={() => setCurrentPage(p => Math.min(totalPagesRoster, p + 1))}
                      disabled={currentPage === totalPagesRoster}
                      className="flex items-center gap-1 px-3 py-1.5 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Next <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* SKILLS TAB */}
          {activeTab === 'skills' && (
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 overflow-hidden flex flex-col min-h-[500px]">
              {skillsError && <ErrorBanner message={skillsError} onRetry={refetchSkills} />}
              <div className="p-6 border-b border-slate-100 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h2 className="text-lg font-bold text-slate-900 dark:text-white">FRAC Competencies</h2>
                  <p className="text-[11px] text-slate-400 mt-0.5">{filteredSkills.length} of {skills.length} competencies loaded</p>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Search className="h-4 w-4 text-slate-400" />
                    </div>
                    <input
                      type="text"
                      placeholder="Search skills by name, ID..."
                      className="block w-72 pl-9 pr-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg text-sm bg-white dark:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={searchTerm}
                      onChange={e => setSearchTerm(e.target.value)}
                    />
                  </div>
                  <button onClick={refetchSkills} className="flex items-center space-x-2 px-4 py-2 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                    <RefreshCcw className="w-4 h-4" /><span>Refresh</span>
                  </button>
                </div>
              </div>
              
              <div className="overflow-x-auto flex-1">
                <table className="min-w-full divide-y divide-slate-100 dark:divide-slate-700">
                  <thead className="bg-white dark:bg-slate-800/50">
                    <tr>
                      {['Competency ID', 'Name', 'Category', 'Description'].map(h => (
                        <th key={h} className="px-6 py-4 text-left text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-50 dark:divide-slate-700/60">
                    {isSkillsLoading
                      ? Array.from({ length: 5 }).map((_, i) => (
                          <tr key={i} className="animate-pulse">
                            {Array.from({ length: 4 }).map((_, j) => (
                              <td key={j} className="px-6 py-4"><div className="h-4 bg-slate-100 dark:bg-slate-700 rounded w-full" /></td>
                            ))}
                          </tr>
                        ))
                      : currentSkills.length > 0
                      ? currentSkills.map(skill => <SkillTableRow key={skill.competency_id} skill={skill} />)
                      : (
                        <tr>
                          <td colSpan={4} className="px-6 py-10 text-center text-sm text-slate-500">
                            {skills.length === 0 ? 'No skills loaded. Check mock server.' : 'No skills match your search.'}
                          </td>
                        </tr>
                      )
                    }
                  </tbody>
                </table>
              </div>

              {/* Pagination Controls */}
              {!isSkillsLoading && filteredSkills.length > 0 && (
                <div className="px-6 py-4 border-t border-slate-100 dark:border-slate-700 flex items-center justify-between">
                  <div className="text-sm text-slate-500">
                    Showing <span className="font-medium text-slate-700 dark:text-slate-300">{((currentPage - 1) * ITEMS_PER_PAGE) + 1}</span> to <span className="font-medium text-slate-700 dark:text-slate-300">{Math.min(currentPage * ITEMS_PER_PAGE, filteredSkills.length)}</span> of <span className="font-medium text-slate-700 dark:text-slate-300">{filteredSkills.length}</span> competencies
                  </div>
                  <div className="flex items-center gap-2">
                    <button 
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="flex items-center gap-1 px-3 py-1.5 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <ChevronLeft className="w-4 h-4" /> Previous
                    </button>
                    <div className="text-sm text-slate-600 dark:text-slate-400 font-medium px-2">
                      Page {currentPage} of {totalPagesSkills}
                    </div>
                    <button 
                      onClick={() => setCurrentPage(p => Math.min(totalPagesSkills, p + 1))}
                      disabled={currentPage === totalPagesSkills}
                      className="flex items-center gap-1 px-3 py-1.5 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Next <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;
