import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Sparkles, RefreshCw, ChevronDown } from 'lucide-react';

// ── Suggestion chips ──────────────────────────────────────────────────────────
const SUGGESTIONS = [
  { label: '💸 Where did I spend most?',     text: 'Where did I spend most this month?' },
  { label: '📊 Show expense breakdown',       text: 'Show me a breakdown of all my expenses' },
  { label: '💰 What was my income?',          text: 'What was my total income this month?' },
  { label: '📈 What is my savings rate?',     text: 'What is my savings rate and how can I improve it?' },
  { label: '⚖️ Income vs Expenses',           text: 'How do my income and expenses compare?' },
  { label: '🎯 Am I over budget?',            text: 'Am I over budget in any category?' },
  { label: '📅 Spending trend',               text: 'What is my spending trend over the last few months?' },
  { label: '💡 How can I save more?',         text: 'How can I save more money this month?' },
];

// ── Simple markdown renderer ──────────────────────────────────────────────────
// Converts bold (**text**), bullet lines (• or -), and newlines to JSX.
const RenderMessage = ({ text }) => {
  const lines = text.split('\n');

  return (
    <div className="space-y-1">
      {lines.map((line, i) => {
        if (!line.trim()) return <div key={i} className="h-1" />;

        // Bold segments: **text**
        const parts = line.split(/(\*\*[^*]+\*\*)/g);
        const rendered = parts.map((part, j) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={j} className="font-semibold text-white">{part.slice(2, -2)}</strong>;
          }
          return <span key={j}>{part}</span>;
        });

        // Bullet lines
        const isBullet = line.trim().startsWith('•') || line.trim().startsWith('-') || line.trim().startsWith('*');
        if (isBullet) {
          return (
            <div key={i} className="flex gap-2">
              <span className="text-emerald-400 mt-0.5 flex-shrink-0">•</span>
              <span>{rendered}</span>
            </div>
          );
        }

        // Heading lines (## or #)
        if (line.trim().startsWith('##') || line.trim().startsWith('#')) {
          const headingText = line.replace(/^#+\s*/, '');
          return (
            <p key={i} className="font-semibold text-emerald-300 text-sm uppercase tracking-wide mt-2">
              {headingText}
            </p>
          );
        }

        return <p key={i}>{rendered}</p>;
      })}
    </div>
  );
};

// ── Month selector ────────────────────────────────────────────────────────────
const getMonthOptions = () => {
  const options = [];
  const now = new Date();
  for (let i = 0; i < 6; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    const label = d.toLocaleString('default', { month: 'long', year: 'numeric' });
    options.push({ value, label });
  }
  return options;
};

