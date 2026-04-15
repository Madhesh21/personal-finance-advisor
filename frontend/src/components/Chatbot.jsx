import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Sparkles } from 'lucide-react';

const SUGGESTIONS = [
  'Where did I spend most?',
  'How can I save more?',
  'What are my top expenses?',
  'How can I reduce my spending?',
];

const Chatbot = () => {
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      text: "Hi! I'm your AI Financial Advisor 👋. Ask me things like \"Where did I spend most?\" or \"How can I save more?\" and I'll analyze your data to help.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text) => {
    const msg = text || input.trim();
    if (!msg) return;

    setMessages(prev => [...prev, { role: 'user', text: msg }]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('/api/chat', { message: msg });
      if (res.data.success) {
        setMessages(prev => [...prev, { role: 'bot', text: res.data.response }]);
      } else {
        setMessages(prev => [...prev, { role: 'bot', text: `Sorry, I couldn't process that. ${res.data.error || ''}` }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: 'Something went wrong connecting to the server. Please make sure the backend is running.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-160px)]">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <div className="p-3 bg-emerald-500/20 rounded-2xl text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
          <Sparkles size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Financial Advisor</h1>
          <p className="text-sm text-slate-400">Personalized insights powered by FinVerde AI</p>
        </div>
      </div>

      {/* Chat Window */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 fin-card bg-[#0a1628]/50 border-slate-800/50 mb-4 shadow-inner">
        {messages.map((msg, i) => (
          <div key={i} className={`flex items-start gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            {/* Avatar */}
            <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center border ${
              msg.role === 'bot'
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
            }`}>
              {msg.role === 'bot' ? <Bot size={20} /> : <User size={20} />}
            </div>

            {/* Bubble */}
            <div className={`max-w-[80%] px-5 py-3.5 rounded-2xl text-[15px] leading-relaxed shadow-lg ${
              msg.role === 'bot'
                ? 'bg-[#112240] text-slate-100 border border-slate-700/50 rounded-tl-none'
                : 'bg-gradient-to-br from-amber-500 to-amber-600 text-[#0a1628] font-medium rounded-tr-none shadow-amber-500/10'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              <Bot size={20} />
            </div>
            <div className="px-5 py-4 bg-[#112240] rounded-2xl rounded-tl-none border border-slate-700/50">
              <div className="flex gap-1.5 items-center h-4">
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce shadow-emerald-500/50" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce shadow-emerald-500/50" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestion Chips */}
      <div className="flex flex-wrap gap-2 mb-4">
        {SUGGESTIONS.map((s, i) => (
          <button
            key={i}
            onClick={() => sendMessage(s)}
            disabled={loading}
            className="px-4 py-2 text-xs font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 rounded-full hover:bg-emerald-500/20 hover:border-emerald-500/50 transition-all disabled:opacity-50"
          >
            {s}
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div className="flex items-center gap-3 p-2 pl-5 bg-[#112240] rounded-2xl border border-slate-700/50 shadow-xl focus-within:border-emerald-500/50 transition-colors">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your finances..."
          disabled={loading}
          className="flex-1 bg-transparent text-[15px] text-white placeholder-slate-500 focus:outline-none py-3"
        />
        <button
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          className="p-3 bg-emerald-600 text-white rounded-xl hover:bg-emerald-500 transition-all shadow-lg active:scale-95 disabled:opacity-30 disabled:grayscale"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
