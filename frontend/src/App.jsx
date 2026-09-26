import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import ApplyPage from './pages/ApplyPage';
import RecruiterDashboard from './pages/RecruiterDashboard';
import AttackerInbox from './pages/AttackerInbox';
import DatabaseViewer from './pages/DatabaseViewer';

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <nav className="navbar">
          <div className="font-bold text-lg" style={{ color: 'var(--primary)' }}>
            TalentDesk AI
          </div>
          <div className="nav-links">
            <NavLink to="/apply" className={({isActive}) => isActive ? 'active' : ''}>Apply</NavLink>
            <NavLink to="/" className={({isActive}) => isActive ? 'active' : ''}>Recruiter Dashboard</NavLink>
            <NavLink to="/inbox" className={({isActive}) => isActive ? 'active' : ''}>Attacker Inbox</NavLink>
            <NavLink to="/db" className={({isActive}) => isActive ? 'active' : ''}>DB Viewer</NavLink>
          </div>
        </nav>

        <main style={{ flex: 1 }}>
          <Routes>
            <Route path="/apply" element={<ApplyPage />} />
            <Route path="/" element={<RecruiterDashboard />} />
            <Route path="/inbox" element={<AttackerInbox />} />
            <Route path="/db" element={<DatabaseViewer />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
