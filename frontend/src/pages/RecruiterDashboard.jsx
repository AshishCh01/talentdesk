import { useState, useEffect, useRef } from 'react';
import api from '../api';

export default function RecruiterDashboard() {
  const [candidates, setCandidates] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [activityLog, setActivityLog] = useState([]);
  
  const chatBottomRef = useRef(null);

  // Load initial candidates
  const loadCandidates = () => {
    api.get('/candidates').then(res => setCandidates(res.data)).catch(console.error);
  };

  useEffect(() => {
    loadCandidates();

    // SSE connection for live activity
    const eventSource = new EventSource(`${api.defaults.baseURL || 'http://localhost:8000'}/activity`);
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setActivityLog(prev => [...prev, data]);
        // Also refresh candidates since a tool might have updated them
        if (data.tool_name === 'update_candidate') {
          loadCandidates();
        }
      } catch (err) {
        console.error("Error parsing SSE data", err);
      }
    };

    return () => eventSource.close();
  }, []);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isTyping]);

  const sendChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const message = chatInput;
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: message }]);
    setIsTyping(true);

    try {
      const res = await api.post('/copilot/chat', { message });
      setChatHistory(prev => [...prev, { role: 'agent', content: res.data.reply }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'agent', content: `Error: ${err.response?.data?.detail || err.message}` }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="dashboard-layout fade-in">
      <div className="dashboard-main">
        <h2 className="text-xl font-bold mb-4">Candidate Pipeline</h2>
        <div className="card overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Role ID</th>
                <th>Status</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map(c => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{c.name}</td>
                  <td>{c.role_id}</td>
                  <td>
                    <span className={`badge badge-${c.status}`}>{c.status}</span>
                  </td>
                  <td>{c.interview_score !== null ? c.interview_score : '-'}</td>
                </tr>
              ))}
              {candidates.length === 0 && (
                <tr>
                  <td colSpan="5" className="text-center text-gray-500 py-4">No candidates found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <h2 className="text-xl font-bold mt-8 mb-4">Live Tool Activity (Agent Logs)</h2>
        <div className="activity-log card">
          {activityLog.length === 0 ? (
            <p className="text-gray-500 italic">Waiting for AI activity...</p>
          ) : (
            activityLog.map((log, i) => (
              <div key={i} className="log-entry">
                <span className="log-time">{new Date(log.created_at).toLocaleTimeString()}</span>
                <span className="log-tool font-mono">{log.tool_name}</span>
                <pre className="log-args">{JSON.stringify(log.arguments, null, 2)}</pre>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="dashboard-sidebar card flex-col">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <span className="sparkle">✨</span> TalentDesk Copilot
        </h2>
        
        <div className="chat-window">
          {chatHistory.length === 0 && (
            <p className="text-gray-500 text-center mt-10 italic text-sm">
              Ask me to screen candidates, check salaries, or send emails.
            </p>
          )}
          {chatHistory.map((msg, i) => (
            <div key={i} className={`chat-bubble chat-${msg.role}`}>
              {msg.content}
            </div>
          ))}
          {isTyping && (
            <div className="chat-bubble chat-agent typing-indicator">
              <span>.</span><span>.</span><span>.</span>
            </div>
          )}
          <div ref={chatBottomRef} />
        </div>

        <form onSubmit={sendChat} className="chat-input-area">
          <input 
            type="text" 
            placeholder="e.g. Screen today's applicants..."
            value={chatInput}
            onChange={e => setChatInput(e.target.value)}
            disabled={isTyping}
          />
          <button type="submit" disabled={isTyping || !chatInput.trim()} className="btn-primary">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
