import React, { useState } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, LineChart, Line 
} from 'recharts';
import { 
  Bell, ChevronDown, CheckCircle, Flame, TrendingUp, Search, Filter, SlidersHorizontal, 
  ArrowRight, User, AlertTriangle
} from 'lucide-react';

const DUMMY_HEATMAP_DATA = [
  { competency: 'Data Privacy', gap: 3.2, color: ['#1e3a8a', '#172554'] }, 
  { competency: 'Survey Design', gap: 2.8, color: ['#0f766e', '#115e59'] }, 
  { competency: 'National Accounts', gap: 1.5, color: ['#2dd4bf', '#0d9488'] }, 
  { competency: 'Python', gap: 2.1, color: ['#eab308', '#84cc16'] }, 
  { competency: 'Machine Learning', gap: 3.5, color: ['#f97316', '#ea580c'] }, 
];

const PIE_DATA = [
  { name: 'Core Skills', value: 32, color: '#93c5fd' },
  { name: 'Advanced Skills', value: 52, color: '#94a3b8' }
];

const SPARKLINE_DATA = [
  { value: 110 }, { value: 112 }, { value: 108 }, { value: 116 }, { value: 115 }, { value: 120 }, { value: 124 }
];

const DUMMY_ROSTER_DATA = [
  { id: 1, name: 'Aarav Sharma', govId: 'EMP-1029', designation: 'Senior Statistician', topMissing: 'Machine Learning', status: 'Training Required' },
  { id: 2, name: 'Priya Patel', govId: 'EMP-1030', designation: 'Data Analyst', topMissing: 'Python', status: 'Compliant' },
  { id: 3, name: 'Rajesh Kumar', govId: 'EMP-1031', designation: 'Survey Director', topMissing: 'Data Privacy', status: 'Training Required' },
  { id: 4, name: 'Neha Gupta', govId: 'EMP-1032', designation: 'Junior Statistician', topMissing: 'Survey Design', status: 'Compliant' },
  { id: 5, name: 'Vikram Singh', govId: 'EMP-1033', designation: 'Policy Advisor', topMissing: 'National Accounts', status: 'Compliant' },
];

const TopographyBackground = () => (
  <div className="absolute inset-0 z-0 pointer-events-none" 
       style={{
         backgroundImage: `url("/bg-topography.png")`,
         backgroundSize: 'cover',
         backgroundPosition: 'center',
         backgroundRepeat: 'no-repeat',
         opacity: 0.6
       }}
  />
);

