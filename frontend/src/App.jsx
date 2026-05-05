import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import TopNavbar from './components/TopNavbar';
import Dashboard from './components/Dashboard';
import Transactions from './components/Transactions';
import Budgets from './components/Budgets';
import Analytics from './components/Analytics';
import Chatbot from './components/Chatbot';
import Settings from './components/Settings';
import SignIn from './components/SignIn';
import SignUp from './components/SignUp';

function AppLayout({ children }) {
  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[#0a1628] text-slate-100 font-sans">
      <TopNavbar />
      <div className="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
        <main className="w-full px-6 py-8 mx-auto xl:px-8 max-w-7xl">
          {children}
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public auth routes — no navbar */}
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />

          {/* Protected routes — wrapped in AppLayout with navbar */}
          <Route path="/" element={
            <ProtectedRoute>
              <AppLayout><Dashboard /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/transactions" element={
            <ProtectedRoute>
              <AppLayout><Transactions /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/budgets" element={
            <ProtectedRoute>
              <AppLayout><Budgets /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/analytics" element={
            <ProtectedRoute>
              <AppLayout><Analytics /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/chatbot" element={
            <ProtectedRoute>
              <AppLayout><Chatbot /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute>
              <AppLayout><Settings /></AppLayout>
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
