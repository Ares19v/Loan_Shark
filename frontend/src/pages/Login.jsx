import React, { useState } from 'react';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('User1');
  const [password, setPassword] = useState('password123');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username && password) {
      onLogin({ username });
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)' }}>
      <div className="card" style={{ width: '420px', padding: '3.5rem 2.8rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <div className="sidebar-logo" style={{ color: 'var(--gray-900)', borderBottom: 'none', padding: 0, animation: 'none' }}>
            LOAN<span style={{ color: 'var(--teal)' }}>shark</span>
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--gray-500)', marginTop: '0.5rem' }}>Agentic Financial Underwriting</div>
        </div>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.4rem' }}>
          <div>
            <label>Username</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} required />
          </div>
          <div>
            <label>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <button type="submit" className="btn-teal" style={{ marginTop: '0.8rem', width: '100%', padding: '0.75rem', fontSize: '0.9rem' }}>Login</button>
        </form>

        <div style={{ marginTop: '2.5rem', padding: '1.2rem', background: 'var(--gray-50)', borderRadius: '8px', fontSize: '0.82rem', color: 'var(--gray-600)', textAlign: 'center', border: '1px solid var(--gray-200)' }}>
          <span style={{ fontWeight: 600, color: 'var(--gray-800)' }}>Demo Credentials</span><br/><br/>
          Username: <strong>User1</strong><br/>
          Password: <strong>password123</strong>
        </div>
      </div>
    </div>
  );
}