// ── Main Chatbot component ────────────────────────────────────────────────────
const Chatbot = () => {
  const monthOptions = getMonthOptions();
  const [selectedMonth, setSelectedMonth] = useState(monthOptions[0].value);
  const [showMonthPicker, setShowMonthPicker] = useState(false);

  const [messages, setMessages] = useState([
    {
      role: 'bot',
      text: "Hi! I'm **FinVerde**, your AI Financial Advisor 👋\n\nI have access to your real transaction data and can answer questions like:\n• Where did I spend the most?\n• What's my savings rate?\n• Am I over budget anywhere?\n• How can I reduce my expenses?\n\nAsk me anything about your finances!",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const inputRef  = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const selectedMonthLabel = monthOptions.find(o => o.value === selectedMonth)?.label || selectedMonth;

  const sendMessage = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;

    const userMsg = { role: 'user', text: msg };
    const updatedMessages = [...messages, userMsg];

    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    try {
      // Send last 10 messages as history (excluding the one we're sending now)
      const history = messages.slice(-10);

      const res = await axios.post('/api/chat', {
        message:    msg,
        month_year: selectedMonth,
        history,
      });

      if (res.data.success) {
        setMessages(prev => [...prev, { role: 'bot', text: res.data.response }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'bot',
          text: `⚠️ ${res.data.error || 'Something went wrong. Please try again.'}`,
        }]);
      }
    } catch (err) {
      const errMsg = err.response?.data?.error || err.message;
      setMessages(prev => [...prev, {
        role: 'bot',
        text: `⚠️ ${errMsg || 'Could not connect to the server. Please make sure the backend is running.'}`,
      }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([{
      role: 'bot',
      text: "Chat cleared! I still have access to your financial data. Ask me anything 👇",
    }]);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-160px)]">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-emerald-500/20 rounded-2xl text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
            <Sparkles size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">FinVerde AI Advisor</h1>
            <p className="text-sm text-slate-400">Powered by Groq · Llama 3.3 70B</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Month picker */}
          <div className="relative">
            <button
              id="month-picker-btn"
              onClick={() => setShowMonthPicker(p => !p)}
              className="flex items-center gap-2 px-3 py-2 text-xs font-semibold text-slate-300 bg-slate-800/70 border border-slate-700/50 rounded-xl hover:border-emerald-500/40 transition-all"
            >
              📅 {selectedMonthLabel}
              <ChevronDown size={12} className={`transition-transform ${showMonthPicker ? 'rotate-180' : ''}`} />
            </button>
            {showMonthPicker && (
              <div className="absolute right-0 mt-2 w-48 bg-[#112240] border border-slate-700/50 rounded-xl shadow-2xl z-50 overflow-hidden">
                {monthOptions.map(opt => (
                  <button
                    key={opt.value}
                    id={`month-opt-${opt.value}`}
                    onClick={() => { setSelectedMonth(opt.value); setShowMonthPicker(false); }}
                    className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${
                      opt.value === selectedMonth
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : 'text-slate-300 hover:bg-slate-700/50'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Clear chat */}
          <button
            id="clear-chat-btn"
            onClick={clearChat}
            title="Clear chat"
            className="p-2 text-slate-400 hover:text-white bg-slate-800/70 border border-slate-700/50 rounded-xl hover:border-slate-600 transition-all"
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* ── Chat window ──────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-6 space-y-5 fin-card bg-[#0a1628]/50 border-slate-800/50 mb-4 shadow-inner">
        {messages.map((msg, i) => (
          <div key={i} className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>

            {/* Avatar */}
            <div className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center border shadow-lg ${
              msg.role === 'bot'
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30 shadow-emerald-500/10'
                : 'bg-amber-500/20 text-amber-400 border-amber-500/30 shadow-amber-500/10'
            }`}>
              {msg.role === 'bot' ? <Bot size={18} /> : <User size={18} />}
            </div>

            {/* Bubble */}
            <div className={`max-w-[82%] px-5 py-3.5 rounded-2xl text-[14.5px] leading-relaxed shadow-lg ${
              msg.role === 'bot'
                ? 'bg-[#112240] text-slate-200 border border-slate-700/50 rounded-tl-none'
                : 'bg-gradient-to-br from-amber-500 to-amber-600 text-[#0a1628] font-medium rounded-tr-none shadow-amber-500/10'
            }`}>
              {msg.role === 'bot'
                ? <RenderMessage text={msg.text} />
                : <span>{msg.text}</span>
              }
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shadow-lg shadow-emerald-500/10">
              <Bot size={18} />
            </div>
            <div className="px-5 py-4 bg-[#112240] rounded-2xl rounded-tl-none border border-slate-700/50 shadow-lg">
              <div className="flex gap-1.5 items-center h-4">
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* ── Suggestion chips ──────────────────────────────────────────────────── */}
      <div className="flex flex-wrap gap-2 mb-3">
        {SUGGESTIONS.map((s, i) => (
          <button
            key={i}
            id={`chip-${i}`}
            onClick={() => sendMessage(s.text)}
            disabled={loading}
            className="px-3 py-1.5 text-xs font-medium text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 rounded-full hover:bg-emerald-500/20 hover:border-emerald-500/50 transition-all disabled:opacity-40 whitespace-nowrap"
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* ── Input area ──────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-3 p-2 pl-5 bg-[#112240] rounded-2xl border border-slate-700/50 shadow-xl focus-within:border-emerald-500/50 transition-colors">
        <input
          ref={inputRef}
          id="chat-input"
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your finances…"
          disabled={loading}
          className="flex-1 bg-transparent text-[15px] text-white placeholder-slate-500 focus:outline-none py-3"
        />
        <button
          id="send-btn"
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          className="p-3 bg-emerald-600 text-white rounded-xl hover:bg-emerald-500 transition-all shadow-lg active:scale-95 disabled:opacity-30 disabled:grayscale"
        >
          <Send size={20} />
        </button>
      </div>

      {/* Context label */}
      <p className="text-center text-xs text-slate-600 mt-2">
        Analyzing data for <span className="text-slate-500">{selectedMonthLabel}</span>
      </p>
    </div>
  );
};

export default Chatbot;
