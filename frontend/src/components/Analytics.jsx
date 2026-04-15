import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Percent } from 'lucide-react';

const COLORS = ['#10b981', '#f59e0b', '#064e3b', '#14b8a6', '#f43f5e', '#3b82f6'];

const MonthPicker = ({ value, onChange }) => (
  <input
    type="month"
    value={value}
    onChange={e => onChange(e.target.value)}
    className="fin-input"
  />
);

const MetricCard = ({ title, value, icon: Icon, colorClass, borderClass }) => (
  <div className={`p-6 ${borderClass}`}>
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

  const [monthYear, setMonthYear] = useState(currentMonth);
  const [metrics, setMetrics] = useState(null);
  const [distribution, setDistribution] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [mRes, dRes, tRes] = await Promise.all([
          axios.get(`/api/analytics/metrics?month_year=${monthYear}`),
          axios.get(`/api/analytics/distribution?month_year=${monthYear}`),
          axios.get('/api/analytics/trends?months=6'),
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
  }, [monthYear]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex space-x-2">
          <div className="w-3 h-3 bg-emerald-500 rounded-full animate-bounce"></div>
          <div className="w-3 h-3 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
          <div className="w-3 h-3 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.5s]"></div>
        </div>
      </div>
    );
  }

  const income = metrics?.total_income ?? 0;
  const expense = metrics?.total_expense ?? 0;
  const net = metrics?.net_balance ?? 0;
  const savings = metrics?.savings_rate_pct ?? 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <div className="w-48">
          <MonthPicker value={monthYear} onChange={setMonthYear} />
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
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

      {/* Income vs Expense Trend */}
      <div className="p-6 fin-card">
        <h2 className="mb-5 text-lg font-semibold text-white border-b border-emerald-500/20 pb-2">Income vs Expense Trend (Last 6 Months)</h2>
        {trends.length > 0 ? (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
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
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                <XAxis dataKey="month" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={v => `$${v}`} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#112240', color: '#f8fafc' }}
                  formatter={v => `$${Number(v).toFixed(2)}`}
                />
                <Legend />
                <Area type="monotone" dataKey="income" name="Income" stroke="#10b981" strokeWidth={2} fill="url(#incomeGrad)" />
                <Area type="monotone" dataKey="expense" name="Expense" stroke="#f43f5e" strokeWidth={2} fill="url(#expenseGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="py-10 text-center text-slate-500">No trend data available yet.</p>
        )}
      </div>

      {/* Distribution & Top Expenses */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Pie Chart */}
        <div className="p-6 fin-card">
          <h2 className="mb-5 text-lg font-semibold text-white border-b border-emerald-500/20 pb-2">Spending by Category</h2>
          {distribution.length > 0 ? (
            <>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={distribution} cx="50%" cy="50%" outerRadius={90} dataKey="actual_spent" nameKey="category_name" paddingAngle={3}>
                      {distribution.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip
                      formatter={v => `$${Number(v).toFixed(2)}`}
                      contentStyle={{ borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#112240', color: '#f8fafc' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 space-y-3">
                {distribution.map((cat, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                      <span className="text-slate-300">{cat.category_name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-500">{cat.percentage}%</span>
                      <span className="font-medium text-white">${Number(cat.actual_spent).toFixed(2)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="py-10 text-center text-slate-500">No expense data for this month.</p>
          )}
        </div>

        {/* Top Expenses Bar */}
        <div className="p-6 fin-card">
          <h2 className="mb-5 text-lg font-semibold text-white border-b border-emerald-500/20 pb-2">Top Expense Categories</h2>
          {distribution.length > 0 ? (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distribution.slice(0, 6)} layout="vertical" margin={{ top: 0, right: 20, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#1e293b" />
                  <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `$${v}`} />
                  <YAxis dataKey="category_name" type="category" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} width={80} />
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#112240', color: '#f8fafc' }}
                    formatter={v => `$${Number(v).toFixed(2)}`}
                  />
                  <Bar dataKey="actual_spent" name="Spent" radius={[0, 4, 4, 0]}>
                    {distribution.slice(0, 6).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="py-10 text-center text-slate-500">No expense data for this month.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Analytics;
