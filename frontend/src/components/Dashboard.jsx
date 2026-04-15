import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  PieChart, Pie, Cell, Tooltip as PieTooltip, Legend as PieLegend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as BarTooltip, Legend as BarLegend
} from 'recharts';
import { ArrowUpRight, ArrowDownRight, Wallet, Target, Sparkles, AlertCircle } from 'lucide-react';

const COLORS = ['#10b981', '#f59e0b', '#064e3b', '#14b8a6', '#f43f5e', '#3b82f6'];

const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [distribution, setDistribution] = useState([]);
  const [budgets, setBudgets] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [metricsRes, distRes, budgetRes, recRes] = await Promise.all([
          axios.get('/api/analytics/metrics'),
          axios.get('/api/analytics/distribution'),
          axios.get('/api/budgets/summary'),
          axios.get('/api/recommendations')
        ]);
        
        if (metricsRes.data.success) setMetrics(metricsRes.data.data);
        if (distRes.data.success) setDistribution(distRes.data.data);
        if (budgetRes.data.success) setBudgets(budgetRes.data.data);
        if (recRes.data.success) setRecommendations(recRes.data.data);
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[60vh]">
        <div className="flex space-x-2">
          <div className="w-3 h-3 bg-emerald-500 rounded-full animate-bounce"></div>
          <div className="w-3 h-3 bg-emerald-500 rounded-full animate-bounce shadow-emerald-500/50 [animation-delay:-.3s]"></div>
          <div className="w-3 h-3 bg-emerald-500 rounded-full animate-bounce shadow-emerald-500/50 [animation-delay:-.5s]"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* Total Income */}
        <div className="p-6 fin-card-emerald">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-400">Total Income</h3>
            <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg shadow-sm">
              <ArrowUpRight size={20} />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-bold text-white tracking-tight">
              ${metrics?.total_income?.toLocaleString() || '0.00'}
            </span>
          </div>
        </div>

        {/* Total Expenses */}
        <div className="p-6 fin-card-rose">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-400">Total Expenses</h3>
            <div className="p-2 bg-rose-500/20 text-rose-400 rounded-lg shadow-sm">
              <ArrowDownRight size={20} />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-bold text-white tracking-tight">
              ${metrics?.total_expense?.toLocaleString() || '0.00'}
            </span>
          </div>
        </div>

        {/* Net Balance */}
        <div className="p-6 fin-card-teal">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-400">Net Balance</h3>
            <div className="p-2 bg-teal-500/20 text-teal-400 rounded-lg shadow-sm">
              <Wallet size={20} />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-bold text-white tracking-tight">
              ${metrics?.net_balance?.toLocaleString() || '0.00'}
            </span>
          </div>
        </div>

        {/* Savings Rate */}
        <div className="p-6 fin-card-gold">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-400">Savings Rate</h3>
            <div className="p-2 bg-amber-500/20 text-amber-400 rounded-lg shadow-sm">
              <Target size={20} />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-bold text-white tracking-tight">
              {metrics?.savings_rate_pct || 0}%
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Expense Distribution */}
        <div className="p-6 lg:col-span-1 fin-card">
          <h2 className="mb-4 pb-2 text-lg font-semibold text-white border-b border-amber-500/30">
            Expense Distribution
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="actual_spent"
                  nameKey="category_name"
                >
                  {distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <PieTooltip 
                  formatter={(value) => `$${Number(value).toFixed(2)}`} 
                  contentStyle={{ borderRadius: '8px', border: 'none', backgroundColor: '#112240', color: '#f8fafc', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-3">
            {distribution.slice(0, 4).map((cat, i) => (
              <div key={i} className="flex justify-between text-sm">
                <div className="flex items-center">
                  <div className="w-3 h-3 mr-3 rounded-sm shadow-sm" style={{ backgroundColor: COLORS[i % COLORS.length] }}></div>
                  <span className="text-slate-300">{cat.category_name}</span>
                </div>
                <span className="font-medium text-white">${cat.actual_spent}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Budgets vs Actual */}
        <div className="p-6 lg:col-span-2 fin-card">
          <h2 className="mb-4 pb-2 text-lg font-semibold text-white border-b border-amber-500/30">
            Budget vs Actual
          </h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={budgets} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                <XAxis dataKey="category_name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 13 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 13 }} tickFormatter={(val) => `$${val}`} />
                <BarTooltip 
                  cursor={{ fill: 'rgba(30, 41, 59, 0.4)' }}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#112240', color: '#f8fafc' }}
                />
                <BarLegend wrapperStyle={{ paddingTop: '10px' }} />
                <Bar dataKey="budget_limit" name="Budget Limit" fill="#334155" radius={[4, 4, 0, 0]} />
                <Bar dataKey="actual_spent" name="Actual Spent" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="p-6 fin-card border-t-[3px] border-t-amber-400">
        <div className="flex items-center mb-6">
          <div className="p-2 mr-3 bg-amber-500/20 text-amber-400 rounded-lg">
            <Sparkles size={20} />
          </div>
          <h2 className="text-lg font-semibold text-white">AI Financial Insights</h2>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {recommendations.length > 0 ? (
            recommendations.map((rec, index) => (
              <div key={index} className="flex p-4 rounded-xl bg-[#0a1628] border border-slate-700/50 shadow-inner">
                <div className="flex-shrink-0 mt-0.5">
                  <AlertCircle size={18} className="text-emerald-500" />
                </div>
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-white">{rec.title || 'Insight'}</h4>
                  <p className="mt-1 text-sm text-slate-400 leading-relaxed">{rec.message || rec.description || (typeof rec === 'string' ? rec : '')}</p>
                </div>
              </div>
            ))
          ) : (
            <p className="text-slate-400 italic">No recommendations available currently.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
