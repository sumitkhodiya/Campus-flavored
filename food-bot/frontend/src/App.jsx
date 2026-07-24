import React, { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import VendorDashboard from './pages/VendorDashboard';
import AdminDashboard from './pages/AdminDashboard';
import { LogoIcon } from './icons';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [userData, setUserData] = useState(() => {
    const saved = localStorage.getItem('user_data');
    return saved ? JSON.parse(saved) : null;
  });

  const handleLoginSuccess = (loginResponse) => {
    setToken(loginResponse.access_token);
    setUserData({ role: loginResponse.role, stall_id: loginResponse.stall_id });
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_data');
    setToken(null);
    setUserData(null);
  };

  if (!token || !userData) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div>
      <div className="top-announcement">To check your event QR attendance, click here to view the details.</div>
      {/* Navbar Header */}
      <nav className="navbar">
        <div className="brand">
          <LogoIcon size={36} />
          <span>Campus Flavored</span>
          <span className="brand-badge">{userData.role}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Logged in as <strong>{userData.role.toUpperCase()}</strong>
            {userData.stall_id ? ` (Stall #${userData.stall_id})` : ''}
          </span>
          <button className="btn btn-outline" onClick={handleLogout}>
            Sign Out
          </button>
        </div>
      </nav>

      {/* Main Content Body */}
      <main className="container">
        {userData.role === 'admin' ? (
          <AdminDashboard />
        ) : (
          <VendorDashboard />
        )}
      </main>
    </div>
  );
}
