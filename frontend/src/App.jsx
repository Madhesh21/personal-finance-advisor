import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TopNavbar from './components/TopNavbar';
import Dashboard from './components/Dashboard';
import Transactions from './components/Transactions';
import Budgets from './components/Budgets';
import Analytics from './components/Analytics';
import Chatbot from './components/Chatbot';
import Settings from './components/Settings';

function App() {
  return (
    <Router>
      <div className="flex flex-col h-screen overflow-hidden bg-[#0a1628] text-slate-100 font-sans">
        <TopNavbar />

        <div className="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
          {/* Page Content */}
          <main className="w-full px-6 py-8 mx-auto xl:px-8 max-w-7xl">
            <Routes>
              <Route path="/"             element={<Dashboard />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/budgets"      element={<Budgets />} />
              <Route path="/analytics"    element={<Analytics />} />
              <Route path="/chatbot"      element={<Chatbot />} />
              <Route path="/settings"     element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
