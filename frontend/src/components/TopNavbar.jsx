import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { Receipt, PieChart, Target, Settings, MessageSquare } from 'lucide-react';

const TopNavbar = () => {
  const menuItems = [
    { title: 'Transactions', icon: <Receipt size={18} />,         path: '/transactions' },
    { title: 'Budgets',      icon: <Target size={18} />,          path: '/budgets' },
    { title: 'Analytics',    icon: <PieChart size={18} />,        path: '/analytics' },
    { title: 'AI Advisor',   icon: <MessageSquare size={18} />,   path: '/chatbot' },
    { title: 'Settings',     icon: <Settings size={18} />,        path: '/settings' },
  ];

  return (
    <header className="sticky top-0 z-30 w-full bg-[#112240] border-b border-slate-700 shadow-md">
      <div className="flex items-center justify-between px-6 py-4 mx-auto max-w-7xl">
        {/* Logo - Clickable to go home */}
        <Link to="/" className="flex items-center">
          <div className="w-10 h-10 bg-emerald-600 rounded-xl shadow-lg flex items-center justify-center border border-emerald-500/30">
            <Target className="text-white w-6 h-6" />
          </div>
          <span className="ml-3 text-xl font-bold text-slate-100 tracking-wide">
            FinVerde
          </span>
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

        {/* Right side spacer to keep nav centered or balanced */}
        <div className="w-[120px] hidden md:block"></div>
      </div>
    </header>
  );
};

export default TopNavbar;
