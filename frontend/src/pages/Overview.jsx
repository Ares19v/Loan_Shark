import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function Overview() {
  const navigate = useNavigate();
  const [state, setState] = useState({ pipeline_status: 'idle', application_id: null });

  useEffect(() => {
    axios.get('/api/state').then(res => setState(res.data)).catch(console.error);
  }, []);

  return (
    <div>
      <div className="section-label">Dashboard Overview</div>

      <div className="metrics-row" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <div className="metric-box">
          <div className="metric-label"><span style={{marginRight: '6px'}}>📝</span>Total Applications</div>
          <div className="metric-value">1,284</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--green)', marginTop: '0.4rem', fontWeight: '500' }}>↑ 12% this month</div>
        </div>
        <div className="metric-box">
          <div className="metric-label"><span style={{marginRight: '6px'}}>⚡</span>Active Pipeline</div>
          <div className="metric-value">{state.pipeline_status === 'running' ? '1' : '0'}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)', marginTop: '0.4rem' }}>Currently processing</div>
        </div>
        <div className="metric-box">
          <div className="metric-label"><span style={{marginRight: '6px'}}>⏱️</span>Avg Processing Time</div>
          <div className="metric-value">4.2m</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--green)', marginTop: '0.4rem', fontWeight: '500' }}>↓ 1.5m faster</div>
        </div>
        <div className="metric-box">
          <div className="metric-label"><span style={{marginRight: '6px'}}>✅</span>Approval Rate</div>
          <div className="metric-value">76.4%</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--red)', marginTop: '0.4rem', fontWeight: '500' }}>↓ 2.1% from last week</div>
        </div>
      </div>

      <div className="form-grid-2" style={{ marginTop: '1.5rem', gridTemplateColumns: '2fr 1fr' }}>
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.4rem' }}>
            <div className="card-title" style={{ marginBottom: 0 }}>Recent Pipeline Activity</div>
            <span className="btn-ghost" onClick={() => navigate('/pipeline')} style={{ fontSize: '0.8rem' }}>View All →</span>
          </div>
          
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Application ID</th>
                  <th>Status</th>
                  <th>Stage</th>
                  <th style={{ textAlign: 'right' }}>Date</th>
                </tr>
              </thead>
              <tbody>
                {state.application_id ? (
                  <tr>
                    <td className="bold">{state.application_id}</td>
                    <td className="status-running">Active</td>
                    <td>Agent Processing</td>
                    <td style={{ textAlign: 'right' }}>Today</td>
                  </tr>
                ) : null}
                <tr>
                  <td className="bold">APP-102938</td>
                  <td className="status-complete">Approved</td>
                  <td>Human Gate</td>
                  <td style={{ textAlign: 'right' }}>Yesterday</td>
                </tr>
                <tr>
                  <td className="bold">APP-847291</td>
                  <td className="status-failed">Rejected</td>
                  <td>Risk Assess</td>
                  <td style={{ textAlign: 'right' }}>Oct 12, 2026</td>
                </tr>
                <tr>
                  <td className="bold">APP-563829</td>
                  <td className="status-complete">Approved</td>
                  <td>Human Gate</td>
                  <td style={{ textAlign: 'right' }}>Oct 11, 2026</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Quick Actions</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <button 
              onClick={() => navigate('/applications')} 
              style={{ padding: '1rem', background: 'var(--gray-50)', border: '1px solid var(--gray-200)', borderRadius: '10px', textAlign: 'left', cursor: 'pointer', transition: 'all 0.2s' }}
              onMouseOver={(e) => { e.currentTarget.style.borderColor = 'var(--teal)'; e.currentTarget.style.background = '#fff'; }}
              onMouseOut={(e) => { e.currentTarget.style.borderColor = 'var(--gray-200)'; e.currentTarget.style.background = 'var(--gray-50)'; }}
            >
              <div style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--gray-900)', marginBottom: '0.2rem' }}>📝 New Application</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--gray-500)' }}>Submit a new loan request to the agent pipeline.</div>
            </button>
            
            <button 
              onClick={() => navigate('/pipeline')} 
              style={{ padding: '1rem', background: 'var(--gray-50)', border: '1px solid var(--gray-200)', borderRadius: '10px', textAlign: 'left', cursor: 'pointer', transition: 'all 0.2s' }}
              onMouseOver={(e) => { e.currentTarget.style.borderColor = 'var(--blue)'; e.currentTarget.style.background = '#fff'; }}
              onMouseOut={(e) => { e.currentTarget.style.borderColor = 'var(--gray-200)'; e.currentTarget.style.background = 'var(--gray-50)'; }}
            >
              <div style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--gray-900)', marginBottom: '0.2rem' }}>🤖 Pipeline Monitor</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--gray-500)' }}>Watch active agents processing loans in real-time.</div>
            </button>
            
            <button 
              onClick={() => navigate('/settings')} 
              style={{ padding: '1rem', background: 'var(--gray-50)', border: '1px solid var(--gray-200)', borderRadius: '10px', textAlign: 'left', cursor: 'pointer', transition: 'all 0.2s' }}
              onMouseOver={(e) => { e.currentTarget.style.borderColor = 'var(--orange)'; e.currentTarget.style.background = '#fff'; }}
              onMouseOut={(e) => { e.currentTarget.style.borderColor = 'var(--gray-200)'; e.currentTarget.style.background = 'var(--gray-50)'; }}
            >
              <div style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--gray-900)', marginBottom: '0.2rem' }}>⚙️ System Settings</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--gray-500)' }}>Configure Band SDK and AI agent behaviors.</div>
            </button>
          </div>
        </div>
      </div>

    </div>
  );
}
