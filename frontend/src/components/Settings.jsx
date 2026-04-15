import React, { useState } from 'react';
import axios from 'axios';
import { Settings as SettingsIcon, Tag, Plus, Info } from 'lucide-react';

const Settings = () => {
  // Add Category state
  const [catName, setCatName] = useState('');
  const [catType, setCatType] = useState('EXPENSE');
  const [catMsg, setCatMsg] = useState('');
  const [catSubmitting, setCatSubmitting] = useState(false);

  const handleAddCategory = async (e) => {
    e.preventDefault();
    setCatSubmitting(true);
    setCatMsg('');
    try {
      const res = await axios.post('/api/categories', {
        category_name: catName.trim(),
        category_type: catType,
      });
      if (res.data.success) {
        setCatMsg(`Category "${catName}" created successfully!`);
        setCatName('');
      } else {
        setCatMsg(res.data.error || 'Error creating category.');
      }
    } catch (err) {
      const errMsg = err.response?.data?.error || 'Error creating category. It may already exist.';
      setCatMsg(errMsg);
    } finally {
      setCatSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="p-3 bg-slate-800 text-slate-400 rounded-2xl">
          <SettingsIcon size={24} />
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Settings</h1>
      </div>

      {/* App Info */}
      <div className="p-6 fin-card border-t-4 border-t-emerald-500">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg">
            <Info size={18} />
          </div>
          <h2 className="text-lg font-bold text-white">Application Profile</h2>
        </div>
        <div className="space-y-1">
          {[
            ['App Name', 'FinVerde Personal Advisor'],
            ['Version', '2.0.0 (Redesign)'],
            ['Environment', 'Production (Local)'],
            ['Backend', 'Flask + Python 3.10'],
            ['Frontend', 'React 18 + Vite'],
            ['Analytics', 'SpaCy Hybrid NLP'],
            ['Database', 'MySQL 8.0'],
          ].map(([label, val]) => (
            <div key={label} className="flex justify-between py-3 border-b border-slate-800/50 last:border-0 group">
              <span className="text-slate-500 text-sm font-medium group-hover:text-slate-400 transition-colors">{label}</span>
              <span className="font-semibold text-slate-200 text-sm">{val}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Add Custom Category */}
      <div className="p-6 fin-card border-t-4 border-t-amber-500">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-amber-500/20 text-amber-400 rounded-lg">
            <Tag size={18} />
          </div>
          <h2 className="text-lg font-bold text-white">Category Manager</h2>
        </div>

        <form onSubmit={handleAddCategory} className="space-y-5">
          {catMsg && (
            <div className={`p-4 text-sm font-semibold rounded-lg border ${catMsg.toLowerCase().includes('error') || catMsg.toLowerCase().includes('exist') ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'}`}>
              {catMsg}
            </div>
          )}

          <div>
            <label className="block mb-2 text-sm font-medium text-slate-400 uppercase tracking-widest">Category Name</label>
            <input
              type="text"
              required
              value={catName}
              onChange={e => setCatName(e.target.value)}
              placeholder="e.g. Subscriptions, Gym, Travel..."
              className="fin-input"
            />
          </div>

          <div>
            <label className="block mb-2 text-sm font-medium text-slate-400 uppercase tracking-widest">Default Type</label>
            <div className="flex p-1 gap-1 bg-slate-900/50 rounded-xl border border-slate-800">
              {['EXPENSE', 'INCOME'].map(t => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setCatType(t)}
                  className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all uppercase tracking-widest ${catType === t ? 'bg-[#1e293b] text-white shadow-xl ring-1 ring-slate-700' : 'text-slate-500 hover:text-slate-400'}`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={catSubmitting}
            className="fin-button-gold w-full flex items-center justify-center gap-2 py-3 mt-2 shadow-amber-500/10"
          >
            <Plus size={18} />
            {catSubmitting ? 'Processing...' : 'Register Category'}
          </button>
        </form>
      </div>

      {/* CSV Format Reference */}
      <div className="p-6 fin-card bg-[#0a1628]/30">
        <h2 className="text-lg font-bold text-white mb-4">CSV Data Specification</h2>
        <div className="overflow-x-auto rounded-xl border border-slate-800 shadow-inner">
          <table className="w-full text-xs text-left">
            <thead className="bg-[#112240] text-slate-500 border-b border-slate-800">
              <tr>
                {['Column', 'Required', 'Format/Example'].map(h => (
                  <th key={h} className="px-4 py-3 font-bold uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {[
                ['date', 'YES', 'YYYY-MM-DD'],
                ['amount', 'YES', 'Decimal (e.g. 45.50)'],
                ['category', 'YES', 'String (matches existing)'],
                ['description', 'YES', 'Any text description'],
                ['type', 'AUTO', 'INCOME or EXPENSE'],
              ].map(([col, req, fmt]) => (
                <tr key={col} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3 font-mono text-emerald-400">{col}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-md font-bold text-[10px] ${req === 'YES' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-slate-700/50 text-slate-400 border border-slate-600/30'}`}>{req}</span>
                  </td>
                  <td className="px-4 py-3 text-slate-400 italic">{fmt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Settings;
