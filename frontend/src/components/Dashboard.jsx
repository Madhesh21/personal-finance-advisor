import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  Wallet, 
  Target, 
  Sparkles, 
  PieChart, 
  ShieldCheck, 
  Zap,
  TrendingUp,
  ChevronRight
} from 'lucide-react';

const Dashboard = () => {
  const features = [
    {
      title: "Smart Tracking",
      description: "Effortlessly log and categorize your transactions with AI-powered suggestions.",
      icon: <Wallet className="text-emerald-400" size={24} />,
      link: "/transactions",
      color: "border-l-emerald-500"
    },
    {
      title: "Budget Mastery",
      description: "Set monthly limits and get real-time alerts before you overspend.",
      icon: <Target className="text-amber-400" size={24} />,
      link: "/budgets",
      color: "border-l-amber-500"
    },
    {
      title: "AI Advisor",
      description: "Receive personalized financial tips based on your spending habits.",
      icon: <Sparkles className="text-purple-400" size={24} />,
      link: "/chatbot",
      color: "border-l-purple-500"
    },
    {
      title: "Deep Analytics",
      description: "Visualize your financial health with beautiful, interactive charts.",
      icon: <PieChart className="text-blue-400" size={24} />,
      link: "/analytics",
      color: "border-l-blue-500"
    }
  ];

  return (
    <div className="flex flex-col space-y-16 pb-20 animate-fade-in">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-8">
        {/* Glow Effects */}
        <div className="absolute top-0 -left-20 w-72 h-72 bg-emerald-500/10 rounded-full blur-[120px] animate-pulse"></div>
        <div className="absolute bottom-0 -right-20 w-96 h-96 bg-amber-500/10 rounded-full blur-[120px] animate-pulse [animation-delay:1s]"></div>

        <div className="relative text-center max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-4 animate-slide-up">
            <Zap size={14} />
            <span>AI-POWERED FINANCIAL FREEDOM</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-white animate-slide-up [animation-delay:0.1s]">
            Take Control of Your <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-500">Financial Future</span>
          </h1>
          
          <p className="text-lg text-slate-400 leading-relaxed max-w-2xl mx-auto animate-slide-up [animation-delay:0.2s]">
            FinVerde combines advanced analytics with intelligent insights to help you track spending, 
            master budgets, and grow your wealth effortlessly.
          </p>

          <div className="flex flex-wrap justify-center gap-4 pt-6 animate-slide-up [animation-delay:0.3s]">
            <Link 
              to="/transactions" 
              className="px-8 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:scale-105 flex items-center group"
            >
              Get Started
              <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" size={20} />
            </Link>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="animate-slide-up [animation-delay:0.4s]">
        <div className="flex items-center justify-between mb-10">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Powerful Features</h2>
            <p className="text-slate-400">Everything you need to manage your money efficiently.</p>
          </div>
          <div className="hidden md:flex space-x-2">
            <div className="w-10 h-10 rounded-full border border-slate-700 flex items-center justify-center text-slate-500">
              <ShieldCheck size={20} />
            </div>
            <div className="w-10 h-10 rounded-full border border-slate-700 flex items-center justify-center text-slate-500">
              <TrendingUp size={20} />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Link 
              key={index} 
              to={feature.link}
              className={`group p-6 bg-[#112240] border border-slate-700/50 border-l-4 ${feature.color} rounded-xl transition-all hover:translate-y-[-8px] hover:shadow-[0_10px_30px_rgba(0,0,0,0.3)] hover:border-slate-600`}
            >
              <div className="p-3 bg-[#0a1628] rounded-lg w-fit mb-4 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              <h3 className="text-lg font-bold text-white mb-2 flex items-center">
                {feature.title}
                <ChevronRight className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity" size={16} />
              </h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                {feature.description}
              </p>
            </Link>
          ))}
        </div>
      </section>

      {/* Social Proof / Stats placeholder */}
      <section className="p-8 rounded-3xl bg-gradient-to-br from-emerald-900/20 to-teal-900/10 border border-emerald-500/20 animate-slide-up [animation-delay:0.5s]">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div className="space-y-1">
            <div className="text-3xl font-bold text-emerald-400">100%</div>
            <div className="text-sm text-slate-400 uppercase tracking-wider">Secure Data</div>
          </div>
          <div className="space-y-1 border-y md:border-y-0 md:border-x border-slate-700/50 py-6 md:py-0">
            <div className="text-3xl font-bold text-amber-400">Real-time</div>
            <div className="text-sm text-slate-400 uppercase tracking-wider">Syncing</div>
          </div>
          <div className="space-y-1">
            <div className="text-3xl font-bold text-purple-400">AI-First</div>
            <div className="text-sm text-slate-400 uppercase tracking-wider">Cloud Engine</div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
