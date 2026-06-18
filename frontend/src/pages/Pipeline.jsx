import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function Pipeline() {
  const [state, setState] = useState({
    pipeline_status: 'idle',
    application_id: '—',
    agent_messages: [],
    applicant: {},
    demo_safe_mode: true
  });
  const [loading, setLoading] = useState(false);

  // Human Gate State
  const [officerName, setOfficerName] = useState('');
  const [overrideReason, setOverrideReason] = useState('');
  const [showOverride, setShowOverride] = useState(false);
  const [adjAmount, setAdjAmount] = useState(0);
  const [adjTenure, setAdjTenure] = useState(0);
  const [checks, setChecks] = useState({ kyc: false, afford: false, rbi: false });

  // Sync adj values
  useEffect(() => {
    if (state.loan_decision) {
      setAdjAmount(state.loan_decision.approved_amount || state.applicant?.loan_amount_raw || 0);
      setAdjTenure(state.loan_decision.approved_tenure_months || 0);
    }
  }, [state.loan_decision]);

  const handleApprove = async () => {
    await axios.post('/api/pipeline/officer-action', {
      action: 'approve', officer_name: officerName,
      adjusted_amount: adjAmount, adjusted_tenure: adjTenure
    });
    fetchState();
  };

  const handleReject = async () => {
    await axios.post('/api/pipeline/officer-action', {
      action: 'reject', officer_name: officerName,
      override_reason: overrideReason
    });
    setShowOverride(false);
    fetchState();
  };

  const fetchState = async () => {
    try {
      const res = await axios.get('/api/state');
      setState(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchState();
  }, []);

  const pollBand = async () => {
    if (state.pipeline_status !== 'running') return;
    try {
      setLoading(true);
      await axios.post('/api/pipeline/poll');
      await fetchState();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let interval;
    if (state.pipeline_status === 'running') {
      interval = setInterval(pollBand, 2000); // Poll every 2 seconds
    }
    return () => clearInterval(interval);
  }, [state.pipeline_status]);

  const app = state.applicant || {};

  const getStatusLabel = (stage) => {
    if (stage === 'error') return { cls: 'status-failed', lbl: 'Failed' };
    if (stage === 'system' || stage === 'thought') return { cls: 'status-info', lbl: 'Info' };
    if (stage === 'human_gate') return { cls: 'status-awaiting', lbl: 'Awaiting' };
    return { cls: 'status-complete', lbl: 'Complete' };
  };

  const getActionName = (stage) => {
    const map = {
      doc: 'Intake', credit: 'Doc Verify', fraud: 'Credit Check',
      risk: 'Fraud Scan', compliance: 'Risk Assess', decision: 'Compliance',
      pricing: 'Decision', communication: 'Pricing', human_gate: 'Human Gate',
      system: 'System', thought: 'Thinking', error: 'Error'
    };
    return map[stage] || stage;
  };

  return (
    <div>
      <div className="section-label">Pipeline Monitor</div>

      <div className="card">
        <div className="card-title">Applicant Details</div>
        <div className="detail-grid">
          <div>
            <div className="detail-label">Applicant Name</div>
            <div className="detail-value">{app.name || '—'}</div>
          </div>
          <div>
            <div className="detail-label">Employment Type</div>
            <div className="detail-value">{app.employment_type || '—'}</div>
          </div>
          <div>
            <div className="detail-label">Loan Amount</div>
            <div className="detail-value">{app.loan_amount || '—'}</div>
          </div>
          <div>
            <div className="detail-label">Loan Purpose</div>
            <div className="detail-value">{app.loan_purpose || '—'}</div>
          </div>
          <div>
            <div className="detail-label">Application ID</div>
            <div className="detail-value">{state.application_id || '—'}</div>
          </div>
          <div>
            <div className="detail-label">Status</div>
            <div className="detail-value" style={{ textTransform: 'capitalize' }}>
              {state.pipeline_status.replace('_', ' ')}
            </div>
          </div>
        </div>
        <div className="action-row">
          <button className="btn-teal">View Full Application</button>
          <button className="btn-ghost">Archive</button>
        </div>
      </div>

      {state.pipeline_status === 'awaiting_approval' && state.loan_decision && (
        <div className="card" style={{ border: '2px solid var(--teal)' }}>
          <div className="card-title">🔐 Human Loan Officer Review</div>
          
          <div style={{ padding: '1rem', background: 'var(--gray-50)', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span className={`badge badge-${state.loan_decision.recommendation === 'APPROVE' ? 'green' : (state.loan_decision.recommendation === 'DENY' ? 'red' : 'orange')}`}>
              {state.loan_decision.recommendation}
            </span>
            <span style={{ fontSize: '0.85rem', color: 'var(--gray-500)' }}>
              Risk: <strong>{state.loan_decision.risk_category}</strong> &nbsp;|&nbsp; 
              Confidence: <strong>{state.loan_decision.confidence}</strong>
            </span>
          </div>

          <div className="form-grid-2">
            <div>
              <div className="form-row">
                <label>Adjusted Loan Amount (INR)</label>
                <input type="number" value={adjAmount} onChange={e => setAdjAmount(Number(e.target.value))} />
              </div>
              <div className="form-row">
                <label>Adjusted Tenure (Months)</label>
                <input type="number" value={adjTenure} onChange={e => setAdjTenure(Number(e.target.value))} />
              </div>
            </div>
            
            <div style={{ background: 'var(--gray-50)', padding: '1rem', borderRadius: '8px' }}>
              <div className="form-row" style={{ marginBottom: '0.5rem' }}>
                <label>Officer Sign-off</label>
                <input type="text" placeholder="Your Name" value={officerName} onChange={e => setOfficerName(e.target.value)} />
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem', fontSize: '0.85rem' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input type="checkbox" checked={checks.kyc} onChange={e => setChecks({...checks, kyc: e.target.checked})} />
                  KYC verified and applicant identity confirmed
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input type="checkbox" checked={checks.afford} onChange={e => setChecks({...checks, afford: e.target.checked})} />
                  Interest rate and EMI affordability reviewed
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input type="checkbox" checked={checks.rbi} onChange={e => setChecks({...checks, rbi: e.target.checked})} />
                  Lending terms compliant with RBI guidelines
                </label>
              </div>
            </div>
          </div>

          {!showOverride ? (
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
              <button 
                className="btn-teal" 
                style={{ flex: 1 }}
                disabled={!officerName || !checks.kyc || !checks.afford || !checks.rbi}
                onClick={handleApprove}
              >
                ✅ Approve & Finalize
              </button>
              <button 
                className="btn-outline" 
                style={{ flex: 1, borderColor: 'var(--red)', color: 'var(--red)' }}
                disabled={!officerName}
                onClick={() => setShowOverride(true)}
              >
                ❌ Reject / Override
              </button>
            </div>
          ) : (
            <div style={{ marginTop: '1.5rem', padding: '1rem', border: '1px solid var(--red)', borderRadius: '8px', background: '#fff5f5' }}>
              <div className="form-row">
                <label style={{ color: 'var(--red)' }}>Rejection / Override Reason</label>
                <input type="text" value={overrideReason} onChange={e => setOverrideReason(e.target.value)} placeholder="Required for audit trail..." />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button className="btn-danger" style={{ flex: 1 }} disabled={!overrideReason} onClick={handleReject}>
                  Confirm Rejection
                </button>
                <button className="btn-outline" style={{ flex: 1 }} onClick={() => setShowOverride(false)}>
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {state.pipeline_status === 'complete' && (
        <div className="card" style={{ background: '#ecfdf5', border: '1px solid var(--green)', textAlign: 'center' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🎉</div>
          <div className="card-title" style={{ color: 'var(--green)' }}>Application Finalized</div>
          <p style={{ color: 'var(--gray-500)', fontSize: '0.9rem' }}>The decision has been logged to the immutable audit trail.</p>
        </div>
      )}

      <div className="card">
        <div className="card-title">Agent Pipeline History</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Status</th>
                <th>Agent Node</th>
                <th>Action</th>
                <th style={{ textAlign: 'right' }}>Output Preview</th>
              </tr>
            </thead>
            <tbody>
              {state.agent_messages.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', color: '#9ca3af', padding: '2rem 0' }}>
                    No active applications. Submit an application to start the pipeline.
                  </td>
                </tr>
              ) : (
                [...state.agent_messages].reverse().map((msg, idx) => {
                  const { cls, lbl } = getStatusLabel(msg.stage);
                  const preview = (msg.text || '').split('\n').filter(l => l.trim() && !l.trim().startsWith('@'))[0] || (msg.text || '').substring(0, 100);
                  
                  return (
                    <tr key={idx}>
                      <td>{msg.time}</td>
                      <td className={cls}>{lbl}</td>
                      <td>{msg.sender_name}</td>
                      <td>{getActionName(msg.stage)}</td>
                      <td className="bold" style={{ textAlign: 'right' }}>
                        {preview.length > 70 ? preview.substring(0, 70) + '…' : preview}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
        <div className="load-more-wrap">
          <button className="btn-load-more" onClick={pollBand} disabled={loading}>
            {loading ? 'Polling...' : 'Poll Latest Updates'}
          </button>
        </div>
      </div>
    </div>
  );
}
