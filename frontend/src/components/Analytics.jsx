import React, { useEffect, useState } from 'react';
import axiosAuth from '../utils/axiosAuth';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, Sector, LabelList,
  ComposedChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Percent, Calendar, Layers, ChevronLeft, ChevronRight, Sparkles, AlertTriangle, CheckCircle, Lightbulb, ShieldCheck, RefreshCw } from 'lucide-react';

const COLORS = [
  '#10b981', '#f59e0b', '#3b82f6', '#f43f5e', '#8b5cf6', 
  '#06b6d4', '#ec4899', '#f97316', '#84cc16', '#0ea5e9',
  '#d946ef', '#6366f1', '#14b8a6', '#ef4444', '#a855f7',
  '#22c55e', '#eab308', '#3b82f6', '#475569', '#94a3b8'
];

const CustomTooltip = ({ active, payload, label, viewType }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#112240] border border-slate-700 p-4 rounded-xl shadow-2xl animate-fade-in min-w-[150px]">
        <p className="text-slate-200 font-bold mb-2 border-b border-slate-700/50 pb-1">
          {viewType === 'Monthly' ? `Day ${label}` : label}
        </p>
        <div className="space-y-1.5">
          {payload.filter(p => p.name !== '_bg').map((entry, index) => (
            <div key={index} className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="text-xs text-slate-400 font-medium">{entry.name}</span>
              </div>
              <span className="text-xs font-bold text-white">${Number(entry.value).toLocaleString()}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }
  return null;
};

const renderActiveShape = (props) => {
  const RADIAN = Math.PI / 180;
  const { cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle, fill, payload, percent, value } = props;
  const sin = Math.sin(-RADIAN * midAngle);
  const cos = Math.cos(-RADIAN * midAngle);
  const sx = cx + (outerRadius + 10) * cos;
  const sy = cy + (outerRadius + 10) * sin;
  const mx = cx + (outerRadius + 30) * cos;
  const my = cy + (outerRadius + 30) * sin;
  const ex = mx + (cos >= 0 ? 1 : -1) * 22;
  const ey = my;
  const textAnchor = cos >= 0 ? 'start' : 'end';

  return (
    <g>
      <path d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`} stroke={fill} fill="none" strokeWidth={2} />
      <circle cx={ex} cy={ey} r={2} fill={fill} stroke="none" />
      <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} textAnchor={textAnchor} fill="#fff" fontSize={14} fontWeight="bold">
        {payload.category_name}
      </text>
      <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} dy={18} textAnchor={textAnchor} fill="#94a3b8" fontSize={12}>
        {`$${value.toFixed(2)} (${(percent * 100).toFixed(1)}%)`}
      </text>
      <path
        d={`M${cx},${cy}L${sx},${sy}`}
        stroke={fill}
        fill="none"
        strokeWidth={1}
        strokeOpacity={0.2}
      />
      <Sector
        cx={cx}
        cy={cy}
        innerRadius={innerRadius}
        outerRadius={outerRadius + 10}
        startAngle={startAngle}
        endAngle={endAngle}
        fill={fill}
      />
    </g>
  );
};

const MonthPicker = ({ value, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = React.useRef(null);
  
  // Parse current value
  const [year, month] = value.split('-').map(Number);
  const [browsingYear, setBrowsingYear] = useState(year);

  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];

  const monthNamesFull = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMonthSelect = (monthIndex) => {
    const formattedMonth = String(monthIndex + 1).padStart(2, '0');
    onChange(`${browsingYear}-${formattedMonth}`);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger */}
      <div 
        onClick={() => {
          setIsOpen(!isOpen);
          setBrowsingYear(year);
        }}
        className="relative group flex items-center bg-[#0a1628] border border-slate-700 text-slate-100 rounded-xl pl-10 pr-4 py-2.5 text-sm cursor-pointer hover:border-emerald-500/50 hover:bg-[#112240] transition-all min-w-[180px] shadow-sm select-none"
      >
        <div className="absolute left-3.5 text-emerald-400 group-hover:scale-110 transition-transform">
          <Calendar size={18} />
        </div>
        <span className="font-semibold tracking-wide">
          {monthNamesFull[month - 1]}, {year}
        </span>
      </div>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 p-4 bg-[#112240] border border-slate-700 rounded-2xl shadow-2xl z-50 animate-fade-in min-w-[280px]">
          {/* Year Navigator */}
          <div className="flex items-center justify-between mb-4 px-1">
            <button 
              onClick={() => setBrowsingYear(browsingYear - 1)}
              className="p-1.5 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-colors"
            >
              <ChevronLeft size={18} />
            </button>
            <span className="text-lg font-bold text-white tracking-widest">{browsingYear}</span>
            <button 
              onClick={() => setBrowsingYear(browsingYear + 1)}
              className="p-1.5 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-colors"
            >
              <ChevronRight size={18} />
            </button>
          </div>

          {/* Months Grid */}
          <div className="grid grid-cols-3 gap-2">
            {months.map((m, idx) => {
              const isSelected = year === browsingYear && month === idx + 1;
              return (
                <button
                  key={m}
                  onClick={() => handleMonthSelect(idx)}
                  className={`py-2 text-sm font-medium rounded-xl transition-all ${
                    isSelected
                      ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/20'
                      : 'text-slate-400 hover:bg-slate-700 hover:text-slate-100'
                  }`}
                >
                  {m}
                </button>
              );
            })}
          </div>

          {/* Footer Shortcuts */}
          <div className="mt-4 pt-4 border-t border-slate-700 flex justify-center">
            <button 
              onClick={() => {
                const d = new Date();
                onChange(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
                setIsOpen(false);
              }}
              className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 transition-colors uppercase tracking-wider"
            >
              Current Month
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const MetricCard = ({ title, value, icon: Icon, colorClass, borderClass }) => (
  <div className={`p-6 ${borderClass} animate-fade-in`}>
    <div className="flex items-center justify-between mb-3">
      <h3 className="text-sm font-medium text-slate-400">{title}</h3>
      <div className={`p-2 rounded-lg ${colorClass}`}><Icon size={18} /></div>
    </div>
    <p className="text-2xl font-bold text-white">{value}</p>
  </div>
);

const Analytics = () => {
  const now = new Date();
  const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;

  const [viewType, setViewType] = useState('Monthly'); // 'Monthly' or 'Overall'
  const [monthYear, setMonthYear] = useState(currentMonth);
  const [activeIndex, setActiveIndex] = useState(0);
  const [metrics, setMetrics] = useState(null);
  const [distribution, setDistribution] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState([]);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [insightsRefreshing, setInsightsRefreshing] = useState(false);

  const fetchInsights = async (isRefresh = false) => {
    if (isRefresh) setInsightsRefreshing(true);
    else setInsightsLoading(true);
    try {
      const targetMonth = viewType === 'Monthly' ? monthYear : new Date().toISOString().slice(0, 7);
      const res = await axiosAuth.get(`/api/recommendations?month_year=${targetMonth}`);
      if (res.data.success) setInsights(res.data.data);
    } catch (err) {
      console.error('Insights fetch error:', err);
    } finally {
      setInsightsLoading(false);
      setInsightsRefreshing(false);
    }
  };

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const targetMonth = viewType === 'Monthly' ? monthYear : 'all';
        const trendParams = viewType === 'Monthly' 
          ? `month_year=${monthYear}` 
          : `months=all`;

        const [mRes, dRes, tRes] = await Promise.all([
          axiosAuth.get(`/api/analytics/metrics?month_year=${targetMonth}`),
          axiosAuth.get(`/api/analytics/distribution?month_year=${targetMonth}`),
          axiosAuth.get(`/api/analytics/trends?${trendParams}`),
        ]);
        
        if (mRes.data.success) setMetrics(mRes.data.data);
        if (dRes.data.success) setDistribution(dRes.data.data);
        if (tRes.data.success) setTrends(tRes.data.data);
      } catch (err) {
        console.error('Analytics fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
    fetchInsights();
  }, [monthYear, viewType]);

  const income = metrics?.total_income ?? 0;
  const expense = metrics?.total_expense ?? 0;
  const net = metrics?.net_balance ?? 0;
  const savings = metrics?.savings_rate_pct ?? 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="flex space-x-2">
          <div className="w-3 h-3 bg-emerald-500 rounded-full animate-bounce"></div>
          <div className="w-3 h-3 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
          <div className="w-3 h-3 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.5s]"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12 animate-fade-in relative z-10">
      {/* Header & View Toggle */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Financial Analytics</h1>
          <p className="text-slate-400 mt-1">
            {viewType === 'Monthly' ? `Detailed insights for ${monthYear}` : 'Aggregate performance of all time'}
          </p>
        </div>

        <div className="flex items-center bg-[#112240] p-1 rounded-xl border border-slate-700/50 shadow-inner">
          <button
            onClick={() => setViewType('Monthly')}
            className={`flex items-center px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              viewType === 'Monthly' 
                ? 'bg-emerald-600 text-white shadow-lg' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Calendar size={16} className="mr-2" />
            Monthly
          </button>
          <button
            onClick={() => setViewType('Overall')}
            className={`flex items-center px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              viewType === 'Overall' 
                ? 'bg-emerald-600 text-white shadow-lg' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers size={16} className="mr-2" />
            Overall
          </button>
        </div>
      </div>

      {/* Month Picker (Only for Monthly view) */}
      {viewType === 'Monthly' && (
        <div className="flex items-center space-x-4 bg-[#112240] w-fit px-5 py-3 rounded-2xl border border-slate-700/50 shadow-xl animate-slide-up relative group z-20">
          <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none rounded-2xl"></div>
          <span className="text-sm font-bold text-slate-200 tracking-tight uppercase">Select Month:</span>
          <MonthPicker value={monthYear} onChange={setMonthYear} />
        </div>
      )}

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 relative z-10">
        <MetricCard 
          title="Total Income" 
          value={`$${income.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} 
          icon={TrendingUp} 
          colorClass="bg-emerald-500/20 text-emerald-400" 
          borderClass="fin-card-emerald"
        />
        <MetricCard 
          title="Total Expenses" 
          value={`$${expense.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} 
          icon={TrendingDown} 
          colorClass="bg-rose-500/20 text-rose-400" 
          borderClass="fin-card-rose"
        />
        <MetricCard 
          title="Net Balance" 
          value={`$${net.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} 
          icon={DollarSign} 
          colorClass="bg-teal-500/20 text-teal-400" 
          borderClass="fin-card-teal"
        />
        <MetricCard 
          title="Savings Rate" 
          value={`${savings}%`} 
          icon={Percent} 
          colorClass="bg-amber-500/20 text-amber-400" 
          borderClass="fin-card-gold"
        />
      </div>

      {/* ── AI-Powered Insights ── */}
      <div className="animate-slide-up [animation-delay:0.1s] relative z-10">
        {/* Section Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-purple-600/30 to-indigo-600/20 border border-purple-500/30">
              <Sparkles className="text-purple-400" size={20} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight">AI-Powered Insights</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                {viewType === 'Monthly' ? `Smart recommendations for ${monthYear}` : 'Based on your latest activity'}
              </p>
            </div>
          </div>
          <button
            onClick={() => fetchInsights(true)}
            disabled={insightsRefreshing}
            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-[#112240] border border-slate-700/50 text-slate-400 hover:text-purple-400 hover:border-purple-500/40 transition-all text-xs font-semibold disabled:opacity-50"
          >
            <RefreshCw size={13} className={insightsRefreshing ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>

        {/* Shimmer skeletons while loading */}
        {insightsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="p-5 fin-card animate-pulse">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-slate-700/60 flex-shrink-0" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-slate-700/60 rounded w-1/2" />
                    <div className="h-3 bg-slate-700/40 rounded w-full" />
                    <div className="h-3 bg-slate-700/40 rounded w-3/4" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : insights.length === 0 ? (
          /* Empty state */
          <div className="fin-card p-10 flex flex-col items-center justify-center text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
              <CheckCircle className="text-emerald-400" size={28} />
            </div>
            <div>
              <p className="text-white font-bold text-lg">You're on track! 🎉</p>
              <p className="text-slate-400 text-sm mt-1 max-w-sm">No alerts this period. Your spending looks healthy — keep up the great work!</p>
            </div>
          </div>
        ) : (
          /* Insight cards grid */
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {insights.map((insight, idx) => {
              const config = {
                SAVINGS: {
                  icon: <TrendingUp size={18} />,
                  iconBg: 'bg-amber-500/15 text-amber-400',
                  border: 'border-l-amber-500',
                  pill: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
                  label: 'Savings'
                },
                BUDGET_EXCEEDED: {
                  icon: <AlertTriangle size={18} />,
                  iconBg: 'bg-rose-500/15 text-rose-400',
                  border: 'border-l-rose-500',
                  pill: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
                  label: 'Budget Alert'
                },
                HIGH_SPENDING: {
                  icon: <Lightbulb size={18} />,
                  iconBg: 'bg-orange-500/15 text-orange-400',
                  border: 'border-l-orange-500',
                  pill: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
                  label: 'High Spending'
                },
                EMERGENCY_FUND: {
                  icon: <ShieldCheck size={18} />,
                  iconBg: 'bg-emerald-500/15 text-emerald-400',
                  border: 'border-l-emerald-500',
                  pill: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
                  label: 'Opportunity'
                },
              }[insight.type] || {
                icon: <Sparkles size={18} />,
                iconBg: 'bg-purple-500/15 text-purple-400',
                border: 'border-l-purple-500',
                pill: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
                label: 'Tip'
              };

              return (
                <div
                  key={idx}
                  className={`group p-5 bg-[#112240] border border-slate-700/50 border-l-4 ${config.border} rounded-xl transition-all hover:translate-y-[-4px] hover:shadow-[0_8px_30px_rgba(0,0,0,0.4)] hover:border-slate-600`}
                  style={{ animationDelay: `${idx * 0.08}s` }}
                >
                  <div className="flex items-start gap-4">
                    {/* Icon badge */}
                    <div className={`p-2.5 rounded-xl flex-shrink-0 ${config.iconBg} group-hover:scale-110 transition-transform`}>
                      {config.icon}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        <h3 className="text-sm font-bold text-white leading-snug">{insight.title}</h3>
                        <span className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full border ${config.pill}`}>
                          {config.label}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed">{insight.message}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Trend Analysis */}
      <div className="p-6 fin-card animate-slide-up [animation-delay:0.1s] relative z-10">
        <div className="flex items-center justify-between mb-6 border-b border-slate-700/50 pb-4">
          <h2 className="text-lg font-bold text-white">
            {viewType === 'Monthly' ? `Daily Spending Trend (${monthYear})` : 'Monthly Growth Trend (All Time)'}
          </h2>
          <div className="text-xs text-slate-500 font-medium">UNIT: USD ($)</div>
        </div>
        
        {trends.length > 0 ? (
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              {viewType === 'Monthly' ? (
                <AreaChart data={trends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" />
                  <XAxis 
                    dataKey="label" 
                    tick={{ fill: '#94a3b8', fontSize: 11 }} 
                    axisLine={false} 
                    tickLine={false}
                    label={{ value: 'Day', position: 'insideBottomRight', offset: -10, fill: '#64748b' }}
                  />
                  <YAxis 
                    tick={{ fill: '#94a3b8', fontSize: 11 }} 
                    axisLine={false} 
                    tickLine={false} 
                    tickFormatter={v => `$${v}`} 
                  />
                  <Tooltip content={<CustomTooltip viewType={viewType} />} />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
                  <Area type="monotone" dataKey="income" name="Income" stroke="#10b981" strokeWidth={3} fill="url(#incomeGrad)" />
                  <Area type="monotone" dataKey="expense" name="Expense" stroke="#f43f5e" strokeWidth={3} fill="url(#expenseGrad)" />
                </AreaChart>
              ) : (
                <ComposedChart data={trends} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <defs>
                    <linearGradient id="overallExpenseGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                  <XAxis 
                    dataKey="label" 
                    tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 500 }} 
                    axisLine={false} 
                    tickLine={false}
                    padding={{ left: 50, right: 50 }}
                    tickFormatter={(val) => val === '%b %Y' || val === '%Y-%m' ? 'No Data' : val}
                  />
                  <YAxis 
                    tick={{ fill: '#94a3b8', fontSize: 11 }} 
                    axisLine={false} 
                    tickLine={false} 
                    tickFormatter={v => `$${v}`} 
                  />
                  <Tooltip 
                    content={<CustomTooltip viewType={viewType} />} 
                    cursor={{ stroke: '#334155', strokeWidth: 2, strokeDasharray: '5 5' }} 
                  />
                  <Legend 
                    verticalAlign="top" 
                    align="right" 
                    iconType="circle" 
                    wrapperStyle={{ paddingBottom: '30px', fontSize: '12px', fontWeight: 600 }} 
                    payload={[{ value: 'Income', type: 'circle', color: '#10b981' }, { value: 'Expense', type: 'circle', color: '#f43f5e' }]}
                  />
                  {/* Background bar to give structure - Hidden from legend and tooltip */}
                  <Bar 
                    dataKey="income" 
                    name="_bg"
                    fill="rgba(255, 255, 255, 0.03)" 
                    barSize={120} 
                    radius={[10, 10, 0, 0]} 
                    isAnimationActive={false}
                    legendType="none"
                    tooltipType="none"
                  />
                  
                  <Area 
                    type="monotone" 
                    dataKey="expense" 
                    name="Expense" 
                    fill="url(#overallExpenseGrad)" 
                    stroke="#f43f5e" 
                    strokeWidth={3}
                    animationDuration={1500}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="income" 
                    name="Income" 
                    stroke="#10b981" 
                    strokeWidth={5} 
                    dot={{ r: 6, fill: '#10b981', strokeWidth: 3, stroke: '#0f172a' }} 
                    activeDot={{ r: 8, fill: '#10b981', strokeWidth: 2, stroke: '#fff' }} 
                    animationDuration={1500}
                  />
                </ComposedChart>
              )}
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500 space-y-3">
            <Layers size={40} className="opacity-20" />
            <p className="italic font-medium text-sm text-center max-w-xs">No transaction history found found for {viewType === 'Monthly' ? 'this month' : 'the selected criteria'}.</p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-slide-up [animation-delay:0.2s] relative z-10">
        {/* Distribution Pie Chart */}
        <div className="p-6 fin-card">
          <h2 className="mb-6 text-lg font-bold text-white border-b border-slate-700/50 pb-4">Spending by Category</h2>
          {distribution.length > 0 ? (
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie 
                    activeIndex={activeIndex}
                    activeShape={renderActiveShape}
                    data={distribution} 
                    cx="50%" 
                    cy="50%" 
                    innerRadius={80}
                    outerRadius={120} 
                    dataKey="actual_spent" 
                    nameKey="category_name" 
                    paddingAngle={4}
                    stroke="none"
                    onMouseEnter={(_, index) => setActiveIndex(index)}
                  >
                    {distribution.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} className="transition-all duration-300" />)}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-20 text-slate-500 space-y-3">
              <PieChart size={40} className="opacity-20" />
              <p className="italic font-medium text-sm">No expenses recorded.</p>
            </div>
          )}
        </div>

        {/* Top Expenses Bar Chart */}
        <div className="p-6 fin-card">
          <h2 className="mb-6 text-lg font-bold text-white border-b border-slate-700/50 pb-4">Top Spending Tiers</h2>
          {distribution.length > 0 ? (
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distribution.slice(0, 8)} layout="vertical" margin={{ top: 0, right: 60, left: 20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#334155" />
                  <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => `$${v}`} />
                  <YAxis dataKey="category_name" type="category" tick={{ fill: '#e2e8f0', fontSize: 10, fontWeight: 500 }} axisLine={false} tickLine={false} width={100} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: 'none', backgroundColor: '#112240', color: '#f8fafc', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)' }}
                    itemStyle={{ color: '#fff' }}
                    formatter={v => `$${Number(v).toFixed(2)}`}
                    cursor={false}
                  />
                  <Bar dataKey="actual_spent" name="Spent" radius={[0, 6, 6, 0]} barSize={24}>
                    <LabelList dataKey="actual_spent" position="right" formatter={v => `$${Number(v).toFixed(0)}`} className="fill-white text-[10px] font-bold" />
                    {distribution.slice(0, 8).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} className="hover:opacity-80 transition-opacity" />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-20 text-slate-500 space-y-3">
              <BarChart size={40} className="opacity-20" />
              <p className="italic font-medium text-sm">Waiting for transaction data...</p>
            </div>
          )}
        </div>
      </div>

    </div>
  );
};

export default Analytics;
