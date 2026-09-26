import { useState, useEffect } from 'react';
import api from '../api';

export default function DatabaseViewer() {
  const [data, setData] = useState({
    roles: [],
    salaryBands: [],
    offers: [],
    candidates: []
  });

  const loadData = async () => {
    try {
      const [r, sb, o, c] = await Promise.all([
        api.get('/db/roles'),
        api.get('/db/salary_bands'),
        api.get('/db/offers'),
        api.get('/candidates')
      ]);
      setData({
        roles: r.data,
        salaryBands: sb.data,
        offers: o.data,
        candidates: c.data
      });
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="page-container fade-in">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <span>🗄️</span> Raw Database Viewer
      </h1>
      <p className="mb-6 text-gray-600">
        This is a read-only view of the Supabase database. Used to show before/after state when the AI agent silently tampers with a record via `update_candidate`.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-bold text-lg mb-2">Candidates</h2>
          <div className="overflow-x-auto">
            <table className="data-table text-xs">
              <thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Score</th><th>Notes</th></tr></thead>
              <tbody>
                {data.candidates.map(x => (
                  <tr key={x.id}>
                    <td>{x.id}</td><td>{x.name}</td><td>{x.status}</td><td>{x.interview_score}</td>
                    <td className="max-w-[150px] truncate" title={x.notes}>{x.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <h2 className="font-bold text-lg mb-2">Salary Bands</h2>
          <table className="data-table text-xs">
            <thead><tr><th>Role ID</th><th>Min</th><th>Max</th></tr></thead>
            <tbody>
              {data.salaryBands.map(x => (
                <tr key={x.id}>
                  <td>{x.role_id}</td><td>${x.min_salary.toLocaleString()}</td><td>${x.max_salary.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
}
