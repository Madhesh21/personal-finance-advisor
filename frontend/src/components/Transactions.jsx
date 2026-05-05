import React, { useState, useEffect, useRef } from 'react';
import axiosAuth from '../utils/axiosAuth';
import { Plus, Receipt, Upload, Download, CheckCircle, XCircle, FileText } from 'lucide-react';

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  // Manual form state
  const [amount, setAmount] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [description, setDescription] = useState('');
  const [transactionDate, setTransactionDate] = useState(new Date().toISOString().split('T')[0]);
  const [type, setType] = useState('EXPENSE');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  // CSV upload state
  const [csvFile, setCsvFile] = useState(null);
  const [csvUploading, setCsvUploading] = useState(false);
  const [csvResult, setCsvResult] = useState(null);
  const fileInputRef = useRef(null);

  // Active tab
  const [activeTab, setActiveTab] = useState('manual'); // 'manual' | 'csv'

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [txRes, catRes] = await Promise.all([
        axiosAuth.get('/api/transactions'),
        axiosAuth.get('/api/categories'),
      ]);
      if (txRes.data.success) setTransactions(txRes.data.data);
      if (catRes.data.success) setCategories(catRes.data.data);
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage('');
    try {
      const res = await axiosAuth.post('/api/transactions', {
        amount: parseFloat(amount),
        category_id: parseInt(categoryId),
        description,
        transaction_date: transactionDate,
        transaction_type: type,
      });
      if (res.data.success) {
        setMessage('Transaction added successfully!');
        setAmount('');
        setDescription('');
        fetchData();
      }
    } catch {
      setMessage('Error adding transaction. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCsvUpload = async (e) => {
    e.preventDefault();
    if (!csvFile) return;
    setCsvUploading(true);
    setCsvResult(null);
    const formData = new FormData();
    formData.append('file', csvFile);
    try {
      const res = await axiosAuth.post('/api/upload/csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setCsvResult(res.data);
      if (res.data.success) {
        setCsvFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
        fetchData();
      }
    } catch (err) {
      setCsvResult(err.response?.data || { success: false, error: 'Upload failed. Please try again.' });
    } finally {
      setCsvUploading(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const res = await axiosAuth.get('/api/upload/template', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = 'transactions_template.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      alert('Failed to download template.');
    }
  };

  const filteredCategories = categories.filter(c => c.category_type === type);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white tracking-tight">Transactions</h1>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Panel: Add Record */}
        <div className="lg:col-span-1 space-y-4">

          {/* Tab Switcher */}
          <div className="flex p-1 gap-1 fin-card border-none bg-slate-900/50">
            <button
              onClick={() => setActiveTab('manual')}
              className={`flex-1 flex items-center justify-center gap-2 py-2 text-sm font-bold rounded-lg transition-all ${activeTab === 'manual' ? 'bg-emerald-500 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
            >
              <Plus size={16} /> Manual
            </button>
            <button
              onClick={() => setActiveTab('csv')}
              className={`flex-1 flex items-center justify-center gap-2 py-2 text-sm font-bold rounded-lg transition-all ${activeTab === 'csv' ? 'bg-emerald-500 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
            >
              <Upload size={16} /> CSV Upload
            </button>
          </div>

          {/* Manual Form */}
          {activeTab === 'manual' && (
            <div className="p-6 fin-card border-t-4 border-t-emerald-500">
              <div className="flex items-center mb-6">
                <div className="p-2 mr-3 bg-emerald-500/20 text-emerald-400 rounded-lg">
                  <Plus size={20} />
                </div>
                <h2 className="text-lg font-semibold text-white">Add Record</h2>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                {message && (
                  <div className={`flex items-center gap-3 p-4 text-sm font-medium rounded-lg ${message.includes('Error') ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                    {message.includes('Error') ? <XCircle size={18} /> : <CheckCircle size={18} />}
                    {message}
                  </div>
                )}

                {/* Income / Expense Toggle */}
                <div className="flex p-1 gap-1 bg-slate-900/50 rounded-lg border border-slate-800">
                  {['EXPENSE', 'INCOME'].map(t => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => { setType(t); setCategoryId(''); }}
                      className={`flex-1 py-1.5 text-xs font-bold rounded transition-all uppercase tracking-wider ${type === t ? 'bg-[#1e293b] text-white shadow-sm ring-1 ring-slate-700' : 'text-slate-500 hover:text-slate-400'}`}
                    >
                      {t}
                    </button>
                  ))}
                </div>

                <div>
                  <label className="block mb-1.5 text-sm font-medium text-slate-300">Amount</label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-4 text-emerald-500 font-bold">$</span>
                    <input type="number" step="0.01" required value={amount} onChange={e => setAmount(e.target.value)}
                      className="fin-input pl-8" placeholder="0.00" />
                  </div>
                </div>

                <div>
                  <label className="block mb-1.5 text-sm font-medium text-slate-300">Category</label>
                  <select required value={categoryId} onChange={e => setCategoryId(e.target.value)}
                    className="fin-input">
                    <option value="" className="bg-[#112240]">Select category...</option>
                    {filteredCategories.map(cat => (
                      <option key={cat.category_id} value={cat.category_id} className="bg-[#112240]">{cat.category_name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block mb-1.5 text-sm font-medium text-slate-300">Date</label>
                  <input type="date" required value={transactionDate} onChange={e => setTransactionDate(e.target.value)}
                    className="fin-input" />
                </div>

                <div>
                  <label className="block mb-1.5 text-sm font-medium text-slate-300">Description</label>
                  <input type="text" value={description} onChange={e => setDescription(e.target.value)}
                    className="fin-input" placeholder="Optional notes" />
                </div>

                <button type="submit" disabled={isSubmitting}
                  className="fin-button-emerald w-full py-3 mt-2">
                  {isSubmitting ? 'Saving...' : 'Save Transaction'}
                </button>
              </form>
            </div>
          )}

          {/* CSV Upload Panel */}
          {activeTab === 'csv' && (
            <div className="p-6 fin-card border-t-4 border-t-amber-500 space-y-6">
              <div className="flex items-center">
                <div className="p-2 mr-3 bg-amber-500/20 text-amber-400 rounded-lg">
                  <Upload size={20} />
                </div>
                <h2 className="text-lg font-semibold text-white">Import Records</h2>
              </div>

              <p className="text-xs text-slate-400 leading-relaxed">
                Import bulk data using a CSV file. Order: <code className="text-emerald-400">date, amount, category, description, type</code>.
              </p>

              <button
                onClick={handleDownloadTemplate}
                className="fin-button-outline w-full flex items-center justify-center gap-2 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10"
              >
                <Download size={16} /> Download Template
              </button>

              <form onSubmit={handleCsvUpload} className="space-y-5">
                <label className="flex flex-col items-center justify-center w-full h-36 border-2 border-dashed rounded-xl cursor-pointer transition-all border-slate-700 hover:border-emerald-500/50 bg-[#0a1628]/30 hover:bg-emerald-500/5 group">
                  <FileText size={32} className="mb-3 text-slate-600 group-hover:text-emerald-500/70 transition-colors" />
                  <span className="text-sm text-slate-400 group-hover:text-slate-200 transition-colors">
                    {csvFile ? csvFile.name : 'Choose CSV file'}
                  </span>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    className="hidden"
                    onChange={e => { setCsvFile(e.target.files[0] || null); setCsvResult(null); }}
                  />
                </label>

                {csvResult && (
                  <div className={`p-4 rounded-xl text-sm space-y-2 border ${csvResult.success ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-rose-500/10 border-rose-500/30'}`}>
                    <div className={`flex items-center gap-2 font-bold ${csvResult.success ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {csvResult.success ? <CheckCircle size={18} /> : <XCircle size={18} />}
                      {csvResult.message || csvResult.error}
                    </div>
                    {csvResult.success && (
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <span className="text-emerald-500">✓ Inserted: {csvResult.inserted}</span>
                        {csvResult.skipped > 0 && <span className="text-amber-500">⚠ Skipped: {csvResult.skipped}</span>}
                      </div>
                    )}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={!csvFile || csvUploading}
                  className="fin-button-gold w-full py-3"
                >
                  {csvUploading ? 'Uploading...' : 'Import Now'}
                </button>
              </form>
            </div>
          )}
        </div>

        {/* Right Panel: Transaction History */}
        <div className="p-6 lg:col-span-2 fin-card">
          <div className="flex items-center mb-6">
            <div className="p-2 mr-3 bg-slate-800 text-slate-400 rounded-lg">
              <Receipt size={22} />
            </div>
            <h2 className="text-lg font-semibold text-white">Transaction Logs</h2>
          </div>

          <div className="overflow-hidden rounded-xl border border-slate-800 shadow-2xl">
            {loading ? (
              <div className="py-20 text-center">
                <div className="flex justify-center space-x-2">
                  <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-bounce"></div>
                  <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                  <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.5s]"></div>
                </div>
              </div>
            ) : transactions.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead className="bg-[#0a1628]/80 text-slate-500 border-b border-slate-800">
                    <tr>
                      {['Date', 'Description', 'Category', 'Amount'].map(h => (
                        <th key={h} className={`px-5 py-4 text-[11px] font-bold uppercase tracking-widest ${h === 'Amount' ? 'text-right' : ''}`}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {transactions.slice(0, 20).map(tx => (
                      <tr key={tx.transaction_id} className="hover:bg-emerald-500/5 transition-colors group">
                        <td className="px-5 py-4 text-xs text-slate-400 whitespace-nowrap font-medium">
                          {new Date(tx.transaction_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                        </td>
                        <td className="px-5 py-4 text-sm font-semibold text-slate-200 max-w-[200px] truncate group-hover:text-white">
                          {tx.description || 'General Transaction'}
                        </td>
                        <td className="px-5 py-4">
                          <span className={`fin-badge-${tx.transaction_type === 'EXPENSE' ? 'rose' : 'emerald'} whitespace-nowrap`}>
                            {tx.category_name}
                          </span>
                        </td>
                        <td className={`px-5 py-4 text-sm font-bold text-right whitespace-nowrap ${tx.transaction_type === 'EXPENSE' ? 'text-rose-400' : 'text-emerald-400'}`}>
                          {tx.transaction_type === 'EXPENSE' ? '-' : '+'}${parseFloat(tx.amount).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-24 text-center">
                <Receipt size={40} className="mx-auto mb-4 text-slate-700 opacity-20" />
                <p className="text-slate-500 text-sm font-medium">Clear as a whistle. No digital footprints yet.</p>
              </div>
            )}
          </div>
          {transactions.length > 20 && (
            <p className="mt-4 text-center text-xs text-slate-600 font-medium">Showing latest 20 transactions</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Transactions;
