import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User, Phone, Target, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

function getStrength(pw) {
  if (!pw) return 0;
  let score = 0;
  if (pw.length >= 8)  score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score;
}

const strengthLabel = ['', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
const strengthColor = ['', '#ef4444', '#f97316', '#eab308', '#10b981', '#10b981'];

export default function SignUp() {
  const [form, setForm]         = useState({ name: '', email: '', phone: '', password: '', confirm: '' });
  const [showPw, setShowPw]     = useState(false);
  const [showCp, setShowCp]     = useState(false);
  const [errors, setErrors]     = useState([]);
  const [loading, setLoading]   = useState(false);

  const { login } = useAuth();
  const navigate  = useNavigate();

  const strength = getStrength(form.password);

  const handleChange = (e) =>
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const validate = () => {
    const errs = [];
    if (!form.name.trim()) errs.push('Full name is required');
    if (!form.email.trim() || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) errs.push('Valid email is required');
    if (form.password.length < 8) errs.push('Password must be at least 8 characters');
    if (form.password !== form.confirm) errs.push('Passwords do not match');
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (errs.length) { setErrors(errs); return; }
    setErrors([]);
    setLoading(true);
    try {
      const res  = await fetch('http://localhost:5000/api/auth/register', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          name: form.name, email: form.email,
          password: form.password, phone: form.phone,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || (data.errors && data.errors[0]) || 'Registration failed');
      login(data.token, data.user);
      navigate('/', { replace: true });
    } catch (err) {
      setErrors([err.message]);
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = (focused) => ({
    width: '100%', padding: '12px 14px 12px 40px',
    background: 'rgba(8,20,34,0.6)',
    border: `1px solid ${focused ? '#10b981' : '#1e3a5f'}`,
    borderRadius: 10, color: '#f1f5f9', fontSize: 14,
    outline: 'none', transition: 'border-color 0.2s',
    boxSizing: 'border-box',
  });

  return (
    <div style={styles.page}>
      <div style={{ ...styles.blob, top: '-60px', left: '-60px', background: 'radial-gradient(circle, rgba(16,185,129,0.12), transparent 70%)' }} />
      <div style={{ ...styles.blob, bottom: '-80px', right: '-40px', width: 480, height: 480, background: 'radial-gradient(circle, rgba(139,92,246,0.08), transparent 70%)' }} />

      <div style={styles.card}>
        {/* Logo */}
        <div style={styles.logoRow}>
          <div style={styles.logoIcon}><Target size={22} color="#fff" /></div>
          <span style={styles.logoText}>FinVerde</span>
        </div>

        <h1 style={styles.title}>Create your account</h1>
        <p style={styles.subtitle}>Start your journey to financial freedom</p>

        {errors.length > 0 && (
          <div style={styles.errorBox}>
            <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 2 }} />
            <div>
              {errors.map((e, i) => <div key={i}>{e}</div>)}
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} style={styles.form}>
          {/* Name */}
          <Field label="Full name" icon={<User size={16} style={styles.iIcon} />}>
            <input id="signup-name" name="name" type="text" required placeholder="John Doe"
              value={form.name} onChange={handleChange} style={inputStyle(false)}
              onFocus={e => e.target.style.borderColor = '#10b981'}
              onBlur={e  => e.target.style.borderColor = '#1e3a5f'} />
          </Field>

          {/* Email */}
          <Field label="Email address" icon={<Mail size={16} style={styles.iIcon} />}>
            <input id="signup-email" name="email" type="email" required placeholder="you@example.com"
              value={form.email} onChange={handleChange} style={inputStyle(false)}
              onFocus={e => e.target.style.borderColor = '#10b981'}
              onBlur={e  => e.target.style.borderColor = '#1e3a5f'} />
          </Field>

          {/* Phone (optional) */}
          <Field label="Phone number (optional)" icon={<Phone size={16} style={styles.iIcon} />}>
            <input id="signup-phone" name="phone" type="tel" placeholder="+1 234 567 8900"
              value={form.phone} onChange={handleChange} style={inputStyle(false)}
              onFocus={e => e.target.style.borderColor = '#10b981'}
              onBlur={e  => e.target.style.borderColor = '#1e3a5f'} />
          </Field>

          {/* Password */}
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Password</label>
            <div style={styles.inputWrapper}>
              <Lock size={16} style={styles.iIcon} />
              <input id="signup-password" name="password" type={showPw ? 'text' : 'password'}
                required placeholder="Min. 8 characters"
                value={form.password} onChange={handleChange}
                style={{ ...inputStyle(false), paddingRight: 44 }}
                onFocus={e => e.target.style.borderColor = '#10b981'}
                onBlur={e  => e.target.style.borderColor = '#1e3a5f'} />
              <button type="button" onClick={() => setShowPw(p => !p)} style={styles.eyeBtn} tabIndex={-1}>
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {/* Strength bar */}
            {form.password && (
              <div>
                <div style={styles.strengthTrack}>
                  {[1,2,3,4,5].map(i => (
                    <div key={i} style={{
                      ...styles.strengthSegment,
                      background: i <= strength ? strengthColor[strength] : '#1e293b',
                      transition: 'background 0.3s',
                    }} />
                  ))}
                </div>
                <span style={{ fontSize: 11, color: strengthColor[strength] }}>
                  {strengthLabel[strength]}
                </span>
              </div>
            )}
          </div>

          {/* Confirm Password */}
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Confirm password</label>
            <div style={styles.inputWrapper}>
              <Lock size={16} style={styles.iIcon} />
              <input id="signup-confirm" name="confirm" type={showCp ? 'text' : 'password'}
                required placeholder="Repeat your password"
                value={form.confirm} onChange={handleChange}
                style={{ ...inputStyle(false), paddingRight: 44 }}
                onFocus={e => e.target.style.borderColor = '#10b981'}
                onBlur={e  => e.target.style.borderColor = '#1e3a5f'} />
              <button type="button" onClick={() => setShowCp(p => !p)} style={styles.eyeBtn} tabIndex={-1}>
                {showCp ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {form.confirm && form.password === form.confirm && (
              <span style={{ fontSize: 11, color: '#10b981', display:'flex', gap: 4, alignItems:'center' }}>
                <CheckCircle2 size={12} /> Passwords match
              </span>
            )}
          </div>

          <button id="signup-submit" type="submit" disabled={loading}
            style={{ ...styles.submitBtn, opacity: loading ? 0.75 : 1 }}
            onMouseEnter={e => !loading && (e.target.style.background = '#059669')}
            onMouseLeave={e => (e.target.style.background = '#10b981')}>
            {loading
              ? <><Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> Creating account…</>
              : 'Create Account'}
          </button>
        </form>

        <p style={styles.switchText}>
          Already have an account?{' '}
          <Link to="/signin" style={styles.switchLink}>Sign in</Link>
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

function Field({ label, icon, children }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <label style={{ fontSize: 13, fontWeight: 500, color: '#94a3b8' }}>{label}</label>
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
        {icon}
        {children}
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
    background: 'linear-gradient(135deg, #060d1a 0%, #0a1628 50%, #081422 100%)',
    fontFamily: "'Inter', sans-serif", padding: '24px',
    position: 'relative', overflow: 'hidden',
  },
  blob: {
    position: 'absolute', width: 400, height: 400, borderRadius: '50%',
    filter: 'blur(80px)', pointerEvents: 'none',
  },
  card: {
    width: '100%', maxWidth: 440,
    background: 'rgba(17,34,64,0.85)',
    backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(30,90,120,0.35)', borderRadius: 20,
    padding: '36px 36px', boxShadow: '0 24px 64px rgba(0,0,0,0.5)',
    animation: 'fadeSlideUp 0.5s ease both',
  },
  logoRow: { display: 'flex', alignItems: 'center', marginBottom: 24 },
  logoIcon: {
    width: 40, height: 40, borderRadius: 12,
    background: 'linear-gradient(135deg, #10b981, #059669)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    boxShadow: '0 0 20px rgba(16,185,129,0.35)',
  },
  logoText: { marginLeft: 12, fontSize: 20, fontWeight: 700, color: '#f1f5f9', letterSpacing: '-0.3px' },
  title:    { fontSize: 24, fontWeight: 800, color: '#f1f5f9', margin: '0 0 6px', letterSpacing: '-0.5px' },
  subtitle: { fontSize: 14, color: '#64748b', margin: '0 0 24px' },
  errorBox: {
    display: 'flex', alignItems: 'flex-start', gap: 8,
    background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)',
    color: '#fca5a5', borderRadius: 10, padding: '10px 14px',
    fontSize: 13, marginBottom: 20,
  },
  form:        { display: 'flex', flexDirection: 'column', gap: 16 },
  fieldGroup:  { display: 'flex', flexDirection: 'column', gap: 6 },
  label:       { fontSize: 13, fontWeight: 500, color: '#94a3b8' },
  inputWrapper:{ position: 'relative', display: 'flex', alignItems: 'center' },
  iIcon:       { position: 'absolute', left: 14, color: '#475569', pointerEvents: 'none' },
  eyeBtn:      { position: 'absolute', right: 12, background: 'none', border: 'none', cursor: 'pointer', color: '#475569', display: 'flex', padding: 4 },
  strengthTrack:   { display: 'flex', gap: 4, marginTop: 6, marginBottom: 3 },
  strengthSegment: { flex: 1, height: 4, borderRadius: 2 },
  submitBtn: {
    marginTop: 4, padding: '13px',
    background: '#10b981', color: '#fff', border: 'none', borderRadius: 10,
    fontSize: 15, fontWeight: 700, cursor: 'pointer',
    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
    transition: 'background 0.2s',
    boxShadow: '0 0 20px rgba(16,185,129,0.3)',
  },
  switchText: { textAlign: 'center', color: '#64748b', fontSize: 13, marginTop: 20 },
  switchLink: { color: '#10b981', fontWeight: 600, textDecoration: 'none' },
};
