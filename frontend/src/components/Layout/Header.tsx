import { useEffect, useState } from 'react';
import { isBackendOnline } from '../../api/client';

export default function Header() {
  const [time, setTime] = useState(() => new Date().toLocaleTimeString());

  useEffect(() => {
    const id = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="app-header">
      <div style={{ flex: 1, minWidth: 0 }}>
        <div className="header-title">
          VanRakshak AI — Gir Forest Human–Wildlife Conflict Mitigation Platform
        </div>
        <div className="header-sub">
          DEMO MODE | Sample Data Only — Not Connected to Live Forest Infrastructure
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
        <span className="header-badge demo">⚡ DEMO</span>
        <span className="header-badge ai">🤖 AI ACTIVE</span>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '4px 10px',
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: 4,
          }}
        >
          <div
            className="status-dot"
            style={{
              background: isBackendOnline() ? 'var(--accent-green)' : 'var(--accent-red)',
            }}
          />
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            {isBackendOnline() ? 'API Online' : 'API Offline'}
          </span>
        </div>

        <span className="header-time">{time}</span>
      </div>
    </header>
  );
}
