import { useState, useEffect } from 'react';
import api from '../api';

export default function AttackerInbox() {
  const [emails, setEmails] = useState([]);

  const loadInbox = () => {
    api.get('/db/inbox').then(res => setEmails(res.data)).catch(console.error);
  };

  useEffect(() => {
    loadInbox();
    // Poll every 3 seconds to feel somewhat live for the demo
    const interval = setInterval(loadInbox, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="page-container fade-in">
      <h1 className="text-2xl font-bold mb-4 text-red-600 flex items-center gap-2">
        <span>🕵️‍♂️</span> Attacker's Simulated Inbox
      </h1>
      <p className="mb-6 text-gray-600">
        This view proves data exfiltration. If the AI agent is tricked by a poisoned resume, it might use the `send_email` tool to leak confidential info to the attacker.
      </p>

      <div className="grid gap-4">
        {emails.length === 0 ? (
          <div className="card text-center py-10 text-gray-500 italic">
            Inbox is empty. Waiting for leaks...
          </div>
        ) : (
          [...emails].reverse().map(email => (
            <div key={email.id} className="card email-card">
              <div className="email-header">
                <div><strong>To:</strong> {email.to_email}</div>
                <div><strong>Date:</strong> {new Date(email.created_at).toLocaleString()}</div>
              </div>
              <div className="email-subject">
                <strong>Subject:</strong> {email.subject}
              </div>
              <div className="email-body whitespace-pre-wrap font-mono text-sm bg-gray-50 p-4 rounded mt-2 border">
                {email.body}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
