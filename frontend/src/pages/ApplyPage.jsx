import { useState, useEffect } from 'react';
import api from '../api';

export default function ApplyPage() {
  const [roles, setRoles] = useState([]);
  const [formData, setFormData] = useState({ name: '', email: '', role_id: '' });
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    api.get('/db/roles').then((res) => setRoles(res.data)).catch(console.error);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setStatus({ type: 'error', message: 'Please select a resume (PDF).' });
      return;
    }

    const data = new FormData();
    data.append('name', formData.name);
    data.append('email', formData.email);
    data.append('role_id', formData.role_id);
    data.append('resume', file);

    setStatus({ type: 'loading', message: 'Submitting application...' });
    try {
      await api.post('/apply', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setStatus({ type: 'success', message: 'Application submitted successfully!' });
      setFormData({ name: '', email: '', role_id: '' });
      setFile(null);
    } catch (err) {
      setStatus({ type: 'error', message: err.response?.data?.detail || 'Application failed.' });
    }
  };

  return (
    <div className="page-container">
      <div className="card max-w-md mx-auto fade-in">
        <h1 className="text-2xl font-bold mb-4">Apply for a Role</h1>
        <form onSubmit={handleSubmit} className="flex-col gap-4">
          <div className="input-group">
            <label>Name</label>
            <input 
              required 
              type="text" 
              value={formData.name} 
              onChange={(e) => setFormData({...formData, name: e.target.value})} 
            />
          </div>
          <div className="input-group">
            <label>Email</label>
            <input 
              required 
              type="email" 
              value={formData.email} 
              onChange={(e) => setFormData({...formData, email: e.target.value})} 
            />
          </div>
          <div className="input-group">
            <label>Role</label>
            <select 
              required 
              value={formData.role_id} 
              onChange={(e) => setFormData({...formData, role_id: e.target.value})}
            >
              <option value="">-- Select a role --</option>
              {roles.map(r => (
                <option key={r.id} value={r.id}>{r.title} ({r.department})</option>
              ))}
            </select>
          </div>
          <div className="input-group">
            <label>Résumé (PDF)</label>
            <input 
              required 
              type="file" 
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files[0])} 
            />
          </div>
          
          {status && (
            <div className={`alert alert-${status.type}`}>
              {status.message}
            </div>
          )}

          <button type="submit" className="btn-primary" disabled={status?.type === 'loading'}>
            Submit Application
          </button>
        </form>
      </div>
    </div>
  );
}
