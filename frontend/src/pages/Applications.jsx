import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function Applications() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    applicant_name: '',
    applicant_age: 30,
    monthly_income: 75000,
    currency: 'INR',
    employment_type: 'salaried',
    employer_name: '',
    years_employed: 3.0,
    loan_amount_requested: 500000,
    loan_purpose: 'personal',
    loan_tenure_months: 60,
    existing_debt_monthly: 0,
    credit_score: 0,
    collateral_offered: '',
    band_chat_id: '',
    intake_handle: '',
    band_human_key: '',
    demo_safe_mode: true,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadDemo = async (scenario) => {
    try {
      const res = await axios.get(`/api/demo/${scenario}`);
      setFormData(prev => ({
        ...prev,
        ...res.data,
        demo_scenario: scenario
      }));
    } catch (e) {
      console.error(e);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await axios.post('/api/application/submit', formData);
      navigate('/pipeline');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' ? Number(value) : value)
    }));
  };

  return (
    <div>
      <div className="section-label">New Application</div>

      <div className="demo-row">
        <div className="demo-btn active-good" onClick={() => loadDemo('good')}>✅ Good Applicant</div>
        <div className="demo-btn active-border" onClick={() => loadDemo('borderline')}>⚠️ Borderline</div>
        <div className="demo-btn active-risk" onClick={() => loadDemo('highrisk')}>❌ High Risk</div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="card">
          <div className="card-title">Applicant Details</div>
          <div className="form-grid-3">
            <div className="form-row">
              <label>Full Name</label>
              <input type="text" name="applicant_name" value={formData.applicant_name} onChange={handleChange} required />
            </div>
            <div className="form-row">
              <label>Age</label>
              <input type="number" name="applicant_age" value={formData.applicant_age} onChange={handleChange} />
            </div>
            <div className="form-row">
              <label>Currency</label>
              <select name="currency" value={formData.currency} onChange={handleChange}>
                <option value="INR">INR</option>
                <option value="USD">USD</option>
              </select>
            </div>
            <div className="form-row">
              <label>Credit Score</label>
              <input type="number" name="credit_score" value={formData.credit_score} onChange={handleChange} />
            </div>
            <div className="form-row">
              <label>Employment Type</label>
              <select name="employment_type" value={formData.employment_type} onChange={handleChange}>
                <option value="salaried">Salaried</option>
                <option value="self_employed">Self Employed</option>
                <option value="business_owner">Business Owner</option>
                <option value="unemployed">Unemployed</option>
              </select>
            </div>
            <div className="form-row">
              <label>Employer / Business</label>
              <input type="text" name="employer_name" value={formData.employer_name} onChange={handleChange} />
            </div>
            <div className="form-row">
              <label>Monthly Income</label>
              <input type="number" name="monthly_income" value={formData.monthly_income} onChange={handleChange} />
            </div>
            <div className="form-row">
              <label>Years Employed</label>
              <input type="number" name="years_employed" step="0.5" value={formData.years_employed} onChange={handleChange} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Loan Request</div>
          <div className="form-grid-3">
            <div className="form-row">
              <label>Loan Amount</label>
              <input type="number" name="loan_amount_requested" value={formData.loan_amount_requested} onChange={handleChange} />
            </div>
            <div className="form-row">
              <label>Loan Purpose</label>
              <select name="loan_purpose" value={formData.loan_purpose} onChange={handleChange}>
                <option value="home">Home</option>
                <option value="vehicle">Vehicle</option>
                <option value="education">Education</option>
                <option value="personal">Personal</option>
                <option value="business">Business</option>
              </select>
            </div>
            <div className="form-row">
              <label>Existing Monthly Debt</label>
              <input type="number" name="existing_debt_monthly" value={formData.existing_debt_monthly} onChange={handleChange} />
            </div>
          </div>
          <div className="form-grid-2" style={{ marginTop: '1.2rem' }}>
            <div className="form-row">
              <label>Tenure (months) - {formData.loan_tenure_months}</label>
              <input type="range" name="loan_tenure_months" min="6" max="360" step="6" value={formData.loan_tenure_months} onChange={handleChange} />
            </div>
            <div className="form-row">
              <label>Collateral Offered (optional)</label>
              <input type="text" name="collateral_offered" value={formData.collateral_offered} onChange={handleChange} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Band Connection</div>
          <div className="form-grid-2">
            <div className="form-row">
              <label>Band Chat / Room ID</label>
              <input type="text" name="band_chat_id" autoComplete="new-password" value={formData.band_chat_id} onChange={handleChange} />
            </div>
            <div className="form-row">
              <label>Intake Agent Handle (@mention)</label>
              <input type="text" name="intake_handle" autoComplete="off" value={formData.intake_handle} onChange={handleChange} />
            </div>
            <div className="form-row">
              <label>Band Human API Key</label>
              <input type="password" name="band_human_key" autoComplete="new-password" placeholder="Leave blank if set in .env" value={formData.band_human_key} onChange={handleChange} />
            </div>
            <div className="form-row checkbox-row" style={{ marginTop: '1.5rem' }}>
              <input type="checkbox" id="safe_mode" name="demo_safe_mode" checked={formData.demo_safe_mode} onChange={handleChange} />
              <label htmlFor="safe_mode">🛡️ Demo-safe Mode (Simulated Replay)</label>
            </div>
          </div>
          <div style={{ marginTop: '1.5rem' }}>
            <button type="submit" className="btn-teal" disabled={loading} style={{ width: '100%' }}>
              {loading ? 'Submitting...' : '🚀 Submit Application'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