const AdminDashboard: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredRoster = DUMMY_ROSTER_DATA.filter(emp => 
    emp.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    emp.govId.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#f8fafc] font-sans relative overflow-hidden text-slate-800">
      <TopographyBackground />
      
      {/* Navigation Bar */}
      <nav className="relative z-10 w-full bg-white/80 backdrop-blur-md border-b border-slate-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="text-2xl font-black tracking-tight flex items-center">
            <span className="text-green-500 mr-1">:</span>MoSPI
          </div>
          <div className="hidden sm:block text-[0.6rem] text-slate-400 font-semibold uppercase tracking-widest mt-1 ml-2">
            Skill Intelligence Platform
          </div>
        </div>
        
        <div className="hidden md:flex items-center space-x-8 text-sm font-semibold text-slate-600">
          <a href="#" className="hover:text-slate-900 transition-colors">HOME</a>
          <a href="#" className="hover:text-slate-900 transition-colors">ABOUT</a>
          <a href="#" className="hover:text-slate-900 transition-colors">FEATURES</a>
          <button className="bg-blue-100 text-blue-700 px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-200 transition-colors">
            <span>DASHBOARD</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center space-x-4">
          <button className="text-slate-400 hover:text-slate-600">
            <Bell className="w-5 h-5" />
          </button>
          <div className="flex items-center space-x-2 cursor-pointer">
            <img 
              src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" 
              alt="User avatar" 
              className="w-8 h-8 rounded-full border border-slate-200"
            />
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>
        </div>
      </nav>

      <div className="relative z-10 max-w-7xl mx-auto p-6 md:p-8 space-y-8">
        
        {/* Operational Summary */}
        <div>
          <h2 className="text-xl font-bold text-slate-900 mb-4">Operational Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Card 1 */}
            <div className="bg-white rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] p-6 flex items-center justify-between border border-slate-100">
              <div className="flex items-center space-x-4">
                <div className="bg-blue-50 p-3 rounded-xl flex-shrink-0">
                  <User className="text-blue-500 w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Total Officials Tracked</p>
                  <h3 className="text-3xl font-black text-slate-800 mt-1">124</h3>
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
            
            {/* Card 2 */}
            <div className="bg-white rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] p-6 flex items-center space-x-4 border border-slate-100">
              <div className="bg-orange-50 p-3 rounded-xl flex-shrink-0">
                <AlertTriangle className="text-orange-400 w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Avg Skill Gap Score</p>
                <h3 className="text-3xl font-black text-slate-800 mt-1">2.1 <span className="text-sm font-medium text-slate-400 normal-case tracking-normal">levels</span></h3>
              </div>
            </div>

            {/* Card 3 */}
            <div className="bg-green-50/50 rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] p-6 flex flex-col justify-center border border-green-100">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="text-green-500 w-5 h-5" />
                  <p className="text-sm font-semibold text-slate-700">Training Compliance</p>
                  <Flame className="text-orange-500 w-4 h-4 ml-1" />
                </div>
                <div className="flex items-center space-x-1 text-green-600 font-bold">
                  <TrendingUp className="w-4 h-4" />
                  <span>68%</span>
                </div>
              </div>
              <div className="w-full bg-green-100 rounded-full h-2.5 overflow-hidden">
                <div className="bg-gradient-to-r from-green-400 to-green-600 h-2.5 rounded-full" style={{ width: '68%' }}></div>
              </div>
            </div>

          </div>
        </div>

        {/* Performance & Insights */}
        <div>
          <h2 className="text-xl font-bold text-slate-900 mb-4">Performance & Insights</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Heatmap */}
            <div className="lg:col-span-2 bg-white rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] p-6 border border-slate-100">
              <h3 className="text-md font-bold text-slate-800 mb-6">Department Skill Shortage Heatmap</h3>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={DUMMY_HEATMAP_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                    <defs>
                      {DUMMY_HEATMAP_DATA.map((entry, index) => (
                        <linearGradient id={`gradient-${index}`} x1="0" y1="0" x2="0" y2="1" key={`def-${index}`}>
                          <stop offset="0%" stopColor={entry.color[0]} stopOpacity={1}/>
                          <stop offset="100%" stopColor={entry.color[1]} stopOpacity={1}/>
                        </linearGradient>
                      ))}
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis 
                      dataKey="competency" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fill: '#64748b', fontSize: 12 }} 
                      dy={15}
                    />
                    <YAxis 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fill: '#64748b', fontSize: 12 }}
                      ticks={[0, 0.9, 1.8, 2.7, 3.6]}
                      domain={[0, 3.6]}
                    />
                    <Tooltip 
                      cursor={{ fill: '#f8fafc' }}
                      contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                    />
                    <Bar dataKey="gap" radius={[6, 6, 0, 0]} barSize={60}>
                      {DUMMY_HEATMAP_DATA.map((_entry, index) => (
                        <Cell key={`cell-${index}`} fill={`url(#gradient-${index})`} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Pie Chart */}
            <div className="bg-white rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] p-6 border border-slate-100 flex flex-col">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-md font-bold text-slate-800">Skill Distribution Overview</h3>
                <div className="bg-green-100 text-green-600 p-1 rounded-md">
                  <TrendingUp className="w-4 h-4" />
                </div>
              </div>
              
              <div className="flex-grow flex items-center justify-center relative">
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={PIE_DATA}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={2}
                      dataKey="value"
                      stroke="none"
                    >
                      {PIE_DATA.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                {/* Custom Labels on Pie */}
                <div className="absolute top-1/2 left-[15%] -translate-y-1/2 -translate-x-1/2 text-xs font-semibold text-slate-500 text-center">
                  Core<br/>Skills <span className="text-slate-800 block">32%</span>
                </div>
                <div className="absolute top-[65%] right-[10%] translate-y-1/2 translate-x-1/2 text-xs font-semibold text-slate-500 text-center">
                  Advanced<br/>Skills <span className="text-slate-800 block">52%</span>
                </div>
              </div>

              <div className="flex justify-center space-x-6 mt-4">
                <div className="flex items-center space-x-2 text-xs font-medium text-slate-500">
                  <span className="w-2 h-2 rounded-full bg-blue-300"></span>
                  <span>Core Skills</span>
                </div>
                <div className="flex items-center space-x-2 text-xs font-medium text-slate-500">
                  <span className="w-2 h-2 rounded-full bg-slate-400"></span>
                  <span>Advanced Skills</span>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Table Row */}
        <div className="bg-white rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-slate-100 overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h2 className="text-lg font-bold text-slate-900">Official Roster</h2>
            
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-4 w-4 text-slate-400" />
                </div>
                <input
                  type="text"
                  placeholder="Search by name or ID..."
                  className="block w-64 pl-9 pr-3 py-2 border border-slate-200 rounded-lg text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <button className="flex items-center space-x-2 px-4 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">
                <SlidersHorizontal className="w-4 h-4" />
                <span>Filters</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">
                <Filter className="w-4 h-4" />
                <span>Filter</span>
                <ChevronDown className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-100">
              <thead className="bg-white">
                <tr>
                  <th scope="col" className="px-6 py-4 text-left text-[0.65rem] font-bold text-slate-400 uppercase tracking-widest">Employee Name</th>
                  <th scope="col" className="px-6 py-4 text-left text-[0.65rem] font-bold text-slate-400 uppercase tracking-widest">Gov ID</th>
                  <th scope="col" className="px-6 py-4 text-left text-[0.65rem] font-bold text-slate-400 uppercase tracking-widest">Designation</th>
                  <th scope="col" className="px-6 py-4 text-left text-[0.65rem] font-bold text-slate-400 uppercase tracking-widest">Top Missing Skill</th>
                  <th scope="col" className="px-6 py-4 text-left text-[0.65rem] font-bold text-slate-400 uppercase tracking-widest">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-50">
                {filteredRoster.map((employee) => (
                  <tr key={employee.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-slate-800">{employee.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{employee.govId}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{employee.designation}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-800 font-medium">{employee.topMissing}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`inline-flex items-center px-3 py-1 rounded-md text-xs font-semibold ${
                        employee.status === 'Compliant' 
                          ? 'bg-green-50 text-green-700' 
                          : 'bg-red-50 text-red-600'
                      }`}>
                        {employee.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {filteredRoster.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-6 py-10 text-center text-sm text-slate-500">
                      No officials found matching your search.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
};

export default AdminDashboard;
