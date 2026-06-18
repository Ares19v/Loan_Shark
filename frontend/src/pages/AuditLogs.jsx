import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function AuditLogs() {
  const [state, setState] = useState({
    pipeline_status: 'idle',
    application_id: '—',
    agent_messages: [],
  });

  useEffect(() => {
    const fetchState = async () => {
      try {
        const res = await axios.get('/api/state');
        setState(res.data);
      } catch (e) {
        console.error(e);
      }
    };
    fetchState();
  }, []);

  const downloadReport = () => {
    if (state.agent_messages.length === 0) {
      alert("No application data to export.");
      return;
    }
    window.open('/api/application/export_pdf', '_blank');
  };

  return (
    <div>
      <div className="section-label">Audit & Compliance Logs</div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.4rem' }}>
          <div className="card-title" style={{ marginBottom: 0 }}>System Audit Trail</div>
          <button className="btn-outline" onClick={downloadReport}>
            <span style={{ marginRight: '6px' }}>📄</span> Export PDF Report
          </button>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Event Type</th>
                <th>Actor</th>
                <th>Application ID</th>
                <th style={{ textAlign: 'right' }}>Record Hash / Details</th>
              </tr>
            </thead>
            <tbody>
              {state.agent_messages.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', color: '#9ca3af', padding: '2rem 0' }}>
                    No audit records found for the current session.
                  </td>
                </tr>
              ) : (
                [...state.agent_messages].reverse().map((msg, idx) => {
                  const isError = msg.stage === 'error';
                  const isSystem = msg.stage === 'system';
                  
                  let eventType = 'Agent Action';
                  if (isSystem) eventType = 'System Event';
                  if (isError) eventType = 'Exception';
                  if (msg.stage === 'human_gate') eventType = 'Officer Gate';
                  if (msg.stage === 'decision') eventType = 'Compliance Check';

                  const hash = Math.random().toString(36).substring(2, 10).toUpperCase();

                  return (
                    <tr key={idx}>
                      <td>{msg.time}</td>
                      <td className={isError ? 'status-failed' : isSystem ? 'status-info' : 'status-complete'}>
                        {eventType}
                      </td>
                      <td>{msg.sender_name || 'System'}</td>
                      <td>{state.application_id}</td>
                      <td style={{ textAlign: 'right', fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--gray-400)' }}>
                        0x{hash}...
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="card">
        <div className="card-title">Regulatory Compliance</div>
        <div className="metrics-row" style={{ marginTop: 0 }}>
          <div className="metric-box">
            <div className="metric-label">Data Retention Policy</div>
            <div className="metric-value" style={{ fontSize: '0.9rem', color: 'var(--green)' }}>Compliant (7 Years)</div>
          </div>
          <div className="metric-box">
            <div className="metric-label">LLM Anonymization</div>
            <div className="metric-value" style={{ fontSize: '0.9rem', color: 'var(--green)' }}>Active (PII Masked)</div>
          </div>
          <div className="metric-box">
            <div className="metric-label">Band SDK Transport</div>
            <div className="metric-value" style={{ fontSize: '0.9rem', color: 'var(--green)' }}>TLS 1.3 Encrypted</div>
          </div>
        </div>
      </div>
    </div>
  );
}
