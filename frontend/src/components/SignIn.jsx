import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, Target, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function SignIn() {
  const [form, setForm]       = useState({ email: '', password: '' });
  const [showPw, setShowPw]   = useState(false);
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);

  const { login }    = useAuth();
  const navigate     = useNavigate();
  const location     = useLocation();
  const redirectTo   = location.state?.from?.pathname || '/';

  const handleChange = (e) =>
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res  = await fetch('http://localhost:5000/api/auth/login', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Login failed');
      login(data.token, data.user);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      {/* Animated background blobs */}
      <div style={{ ...styles.blob, top: '-80px', left: '-80px', background: 'radial-gradient(circle, rgba(16,185,129,0.15), transparent 70%)' }} />
      <div style={{ ...styles.blob, bottom: '-100px', right: '-60px', width: 500, height: 500, background: 'radial-gradient(circle, rgba(245,158,11,0.1), transparent 70%)' }} />

      <div style={styles.card}>
        {/* Logo */}
        <div style={styles.logoRow}>
          <div style={styles.logoIcon}><Target size={22} color="#fff" /></div>
          <span style={styles.logoText}>FinVerde</span>
        </div>

        <h1 style={styles.title}>Welcome back</h1>
        <p style={styles.subtitle}>Sign in to manage your financial future</p>

        {error && (
          <div style={styles.errorBox}>
            <AlertCircle size={16} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={styles.form}>
          {/* Email */}
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Email address</label>
            <div style={styles.inputWrapper}>
              <Mail size={16} style={styles.inputIcon} />
              <input
                id="signin-email"
                name="email"
                type="email"
                autoComplete="email"
                required
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
                style={styles.input}
                onFocus={e => e.target.style.borderColor = '#10b981'}
                onBlur={e  => e.target.style.borderColor = '#1e3a5f'}
              />
            </div>
          </div>

          {/* Password */}
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Password</label>
            <div style={styles.inputWrapper}>
              <Lock size={16} style={styles.inputIcon} />
              <input
                id="signin-password"
                name="password"
                type={showPw ? 'text' : 'password'}
                autoComplete="current-password"
                required
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
                style={{ ...styles.input, paddingRight: 44 }}
                onFocus={e => e.target.style.borderColor = '#10b981'}
                onBlur={e  => e.target.style.borderColor = '#1e3a5f'}
              />
              <button
                type="button"
                onClick={() => setShowPw(p => !p)}
                style={styles.eyeBtn}
                tabIndex={-1}
              >
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button
            id="signin-submit"
            type="submit"
            disabled={loading}
            style={{ ...styles.submitBtn, opacity: loading ? 0.75 : 1 }}
            onMouseEnter={e => !loading && (e.target.style.background = '#059669')}
            onMouseLeave={e => (e.target.style.background = '#10b981')}
          >
            {loading
              ? <><Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> Signing in…</>
              : 'Sign In'}
          </button>
        </form>

        <p style={styles.switchText}>
          Don't have an account?{' '}
          <Link to="/signup" style={styles.switchLink}>Create one free</Link>
        </p>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(24px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #060d1a 0%, #0a1628 50%, #081422 100%)',
    fontFamily: "'Inter', sans-serif",
    padding: '24px',
    position: 'relative',
    overflow: 'hidden',
  },
  blob: {
    position: 'absolute',
    width: 400,
    height: 400,
    borderRadius: '50%',
    filter: 'blur(80px)',
    pointerEvents: 'none',
  },
  card: {
    width: '100%',
    maxWidth: 420,
    background: 'rgba(17,34,64,0.85)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(30,90,120,0.35)',
    borderRadius: 20,
    padding: '40px 36px',
    boxShadow: '0 24px 64px rgba(0,0,0,0.5)',
    animation: 'fadeSlideUp 0.5s ease both',
  },
  logoRow: {
    display: 'flex', alignItems: 'center', marginBottom: 28,
  },
  logoIcon: {
    width: 40, height: 40, borderRadius: 12,
    background: 'linear-gradient(135deg, #10b981, #059669)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    boxShadow: '0 0 20px rgba(16,185,129,0.35)',
  },
  logoText: {
    marginLeft: 12, fontSize: 20, fontWeight: 700,
    color: '#f1f5f9', letterSpacing: '-0.3px',
  },
  title: {
    fontSize: 26, fontWeight: 800, color: '#f1f5f9',
    margin: '0 0 6px', letterSpacing: '-0.5px',
  },
  subtitle: {
    fontSize: 14, color: '#64748b', margin: '0 0 28px',
  },
  errorBox: {
    display: 'flex', alignItems: 'center', gap: 8,
    background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)',
    color: '#fca5a5', borderRadius: 10, padding: '10px 14px',
    fontSize: 13, marginBottom: 20,
  },
  form: { display: 'flex', flexDirection: 'column', gap: 20 },
  fieldGroup: { display: 'flex', flexDirection: 'column', gap: 6 },
  label: { fontSize: 13, fontWeight: 500, color: '#94a3b8' },
  inputWrapper: { position: 'relative', display: 'flex', alignItems: 'center' },
  inputIcon: {
    position: 'absolute', left: 14, color: '#475569', pointerEvents: 'none',
  },
  input: {
    width: '100%', padding: '12px 14px 12px 40px',
    background: 'rgba(8,20,34,0.6)',
    border: '1px solid #1e3a5f',
    borderRadius: 10, color: '#f1f5f9', fontSize: 14,
    outline: 'none', transition: 'border-color 0.2s',
    boxSizing: 'border-box',
  },
  eyeBtn: {
    position: 'absolute', right: 12, background: 'none',
    border: 'none', cursor: 'pointer', color: '#475569',
    display: 'flex', padding: 4,
  },
  submitBtn: {
    marginTop: 6, padding: '13px',
    background: '#10b981', color: '#fff',
    border: 'none', borderRadius: 10,
    fontSize: 15, fontWeight: 700,
    cursor: 'pointer', display: 'flex',
    alignItems: 'center', justifyContent: 'center',
    gap: 8, transition: 'background 0.2s, transform 0.1s',
    boxShadow: '0 0 20px rgba(16,185,129,0.3)',
  },
  switchText: { textAlign: 'center', color: '#64748b', fontSize: 13, marginTop: 24 },
  switchLink: { color: '#10b981', fontWeight: 600, textDecoration: 'none' },
};
