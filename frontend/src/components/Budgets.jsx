import React, { useEffect, useState } from 'react';
import axiosAuth from '../utils/axiosAuth';
import { Target, Plus, Trash2, AlertTriangle, CheckCircle } from 'lucide-react';

const MonthPicker = ({ value, onChange }) => (
  <input
    type="month"
    value={value}
    onChange={e => onChange(e.target.value)}
    className="fin-input h-10"
  />
);

const ProgressBar = ({ percent }) => {
  const clamped = Math.min(percent, 100);
  const color =
    percent >= 100 ? 'bg-rose-500' :
    percent >= 80  ? 'bg-amber-500' :
                     'bg-emerald-500';
  return (
    <div className="w-full h-2.5 overflow-hidden bg-slate-800 rounded-full border border-slate-700/50">
      <div className={`h-full rounded-full transition-all duration-700 ease-out ${color} shadow-[0_0_8px_rgba(0,0,0,0.3)]`} style={{ width: `${clamped}%` }} />
    </div>
  );
};

const Budgets = () => {
  const now = new Date();
  const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;

  const [monthYear, setMonthYear] = useState(currentMonth);
  const [summary, setSummary] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  // Add budget form
  const [formCatId, setFormCatId] = useState('');
  const [formLimit, setFormLimit] = useState('');
  const [formMsg, setFormMsg] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [sumRes, alertRes, catRes] = await Promise.all([
        axiosAuth.get(`/api/budgets/summary?month_year=${monthYear}`),
        axiosAuth.get(`/api/budgets/alerts?month_year=${monthYear}`),
        axiosAuth.get('/api/categories?type=EXPENSE'),
      ]);
      if (sumRes.data.success) setSummary(sumRes.data.data);
      if (alertRes.data.success) setAlerts(alertRes.data.alerts ?? []);
      if (catRes.data.success) setCategories(catRes.data.data);
    } catch (err) {
      console.error('Budgets fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, [monthYear]);

  const handleAddBudget = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFormMsg('');
    try {
      const res = await axiosAuth.post('/api/budgets', {
        category_id: parseInt(formCatId),
        monthly_limit: parseFloat(formLimit),
        month_year: monthYear,
      });
      if (res.data.success) {
        setFormMsg('Budget saved!');
        setFormCatId('');
        setFormLimit('');
        fetchAll();
      }
    } catch {
      setFormMsg('Error saving budget. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (budgetId) => {
    if (!window.confirm('Delete this budget?')) return;
    try {
      await axiosAuth.delete(`/api/budgets/${budgetId}`);
      fetchAll();
    } catch (err) {
      console.error('Delete error:', err);
    }
  };


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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Budgets</h1>
        <div className="w-48">
          <MonthPicker value={monthYear} onChange={setMonthYear} />
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-3">
          {alerts.map((a, i) => (
            <div key={i} className={`flex items-start gap-4 p-4 rounded-xl border ${a.percent_used >= 100 ? 'bg-rose-500/10 border-rose-500/30' : 'bg-amber-500/10 border-amber-500/30'}`}>
              <AlertTriangle size={20} className={a.percent_used >= 100 ? 'text-rose-500 mt-0.5 flex-shrink-0' : 'text-amber-500 mt-0.5 flex-shrink-0'} />
              <p className={`text-sm font-medium ${a.percent_used >= 100 ? 'text-rose-400' : 'text-amber-400'}`}>{a.alert}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Add Budget Form */}
        <div className="p-6 fin-card h-fit border-t-4 border-t-emerald-500">
          <div className="flex items-center mb-6">
            <div className="p-2 mr-3 bg-emerald-500/20 text-emerald-400 rounded-lg">
              <Plus size={20} />
            </div>
            <h2 className="text-lg font-semibold text-white">Set Budget</h2>
          </div>

          <form onSubmit={handleAddBudget} className="space-y-5">
            {formMsg && (
              <div className={`p-4 text-sm font-medium rounded-lg ${formMsg.includes('Error') ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                {formMsg}
              </div>
            )}

            <div>
              <label className="block mb-2 text-sm font-medium text-slate-300">Category</label>
              <select
                required
                value={formCatId}
                onChange={e => setFormCatId(e.target.value)}
                className="fin-input"
              >
                <option value="" className="bg-[#112240]">Select category...</option>
                {categories.map(c => (
                  <option key={c.category_id} value={c.category_id} className="bg-[#112240]">{c.category_name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block mb-2 text-sm font-medium text-slate-300">Monthly Limit ($)</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-500">$</span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  value={formLimit}
                  onChange={e => setFormLimit(e.target.value)}
                  className="fin-input pl-8"
                  placeholder="0.00"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="fin-button-emerald w-full py-3"
            >
              {isSubmitting ? 'Saving...' : 'Save Budget'}
            </button>
          </form>
        </div>

        {/* Budget Summary List */}
        <div className="lg:col-span-2 space-y-4">
          {summary.filter(row => row.budget_limit > 0).length === 0 && (
            <div className="p-12 text-center fin-card text-slate-400 border-dashed border-2 border-slate-700">
              <div className="flex flex-col items-center">
                <Target size={48} className="text-slate-600 mb-4 opacity-20" />
                <p>No budgets set for this month. Use the form to add one.</p>
              </div>
            </div>
          )}
          {summary.filter(row => row.budget_limit > 0).map((row, i) => (
            <div key={i} className="p-6 fin-card hover:border-slate-500 transition-colors">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`p-1.5 rounded-full ${row.percent_used >= 100 ? 'bg-rose-500/20 text-rose-500' : 'bg-emerald-500/20 text-emerald-500'}`}>
                    {row.percent_used >= 100 ? (
                      <AlertTriangle size={18} />
                    ) : (
                      <CheckCircle size={18} />
                    )}
                  </div>
                  <span className="font-semibold text-lg text-white">{row.category_name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="text-sm font-medium text-white">
                      ${Number(row.actual_spent).toFixed(2)}
                    </span>
                    <span className="text-sm text-slate-500 mx-1">/</span>
                    <span className="text-sm text-slate-400">
                      ${Number(row.budget_limit).toFixed(2)}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDelete(row.budget_id)}
                    className="p-2 text-slate-500 rounded-lg hover:text-rose-500 hover:bg-rose-500/10 transition-all"
                    title="Delete budget"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
              <ProgressBar percent={row.percent_used} />
              <div className="flex justify-between mt-3 text-sm">
                <span className="text-slate-400 font-medium">{row.percent_used}% used</span>
                <span className={`font-semibold ${row.remaining < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {row.remaining < 0 ? `${Math.abs(Number(row.remaining)).toFixed(2)} over limit` : `$${Number(row.remaining).toFixed(2)} remaining`}
                </span>
              </div>
            </div>
          ))}

          {/* Categories with no budget */}
          {summary.filter(row => row.budget_limit === 0 && row.actual_spent > 0).length > 0 && (
            <div className="p-6 fin-card border-l-4 border-l-amber-500">
              <h3 className="mb-4 text-xs font-bold text-amber-500 uppercase tracking-widest">Unbudgeted Spending</h3>
              <div className="space-y-3">
                {summary.filter(row => row.budget_limit === 0 && row.actual_spent > 0).map((row, i) => (
                  <div key={i} className="flex justify-between items-center text-sm border-b border-slate-700/50 pb-2 last:border-0 last:pb-0">
                    <span className="text-slate-300 font-medium">{row.category_name}</span>
                    <span className="font-bold text-white bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">${Number(row.actual_spent).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Budgets;
