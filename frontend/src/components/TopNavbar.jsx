import React, { useState, useRef, useEffect } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { Receipt, PieChart, Target, Settings, MessageSquare, LogOut, ChevronDown, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const TopNavbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const menuItems = [
    { title: 'Transactions', icon: <Receipt size={18} />,      path: '/transactions' },
    { title: 'Budgets',      icon: <Target size={18} />,        path: '/budgets' },
    { title: 'Analytics',   icon: <PieChart size={18} />,      path: '/analytics' },
    { title: 'AI Advisor',  icon: <MessageSquare size={18} />, path: '/chatbot' },
    { title: 'Settings',    icon: <Settings size={18} />,      path: '/settings' },
  ];

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/signin');
  };

  // Generate initials avatar from user name
  const initials = user?.name
    ? user.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
    : '?';

  return (
    <header className="sticky top-0 z-30 w-full bg-[#112240] border-b border-slate-700 shadow-md">
      <div className="flex items-center justify-between px-6 py-4 mx-auto max-w-7xl">

        {/* Logo */}
        <Link to="/" className="flex items-center">
          <div className="w-10 h-10 bg-emerald-600 rounded-xl shadow-lg flex items-center justify-center border border-emerald-500/30">
            <Target className="text-white w-6 h-6" />
          </div>
          <span className="ml-3 text-xl font-bold text-slate-100 tracking-wide">FinVerde</span>
        </Link>

        {/* Nav Tabs */}
        <nav className="flex space-x-2">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center px-4 py-2 text-sm font-medium rounded-full transition-all duration-200 ${
                  isActive
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.1)]'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                }`
              }
            >
              <div className="mr-2">{item.icon}</div>
              {item.title}
            </NavLink>
          ))}
        </nav>

        {/* User Avatar + Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            id="user-menu-button"
            onClick={() => setDropdownOpen(o => !o)}
            className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-slate-800 transition-colors"
          >
            {/* Initials avatar */}
            <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-white text-xs font-bold shadow-md border border-emerald-500/40">
              {initials}
            </div>
            <span className="text-sm font-medium text-slate-200 hidden md:block max-w-[100px] truncate">
              {user?.name?.split(' ')[0] ?? 'Account'}
            </span>
            <ChevronDown
              size={14}
              className={`text-slate-400 transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`}
            />
          </button>

          {/* Dropdown menu */}
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-52 bg-[#112240] border border-slate-700 rounded-xl shadow-xl overflow-hidden z-50 animate-fade-in">
              {/* User info header */}
              <div className="px-4 py-3 border-b border-slate-700/60">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-emerald-600 flex items-center justify-center text-white text-sm font-bold border border-emerald-500/40">
                    {initials}
                  </div>
                  <div className="overflow-hidden">
                    <p className="text-sm font-semibold text-slate-100 truncate">{user?.name}</p>
                    <p className="text-xs text-slate-400 truncate">{user?.email}</p>
                  </div>
                </div>
              </div>

              {/* Profile link */}
              <Link
                to="/settings"
                onClick={() => setDropdownOpen(false)}
                className="flex items-center gap-3 px-4 py-3 text-sm text-slate-300 hover:bg-slate-800 hover:text-slate-100 transition-colors"
              >
                <User size={15} className="text-slate-400" />
                Profile & Settings
              </Link>

              {/* Logout */}
              <button
                id="logout-button"
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 transition-colors border-t border-slate-700/60"
              >
                <LogOut size={15} />
                Sign out
              </button>
            </div>
          )}
        </div>

      </div>
    </header>
  );
};

export default TopNavbar;
