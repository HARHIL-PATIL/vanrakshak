import { NavLink } from 'react-router-dom';
import { useState } from 'react';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: '🏠' },
  { path: '/alerts', label: 'Alerts', icon: '⚠️' },
  { path: '/incidents', label: 'Incidents', icon: '📋' },
  { path: '/compensation', label: 'Compensation', icon: '💰' },
  { path: '/agents', label: 'Agent Monitor', icon: '🤖' },
  { path: '/demo', label: 'Demo Scenario', icon: '🎬' },
];

export default function Sidebar() {
  const [role, setRole] = useState('Forest Officer');

  return (
    <aside className="app-sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 22 }}>🌿</span>
          <div>
            <div className="sidebar-logo-title">VanRakshak AI</div>
            <div className="sidebar-logo-sub">Gir Forest HWC Platform</div>
          </div>
        </div>
        <div className="sidebar-demo-badge">⚡ DEMO MODE</div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Navigation</div>
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `sidebar-nav-item${isActive ? ' active' : ''}`
            }
          >
            <span className="sidebar-nav-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Role Selector */}
      <div className="sidebar-role-selector">
        <div className="sidebar-role-label">Current Role (Visual Only)</div>
        <select
          className="sidebar-role-select"
          value={role}
          onChange={(e) => setRole(e.target.value)}
        >
          <option>Forest Officer</option>
          <option>Villager</option>
          <option>Admin</option>
        </select>
      </div>

      {/* System status */}
      <div className="sidebar-status">
        <div className="status-dot online" />
        <span>System Operational</span>
      </div>
      <div className="sidebar-status" style={{ paddingTop: 0 }}>
        <div className="status-dot warning" />
        <span>Backend: localhost:8000</span>
      </div>
    </aside>
  );
}
