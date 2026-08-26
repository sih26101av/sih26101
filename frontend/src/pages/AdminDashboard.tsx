import React, { useState, useMemo } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, LineChart, Line 
} from 'recharts';
import { 
  Bell, ChevronDown, CheckCircle, Flame, TrendingUp, Search, Filter, SlidersHorizontal, 
  ArrowRight, User, AlertTriangle, Sun, Moon, RefreshCcw
} from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import { useAdminData } from '../hooks/useAdminData';
import type { RawAdminUser } from '../services/api';

// ─── Static constants ─────────────────────────────────────────────────────────
const SPARKLINE_DATA = [
  { value: 110 }, { value: 112 }, { value: 108 }, { value: 116 }, { value: 115 }, { value: 120 }, { value: 124 }
];
const PIE_DATA = [
  { name: 'Core Skills',     value: 32, color: '#93c5fd' },
  { name: 'Advanced Skills', value: 52, color: '#94a3b8'  }
];

// ─── Status helpers ───────────────────────────────────────────────────────────
function enrollmentLabel(status: number | undefined): string {
  if (status === 2) return 'Compliant';
  if (status === 1) return 'In Progress';
  return 'Training Required';
}

// ─── Subcomponents ────────────────────────────────────────────────────────────
const TopographyBackground = () => (
  <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.25] dark:opacity-10 dark:invert"
       style={{
         backgroundImage: `url("/bg-new-topo.png")`,
         backgroundSize: 'cover',
         backgroundPosition: 'center',
         transform: 'scale(1.2) translateX(-5%)',
       }}
  />
);

