import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function Settings() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSave = (e) => {
    e.preventDefault();
    setLoading(true);
    // Simulate save
    setTimeout(() => {
      setLoading(false);
      setMessage('Settings saved successfully.');
      setTimeout(() => setMessage(''), 3000);
    }, 800);
  };

  const handleReset = async () => {
    if (window.confirm("Are you sure you want to reset the pipeline? This will clear all active application data.")) {
      try {
        await axios.post('/api/pipeline/reset');
        setMessage('Pipeline reset successfully.');
        setTimeout(() => setMessage(''), 3000);
      } catch (e) {
        alert("Failed to reset pipeline.");
      }
    }
  };

  return (
    <div>
      <div className="section-label">System Settings</div>

      {message && <div className="alert alert-success">{message}</div>}

      <div className="form-grid-2">
        <div className="card">
          <div className="card-title">Band Platform Connection</div>
          <div className="form-row" style={{ marginBottom: '1.2rem' }}>
            <label>Band Chat ID</label>
            <input type="text" autoComplete="new-password" defaultValue="chat_123abc" />
          </div>
          <div className="form-row" style={{ marginBottom: '1.2rem' }}>
            <label>Intake Agent Handle</label>
            <input type="text" autoComplete="off" defaultValue="@IntakeAgent" />
          </div>
          <div className="form-row" style={{ marginBottom: '1.2rem' }}>
            <label>Band Human API Key</label>
            <input type="password" autoComplete="new-password" defaultValue="••••••••••••••••" />
            <div style={{ fontSize: '0.7rem', color: 'var(--gray-400)', marginTop: '0.4rem' }}>
              Used to authenticate human-in-the-loop actions.
            </div>
          </div>
        </div>

        <div>
          <div className="card">
            <div className="card-title">Demo & Debugging</div>
            <div className="form-row checkbox-row" style={{ marginBottom: '1.2rem' }}>
              <input type="checkbox" id="setting_demo" defaultChecked />
              <label htmlFor="setting_demo">Enable Demo-safe Mode by Default</label>
            </div>
            <div className="form-row checkbox-row" style={{ marginBottom: '1.2rem' }}>
              <input type="checkbox" id="setting_logs" defaultChecked />
              <label htmlFor="setting_logs">Verbose Agent Logging</label>
            </div>
            
            <div className="divider"></div>
            
            <div className="form-row">
              <label>System Maintenance</label>
              <button className="btn-danger" onClick={handleReset} style={{ width: '100%', marginTop: '0.5rem' }}>
                Reset Pipeline State
              </button>
              <div style={{ fontSize: '0.7rem', color: 'var(--gray-400)', marginTop: '0.4rem', textAlign: 'center' }}>
                Clears all in-memory application data and stops polling.
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-title">Profile Preferences</div>
            <div className="form-row" style={{ marginBottom: '1.2rem' }}>
              <label>Loan Officer Name</label>
              <input type="text" defaultValue="Loan Officer" />
            </div>
            <div className="form-row" style={{ marginBottom: '1.2rem' }}>
              <label>Approval Threshold</label>
              <select defaultValue="standard">
                <option value="strict">Strict (Requires 2+ Approvals)</option>
                <option value="standard">Standard (Agent + Officer)</option>
                <option value="auto">Auto-Approve Low Risk</option>
              </select>
            </div>
            <button className="btn-teal" onClick={handleSave} disabled={loading} style={{ width: '100%' }}>
              {loading ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