const SkeletonCard = () => (
  <div className="bg-white dark:bg-slate-800/80 rounded-2xl p-6 border border-slate-100 dark:border-slate-700/60 animate-pulse">
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
      <p className="font-semibold text-red-700 dark:text-red-400">Failed to load live data</p>
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
const RosterRow: React.FC<{ employee: RawAdminUser }> = ({ employee }) => {
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

// ─── Main Component ───────────────────────────────────────────────────────────
const AdminDashboard: React.FC = () => {
  const { theme, toggleTheme }                = useTheme();
  const { roster, kpis, heatmap, isLoading, error, refetch } = useAdminData();
  const [searchTerm, setSearchTerm]           = useState('');

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

  // Fallback heatmap when server is offline or no data
  const chartData =
    heatmap.length > 0
      ? heatmap
      : [
          { competency: 'Data Privacy',      gap: 3.2, color: ['#1e3a8a', '#172554'] as [string,string] },
          { competency: 'Survey Design',     gap: 2.8, color: ['#0f766e', '#115e59'] as [string,string] },
          { competency: 'National Accounts', gap: 1.5, color: ['#2dd4bf', '#0d9488'] as [string,string] },
          { competency: 'Python',            gap: 2.1, color: ['#eab308', '#84cc16'] as [string,string] },
          { competency: 'Machine Learning',  gap: 3.5, color: ['#f97316', '#ea580c'] as [string,string] },
        ];

  const isDark = theme === 'dark';
  const axisColor   = isDark ? '#94a3b8' : '#64748b';
  const gridColor   = isDark ? '#334155' : '#f1f5f9';
  const tooltipBg   = isDark ? '#0f172a' : '#ffffff';
  const tooltipBorder = isDark ? '#334155' : '#e2e8f0';

  return (
    <div className="min-h-screen bg-[#f8fafc] dark:bg-slate-900 font-sans relative overflow-hidden text-slate-800 dark:text-slate-200 transition-colors duration-300">
      <TopographyBackground />
      
      {/* Navigation Bar */}
      <nav className="relative z-10 w-full bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-6 py-4 flex items-center justify-between transition-colors duration-300">
        <div className="flex items-center space-x-2">
          <div className="text-2xl font-black tracking-tight flex items-center text-slate-900 dark:text-white">
            <span className="text-green-500 mr-1">:</span>MoSPI
          </div>
          <div className="hidden sm:block text-[0.6rem] text-slate-400 font-semibold uppercase tracking-widest mt-1 ml-2">
            Admin Dashboard
          </div>
        </div>
        
        <div className="hidden md:flex items-center space-x-8 text-sm font-semibold text-slate-600 dark:text-slate-300">
          <a href="/" className="hover:text-slate-900 dark:hover:text-white transition-colors">HOME</a>
          <a href="#" className="hover:text-slate-900 dark:hover:text-white transition-colors">ABOUT</a>
          <a href="#" className="hover:text-slate-900 dark:hover:text-white transition-colors">FEATURES</a>
          <button className="bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-200 dark:hover:bg-blue-800/50 transition-colors">
            <span>DASHBOARD</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center space-x-4">
          <button 
            onClick={toggleTheme}
            className="p-2 rounded-full text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            aria-label="Toggle Theme"
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
          <button className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
            <Bell className="w-5 h-5" />
          </button>
          <div className="flex items-center space-x-2 cursor-pointer pl-2 border-l border-slate-200 dark:border-slate-700">
            <img 
              src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" 
              alt="Admin avatar" 
              className="w-8 h-8 rounded-full border border-slate-200 dark:border-slate-700"
            />
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>
        </div>
      </nav>

      <div className="relative z-10 max-w-7xl mx-auto p-6 md:p-8 space-y-8">

        {/* Live data status bar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${error ? 'bg-red-500' : isLoading ? 'bg-yellow-400 animate-pulse' : 'bg-green-500'}`} />
            <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
              {error ? 'Server offline — showing fallback data' : isLoading ? 'Loading live data…' : `Live — ${roster.length} officials loaded`}
            </span>
          </div>
          <button
            onClick={refetch}
            className="flex items-center gap-1.5 text-[11px] font-bold text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            <RefreshCcw className="w-3.5 h-3.5" /> Refresh
          </button>
        </div>

        {/* Error banner */}
        {error && <ErrorBanner message={error} onRetry={refetch} />}
        
        {/* Operational Summary */}
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Operational Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {isLoading ? (
              <>
                <SkeletonCard /><SkeletonCard /><SkeletonCard />
              </>
            ) : (
              <>
                {/* KPI 1 — Total Officials */}
                <div className="bg-white dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] dark:shadow-none p-6 flex items-center justify-between border border-slate-100 dark:border-slate-700/60 transition-colors duration-300">
                  <div className="flex items-center space-x-4">
                    <div className="bg-blue-50 dark:bg-blue-900/40 p-3 rounded-xl flex-shrink-0">
                      <User className="text-blue-500 dark:text-blue-400 w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Total Officials Tracked</p>
                      <h3 className="text-3xl font-black text-slate-800 dark:text-white mt-1">
                        {kpis.totalOfficials > 0 ? kpis.totalOfficials : 124}
                      </h3>
                    </div>
                  </div>
                  <div className="w-24 h-12">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={SPARKLINE_DATA}>
                        <Line type="monotone" dataKey="value" stroke={isDark ? '#60a5fa' : '#3b82f6'} strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
                
                {/* KPI 2 — Avg Skill Gap */}
                <div className="bg-white dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] dark:shadow-none p-6 flex items-center space-x-4 border border-slate-100 dark:border-slate-700/60 transition-colors duration-300">
                  <div className="bg-orange-50 dark:bg-orange-900/30 p-3 rounded-xl flex-shrink-0">
                    <AlertTriangle className="text-orange-400 dark:text-orange-300 w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Avg Skill Gap Score</p>
                    <h3 className="text-3xl font-black text-slate-800 dark:text-white mt-1">
                      {kpis.avgSkillGapScore > 0 ? kpis.avgSkillGapScore : 2.1}
                      <span className="text-sm font-medium text-slate-400 normal-case tracking-normal ml-1">levels</span>
                    </h3>
                  </div>
                </div>

                {/* KPI 3 — Training Compliance */}
                <div className="bg-green-50/50 dark:bg-green-900/20 backdrop-blur-sm rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] dark:shadow-none p-6 flex flex-col justify-center border border-green-100 dark:border-green-800/50 transition-colors duration-300">
                  <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="text-green-500 dark:text-green-400 w-5 h-5" />
                      <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">Training Compliance</p>
                      <Flame className="text-orange-500 w-4 h-4 ml-1" />
                    </div>
                    <div className="flex items-center space-x-1 text-green-600 dark:text-green-400 font-bold">
                      <TrendingUp className="w-4 h-4" />
                      <span>{kpis.trainingCompliancePct > 0 ? kpis.trainingCompliancePct : 68}%</span>
                    </div>
                  </div>
                  <div className="w-full bg-green-100 dark:bg-green-900/50 rounded-full h-2.5 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-green-400 to-green-600 h-2.5 rounded-full transition-all duration-1000"
                      style={{ width: `${kpis.trainingCompliancePct > 0 ? kpis.trainingCompliancePct : 68}%` }}
                    />
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Performance & Insights */}
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Performance & Insights</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Heatmap — driven by live data */}
            <div className="lg:col-span-2 bg-white dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] dark:shadow-none p-6 border border-slate-100 dark:border-slate-700/60 transition-colors duration-300">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-md font-bold text-slate-800 dark:text-white">Department Skill Shortage Heatmap</h3>
                {!error && !isLoading && heatmap.length > 0 && (
                  <span className="text-[10px] font-bold text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/30 px-2 py-1 rounded-full">LIVE</span>
                )}
              </div>
              <div className="h-72 w-full">
                {isLoading ? (
                  <div className="h-full flex items-center justify-center animate-pulse">
                    <div className="w-full h-48 bg-slate-100 dark:bg-slate-700 rounded-xl" />
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                      <defs>
                        {chartData.map((entry, index) => (
                          <linearGradient id={`gradient-${index}`} x1="0" y1="0" x2="0" y2="1" key={`def-${index}`}>
                            <stop offset="0%" stopColor={entry.color[0]} stopOpacity={1}/>
                            <stop offset="100%" stopColor={entry.color[1]} stopOpacity={1}/>
                          </linearGradient>
                        ))}
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={gridColor} />
                      <XAxis dataKey="competency" axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 12 }} dy={15} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 12 }} />
                      <Tooltip
                        cursor={{ fill: isDark ? '#1e293b' : '#f8fafc' }}
                        contentStyle={{ borderRadius: '12px', border: `1px solid ${tooltipBorder}`, backgroundColor: tooltipBg, boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                        labelStyle={{ color: isDark ? '#e2e8f0' : '#0f172a', fontWeight: 600 }}
                        formatter={(value) => [`${value} deficiency units`, 'Gap Score']}
                      />
                      <Bar dataKey="gap" radius={[6, 6, 0, 0]} barSize={60}>
                        {chartData.map((_entry, index) => (
                          <Cell key={`cell-${index}`} fill={`url(#gradient-${index})`} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* Pie Chart */}
            <div className="bg-white dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] dark:shadow-none p-6 border border-slate-100 dark:border-slate-700/60 flex flex-col transition-colors duration-300">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-md font-bold text-slate-800 dark:text-white">Skill Distribution</h3>
                <div className="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 p-1 rounded-md">
                  <TrendingUp className="w-4 h-4" />
                </div>
              </div>
              
              <div className="flex-grow flex items-center justify-center relative">
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie data={PIE_DATA} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={2} dataKey="value" stroke="none">
                      {PIE_DATA.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ borderRadius: '12px', border: `1px solid ${tooltipBorder}`, backgroundColor: tooltipBg, boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute top-1/2 left-[15%] -translate-y-1/2 -translate-x-1/2 text-xs font-semibold text-slate-500 dark:text-slate-400 text-center">
                  Core<br/>Skills <span className="text-slate-800 dark:text-white block">32%</span>
                </div>
                <div className="absolute top-[65%] right-[10%] translate-y-1/2 translate-x-1/2 text-xs font-semibold text-slate-500 dark:text-slate-400 text-center">
                  Advanced<br/>Skills <span className="text-slate-800 dark:text-white block">52%</span>
                </div>
              </div>

              <div className="flex justify-center space-x-6 mt-4">
                <div className="flex items-center space-x-2 text-xs font-medium text-slate-500 dark:text-slate-400">
                  <span className="w-2 h-2 rounded-full bg-blue-300"></span><span>Core Skills</span>
                </div>
                <div className="flex items-center space-x-2 text-xs font-medium text-slate-500 dark:text-slate-400">
                  <span className="w-2 h-2 rounded-full bg-slate-400"></span><span>Advanced</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Official Roster Table — live, searchable */}
        <div className="bg-white dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] dark:shadow-none border border-slate-100 dark:border-slate-700/60 overflow-hidden transition-colors duration-300">
          <div className="p-6 border-b border-slate-100 dark:border-slate-700/60 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
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
                  placeholder="Search by name, ID or department…"
                  className="block w-72 pl-9 pr-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg text-sm placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-slate-700 text-slate-900 dark:text-white transition-colors duration-300"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                />
              </div>
              <button className="flex items-center space-x-2 px-4 py-2 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                <SlidersHorizontal className="w-4 h-4" /><span>Filters</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                <Filter className="w-4 h-4" /><span>Filter</span><ChevronDown className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-100 dark:divide-slate-700/60">
              <thead className="bg-white dark:bg-slate-800 transition-colors duration-300">
                <tr>
                  {['Employee Name', 'Gov ID', 'Designation', 'Top Missing Skill', 'Status'].map(h => (
                    <th key={h} scope="col" className="px-6 py-4 text-left text-[0.65rem] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-slate-800/50 divide-y divide-slate-50 dark:divide-slate-700/60 transition-colors duration-300">
                {isLoading
                  ? Array.from({ length: 5 }).map((_, i) => (
                      <tr key={i} className="animate-pulse">
                        {Array.from({ length: 5 }).map((_, j) => (
                          <td key={j} className="px-6 py-4">
                            <div className="h-4 bg-slate-100 dark:bg-slate-700 rounded w-full" />
                          </td>
                        ))}
                      </tr>
                    ))
                  : filteredRoster.length > 0
                  ? filteredRoster.map(emp => <RosterRow key={emp.userId} employee={emp} />)
                  : (
                    <tr>
                      <td colSpan={5} className="px-6 py-10 text-center text-sm text-slate-500 dark:text-slate-400">
                        {roster.length === 0
                          ? 'No officials loaded. Check server connection.'
                          : 'No officials match your search.'}
                      </td>
                    </tr>
                  )
                }
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
};

export default AdminDashboard;
